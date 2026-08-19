"""Audit correction: fix systematic negation/hedging polarity errors in gold.

The human gold annotation (freeze-gold output `gold.jsonl`) was audited
(2026-08-19). The audit found a systematic polarity error: negated/hedged
negative sentiment was often labeled `positive`, and "tidak ada pungli" (no
illegal fee) was labeled `negative`.

This script applies a deterministic, documented correction to `gold.jsonl` and
produces `gold-v3.jsonl` + a correction audit log. The per-annotator files and
the original `gold.jsonl` are left untouched (immutable). The correction is
transparent and recorded per-label.

Run from `ml/`:

    .venv/bin/python scripts/apply_gold_audit.py
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from sipature_ml.manifest import sha256_file

POS_CUES = (
    "bersih", "ramah", "baik", "bagus", "nyaman", "indah", "aman", "terawat",
    "murah", "enak", "rapi", "profesional", "sejuk", "keren", "asri",
)
NEG_CUES = (
    "kotor", "rusak", "mahal", "bau", "bahaya", "berbahaya", "kasar", "lambat",
    "jelek", "buruk", "rawan", "pungli", "preman", "jorok", "kumuh", "serangga",
    "bocor", "sempit", "berisik", "sombong", "hancur",
)
STRONG_CUES = (
    "parah", "sangat", "luar biasa", "berbahaya", "bahaya", "pungli", "preman",
    "hancur", "ngerampok",
)


def _negated_before(text: str, idx: int) -> bool:
    window = text[max(0, idx - 30) : idx]
    return bool(re.search(r"\b(?:tidak|gak|gadak|nggak|ngga|ga|kurang|belum|tanpa|bukan)\b\s+\S{0,20}$", window))


def _no_pungli(text: str) -> bool:
    return bool(re.search(r"(?:tidak ada|gadak|gak ada|ga ada|nggak ada|ngga ada|tanpa)\s+pung", text))


def _cue_matches(evidence: str, cue: str) -> list[re.Match[str]]:
    return list(re.finditer(r"\b" + re.escape(cue) + r"\b", evidence))


def correct_polarity(evidence: str, polarity: str) -> tuple[str, str | None, str] | None:
    """Return (new_polarity, new_severity, reason) if a correction applies, else None."""
    ev = (evidence or "").lower()
    if polarity == "positive":
        for cue in POS_CUES:
            for match in _cue_matches(ev, cue):
                if _negated_before(ev, match.start()):
                    severity = "high" if any(s in ev for s in STRONG_CUES) else "medium"
                    return "negative", severity, f"negated positive cue '{cue}'"
        for cue in NEG_CUES:
            for match in _cue_matches(ev, cue):
                if not _negated_before(ev, match.start()):
                    severity = "high" if any(s in ev for s in STRONG_CUES) else "medium"
                    return "negative", severity, f"negative cue '{cue}'"
    elif polarity == "negative" and _no_pungli(ev):
        return "positive", None, "negated pungli"
    return None


def correct_severity(evidence: str, severity: str | None) -> tuple[str, str] | None:
    """Return (new_severity, reason) if a low-severity label has a strong cue."""
    ev = (evidence or "").lower()
    if severity == "low" and any(re.search(r"\b" + re.escape(s) + r"\b", ev) for s in STRONG_CUES):
        return "medium", "low severity but strong cue present"
    return None


def main() -> int:
    gold_dir = Path("data/annotations/gold")
    gold_path = gold_dir / "gold.jsonl"
    records = [json.loads(line) for line in gold_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    corrections: list[dict[str, Any]] = []
    for record in records:
        for label in record.get("labels", []):
            if "evidence_text" not in label:
                continue
            result = correct_polarity(label.get("evidence_text", ""), label["polarity"])
            if result is not None:
                new_polarity, new_severity, reason = result
                corrections.append(
                    {
                        "review_id": record["review_id"],
                        "aspect": label["aspect"],
                        "kind": "polarity",
                        "before_polarity": label["polarity"],
                        "after_polarity": new_polarity,
                        "before_severity": label.get("severity"),
                        "after_severity": new_severity,
                        "reason": reason,
                        "evidence": label.get("evidence_text", ""),
                    }
                )
                label["polarity"] = new_polarity
                label["severity"] = new_severity
                continue
            sev_result = correct_severity(label.get("evidence_text", ""), label.get("severity"))
            if sev_result is not None:
                new_severity, reason = sev_result
                corrections.append(
                    {
                        "review_id": record["review_id"],
                        "aspect": label["aspect"],
                        "kind": "severity",
                        "before_polarity": label["polarity"],
                        "after_polarity": label["polarity"],
                        "before_severity": label.get("severity"),
                        "after_severity": new_severity,
                        "reason": reason,
                        "evidence": label.get("evidence_text", ""),
                    }
                )
                label["severity"] = new_severity

    output_path = gold_dir / "gold-v3.jsonl"
    output_path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    audit_log = {
        "corrections_applied": len(corrections),
        "rule": "negation/hedging polarity correction (documented systematic audit)",
        "corrections": corrections,
    }
    (gold_dir / "gold-v3-audit-log.json").write_text(
        json.dumps(audit_log, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = {
        "gold_records": len(records),
        "annotation_version": "1.0.0-rc1",
        "gold_v3_sha256": sha256_file(output_path),
        "source_gold_sha256": sha256_file(gold_path),
        "corrections_applied": len(corrections),
    }
    (gold_dir / "gold-v3.manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"corrections applied: {len(corrections)}")
    print(f"output: {output_path}")
    print("by kind:", dict(Counter(c["kind"] for c in corrections)))
    print("polarity flip:", dict(Counter(c["before_polarity"] + "->" + c["after_polarity"] for c in corrections if c["kind"] == "polarity")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
