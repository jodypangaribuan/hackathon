-- ============================================================================
-- SIPATURE — PostgreSQL schema
-- ============================================================================
-- Target: PostgreSQL 15+
--
-- Design principles
--  - Deterministic TEXT primary keys for imported ML identifiers (destinations,
--    reviews, aspects) so the DB mirrors the frozen pipeline hashes 1:1.
--  - UUID + IDENTITY for workflow records created inside the app (alerts,
--    verifications).
--  - Native ENUMs for fixed vocabularies; JSONB for flexible structures
--    (priority_components, limitations).
--  - TIMESTAMPTZ everywhere; every table has created_at / updated_at.
--  - Restricted review-level data is isolated in dedicated tables (reviews,
--    review_predictions) with an explicit comment; never expose reviewer identity.
--  - Provenance is first-class: model_versions + data_exports pin every batch.
--
-- Usage: psql "$DATABASE_URL" -f db/schema.sql
-- ============================================================================

-- ---------------------------------------------------------------------------
-- ENUMS
-- ---------------------------------------------------------------------------
CREATE TYPE place_kind        AS ENUM ('wisata', 'kuliner', 'akomodasi', 'layanan');
CREATE TYPE canonical_status  AS ENUM ('metadata_anchor', 'unresolved_placeholder');
CREATE TYPE priority_level    AS ENUM ('Critical', 'High', 'Medium', 'Monitor', 'Insufficient Data');
CREATE TYPE confidence_level  AS ENUM ('high', 'medium', 'low', 'insufficient');
CREATE TYPE polarity          AS ENUM ('positive', 'negative', 'neutral');
CREATE TYPE severity_level    AS ENUM ('low', 'medium', 'high');
CREATE TYPE severity_status   AS ENUM ('unavailable_no_supported_model');
CREATE TYPE evidence_status   AS ENUM ('withheld_pending_privacy_review', 'published');
CREATE TYPE match_status      AS ENUM ('auto_match', 'human_verified_match', 'human_verified_no_match', 'manual_review', 'unresolved');
CREATE TYPE review_kind       AS ENUM ('text_and_rating', 'text_only', 'rating_only', 'empty_record');
CREATE TYPE silver_status     AS ENUM ('consensus', 'no_supported_aspect', 'review_recommended');
CREATE TYPE verification_status AS ENUM ('pending', 'confirmed', 'rejected', 'uncertain');

-- ---------------------------------------------------------------------------
-- TAXONOMY (reference)
-- ---------------------------------------------------------------------------
CREATE TABLE aspects (
    key           TEXT PRIMARY KEY,               -- cleanliness, waste, ...
    label         TEXT NOT NULL,                  -- "Kebersihan", ...
    aspect_group  TEXT NOT NULL,                  -- environmental, infrastructure, visitor_experience, operations
    definition    TEXT,
    is_rare       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE aspects IS 'Taxonomy aspek MVP (1.0.0-rc1), diimpor dari ml/configs/taxonomy.yaml.';

-- ---------------------------------------------------------------------------
-- PROVENANCE
-- ---------------------------------------------------------------------------
CREATE TABLE model_versions (
    version             TEXT PRIMARY KEY,         -- tfidf-aspect-silver-v1, lexical-polarity-v1, ...
    model_type          TEXT NOT NULL,            -- aspect | polarity | severity
    manifest_sha256     TEXT,                     -- model artifact manifest hash
    model_sha256        TEXT,                     -- serialized model hash
    taxonomy_sha256     TEXT,
    config_sha256       TEXT,
    reference_label_type TEXT,                    -- ai_assisted_weak_supervision_silver
    is_active           BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE model_versions IS 'Registri model berversi; hash mengikat ke manifest pipeline ML.';

CREATE TABLE data_exports (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    schema_version    TEXT NOT NULL,
    model_version     TEXT NOT NULL,              -- a9-tfidf-lexical-v1.0.4
    generated_at      TIMESTAMPTZ NOT NULL,
    source_manifest   TEXT NOT NULL,              -- SHA-256 of prioritization manifest
    export_sha256     TEXT NOT NULL,
    total_clean_reviews       INTEGER,
    textual_reviews_analyzed  INTEGER,
    reviews_with_predictions  INTEGER,
    aspect_predictions        INTEGER,
    actionable_destinations   INTEGER,
    actionable_issues         INTEGER,
    limitations       JSONB NOT NULL DEFAULT '[]',
    corpus_json       JSONB NOT NULL DEFAULT '{}',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (export_sha256)
);

COMMENT ON TABLE data_exports IS 'Snapshot tiap batch A9 → app; satu baris per regenerasi data.';

-- ---------------------------------------------------------------------------
-- DESTINATIONS
-- ---------------------------------------------------------------------------
CREATE TABLE destinations (
    id                 TEXT PRIMARY KEY,          -- dest_wisata_<hash> (deterministik)
    name               TEXT NOT NULL,
    kind               place_kind NOT NULL,
    canonical_status   canonical_status NOT NULL DEFAULT 'metadata_anchor',

    -- geografi & identitas kanonik
    latitude           DOUBLE PRECISION,
    longitude          DOUBLE PRECISION,
    address            TEXT,
    category           TEXT,

    -- enrich metadata (metadata-enrichment.json)
    legacy_id          TEXT,
    place_type         TEXT,
    entry_fee          TEXT,
    operational_hours  TEXT,
    gmaps_rating       DOUBLE PRECISION,
    operational_status TEXT,
    facilities         TEXT,
    kabupaten          TEXT,
    kecamatan          TEXT,

    -- agregat dari A9 export
    priority           priority_level NOT NULL DEFAULT 'Insufficient Data',
    priority_score     DOUBLE PRECISION,
    health_score       DOUBLE PRECISION,
    concern_score      DOUBLE PRECISION,
    data_confidence    confidence_level NOT NULL DEFAULT 'insufficient',
    text_review_count  INTEGER NOT NULL DEFAULT 0,
    all_review_count   INTEGER NOT NULL DEFAULT 0,
    rank               INTEGER,

    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_destinations_priority ON destinations (priority) WHERE priority <> 'Insufficient Data';
CREATE INDEX idx_destinations_geo ON destinations (latitude, longitude);
CREATE INDEX idx_destinations_kabupaten ON destinations (kabupaten);

COMMENT ON TABLE destinations IS 'Canonical destinations + enrich metadata + A9 agregat (peta & overview).';

-- ---------------------------------------------------------------------------
-- ENTITY LINKS (audit)
-- ---------------------------------------------------------------------------
CREATE TABLE entity_links (
    source_record_id  TEXT NOT NULL,
    destination_id    TEXT REFERENCES destinations(id) ON DELETE CASCADE,
    source_kind       TEXT NOT NULL,
    match_status      match_status NOT NULL,
    match_rule        TEXT NOT NULL,
    name_similarity   DOUBLE PRECISION,
    address_similarity DOUBLE PRECISION,
    distance_meters   DOUBLE PRECISION,
    PRIMARY KEY (source_record_id)
);

CREATE INDEX idx_entity_links_destination ON entity_links (destination_id);
CREATE INDEX idx_entity_links_status ON entity_links (match_status);

COMMENT ON TABLE entity_links IS 'Peta source-record → canonical destination (provenance entity resolution).';

-- ---------------------------------------------------------------------------
-- DESTINATION-ASPECT SIGNALS
-- ---------------------------------------------------------------------------
CREATE TABLE destination_signals (
    destination_id        TEXT NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
    aspect                TEXT NOT NULL REFERENCES aspects(key),
    mention_count         INTEGER NOT NULL DEFAULT 0,
    negative_count        INTEGER NOT NULL DEFAULT 0,
    severe_count          INTEGER,                 -- NULL = unavailable
    complaint_rate        DOUBLE PRECISION,
    smoothed_complaint_rate DOUBLE PRECISION,
    mean_confidence       DOUBLE PRECISION,
    persistence           DOUBLE PRECISION,
    freshness             DOUBLE PRECISION,
    unique_review_count   INTEGER NOT NULL DEFAULT 0,
    text_review_count     INTEGER NOT NULL DEFAULT 0,
    all_review_count      INTEGER NOT NULL DEFAULT 0,
    data_confidence       confidence_level NOT NULL DEFAULT 'insufficient',
    severity_status       severity_status NOT NULL DEFAULT 'unavailable_no_supported_model',

    -- prioritas & intervensi (a9.yaml interventions mapping)
    priority              priority_level NOT NULL DEFAULT 'Insufficient Data',
    priority_score        DOUBLE PRECISION,
    priority_components   JSONB NOT NULL DEFAULT '{}',
    explanation           TEXT,
    recommended_verification TEXT,
    candidate_intervention   TEXT,

    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (destination_id, aspect)
);

CREATE INDEX idx_signals_priority ON destination_signals (priority) WHERE priority <> 'Insufficient Data';
CREATE INDEX idx_signals_aspect ON destination_signals (aspect);

COMMENT ON TABLE destination_signals IS 'Sinyal per destinasi-aspek (agregat A9) + prioritas + intervensi kandidat.';

-- ---------------------------------------------------------------------------
-- EVIDENCE (verbatim, restricted until privacy review)
-- ---------------------------------------------------------------------------
CREATE TABLE evidence (
    id                      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    destination_id          TEXT NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
    aspect                  TEXT NOT NULL REFERENCES aspects(key),
    review_id               TEXT NOT NULL,
    source_file             TEXT,
    source_row              INTEGER,
    text                    TEXT NOT NULL,          -- verbatim snippet
    aspect_probability      DOUBLE PRECISION NOT NULL,
    published_date_estimate DATE,
    evidence_status         evidence_status NOT NULL DEFAULT 'withheld_pending_privacy_review',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_evidence_dest_aspect ON evidence (destination_id, aspect);
CREATE INDEX idx_evidence_review ON evidence (review_id);

COMMENT ON TABLE evidence IS 'Kutipan verbatim pendukung issue. RESTRICTED — jangan tampilkan sebelum privacy review.';

-- ---------------------------------------------------------------------------
-- REVIEWS (restricted)
-- ---------------------------------------------------------------------------
CREATE TABLE reviews (
    id                      TEXT PRIMARY KEY,       -- review_<hash>
    destination_id          TEXT NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
    review_text_raw         TEXT NOT NULL,          -- RESTRICTED
    rating                  DOUBLE PRECISION,
    has_text                BOOLEAN NOT NULL,
    review_kind             review_kind NOT NULL,
    published_date_estimate DATE,
    duplicate_group_id      TEXT,
    source_file             TEXT,
    source_row              INTEGER,
    silver_status           silver_status,
    pass_agreement          DOUBLE PRECISION,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reviews_destination ON reviews (destination_id);
CREATE INDEX idx_reviews_duplicate ON reviews (duplicate_group_id);

COMMENT ON TABLE reviews IS 'Canonical review records. RESTRICTED — berisi teks review; jangan ekspos identitas reviewer.';

-- ---------------------------------------------------------------------------
-- REVIEW PREDICTIONS (restricted)
-- ---------------------------------------------------------------------------
CREATE TABLE review_predictions (
    review_id              TEXT NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    aspect                 TEXT NOT NULL REFERENCES aspects(key),
    aspect_probability     DOUBLE PRECISION NOT NULL,
    polarity               polarity NOT NULL,
    polarity_probability   DOUBLE PRECISION,          -- NULL (lexical fallback)
    severity               severity_level,
    severity_probability   DOUBLE PRECISION,
    model_version          TEXT NOT NULL REFERENCES model_versions(version),
    generated_at           TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (review_id, aspect)
);

CREATE INDEX idx_predictions_destination ON review_predictions (aspect);

COMMENT ON TABLE review_predictions IS 'Prediksi per review per aspek. RESTRICTED (review-level).';

-- ---------------------------------------------------------------------------
-- ALERTS + VERIFICATION (final-round human workflow)
-- ---------------------------------------------------------------------------
CREATE TABLE alerts (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    destination_id          TEXT NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
    aspect                  TEXT NOT NULL REFERENCES aspects(key),
    priority                priority_level NOT NULL,
    priority_score          DOUBLE PRECISION,
    recommended_verification TEXT,
    candidate_intervention   TEXT,
    status                  verification_status NOT NULL DEFAULT 'pending',
    assigned_to             TEXT,                    -- internal annotator/operator id (opaque)
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (destination_id, aspect)
);

CREATE INDEX idx_alerts_status ON alerts (status);

COMMENT ON TABLE alerts IS 'Issue actionable yang dipromosikan untuk verifikasi lapangan/manusia.';

CREATE TABLE alert_verifications (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alert_id         UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    status           verification_status NOT NULL,
    verdict_note     TEXT,
    rejection_reason TEXT,                          -- bila status = rejected
    verified_by      TEXT,                          -- opaque reviewer id
    verified_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_alert_verifications_alert ON alert_verifications (alert_id);

COMMENT ON TABLE alert_verifications IS 'Audit trail keputusan verifikasi per alert (confirmed/rejected/uncertain).';

-- ---------------------------------------------------------------------------
-- VIEWS
-- ---------------------------------------------------------------------------
-- Flat actionable intervention list (sumber halaman /intervensi).
CREATE VIEW v_interventions AS
SELECT
    d.id || '--' || s.aspect      AS id,
    d.id                          AS place_id,
    d.name                        AS place_name,
    d.kabupaten                   AS kabupaten,
    s.aspect                      AS aspect,
    a.label                       AS aspect_label,
    a.aspect_group                AS category,
    s.candidate_intervention      AS title,
    s.recommended_verification    AS verification,
    s.explanation                 AS explanation,
    s.mention_count,
    s.negative_count,
    s.smoothed_complaint_rate,
    s.data_confidence,
    s.priority,
    s.priority_score,
    ROW_NUMBER() OVER (
        ORDER BY s.priority_score DESC NULLS LAST, d.id, s.aspect
    )                             AS rank
FROM destination_signals s
JOIN destinations d ON d.id = s.destination_id
JOIN aspects a      ON a.key = s.aspect
WHERE s.priority <> 'Insufficient Data';

COMMENT ON VIEW v_interventions IS 'Daftar intervensi actionable, tersortir & ter-rank.';
