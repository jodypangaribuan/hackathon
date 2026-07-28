"""Report-ready figures for cleaning and entity-resolution results."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _style(ax: plt.Axes, title: str) -> None:
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold", pad=16)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#deded8", linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)


def generate_quality_figures(
    report_dir: Path,
    processed_dir: Path,
    figure_dir: Path,
) -> list[str]:
    figure_dir.mkdir(parents=True, exist_ok=True)
    cleaning = json.loads((report_dir / "cleaning_summary.json").read_text())
    resolution = json.loads((report_dir / "entity_resolution_summary.json").read_text())
    metrics = json.loads((report_dir / "entity_resolution_metrics.json").read_text())
    links = pd.read_parquet(processed_dir / "entity_links.parquet")
    reviews = pd.read_parquet(processed_dir / "canonical_reviews.parquet")
    canonical = pd.read_parquet(processed_dir / "canonical_destinations.parquet")
    outputs: list[str] = []
    blue, orange, green, red, gray, purple = "#2A78D6", "#EB6834", "#1BAF7A", "#D03B3B", "#898781", "#7C6BC4"

    def save(name: str, fig: plt.Figure) -> None:
        _save(fig, figure_dir / name)
        outputs.append(name)

    values = [
        cleaning["reviews"]["raw_records"],
        cleaning["reviews"]["exact_duplicate_excess_removed"],
        cleaning["reviews"]["empty_records_excluded"],
        cleaning["reviews"]["clean_records"],
        cleaning["reviews"]["clean_textual_records"],
    ]
    labels = ["Raw", "Duplikat excess", "Empty excluded", "Clean", "Clean textual"]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(labels, values, color=[blue, red, gray, green, orange])
    ax.bar_label(bars, labels=[f"{value:,}" for value in values], padding=4)
    _style(ax, "Cleaning Funnel Review")
    ax.tick_params(axis="x", rotation=15)
    save("17_cleaning_funnel.png", fig)

    date_values = cleaning["reviews"]["date_parse_status"]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        ["Parsed approximate", "Missing anchor", "Missing published-at"],
        [date_values.get("parsed_approximate", 0), date_values.get("missing_scrape_anchor", 0), date_values.get("missing_published_at", 0)],
        color=[green, orange, gray],
    )
    ax.bar_label(bars, padding=4)
    _style(ax, "Hasil Parsing Waktu Review")
    ax.tick_params(axis="x", rotation=12)
    save("18_relative_date_parsing.png", fig)

    status = links["match_status"].value_counts()
    fig, ax = plt.subplots(figsize=(9, 5))
    order = [item for item in ["auto_match", "human_verified_match", "human_verified_no_match", "manual_review", "unresolved"] if item in status]
    colors = [green, blue, red, purple, gray][: len(order)]
    bars = ax.bar(order, [status[item] for item in order], color=colors)
    ax.bar_label(bars, padding=4)
    _style(ax, "Status Entity Link Setelah Adjudication")
    ax.tick_params(axis="x", rotation=15)
    save("19_entity_link_status.png", fig)

    review_status = reviews.groupby("match_status").size().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(review_status.index, review_status.values, color=[green, blue, gray, purple, red][: len(review_status)])
    ax.bar_label(bars, labels=[f"{value:,}" for value in review_status.values], padding=4)
    _style(ax, "Coverage Linkage pada Clean Review")
    ax.tick_params(axis="x", rotation=15)
    save("20_review_linkage_coverage.png", fig)

    pre = metrics["pre_adjudication"]
    matrix = [[pre["tn"], pre["fp"]], [pre["fn"], pre["tp"]]]
    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(matrix, cmap="Blues")
    ax.set_xticks([0, 1], ["Predicted no-match", "Predicted match"])
    ax.set_yticks([0, 1], ["Actual no-match", "Actual match"])
    for row in range(2):
        for col in range(2):
            ax.text(col, row, str(matrix[row][col]), ha="center", va="center", fontsize=17, fontweight="bold")
    ax.set_title("Reviewed Pair Confusion Matrix Sebelum Adjudication", loc="left", fontsize=14, fontweight="bold", pad=16)
    fig.colorbar(image, ax=ax)
    save("21_entity_review_confusion_matrix.png", fig)

    canonical_status = canonical["canonical_status"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(canonical_status.index, canonical_status.values, color=[blue, gray])
    ax.bar_label(bars, padding=4)
    _style(ax, "Komposisi Canonical Destination")
    ax.tick_params(axis="x", rotation=12)
    save("22_canonical_destination_composition.png", fig)

    summary = {
        "figures": outputs,
        "clean_records": cleaning["reviews"]["clean_records"],
        "canonical_destinations": resolution["canonical_destinations"],
        "reviewed_pair_metrics": metrics,
    }
    (report_dir / "quality_figure_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return outputs
