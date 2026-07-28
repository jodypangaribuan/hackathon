"""Reproducible EDA profiling and report-ready figure generation."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer

from .manifest import sha256_file

REVIEW_SUFFIXES = ("wisata-v2.csv", "resto-hotel-v2.csv")
METADATA_SUFFIXES = ("wisata-metadata.csv", "resto-metadata.csv", "hotel-metadata.csv")

ASPECT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Kebersihan": ("bersih", "kotor", "jorok", "bau", "serangga", "laba-laba"),
    "Sampah": ("sampah", "plastik", "berserakan", "limbah"),
    "Sanitasi": ("toilet", "wc", "kamar mandi", "mck", "air mati"),
    "Keramaian": ("ramai", "padat", "penuh", "antre", "antri"),
    "Akses/Jalan": ("akses", "jalan", "rusak", "berlubang", "terjal", "berbatu"),
    "Parkir": ("parkir", "parkiran"),
    "Keamanan": ("aman", "bahaya", "licin", "rawan", "preman"),
    "Harga/Pungutan": ("harga", "tarif", "tiket", "pungli", "pungutan", "mahal"),
    "Pelayanan": ("pelayanan", "petugas", "staf", "staff", "ramah", "kasar"),
    "Perawatan": ("terawat", "perawatan", "maintenance", "terbengkalai"),
    "Jam Operasional": ("jam buka", "jam operasional", "tutup", "buka"),
    "Pemandangan": ("pemandangan", "view", "indah", "cantik", "bagus"),
}

COMPLAINT_KEYWORDS = (
    "kotor", "jorok", "bau", "sampah", "berserakan", "rusak", "berlubang", "terjal",
    "bahaya", "rawan", "pungli", "pungutan", "mahal", "kasar", "tidak terawat",
    "air mati", "tutup", "sempit", "licin", "kecewa", "buruk", "jelek",
)

NGRAM_STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "untuk", "ini", "itu", "ada", "dengan",
    "the", "and", "of", "to", "a", "is", "in", "for", "it", "was",
}

INDONESIAN_MARKERS = (
    "yang", "dan", "tidak", "sangat", "tempat", "bagus", "jalan", "dengan", "untuk",
)
ENGLISH_MARKERS = ("the", "and", "not", "very", "place", "good", "road", "with", "for")
NEGATIONS = ("tidak", "tak", "bukan", "belum", "jangan", "kurang", "tanpa", "nggak", "gak")
CONTRASTS = ("tapi", "tetapi", "namun", "walau", "meski", "although", "but", "however")


def _find(dataset_dir: Path, suffix: str) -> Path:
    matches = [path for path in dataset_dir.glob("*.csv") if path.name.endswith(suffix)]
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected one file ending in {suffix!r}, found {len(matches)}")
    return matches[0]


def _nonblank(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.replace(r"\s+", " ", regex=True).str.strip()


def _parse_rating(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = str(value).strip()
    if not re.fullmatch(r"[0-5](?:[.,]\d+)?", text):
        return None
    rating = float(text.replace(",", "."))
    return rating if 0 <= rating <= 5 else None


def _parse_coordinate(value: Any) -> tuple[float, float] | None:
    match = re.fullmatch(
        r"\s*([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)\s*",
        "" if pd.isna(value) else str(value),
    )
    if not match:
        return None
    latitude, longitude = map(float, match.groups())
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None
    return latitude, longitude


def load_reviews(dataset_dir: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for suffix in REVIEW_SUFFIXES:
        path = _find(dataset_dir, suffix)
        frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
        frame["source_file"] = suffix
        frame["source_row"] = np.arange(2, len(frame) + 2)
        frames.append(frame)
    reviews = pd.concat(frames, ignore_index=True, sort=False)
    reviews["place_name"] = _nonblank(reviews["place-name"])
    reviews["review_text"] = _nonblank(reviews["review-text"])
    reviews["rating"] = reviews["reviewer-rating"].map(_parse_rating)
    reviews["has_text"] = reviews["review_text"].ne("")
    reviews["has_rating"] = reviews["rating"].notna()
    reviews["review_kind"] = np.select(
        [
            reviews["has_text"] & reviews["has_rating"],
            reviews["has_text"],
            reviews["has_rating"],
        ],
        ["text_and_rating", "text_only", "rating_only"],
        default="empty_record",
    )
    reviews["text_chars"] = reviews["review_text"].str.len()
    reviews["text_words"] = reviews["review_text"].str.split().str.len().fillna(0).astype(int)
    duplicate_columns = [
        "source_file", "place-name", "name", "reviewer-rating", "review-text",
        "published-at", "scraped-at-date",
    ]
    reviews["is_exact_duplicate_excess"] = reviews.duplicated(
        subset=duplicate_columns, keep="first"
    )
    return reviews


def _contains_terms(text: pd.Series, terms: tuple[str, ...]) -> pd.Series:
    pattern = r"(?:^|\W)(?:" + "|".join(re.escape(term) for term in terms) + r")(?:$|\W)"
    return text.str.lower().str.contains(pattern, regex=True, na=False)


def profile_reviews(reviews: pd.DataFrame) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    textual = reviews.loc[reviews["has_text"]].copy()
    aspect_flags = pd.DataFrame(
        {aspect: _contains_terms(textual["review_text"], terms) for aspect, terms in ASPECT_KEYWORDS.items()},
        index=textual.index,
    )
    aspect_counts = aspect_flags.sum().sort_values(ascending=False).rename("review_count").to_frame()
    aspect_counts["share_of_textual_reviews"] = aspect_counts["review_count"] / len(textual)

    lower = textual["review_text"].str.lower()
    indonesian = _contains_terms(lower, INDONESIAN_MARKERS)
    english = _contains_terms(lower, ENGLISH_MARKERS)
    language = np.select(
        [indonesian & english, indonesian, english],
        ["Mixed markers", "Indonesian markers", "English markers"],
        default="Undetermined",
    )
    language_counts = pd.Series(language).value_counts().rename_axis("heuristic").rename("count")
    normalized_text = lower.str.replace(r"\s+", " ", regex=True).str.strip()
    repeated_text_excess = int(normalized_text.duplicated(keep="first").sum())
    generic_counts = normalized_text.value_counts()
    repeated_substantive_texts = int(
        ((generic_counts > 1) & (generic_counts.index.str.split().str.len() > 3)).sum()
    )
    complaint_flags = _contains_terms(lower, COMPLAINT_KEYWORDS)

    scrape_dates = _nonblank(reviews["scraped-at-date"])
    published_values = _nonblank(reviews["published-at"])

    rating_counts = reviews["rating"].value_counts(dropna=False).sort_index()
    integer_rating_counts = {
        str(star): int((reviews["rating"] == star).sum()) for star in range(1, 6)
    }
    summary: dict[str, Any] = {
        "total_review_records": len(reviews),
        "textual_reviews": int(reviews["has_text"].sum()),
        "blank_text_records": int((~reviews["has_text"]).sum()),
        "rating_only_reviews": int((reviews["review_kind"] == "rating_only").sum()),
        "text_only_reviews": int((reviews["review_kind"] == "text_only").sum()),
        "empty_review_records": int((reviews["review_kind"] == "empty_record").sum()),
        "valid_rating_records": int(reviews["has_rating"].sum()),
        "noninteger_rating_records": int(
            reviews["rating"].dropna().map(lambda value: not float(value).is_integer()).sum()
        ),
        "exact_duplicate_excess_rows": int(reviews["is_exact_duplicate_excess"].sum()),
        "unique_exact_place_names": int(reviews["place_name"].nunique()),
        "integer_rating_distribution": integer_rating_counts,
        "rating_mean": round(float(reviews["rating"].mean()), 4),
        "text_character_quantiles": {
            str(key): round(float(value), 2)
            for key, value in textual["text_chars"].quantile([0.25, 0.5, 0.75, 0.95, 0.99]).items()
        },
        "text_word_quantiles": {
            str(key): round(float(value), 2)
            for key, value in textual["text_words"].quantile([0.25, 0.5, 0.75, 0.95, 0.99]).items()
        },
        "very_short_text_reviews_le_3_words": int((textual["text_words"] <= 3).sum()),
        "negation_reviews": int(_contains_terms(lower, NEGATIONS).sum()),
        "contrast_reviews": int(_contains_terms(lower, CONTRASTS).sum()),
        "candidate_complaint_reviews": int(complaint_flags.sum()),
        "repeated_text_excess_rows": repeated_text_excess,
        "repeated_substantive_text_groups": repeated_substantive_texts,
        "scrape_date_available": int(scrape_dates.ne("").sum()),
        "scrape_date_missing": int(scrape_dates.eq("").sum()),
        "scrape_date_distribution": {
            key: int(value) for key, value in scrape_dates.replace("", "Missing").value_counts().items()
        },
        "published_at_available": int(published_values.ne("").sum()),
        "published_at_missing": int(published_values.eq("").sum()),
        "language_marker_counts": {key: int(value) for key, value in language_counts.items()},
        "raw_rating_value_count": len(rating_counts),
    }

    place_coverage = (
        reviews.groupby("place_name", dropna=False)
        .agg(
            total_reviews=("place_name", "size"),
            textual_reviews=("has_text", "sum"),
            mean_rating=("rating", "mean"),
        )
        .sort_values("textual_reviews", ascending=False)
        .reset_index()
    )
    complaint_by_place = complaint_flags.groupby(textual["place_name"]).agg(["sum", "count"])
    complaint_by_place["candidate_complaint_rate"] = (
        complaint_by_place["sum"] / complaint_by_place["count"]
    )
    place_coverage = place_coverage.merge(
        complaint_by_place[["candidate_complaint_rate"]],
        left_on="place_name",
        right_index=True,
        how="left",
    ).fillna({"candidate_complaint_rate": 0.0})
    return summary, aspect_counts.reset_index(names="aspect"), place_coverage


def profile_ngrams(texts: pd.Series) -> pd.DataFrame:
    """Return top unigram, bigram, and trigram counts for descriptive EDA."""

    outputs: list[pd.DataFrame] = []
    for n in (1, 2, 3):
        common_options = {
            "lowercase": True,
            "stop_words": list(NGRAM_STOPWORDS),
            "ngram_range": (n, n),
            "max_features": 50000,
            "token_pattern": r"(?u)\b[^\W\d_][^\W_]+\b",
        }
        vectorizer = CountVectorizer(min_df=2, **common_options)
        try:
            matrix = vectorizer.fit_transform(texts)
        except ValueError as error:
            if "no terms remain" not in str(error).lower():
                raise
            vectorizer = CountVectorizer(min_df=1, **common_options)
            matrix = vectorizer.fit_transform(texts)
        counts = np.asarray(matrix.sum(axis=0)).ravel()
        terms = vectorizer.get_feature_names_out()
        order = np.argsort(counts)[::-1][:20]
        outputs.append(
            pd.DataFrame(
                {
                    "n": n,
                    "ngram": terms[order],
                    "count": counts[order].astype(int),
                }
            )
        )
    return pd.concat(outputs, ignore_index=True)


def profile_files(dataset_dir: Path) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for path in sorted(dataset_dir.glob("*.csv")):
        frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
        cells = frame.map(lambda value: str(value).strip() if value is not None else "")
        total_cells = max(frame.shape[0] * frame.shape[1], 1)
        records.append(
            {
                "filename": path.name,
                "rows_physical_schema": len(frame),
                "columns_physical_schema": len(frame.columns),
                "missing_cell_rate": float(cells.eq("").to_numpy().sum() / total_cells),
                "exact_duplicate_excess_rows": int(frame.duplicated().sum()),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return pd.DataFrame(records)


def profile_metadata(dataset_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    completeness: list[dict[str, Any]] = []
    coordinates: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    field_map = {
        "wisata-metadata.csv": {
            "name": "place-name", "category": "place-type", "coordinate": "lat-long",
            "rating": "place-rating", "facilities": None, "status": "status",
            "hours": "operational-hour", "price": "entry-fee", "address": "address",
        },
        "resto-metadata.csv": {
            "name": "place-name", "category": "place-type", "coordinate": "lat-long",
            "rating": "place-rating", "facilities": "Fasilitas", "status": "status",
            "hours": "opening-hours", "price": "price-per-head", "address": "address",
        },
        "hotel-metadata.csv": {
            "name": "place-name", "category": "place-type", "coordinate": "lat-long",
            "rating": "place-rating", "facilities": "Fasilitas", "status": "status",
            "hours": None, "price": "price-per-head", "address": "address",
        },
    }
    for suffix, mapping in field_map.items():
        path = _find(dataset_dir, suffix)
        frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
        source = suffix.removesuffix("-metadata.csv").title()
        for canonical, column in mapping.items():
            available = 0 if column is None else int(_nonblank(frame[column]).ne("").sum())
            completeness.append(
                {
                    "source": source,
                    "field": canonical,
                    "available_count": available,
                    "total_count": len(frame),
                    "availability_rate": available / len(frame),
                }
            )
        coordinate_column = mapping["coordinate"]
        parsed = frame[coordinate_column].map(_parse_coordinate)
        for value in parsed.dropna():
            coordinates.append({"source": source, "latitude": value[0], "longitude": value[1]})
        summary[source] = {
            "records": len(frame),
            "parsed_coordinates": int(parsed.notna().sum()),
            "invalid_coordinates": int(parsed.isna().sum()),
            "duplicate_exact_rows": int(frame.duplicated().sum()),
            "duplicate_normalized_names": int(
                _nonblank(frame[mapping["name"]]).str.lower().duplicated(keep=False).sum()
            ),
        }
    coordinate_frame = pd.DataFrame(coordinates)
    summary["coordinate_duplicate_points"] = int(
        coordinate_frame.duplicated(subset=["latitude", "longitude"], keep=False).sum()
    )
    summary["coordinate_region_warnings"] = int(
        (~coordinate_frame["latitude"].between(1, 4) | ~coordinate_frame["longitude"].between(97, 101)).sum()
    )
    return pd.DataFrame(completeness), coordinate_frame, summary


def profile_service_density(dataset_dir: Path, radius_km: float = 5.0) -> pd.DataFrame:
    """Count hotel/restaurant metadata points near every attraction using Haversine distance."""

    sources: dict[str, pd.DataFrame] = {}
    for suffix in METADATA_SUFFIXES:
        path = _find(dataset_dir, suffix)
        frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
        parsed = frame["lat-long"].map(_parse_coordinate)
        frame = frame.loc[parsed.notna(), ["place-name"]].copy()
        frame[["latitude", "longitude"]] = pd.DataFrame(parsed.dropna().tolist(), index=frame.index)
        sources[suffix] = frame

    attractions = sources["wisata-metadata.csv"]
    services = pd.concat(
        [
            sources["resto-metadata.csv"].assign(service_type="restaurant"),
            sources["hotel-metadata.csv"].assign(service_type="hotel"),
        ],
        ignore_index=True,
    )
    service_lat = np.radians(services["latitude"].to_numpy())
    service_lon = np.radians(services["longitude"].to_numpy())
    results: list[dict[str, Any]] = []
    for _, attraction in attractions.iterrows():
        lat1 = math.radians(float(attraction["latitude"]))
        lon1 = math.radians(float(attraction["longitude"]))
        delta_lat = service_lat - lat1
        delta_lon = service_lon - lon1
        haversine = np.sin(delta_lat / 2) ** 2 + np.cos(lat1) * np.cos(service_lat) * np.sin(delta_lon / 2) ** 2
        distances = 6371.0088 * 2 * np.arcsin(np.sqrt(haversine))
        within = distances <= radius_km
        results.append(
            {
                "place_name": attraction["place-name"],
                "latitude": attraction["latitude"],
                "longitude": attraction["longitude"],
                "restaurants_within_5km": int(
                    (within & services["service_type"].eq("restaurant").to_numpy()).sum()
                ),
                "hotels_within_5km": int(
                    (within & services["service_type"].eq("hotel").to_numpy()).sum()
                ),
                "services_within_5km": int(within.sum()),
                "nearest_service_km": round(float(distances.min()), 3),
            }
        )
    return pd.DataFrame(results)


def _save_figure(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _style_axis(ax: plt.Axes, title: str) -> None:
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold", pad=16)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#deded8", linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)


def generate_figures(
    *,
    reviews: pd.DataFrame,
    review_summary: dict[str, Any],
    aspects: pd.DataFrame,
    place_coverage: pd.DataFrame,
    file_profile: pd.DataFrame,
    completeness: pd.DataFrame,
    coordinates: pd.DataFrame,
    ngrams: pd.DataFrame,
    service_density: pd.DataFrame,
    figure_dir: Path,
) -> list[str]:
    figure_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    blue, orange, green, red, gray = "#2A78D6", "#EB6834", "#1BAF7A", "#D03B3B", "#898781"
    outputs: list[str] = []

    def save(name: str, fig: plt.Figure) -> None:
        _save_figure(fig, figure_dir / name)
        outputs.append(name)

    # 1. Dataset size
    plot_data = file_profile.nlargest(10, "rows_physical_schema").sort_values("rows_physical_schema")
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = plot_data["filename"].str.replace("Dataset HackathonTourism - IT DEL.xlsx - ", "", regex=False)
    bars = ax.barh(labels, plot_data["rows_physical_schema"], color=blue)
    ax.bar_label(bars, fmt="{:,.0f}", padding=4, fontsize=8)
    _style_axis(ax, "Ukuran Dataset Berdasarkan Record CSV")
    ax.set_xlabel("Record (di luar header fisik)")
    save("01_dataset_row_counts.png", fig)

    # 2. Review funnel
    funnel_labels = ["Semua record", "Memiliki rating", "Memiliki teks", "Rating-only", "Duplikat excess"]
    funnel_values = [
        review_summary["total_review_records"], review_summary["valid_rating_records"],
        review_summary["textual_reviews"], review_summary["rating_only_reviews"],
        review_summary["exact_duplicate_excess_rows"],
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(funnel_labels, funnel_values, color=[blue, green, orange, gray, red])
    ax.bar_label(bars, labels=[f"{value:,}" for value in funnel_values], padding=4)
    _style_axis(ax, "Funnel Ketersediaan Review")
    ax.tick_params(axis="x", rotation=18)
    save("02_review_availability_funnel.png", fig)

    # 3. Rating distribution
    stars = list(range(1, 6))
    values = [review_summary["integer_rating_distribution"][str(star)] for star in stars]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar([str(star) for star in stars], values, color=[red, orange, "#FAB219", blue, green])
    ax.bar_label(bars, labels=[f"{value:,}\n({value / sum(values):.1%})" for value in values], padding=4)
    _style_axis(ax, "Distribusi Rating Review")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Jumlah record")
    save("03_rating_distribution.png", fig)

    # 4. Text length
    textual = reviews.loc[reviews["has_text"]]
    capped = textual["text_words"].clip(upper=int(textual["text_words"].quantile(0.99)))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(capped, bins=40, color=blue, alpha=0.9)
    median = textual["text_words"].median()
    p95 = textual["text_words"].quantile(0.95)
    ax.axvline(median, color=red, linestyle="--", label=f"Median {median:.0f} kata")
    ax.axvline(p95, color=orange, linestyle="--", label=f"P95 {p95:.0f} kata")
    _style_axis(ax, "Distribusi Panjang Review Berteks")
    ax.set_xlabel("Jumlah kata")
    ax.set_ylabel("Review")
    ax.legend(frameon=False)
    save("04_review_text_length.png", fig)

    # 5. Place coverage
    top = place_coverage.head(20).sort_values("textual_reviews")
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(top["place_name"], top["total_reviews"], color="#d9d9d3", label="Semua review")
    ax.barh(top["place_name"], top["textual_reviews"], color=blue, label="Review berteks")
    _style_axis(ax, "20 Tempat dengan Review Berteks Terbanyak")
    ax.set_xlabel("Jumlah review")
    ax.legend(frameon=False)
    save("05_top_place_review_coverage.png", fig)

    # 6. Coverage distribution
    bins = [-1, 0, 4, 19, 49, np.inf]
    labels = ["0", "1–4", "5–19", "20–49", "50+"]
    coverage_bands = pd.cut(place_coverage["textual_reviews"], bins=bins, labels=labels)
    band_counts = coverage_bands.value_counts().reindex(labels).fillna(0).astype(int)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, band_counts.values, color=[red, orange, "#FAB219", blue, green])
    ax.bar_label(bars, padding=4)
    _style_axis(ax, "Sebaran Coverage Teks per Nama Tempat")
    ax.set_xlabel("Jumlah review berteks")
    ax.set_ylabel("Nama tempat exact")
    save("06_place_text_coverage_bands.png", fig)

    # 7. Candidate aspects
    aspect_plot = aspects.sort_values("review_count")
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(aspect_plot["aspect"], aspect_plot["review_count"], color=orange)
    ax.bar_label(bars, labels=[f"{value:,}" for value in aspect_plot["review_count"]], padding=4, fontsize=8)
    _style_axis(ax, "Prevalensi Kandidat Aspek Berbasis Seed Keywords")
    ax.set_xlabel("Review berteks yang memuat minimal satu seed term")
    save("07_candidate_aspect_prevalence.png", fig)

    # 8. Language/linguistic markers
    language = review_summary["language_marker_counts"]
    marker_labels = list(language) + ["Negation", "Contrast"]
    marker_values = list(language.values()) + [review_summary["negation_reviews"], review_summary["contrast_reviews"]]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(marker_labels, marker_values, color=[blue, green, orange, gray, red, "#7C6BC4"])
    ax.bar_label(bars, labels=[f"{value:,}" for value in marker_values], padding=4, fontsize=8)
    _style_axis(ax, "Indikator Bahasa, Negasi, dan Kontras")
    ax.tick_params(axis="x", rotation=20)
    save("08_language_negation_markers.png", fig)

    # 9. Missing cells by file
    missing = file_profile.nlargest(12, "missing_cell_rate").sort_values("missing_cell_rate")
    labels_missing = missing["filename"].str.replace("Dataset HackathonTourism - IT DEL.xlsx - ", "", regex=False)
    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(labels_missing, missing["missing_cell_rate"] * 100, color=red)
    ax.bar_label(bars, labels=[f"{value:.1%}" for value in missing["missing_cell_rate"]], padding=4, fontsize=8)
    _style_axis(ax, "Proporsi Sel Kosong per File")
    ax.set_xlabel("Sel kosong (%)")
    save("09_file_missing_cell_rates.png", fig)

    # 10. Metadata completeness
    pivot = completeness.pivot(index="field", columns="source", values="availability_rate").fillna(0)
    fig, ax = plt.subplots(figsize=(8, 6))
    image = ax.imshow(pivot.values * 100, cmap="Blues", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns)
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    for row in range(len(pivot.index)):
        for col in range(len(pivot.columns)):
            value = pivot.iloc[row, col] * 100
            ax.text(col, row, f"{value:.0f}%", ha="center", va="center", color="white" if value > 60 else "#111")
    ax.set_title("Kelengkapan Field Metadata Utama", loc="left", fontsize=15, fontweight="bold", pad=16)
    fig.colorbar(image, ax=ax, label="Availability (%)")
    save("10_metadata_completeness_heatmap.png", fig)

    # 11. Coordinate map
    fig, ax = plt.subplots(figsize=(8, 7))
    for source, group in coordinates.groupby("source"):
        ax.scatter(group["longitude"], group["latitude"], s=22, alpha=0.72, label=source)
    ax.set_title("Sebaran Koordinat Metadata Pariwisata", loc="left", fontsize=15, fontweight="bold", pad=16)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(color="#deded8", linewidth=0.7)
    ax.legend(frameon=False)
    save("11_metadata_coordinate_distribution.png", fig)

    # 12. Duplicate audit
    duplicate_data = pd.DataFrame(
        {
            "Category": ["Review duplicate excess", "Empty review records", "Noninteger ratings"],
            "Count": [
                review_summary["exact_duplicate_excess_rows"],
                review_summary["empty_review_records"],
                review_summary["noninteger_rating_records"],
            ],
        }
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(duplicate_data["Category"], duplicate_data["Count"], color=[red, gray, orange])
    ax.bar_label(bars, padding=4)
    _style_axis(ax, "Anomali Review yang Memerlukan Penanganan")
    ax.tick_params(axis="x", rotation=15)
    save("12_review_quality_anomalies.png", fig)

    # 13. N-grams
    fig, axes = plt.subplots(1, 3, figsize=(15, 6), sharex=False)
    for axis, n, title in zip(axes, (1, 2, 3), ("Unigram", "Bigram", "Trigram"), strict=True):
        values = ngrams.loc[ngrams["n"] == n].head(10).sort_values("count")
        bars = axis.barh(values["ngram"], values["count"], color=blue)
        axis.bar_label(bars, padding=3, fontsize=7)
        axis.set_title(title, fontweight="bold")
        axis.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Top N-gram Review Setelah Stopword Ringkas", x=0.05, ha="left", fontsize=16, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save("13_top_review_ngrams.png", fig)

    # 14. Freshness availability
    freshness_labels = ["Scrape date tersedia", "Scrape date missing", "Published-at tersedia", "Published-at missing"]
    freshness_values = [
        review_summary["scrape_date_available"], review_summary["scrape_date_missing"],
        review_summary["published_at_available"], review_summary["published_at_missing"],
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(freshness_labels, freshness_values, color=[green, red, blue, orange])
    ax.bar_label(bars, labels=[f"{value:,}" for value in freshness_values], padding=4)
    _style_axis(ax, "Ketersediaan Field Waktu Review")
    ax.tick_params(axis="x", rotation=18)
    save("14_review_time_field_availability.png", fig)

    # 15. Volume vs candidate complaint rate
    scatter = place_coverage.loc[place_coverage["textual_reviews"] >= 5]
    fig, ax = plt.subplots(figsize=(9, 6))
    points = ax.scatter(
        scatter["textual_reviews"],
        scatter["candidate_complaint_rate"] * 100,
        c=scatter["mean_rating"],
        cmap="viridis",
        s=24,
        alpha=0.75,
    )
    ax.set_xscale("log")
    _style_axis(ax, "Volume Teks vs Candidate Complaint Rate")
    ax.set_xlabel("Review berteks (log scale)")
    ax.set_ylabel("Candidate complaint rate (%)")
    fig.colorbar(points, ax=ax, label="Mean rating")
    save("15_volume_vs_candidate_complaint_rate.png", fig)

    # 16. Nearby service density
    fig, ax = plt.subplots(figsize=(9, 5))
    clipped_services = service_density["services_within_5km"].clip(upper=50)
    ax.hist(clipped_services, bins=26, color=green, alpha=0.9)
    median_services = service_density["services_within_5km"].median()
    ax.axvline(median_services, color=red, linestyle="--", label=f"Median {median_services:.0f} layanan")
    _style_axis(ax, "Kepadatan Hotel/Restoran dalam Radius 5 km")
    ax.set_xlabel("Jumlah metadata hotel + restoran")
    ax.set_ylabel("Destinasi wisata")
    ax.legend(frameon=False)
    save("16_nearby_service_density_5km.png", fig)
    return outputs


def run_eda(dataset_dir: Path, report_dir: Path, figure_dir: Path) -> dict[str, Any]:
    dataset_dir = dataset_dir.resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    reviews = load_reviews(dataset_dir)
    review_summary, aspects, place_coverage = profile_reviews(reviews)
    ngrams = profile_ngrams(reviews.loc[reviews["has_text"], "review_text"])
    file_profile = profile_files(dataset_dir)
    completeness, coordinates, metadata_summary = profile_metadata(dataset_dir)
    service_density = profile_service_density(dataset_dir)

    figures = generate_figures(
        reviews=reviews,
        review_summary=review_summary,
        aspects=aspects,
        place_coverage=place_coverage,
        file_profile=file_profile,
        completeness=completeness,
        coordinates=coordinates,
        ngrams=ngrams,
        service_density=service_density,
        figure_dir=figure_dir,
    )

    file_profile.to_csv(report_dir / "eda_file_profile.csv", index=False)
    aspects.to_csv(report_dir / "eda_candidate_aspects.csv", index=False)
    place_coverage.to_csv(report_dir / "eda_place_coverage.csv", index=False)
    completeness.to_csv(report_dir / "eda_metadata_completeness.csv", index=False)
    coordinates.to_csv(report_dir / "eda_coordinates.csv", index=False)
    ngrams.to_csv(report_dir / "eda_ngrams.csv", index=False)
    service_density.to_csv(report_dir / "eda_service_density.csv", index=False)

    summary = {
        "eda_version": "0.1.0",
        "dataset_dir": str(dataset_dir),
        "review_summary": review_summary,
        "metadata_summary": metadata_summary,
        "service_density_summary": {
            "attractions": len(service_density),
            "radius_km": 5.0,
            "median_services": float(service_density["services_within_5km"].median()),
            "destinations_with_no_services": int((service_density["services_within_5km"] == 0).sum()),
            "median_nearest_service_km": round(float(service_density["nearest_service_km"].median()), 3),
        },
        "figures": figures,
        "source_files": {
            path.name: sha256_file(path) for path in sorted(dataset_dir.glob("*.csv"))
        },
        "limitations": [
            "Language groups are marker-based heuristics, not model predictions.",
            "Candidate aspect prevalence uses seed keywords and is not gold annotation.",
            "Physical-schema missingness includes irregular spreadsheet header structures.",
            "Place coverage uses exact source names before entity resolution.",
            "Coordinates assume WGS84 and have not been address-validated.",
        ],
    }
    (report_dir / "eda_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary
