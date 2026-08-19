"""High-precision gold-annotation audit (polarity, severity, aspect).

Refined over the first pass: word-boundary negation detection, contrast-marker
clause splitting, and aspect-vs-seed-term verification. Aim is precision over
recall — each flag should be a likely real error, not a heuristic echo.

Run from `ml/`:
    .venv/bin/python scripts/audit_gold.py
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from sipature_ml.config import load_config

FILES = {aid: Path(f"data/annotations/gold/{aid}_completed.jsonl") for aid in ("A1", "A2", "A3")}

POS_CUES = ("bersih", "ramah", "baik", "bagus", "nyaman", "indah", "aman", "terawat", "murah", "enak", "rapi", "profesional", "sejuk", "keren", "asri", "luas")
NEG_CUES = ("kotor", "rusak", "mahal", "bau", "bahaya", "kasar", "lambat", "jelek", "buruk", "rawan", "pungli", "preman", "jorok", "kumuh", "bocor", "sempit", "berisik", "sombong", "hancur")
STRONG_CUES = ("parah", "sangat", "luar biasa", "berbahaya", "bahaya", "pungli", "preman", "hancur", "ngerampok", "membludak")
CONTRASTS = ("tetapi", "tapi", "namun", "walaupun", "meskipun", "padahal", "sayangnya")
NEG_PAT = r"\b(?:tidak|gak|gadak|nggak|ngga|ga|kurang|belum|tanpa|bukan)\b"


def _clause_for(evidence: str, cue_idx: int) -> str:
    """Return the clause containing the cue (split on contrast markers)."""
    splits = re.split(r"\b(?:tetapi|tapi|namun|walaupun|meskipun|padahal|sayangnya|walau)\b", evidence)
    pos = 0
    for clause in splits:
        start = pos
        end = pos + len(clause)
        if start <= cue_idx < end:
            return clause
        pos = end + 1
    return evidence


def _negated_in_clause(clause: str, cue: str) -> bool:
    for m in re.finditer(r"\b" + re.escape(cue) + r"\b", clause):
        window = clause[max(0, m.start() - 30): m.start()]
        if re.search(NEG_PAT + r"\s+\S{0,20}$", window):
            return True
    return False


def _cue_in_clause(clause: str, cues: tuple[str, ...]) -> bool:
    return any(re.search(r"\b" + re.escape(c) + r"\b", clause) for c in cues)


def _no_pungli(text: str) -> bool:
    return bool(re.search(r"\b(?:tidak ada|gadak|gak ada|ga ada|nggak ada|tanpa)\s+pung", text))


def _seed_hits(text: str, taxonomy: dict[str, Any]) -> dict[str, list[str]]:
    lowered = text.casefold()
    return {
        aspect: [t for t in defn["seed_terms"] if re.search(rf"(?<!\w){re.escape(t.casefold())}(?!\w)", lowered)]
        for aspect, defn in taxonomy["aspect_definitions"].items()
    }


def main() -> int:
    taxonomy = load_config("taxonomy")
    recs = {aid: [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
            for aid, p in FILES.items()}

    flags: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for aid, rs in recs.items():
        for r in rs:
            for lab in r["labels"]:
                ev = (lab.get("evidence_text") or "").lower()
                pol = lab["polarity"]
                sev = lab.get("severity")
                aspect = lab["aspect"]

                # ---- polarity: clause-aware negation/hedging ----
                if pol == "positive":
                    for cue in POS_CUES:
                        for m in re.finditer(r"\b" + re.escape(cue) + r"\b", ev):
                            clause = _clause_for(ev, m.start())
                            if _negated_in_clause(clause, cue):
                                flags["polarity_negated_positive"].append({
                                    "annotator": aid, "review_id": r["review_id"], "aspect": aspect,
                                    "polarity": pol, "suggested": "negative", "cue": cue,
                                    "evidence": lab.get("evidence_text", ""), "text": r["text"][:130],
                                })
                                break
                    if aspect not in {f["aspect"] for f in flags["polarity_negated_positive"] if f["review_id"] == r["review_id"]}:
                        for cue in NEG_CUES:
                            for m in re.finditer(r"\b" + re.escape(cue) + r"\b", ev):
                                clause = _clause_for(ev, m.start())
                                if not _negated_in_clause(clause, cue):
                                    flags["polarity_negative_cue_positive"].append({
                                        "annotator": aid, "review_id": r["review_id"], "aspect": aspect,
                                        "polarity": pol, "suggested": "negative", "cue": cue,
                                        "evidence": lab.get("evidence_text", ""), "text": r["text"][:130],
                                    })
                                    break
                if pol == "negative" and _no_pungli(ev):
                    flags["polarity_no_pungli_negative"].append({
                        "annotator": aid, "review_id": r["review_id"], "aspect": aspect,
                        "polarity": pol, "suggested": "positive",
                        "evidence": lab.get("evidence_text", ""), "text": r["text"][:130],
                    })

                # ---- severity: high without strong cue / low with strong cue ----
                if pol == "negative" and sev == "high" and not _cue_in_clause(ev, STRONG_CUES):
                    flags["severity_high_no_strong_cue"].append({
                        "annotator": aid, "review_id": r["review_id"], "aspect": aspect,
                        "severity": sev, "evidence": lab.get("evidence_text", ""), "text": r["text"][:130],
                    })
                if pol == "negative" and sev == "low" and _cue_in_clause(ev, STRONG_CUES):
                    flags["severity_low_with_strong_cue"].append({
                        "annotator": aid, "review_id": r["review_id"], "aspect": aspect,
                        "severity": sev, "evidence": lab.get("evidence_text", ""), "text": r["text"][:130],
                    })

                # ---- aspect: evidence has other aspect's seeds but none of its own ----
                hits = _seed_hits(ev, taxonomy)
                own = hits.get(aspect, [])
                if not own:
                    other = {a: t for a, t in hits.items() if a != aspect and t}
                    if other:
                        flags["possible_wrong_aspect"].append({
                            "annotator": aid, "review_id": r["review_id"], "aspect": aspect,
                            "other_aspect_seeds": {a: t[:4] for a, t in list(other.items())[:2]},
                            "evidence": lab.get("evidence_text", ""), "text": r["text"][:130],
                        })

    def uniq(items, key=("review_id", "aspect")):
        seen = set()
        out = []
        for i in items:
            k = tuple(i[k_] for k_ in key)
            if k in seen:
                continue
            seen.add(k)
            out.append(i)
        return out

    print("=" * 72)
    print("HIGH-PRECISION AUDIT (polarity / severity / aspect)")
    print("=" * 72)
    for cat, items in sorted(flags.items(), key=lambda kv: -len(kv[1])):
        u = uniq(items)
        print(f"\n### {cat}: {len(items)} label-flag, {len(u)} unique")
        for i in u[:5]:
            if cat.startswith("polarity"):
                print(f"  {i['annotator']} [{i['aspect']}] {i['polarity']}->{i['suggested']} cue={i.get('cue')} ev={i['evidence'][:50]!r}")
            elif cat.startswith("severity"):
                print(f"  {i['annotator']} [{i['aspect']}] sev={i['severity']} ev={i['evidence'][:50]!r}")
            else:
                print(f"  {i['annotator']} [{i['aspect']}] other={dict(i['other_aspect_seeds'])} ev={i['evidence'][:50]!r}")

    out = Path("data/annotations/gold/audit-report-v3.json")
    out.write_text(json.dumps({k: uniq(v) for k, v in flags.items()}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nsaved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
