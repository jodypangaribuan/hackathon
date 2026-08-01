"""Report-ready figures for cleaning and entity-resolution results."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import yaml

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

    review_counts = cleaning["reviews"]
    raw = review_counts["raw_records"]
    duplicate = review_counts["exact_duplicate_excess_removed"]
    empty = review_counts["empty_records_excluded"]
    clean = review_counts["clean_records"]
    textual = review_counts["clean_textual_records"]
    rating_only = review_counts["clean_rating_only_records"]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.axis("off")

    def box(x: float, y: float, text: str, color: str, width: float = 0.19) -> None:
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="white",
            bbox={"boxstyle": "round,pad=0.7", "facecolor": color, "edgecolor": "none"},
            transform=ax.transAxes,
        )

    box(0.11, 0.54, f"Data mentah\n{raw:,} record", blue)
    box(0.50, 0.54, f"Data bersih\n{clean:,} record", green)
    box(0.85, 0.72, f"Review berteks\n{textual:,}", orange)
    box(0.85, 0.35, f"Rating-only\n{rating_only:,}", gray)
    ax.annotate(
        "",
        xy=(0.40, 0.54),
        xytext=(0.22, 0.54),
        xycoords="axes fraction",
        arrowprops={"arrowstyle": "->", "lw": 2, "color": "#4b5563"},
    )
    ax.text(
        0.31,
        0.66,
        f"Dikeluarkan dari data bersih:\n{duplicate:,} duplikat teknis + {empty:,} data kosong",
        ha="center",
        va="bottom",
        fontsize=9.5,
        color="#374151",
        transform=ax.transAxes,
    )
    for target_y in (0.72, 0.35):
        ax.annotate(
            "",
            xy=(0.75, target_y),
            xytext=(0.61, 0.54),
            xycoords="axes fraction",
            arrowprops={"arrowstyle": "->", "lw": 2, "color": "#4b5563"},
        )
    ax.text(
        0.70,
        0.16,
        "Data bersih dipisahkan berdasarkan ketersediaan teks.",
        ha="center",
        va="center",
        fontsize=9.5,
        color="#374151",
        transform=ax.transAxes,
    )
    ax.set_title("Alur Pembersihan dan Pemisahan Data Review", loc="left", fontsize=15, fontweight="bold", pad=16)
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
    status_labels = {
        "auto_match": "Cocok otomatis",
        "human_verified_match": "Cocok terverifikasi",
        "human_verified_no_match": "Tidak cocok terverifikasi",
        "manual_review": "Perlu pemeriksaan",
        "unresolved": "Belum terselesaikan",
    }
    colors = [green, blue, red, purple, gray][: len(order)]
    bars = ax.bar([status_labels[item] for item in order], [status[item] for item in order], color=colors)
    ax.bar_label(bars, padding=4)
    _style(ax, "Status 810 Hubungan Entitas Tempat Setelah Pemeriksaan")
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


def generate_annotation_figures(
    annotation_dir: Path,
    report_dir: Path,
    figure_dir: Path,
) -> list[str]:
    """Generate sampling figures; label figures require completed human annotations."""

    figure_dir.mkdir(parents=True, exist_ok=True)
    support = pd.read_csv(report_dir / "annotation_candidate_support.csv")
    pilot = pd.read_csv(annotation_dir / "pilot_sampling_audit.csv")
    assignments = pd.read_csv(annotation_dir / "annotation_assignments.csv")
    outputs: list[str] = []
    blue, orange, green, purple = "#2A78D6", "#EB6834", "#1BAF7A", "#7C6BC4"

    def save(name: str, fig: plt.Figure) -> None:
        _save(fig, figure_dir / name)
        outputs.append(name)

    sorted_support = support.sort_values("clean_pool_candidate_support")
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(sorted_support["aspect"], sorted_support["clean_pool_candidate_support"], color=blue, label="Clean pool")
    ax.barh(sorted_support["aspect"], sorted_support["main_candidate_support"], color=orange, label="Main sample")
    _style(ax, "Candidate Aspect Support dan Main Sample")
    ax.set_xlabel("Review dengan minimal satu seed term")
    ax.legend(frameon=False)
    save("23_annotation_candidate_support.png", fig)

    dimensions = ["source_kind", "rating_band", "length_band", "language_marker", "recency_band"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    for ax, dimension in zip(axes.flat, dimensions, strict=False):
        counts = pilot[dimension].value_counts().sort_values(ascending=False)
        bars = ax.bar(counts.index.astype(str), counts.values, color=green)
        ax.bar_label(bars, padding=3, fontsize=7)
        ax.set_title(dimension.replace("_", " ").title(), fontweight="bold")
        ax.tick_params(axis="x", rotation=25)
        ax.spines[["top", "right"]].set_visible(False)
    axes.flat[-1].axis("off")
    fig.suptitle("Stratifikasi Pilot Annotation", x=0.04, ha="left", fontsize=17, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save("24_pilot_sampling_stratification.png", fig)

    main_assignments = assignments.loc[assignments["phase"] == "main"]
    per_annotator = main_assignments.groupby("annotator_id").size()
    double_count = main_assignments.loc[main_assignments["is_double_annotated"], "review_id"].nunique()
    single_count = main_assignments.loc[~main_assignments["is_double_annotated"], "review_id"].nunique()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    bars = axes[0].bar(per_annotator.index, per_annotator.values, color=[blue, orange, green])
    axes[0].bar_label(bars, padding=4)
    axes[0].set_title("Task per Annotator", fontweight="bold")
    axes[0].spines[["top", "right"]].set_visible(False)
    bars = axes[1].bar(["Single", "Double"], [single_count, double_count], color=[purple, green])
    axes[1].bar_label(bars, padding=4)
    axes[1].set_title("Main Review Coverage", fontweight="bold")
    axes[1].spines[["top", "right"]].set_visible(False)
    fig.suptitle("Rencana Assignment Main Annotation", x=0.04, ha="left", fontsize=17, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save("25_main_annotation_assignments.png", fig)

    taxonomy = yaml.safe_load((Path(__file__).resolve().parents[2] / "configs" / "taxonomy.yaml").read_text())
    group_counts = {group: len(aspects) for group, aspects in taxonomy["aspects"].items()}
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(group_counts.keys(), group_counts.values(), color=[green, blue, orange, purple])
    ax.bar_label(bars, padding=4)
    _style(ax, "Komposisi Taxonomy MVP")
    ax.tick_params(axis="x", rotation=15)
    ax.set_ylabel("Jumlah aspek")
    save("26_taxonomy_group_composition.png", fig)

    main = pd.read_csv(annotation_dir / "main_sampling_audit.csv")
    aspect_names = support["aspect"].tolist()
    cooccurrence = pd.DataFrame(0, index=aspect_names, columns=aspect_names, dtype=int)
    for raw_aspects in main["candidate_aspects"]:
        aspects = ast.literal_eval(raw_aspects) if isinstance(raw_aspects, str) else []
        for left in aspects:
            for right in aspects:
                if left in cooccurrence.index and right in cooccurrence.columns:
                    cooccurrence.loc[left, right] += 1
    fig, ax = plt.subplots(figsize=(10, 9))
    image = ax.imshow(cooccurrence.values, cmap="Oranges", aspect="auto")
    ax.set_xticks(range(len(aspect_names)), aspect_names, rotation=55, ha="right")
    ax.set_yticks(range(len(aspect_names)), aspect_names)
    ax.set_title("Candidate Aspect Co-occurrence pada Main Sample", loc="left", fontsize=15, fontweight="bold", pad=16)
    fig.colorbar(image, ax=ax, label="Jumlah review")
    save("27_candidate_aspect_cooccurrence.png", fig)

    destination_counts = main.groupby("destination_id")["review_id"].size()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(destination_counts, bins=range(1, int(destination_counts.max()) + 2), color=blue, align="left")
    _style(ax, "Coverage Destination pada Main Sample")
    ax.set_xlabel("Review per destination")
    ax.set_ylabel("Jumlah destination")
    save("28_main_destination_coverage.png", fig)
    return outputs


def generate_silver_figures(
    annotation_dir: Path,
    figure_dir: Path,
) -> list[str]:
    """Generate aggregate figures from AI-assisted silver annotations."""

    figure_dir.mkdir(parents=True, exist_ok=True)
    records = [
        json.loads(line)
        for line in (annotation_dir / "silver-v1.0.0.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    main_ids = set(pd.read_csv(annotation_dir / "main_sampling_audit.csv")["review_id"])
    main = [record for record in records if record["review_id"] in main_ids]
    outputs: list[str] = []
    blue, orange, green, red, gray, purple = "#2A78D6", "#EB6834", "#1BAF7A", "#D03B3B", "#898781", "#7C6BC4"

    def save(name: str, fig: plt.Figure) -> None:
        _save(fig, figure_dir / name)
        outputs.append(name)

    aspect_counts: dict[str, int] = {}
    polarity_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for record in main:
        status_counts[record["silver_status"]] = status_counts.get(record["silver_status"], 0) + 1
        for label in record["labels"]:
            aspect_counts[label["aspect"]] = aspect_counts.get(label["aspect"], 0) + 1
            polarity_counts[label["polarity"]] = polarity_counts.get(label["polarity"], 0) + 1
            if label["severity"]:
                severity_counts[label["severity"]] = severity_counts.get(label["severity"], 0) + 1

    aspect_series = pd.Series(aspect_counts).sort_values()
    fig, ax = plt.subplots(figsize=(9, 7))
    bars = ax.barh(aspect_series.index, aspect_series.values, color=blue)
    ax.bar_label(bars, padding=4)
    _style(ax, "Distribusi Aspect Silver pada Main Sample")
    ax.set_xlabel("Jumlah silver labels")
    save("29_silver_aspect_distribution.png", fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    polarity_order = [item for item in ["positive", "negative", "neutral"] if item in polarity_counts]
    bars = axes[0].bar(polarity_order, [polarity_counts[item] for item in polarity_order], color=[green, red, gray])
    axes[0].bar_label(bars, padding=4)
    axes[0].set_title("Polarity", fontweight="bold")
    axes[0].spines[["top", "right"]].set_visible(False)
    severity_order = [item for item in ["low", "medium", "high"] if item in severity_counts]
    bars = axes[1].bar(severity_order, [severity_counts[item] for item in severity_order], color=[orange, purple, red])
    axes[1].bar_label(bars, padding=4)
    axes[1].set_title("Negative Severity", fontweight="bold")
    axes[1].spines[["top", "right"]].set_visible(False)
    fig.suptitle("Distribusi Polarity dan Severity Silver", x=0.04, ha="left", fontsize=17, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save("30_silver_polarity_severity.png", fig)

    aspects = sorted(aspect_counts)
    cooccurrence = pd.DataFrame(0, index=aspects, columns=aspects, dtype=int)
    for record in main:
        present = {label["aspect"] for label in record["labels"]}
        for left in present:
            for right in present:
                cooccurrence.loc[left, right] += 1
    fig, ax = plt.subplots(figsize=(10, 9))
    image = ax.imshow(cooccurrence.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(aspects)), aspects, rotation=55, ha="right")
    ax.set_yticks(range(len(aspects)), aspects)
    ax.set_title("Silver Aspect Co-occurrence", loc="left", fontsize=15, fontweight="bold", pad=16)
    fig.colorbar(image, ax=ax, label="Jumlah review")
    save("31_silver_aspect_cooccurrence.png", fig)

    status_series = pd.Series(status_counts).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(status_series.index, status_series.values, color=[green, orange, gray])
    ax.bar_label(bars, padding=4)
    _style(ax, "Status Silver Annotation pada Main Sample")
    ax.tick_params(axis="x", rotation=15)
    save("32_silver_status_distribution.png", fig)

    agreements = [record["pass_agreement"] for record in main]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(agreements, bins=np.linspace(0, 1, 13), color=purple)
    _style(ax, "Distribusi AI Pass Agreement")
    ax.set_xlabel("Mean pairwise aspect-set Jaccard")
    ax.set_ylabel("Review")
    save("33_silver_pass_agreement.png", fig)
    return outputs
