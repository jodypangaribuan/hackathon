"""Siapkan queue adjudikasi dari tiga file gold annotation.

Auto-adjudikasi review yang secara semantik (aspect/polarity/severity) sudah
disepakati (unanimous atau majority 2/3) dengan menormalisasi span evidence ke
satu nilai kanonik. Sisanya (tie semantik 3-arah + double-annotated yang
berbeda semantik) ditulis ke `adjudication_queue.json` untuk adjudikasi manual.

Catatan: `freeze_gold` membandingkan label LENGKAP termasuk `evidence_text`,
sehingga perbedaan span evidence murni pun dianggap selisih dan wajib
diadjudikasi. Rule di sini menutup kasus itu secara otomatis.

Jalankan dari `ml/`:
    python ../tools/adjudicator/prepare_adjudication.py \
        data/annotations/gold/A1_completed.jsonl \
        data/annotations/gold/A2_completed.jsonl \
        data/annotations/gold/A3_completed.jsonl \
        --agreement data/annotations/gold/agreement.json \
        --out-dir data/annotations/gold
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path


def _semantic_signature(record: dict) -> frozenset:
    return frozenset(
        (label["aspect"], label["polarity"], label["severity"]) for label in record["labels"]
    )


def _full_signature(record: dict) -> frozenset:
    return frozenset(json.dumps(label, sort_keys=True) for label in record["labels"])


def _canonicalize(records: list[dict], signature: frozenset) -> list[dict]:
    """Pilih satu label final dari annotator yang berbagi `signature` semantik.

    Untuk tiap aspect, ambil evidence terbanyak (mode), tie-break ke annotator
    dengan ID terkecil (A1 < A2 < A3).
    """
    annotators = sorted(records, key=lambda r: r["annotator_id"])
    evidence_by_aspect: dict[str, list[tuple[int, str]]] = collections.defaultdict(list)
    for order, record in enumerate(annotators):
        for label in record["labels"]:
            if (label["aspect"], label["polarity"], label["severity"]) in signature:
                evidence_by_aspect[label["aspect"]].append((order, label["evidence_text"]))
    labels: list[dict] = []
    for aspect in sorted(evidence_by_aspect):
        evidences = [ev for _, ev in evidence_by_aspect[aspect]]
        mode = collections.Counter(evidences).most_common(1)[0][0]
        polarity, severity = next(
            (p, s) for a, p, s in signature if a == aspect
        )
        labels.append(
            {
                "aspect": aspect,
                "polarity": polarity,
                "severity": severity,
                "evidence_text": mode,
            }
        )
    return labels


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--agreement", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    by_review: dict[str, list[dict]] = collections.defaultdict(list)
    for path in args.paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                by_review[record["review_id"]].append(record)

    def _sorted_labels(record: dict) -> list[dict]:
        return sorted(record["labels"], key=lambda label: label["aspect"])

    # Disagreement dalam arti `freeze_gold`: label lengkap (termasuk evidence) beda.
    disagreement_ids: set[str] = set()
    for review_id, records in by_review.items():
        if len(records) < 2:
            continue
        base = _sorted_labels(records[0])
        if any(_sorted_labels(r) != base for r in records[1:]):
            disagreement_ids.add(review_id)

    auto: list[dict] = []
    pending: list[dict] = []
    for review_id in sorted(disagreement_ids):
        records = by_review[review_id]
        signatures = collections.Counter(_semantic_signature(r) for r in records)
        top_signature, top_count = signatures.most_common(1)[0]
        if top_count >= 2:
            chosen = [r for r in records if _semantic_signature(r) == top_signature]
            winner = chosen[0]
            note = (
                "auto-adjudicated: unanimous aspect/polarity/severity, evidence canonicalized"
                if top_count == len(records)
                else "auto-adjudicated: 2/3 semantic majority, evidence canonicalized"
            )
            auto.append(
                {
                    "review_id": review_id,
                    "annotator_id": "ADJ",
                    "destination_id": winner["destination_id"],
                    "text": winner["text"],
                    "rating_context": winner.get("rating_context"),
                    "labels": _canonicalize(chosen, top_signature),
                    "annotation_version": winner["annotation_version"],
                    "annotation_status": "adjudicated",
                    "review_notes": note,
                }
            )
            continue

        ordered = sorted(records, key=lambda x: x["annotator_id"])
        first = ordered[0]
        pending.append(
            {
                "review_id": review_id,
                "destination_id": first["destination_id"],
                "text": first["text"],
                "rating_context": first.get("rating_context"),
                "annotation_version": first["annotation_version"],
                "annotators": {
                    r["annotator_id"]: {"labels": r["labels"]} for r in ordered
                },
            }
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    auto_path = args.out_dir / "adjudicated_auto.jsonl"
    with auto_path.open("w", encoding="utf-8") as handle:
        for record in auto:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    queue_path = args.out_dir / "adjudication_queue.json"
    queue_path.write_text(json.dumps(pending, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"auto-adjudicated: {len(auto)} -> {auto_path}")
    print(f"pending manual:   {len(pending)} -> {queue_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
