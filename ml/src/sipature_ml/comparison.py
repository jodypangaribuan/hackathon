"""Preliminary (silver) vs Final (gold) baseline score comparison.

The preliminary round reported metrics against the locked silver test (weak
supervision). The final round re-evaluates the same models against the
human-gold reference (`gold.jsonl`), reusing the same leakage-safe split. This
module produces a side-by-side comparison table and figure plus a summary JSON.

Note: gold metrics for keyword and TF-IDF are produced by
`evaluate-gold-baselines`; IndoBERT-on-gold requires GPU and is reported as
"pending" until run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Preliminary (locked silver test) IndoBERT numbers, from the A8 report
# (`docs/indobert-a8-evaluation-report.md`). Gold (final) numbers are pending GPU.
INDOBERT_SILVER = {
    "aspect": {"macro_f1": 0.5247, "micro_f1": 0.5241},
    "polarity": {"macro_f1": 0.7459},
}


def _load_metric(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _round(value: float | None, digits: int = 4) -> float | None:
    return None if value is None else round(value, digits)


def _indobert_gold(metrics_dir: Path) -> dict[str, Any] | None:
    metric = _load_metric(metrics_dir / "indobert-gold-v1-test-metrics.json")
    if metric is None or "macro_f1" not in metric:
        return None
    return {"macro_f1": metric["macro_f1"], "micro_f1": metric["micro_f1"]}


def run_preliminary_final_comparison(
    metrics_dir: Path,
    figure_dir: Path,
) -> dict[str, Any]:
    """Compare preliminary (silver) vs final (gold) macro/micro F1 per model."""
    metrics_dir = Path(metrics_dir)
    figure_dir = Path(figure_dir)

    models: dict[str, dict[str, Any]] = {}
    for key, label in (("keyword", "Keyword"), ("tfidf", "TF-IDF")):
        silver = _load_metric(metrics_dir / f"{key}-silver-v1-test-metrics.json")
        gold = _load_metric(metrics_dir / f"{key}-gold-v1-test-metrics.json")
        models[label] = {
            "preliminary": (
                {"macro_f1": silver["macro_f1"], "micro_f1": silver["micro_f1"]}
                if silver
                else None
            ),
            "final": (
                {"macro_f1": gold["macro_f1"], "micro_f1": gold["micro_f1"]}
                if gold
                else None
            ),
        }
    models["IndoBERT (aspek)"] = {
        "preliminary": INDOBERT_SILVER["aspect"],
        "final": _indobert_gold(metrics_dir),
    }

    notes = [
        "Keyword silver Macro F1 0.9768 is circular against silver rules.",
        "IndoBERT polarity (silver 0.7459) is a separate task and not in the aspect comparison.",
    ]
    if models["IndoBERT (aspek)"]["final"] is None:
        notes.append("IndoBERT final (gold) is pending GPU/Colab execution.")
    else:
        notes.append("IndoBERT final (gold) is inference-only (silver-trained A7 model, no re-tune).")

    summary = {
        "reference": {
            "preliminary": "locked silver test (AI-assisted weak supervision)",
            "final": "human-gold test (3-annotator, freeze-gold), same leakage-safe split",
            "split_version": "silver-split-1.0.0",
        },
        "models": models,
        "notes": notes,
    }

    figure_dir.mkdir(parents=True, exist_ok=True)
    labels = list(models)
    prelim = [models[m]["preliminary"]["macro_f1"] if models[m]["preliminary"] else 0.0 for m in labels]
    final = [models[m]["final"]["macro_f1"] if models[m]["final"] else 0.0 for m in labels]

    x = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars_pre = ax.bar(x - width / 2, prelim, width, label="Preliminary (silver)", color="#EB6834")
    bars_fin = ax.bar(x + width / 2, final, width, label="Final (gold)", color="#2A78D6")
    ax.bar_label(bars_pre, fmt="%.3f", padding=3, fontsize=9)
    ax.bar_label(bars_fin, fmt="%.3f", padding=3, fontsize=9)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Macro F1 (aspect detection)")
    ax.set_title("Preliminary (silver) vs Final (gold) — Macro F1", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    # Mark IndoBERT gold as pending when not yet evaluated.
    if models["IndoBERT (aspek)"]["final"] is None:
        ax.annotate(
            "gold pending (GPU)",
            xy=(x[-1] + width / 2, 0.02),
            xytext=(x[-1] + width / 2, 0.14),
            ha="center",
            fontsize=9,
            color="#2A78D6",
            arrowprops={"arrowstyle": "->", "color": "#2A78D6"},
        )
    fig.tight_layout()
    path = figure_dir / "37_preliminary_vs_final_macro_f1.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    summary["figure"] = path.name

    # Rounded, serializable copy for the summary JSON.
    for stages in models.values():
        for stage, metrics in stages.items():
            if metrics is not None:
                stages[stage] = {
                    "macro_f1": _round(metrics["macro_f1"]),
                    "micro_f1": _round(metrics.get("micro_f1")),
                }
    (figure_dir / "preliminary_final_comparison.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary
