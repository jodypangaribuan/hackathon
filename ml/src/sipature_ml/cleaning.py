"""Deterministic cleaning for SIPATURE review and place-source records."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .eda import REVIEW_SUFFIXES, _find, _parse_coordinate, _parse_rating
from .manifest import sha256_file

CONTROL_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
SPACE_PATTERN = re.compile(r"\s+")


def normalize_text(value: Any) -> str:
    """Normalize Unicode and whitespace without removing punctuation, typos, or negation."""

    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = CONTROL_PATTERN.sub("", text)
    return SPACE_PATTERN.sub(" ", text).strip()


def normalize_name(value: Any) -> str:
    text = unicodedata.normalize("NFKD", normalize_text(value).casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _stable_id(prefix: str, *parts: Any) -> str:
    payload = "\x1f".join(normalize_text(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]}"


def _relative_date(raw: str, scraped_at: str) -> tuple[str | None, str | None, str]:
    """Return conservative date estimate, precision, and parse status."""

    raw = normalize_text(raw).casefold()
    scraped_at = normalize_text(scraped_at)
    if not raw:
        return None, None, "missing_published_at"
    if not scraped_at:
        return None, None, "missing_scrape_anchor"
    try:
        timestamp = pd.Timestamp(scraped_at)
    except (TypeError, ValueError):
        return None, None, "missing_scrape_anchor"
    if pd.isna(timestamp):
        return None, None, "missing_scrape_anchor"
    anchor = timestamp.date()

    text = raw.replace("edited", "").strip()
    replacements = {
        "setahun": "1 tahun", "sebulan": "1 bulan", "seminggu": "1 minggu",
        "sehari": "1 hari", "an hour": "1 hour", "a year": "1 year",
        "a month": "1 month", "a week": "1 week", "a day": "1 day",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    number_match = re.search(r"(\d+)", text)
    amount = int(number_match.group(1)) if number_match else 1

    if re.search(r"year|tahun", text):
        estimate = pd.Timestamp(anchor) - pd.DateOffset(years=amount)
        return estimate.date().isoformat(), "year", "parsed_approximate"
    if re.search(r"month|bulan", text):
        estimate = pd.Timestamp(anchor) - pd.DateOffset(months=amount)
        return estimate.date().isoformat(), "month", "parsed_approximate"
    if re.search(r"week|minggu", text):
        estimate = pd.Timestamp(anchor) - pd.Timedelta(weeks=amount)
        return estimate.date().isoformat(), "week", "parsed_approximate"
    if re.search(r"day|hari", text):
        estimate = pd.Timestamp(anchor) - pd.Timedelta(days=amount)
        return estimate.date().isoformat(), "day", "parsed_approximate"
    if re.search(r"hour|jam|minute|menit", text):
        return anchor.isoformat(), "day", "parsed_approximate"
    return None, None, "unparsed_relative_date"


def clean_reviews(dataset_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    frames: list[pd.DataFrame] = []
    for suffix in REVIEW_SUFFIXES:
        path = _find(dataset_dir, suffix)
        frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
        frame["source_file"] = suffix
        frame["source_row"] = np.arange(2, len(frame) + 2)
        frame["source_kind"] = "wisata" if suffix == "wisata-v2.csv" else "service"
        frames.append(frame)
    raw = pd.concat(frames, ignore_index=True, sort=False)

    clean = pd.DataFrame(
        {
            "source_file": raw["source_file"],
            "source_row": raw["source_row"].astype(int),
            "source_kind": raw["source_kind"],
            "place_name_raw": raw["place-name"].map(normalize_text),
            "place_name_normalized": raw["place-name"].map(normalize_name),
            "rating_raw": raw["reviewer-rating"].map(normalize_text),
            "review_text_raw": raw["review-text"].map(normalize_text),
            "published_at_raw": raw["published-at"].map(normalize_text),
            "scraped_at_raw": raw["scraped-at-date"].map(normalize_text),
            "reviewer_type_raw": raw.get("reviewer-type", pd.Series("", index=raw.index)).map(normalize_text),
        }
    )
    clean["review_id"] = [
        _stable_id("review", source, row) for source, row in zip(clean["source_file"], clean["source_row"], strict=True)
    ]
    clean["rating"] = clean["rating_raw"].map(_parse_rating)
    clean["has_text"] = clean["review_text_raw"].ne("")
    clean["has_rating"] = clean["rating"].notna()
    clean["review_kind"] = np.select(
        [clean["has_text"] & clean["has_rating"], clean["has_text"], clean["has_rating"]],
        ["text_and_rating", "text_only", "rating_only"],
        default="empty_record",
    )
    date_results = [
        _relative_date(published, scraped)
        for published, scraped in zip(clean["published_at_raw"], clean["scraped_at_raw"], strict=True)
    ]
    clean[["published_date_estimate", "published_date_precision", "date_parse_status"]] = pd.DataFrame(
        date_results, index=clean.index
    )

    duplicate_fields = [
        "source_file", "place_name_normalized", "rating_raw", "review_text_raw",
        "published_at_raw", "scraped_at_raw",
    ]
    reviewer_name_transient = raw["name"].map(normalize_name)
    duplicate_payload = clean[duplicate_fields].astype(str).agg("\x1f".join, axis=1)
    duplicate_payload = duplicate_payload + "\x1f" + reviewer_name_transient
    clean["duplicate_group_id"] = duplicate_payload.map(
        lambda value: f"dup_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]}"
    )
    clean["is_exact_duplicate"] = duplicate_payload.duplicated(keep=False)
    clean["is_duplicate_excess"] = duplicate_payload.duplicated(keep="first")

    quarantine_records: list[dict[str, Any]] = []
    for row in clean.itertuples(index=False):
        if row.review_kind == "empty_record":
            quarantine_records.append(
                {"review_id": row.review_id, "reason": "empty_rating_and_text", "action": "excluded"}
            )
        if row.rating is not None and not float(row.rating).is_integer():
            quarantine_records.append(
                {"review_id": row.review_id, "reason": "unexpected_noninteger_review_rating", "action": "retained_with_warning"}
            )
        if row.rating_raw and row.rating is None:
            quarantine_records.append(
                {"review_id": row.review_id, "reason": "unparseable_or_out_of_range_rating", "action": "retained_text_only_if_available"}
            )
        if not row.place_name_normalized:
            quarantine_records.append(
                {"review_id": row.review_id, "reason": "missing_place_name", "action": "excluded"}
            )
    quarantine = pd.DataFrame(quarantine_records, columns=["review_id", "reason", "action"])
    duplicates = clean.loc[clean["is_exact_duplicate"]].copy()

    usable = clean.loc[
        ~clean["is_duplicate_excess"]
        & clean["place_name_normalized"].ne("")
        & clean["review_kind"].ne("empty_record")
    ].copy()
    summary = {
        "raw_records": len(clean),
        "exact_duplicate_excess_removed": int(clean["is_duplicate_excess"].sum()),
        "empty_records_excluded": int((clean["review_kind"] == "empty_record").sum()),
        "clean_records": len(usable),
        "clean_textual_records": int(usable["has_text"].sum()),
        "clean_rating_only_records": int((usable["review_kind"] == "rating_only").sum()),
        "quarantine_flags": len(quarantine),
        "date_parse_status": {
            str(key): int(value) for key, value in clean["date_parse_status"].value_counts().items()
        },
    }
    return usable, quarantine, duplicates, summary


def _metadata_records(dataset_dir: Path) -> pd.DataFrame:
    definitions = {
        "wisata-metadata.csv": ("wisata", "place-name", "place-type", "lat-long", "address", "place-rating", "status", "entry-fee", "operational-hour", None),
        "resto-metadata.csv": ("resto", "place-name", "place-type", "lat-long", "address", "place-rating", "status", "price-per-head", "opening-hours", "Fasilitas"),
        "hotel-metadata.csv": ("hotel", "place-name", "place-type", "lat-long", "address", "place-rating", "status", "price-per-head", None, "Fasilitas"),
    }
    records: list[dict[str, Any]] = []
    for suffix, fields in definitions.items():
        kind, name_col, category_col, coord_col, address_col, rating_col, status_col, price_col, hours_col, facilities_col = fields
        path = _find(dataset_dir, suffix)
        frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
        for index, row in frame.iterrows():
            coordinate = _parse_coordinate(row[coord_col])
            records.append(
                {
                    "source_record_id": _stable_id("place_src", suffix, index + 2),
                    "source_file": suffix,
                    "source_row": index + 2,
                    "source_kind": kind,
                    "is_anchor": True,
                    "name_raw": normalize_text(row[name_col]),
                    "name_normalized": normalize_name(row[name_col]),
                    "category_raw": normalize_text(row[category_col]),
                    "address_raw": normalize_text(row[address_col]),
                    "address_normalized": normalize_name(row[address_col]),
                    "coordinate_raw": normalize_text(row[coord_col]),
                    "latitude": coordinate[0] if coordinate else np.nan,
                    "longitude": coordinate[1] if coordinate else np.nan,
                    "rating_raw": normalize_text(row[rating_col]),
                    "rating": _parse_rating(row[rating_col]),
                    "status_raw": normalize_text(row[status_col]),
                    "price_raw": normalize_text(row[price_col]),
                    "hours_raw": normalize_text(row[hours_col]) if hours_col else "",
                    "facilities_raw": normalize_text(row[facilities_col]) if facilities_col else "",
                }
            )
    return pd.DataFrame(records)


def _supporting_records(dataset_dir: Path) -> pd.DataFrame:
    definitions = {
        "tempat-wisata-v1.csv": ("wisata", "place", "type", "add", "rating", "entry-fee", "service-hour", "addons"),
        "hotel-resto-v1.csv": ("service", "place", "type", "add", "rating", "htm", "service-hour", "facilitates"),
        "waktu operasional destinasi.csv": ("wisata", "OBJEK / DESTINASI WISATA", None, "ALAMAT", None, None, "WAKTU OPERASIONAL", "FASILITAS UMUM"),
    }
    records: list[dict[str, Any]] = []
    for suffix, fields in definitions.items():
        kind, name_col, category_col, address_col, rating_col, price_col, hours_col, facilities_col = fields
        path = _find(dataset_dir, suffix)
        frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
        for index, row in frame.iterrows():
            name = normalize_text(row[name_col])
            if not name:
                continue
            records.append(
                {
                    "source_record_id": _stable_id("place_src", suffix, index + 2),
                    "source_file": suffix,
                    "source_row": index + 2,
                    "source_kind": kind,
                    "is_anchor": False,
                    "name_raw": name,
                    "name_normalized": normalize_name(name),
                    "category_raw": normalize_text(row[category_col]) if category_col else "",
                    "address_raw": normalize_text(row[address_col]),
                    "address_normalized": normalize_name(row[address_col]),
                    "coordinate_raw": "",
                    "latitude": np.nan,
                    "longitude": np.nan,
                    "rating_raw": normalize_text(row[rating_col]) if rating_col else "",
                    "rating": _parse_rating(row[rating_col]) if rating_col else None,
                    "status_raw": "",
                    "price_raw": normalize_text(row[price_col]) if price_col else "",
                    "hours_raw": normalize_text(row[hours_col]),
                    "facilities_raw": normalize_text(row[facilities_col]),
                }
            )
    return pd.DataFrame(records)


def clean_place_sources(dataset_dir: Path) -> pd.DataFrame:
    return pd.concat([_metadata_records(dataset_dir), _supporting_records(dataset_dir)], ignore_index=True)


def run_cleaning(dataset_dir: Path, output_dir: Path, report_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    reviews, quarantine, duplicates, review_summary = clean_reviews(dataset_dir)
    places = clean_place_sources(dataset_dir)

    reviews.to_parquet(output_dir / "clean_reviews.parquet", index=False)
    reviews.loc[reviews["has_text"]].to_parquet(output_dir / "text_training_pool.parquet", index=False)
    reviews.loc[reviews["review_kind"] == "rating_only"].to_parquet(
        output_dir / "rating_only_pool.parquet", index=False
    )
    quarantine.to_parquet(output_dir / "quarantine_rows.parquet", index=False)
    duplicates.to_parquet(output_dir / "duplicate_groups.parquet", index=False)
    places.to_parquet(output_dir / "clean_place_sources.parquet", index=False)

    summary = {
        "cleaning_version": "0.1.0",
        "reviews": review_summary,
        "place_source_records": len(places),
        "anchor_place_records": int(places["is_anchor"].sum()),
        "supporting_place_records": int((~places["is_anchor"]).sum()),
        "source_files": {
            path.name: sha256_file(path) for path in sorted(dataset_dir.glob("*.csv"))
        },
        "outputs": {
            path.name: sha256_file(path) for path in sorted(output_dir.glob("*.parquet"))
        },
    }
    (report_dir / "cleaning_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary
