from sipature_ml.cleaning import _relative_date, clean_reviews, normalize_name, normalize_text


def test_normalize_text_preserves_punctuation_and_negation() -> None:
    assert normalize_text("  Tidak\nbersih, tapi bagus!  ") == "Tidak bersih, tapi bagus!"


def test_normalize_name_removes_diacritics_and_punctuation() -> None:
    assert normalize_name("Café Toba - Balige") == "cafe toba balige"


def test_relative_date_is_anchored_and_approximate() -> None:
    estimate, precision, status = _relative_date("2 tahun lalu di", "2025-07-29")
    assert estimate == "2023-07-29"
    assert precision == "year"
    assert status == "parsed_approximate"


def test_relative_date_requires_scrape_anchor() -> None:
    assert _relative_date("a year ago", "") == (None, None, "missing_scrape_anchor")


def test_clean_reviews_uses_reviewer_only_for_duplicate_fingerprint(tmp_path) -> None:
    header = "place-name,reviewer-id,name,reviewer-rating,review-text,published-at,scraped-at-date\n"
    rows = (
        "A,,Reviewer One,5,Bagus,a day ago,2025-07-28\n"
        "A,,Reviewer Two,5,Bagus,a day ago,2025-07-28\n"
        "A,,Reviewer One,5,Bagus,a day ago,2025-07-28\n"
    )
    (tmp_path / "wisata-v2.csv").write_text(header + rows, encoding="utf-8-sig")
    service_header = header.rstrip("\n") + ",reviewer-type\n"
    (tmp_path / "resto-hotel-v2.csv").write_text(service_header, encoding="utf-8-sig")
    clean, _, duplicates, summary = clean_reviews(tmp_path)
    assert summary["exact_duplicate_excess_removed"] == 1
    assert len(clean) == 2
    assert len(duplicates) == 2
    assert "reviewer_name" not in clean.columns
    assert "reviewer_id" not in clean.columns
