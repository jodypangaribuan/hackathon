import {
  bigint,
  boolean,
  date,
  doublePrecision,
  index,
  integer,
  jsonb,
  pgEnum,
  pgTable,
  primaryKey,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from "drizzle-orm/pg-core";

// ============================================================================
// ENUMS (selaras dengan db/schema.sql)
// ============================================================================
export const placeKind = pgEnum("place_kind", [
  "wisata",
  "kuliner",
  "akomodasi",
  "layanan",
]);
export const canonicalStatus = pgEnum("canonical_status", [
  "metadata_anchor",
  "unresolved_placeholder",
]);
export const priorityLevel = pgEnum("priority_level", [
  "Critical",
  "High",
  "Medium",
  "Monitor",
  "Insufficient Data",
]);
export const confidenceLevel = pgEnum("confidence_level", [
  "high",
  "medium",
  "low",
  "insufficient",
]);
export const polarity = pgEnum("polarity", [
  "positive",
  "negative",
  "neutral",
]);
export const severityLevel = pgEnum("severity_level", [
  "low",
  "medium",
  "high",
]);
export const severityStatus = pgEnum("severity_status", [
  "unavailable_no_supported_model",
]);
export const evidenceStatus = pgEnum("evidence_status", [
  "withheld_pending_privacy_review",
  "published",
]);
export const matchStatus = pgEnum("match_status", [
  "auto_match",
  "human_verified_match",
  "human_verified_no_match",
  "manual_review",
  "unresolved",
]);
export const reviewKind = pgEnum("review_kind", [
  "text_and_rating",
  "text_only",
  "rating_only",
  "empty_record",
]);
export const silverStatus = pgEnum("silver_status", [
  "consensus",
  "no_supported_aspect",
  "review_recommended",
]);
export const verificationStatus = pgEnum("verification_status", [
  "pending",
  "confirmed",
  "rejected",
  "uncertain",
]);

// ============================================================================
// TAXONOMY
// ============================================================================
export const aspects = pgTable("aspects", {
  key: text("key").primaryKey(),
  label: text("label").notNull(),
  aspectGroup: text("aspect_group").notNull(),
  definition: text("definition"),
  isRare: boolean("is_rare").notNull().default(false),
  createdAt: timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
});

// ============================================================================
// PROVENANCE
// ============================================================================
export const modelVersions = pgTable("model_versions", {
  version: text("version").primaryKey(),
  modelType: text("model_type").notNull(),
  manifestSha256: text("manifest_sha256"),
  modelSha256: text("model_sha256"),
  taxonomySha256: text("taxonomy_sha256"),
  configSha256: text("config_sha256"),
  referenceLabelType: text("reference_label_type"),
  isActive: boolean("is_active").notNull().default(false),
  createdAt: timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
});

export const dataExports = pgTable(
  "data_exports",
  {
    id: bigint("id", { mode: "number" })
      .primaryKey()
      .generatedAlwaysAsIdentity(),
    schemaVersion: text("schema_version").notNull(),
    modelVersion: text("model_version").notNull(),
    generatedAt: timestamp("generated_at", { withTimezone: true }).notNull(),
    sourceManifest: text("source_manifest").notNull(),
    exportSha256: text("export_sha256").notNull(),
    totalCleanReviews: integer("total_clean_reviews"),
    textualReviewsAnalyzed: integer("textual_reviews_analyzed"),
    reviewsWithPredictions: integer("reviews_with_predictions"),
    aspectPredictions: integer("aspect_predictions"),
    actionableDestinations: integer("actionable_destinations"),
    actionableIssues: integer("actionable_issues"),
    limitations: jsonb("limitations").notNull().default([]),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    uniqueIndex("data_exports_export_sha256_key").on(table.exportSha256),
  ],
);

// ============================================================================
// DESTINATIONS
// ============================================================================
export const destinations = pgTable(
  "destinations",
  {
    id: text("id").primaryKey(),
    name: text("name").notNull(),
    kind: placeKind("kind").notNull(),
    canonicalStatus: canonicalStatus("canonical_status")
      .notNull()
      .default("metadata_anchor"),

    latitude: doublePrecision("latitude"),
    longitude: doublePrecision("longitude"),
    address: text("address"),
    category: text("category"),

    legacyId: text("legacy_id"),
    placeType: text("place_type"),
    entryFee: text("entry_fee"),
    operationalHours: text("operational_hours"),
    gmapsRating: doublePrecision("gmaps_rating"),
    operationalStatus: text("operational_status"),
    facilities: text("facilities"),
    kabupaten: text("kabupaten"),
    kecamatan: text("kecamatan"),

    priority: priorityLevel("priority")
      .notNull()
      .default("Insufficient Data"),
    priorityScore: doublePrecision("priority_score"),
    healthScore: doublePrecision("health_score"),
    concernScore: doublePrecision("concern_score"),
    dataConfidence: confidenceLevel("data_confidence")
      .notNull()
      .default("insufficient"),
    textReviewCount: integer("text_review_count").notNull().default(0),
    allReviewCount: integer("all_review_count").notNull().default(0),
    rank: integer("rank"),

    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("idx_destinations_priority").on(table.priority),
    index("idx_destinations_geo").on(table.latitude, table.longitude),
    index("idx_destinations_kabupaten").on(table.kabupaten),
  ],
);

// ============================================================================
// ENTITY LINKS
// ============================================================================
export const entityLinks = pgTable(
  "entity_links",
  {
    sourceRecordId: text("source_record_id").primaryKey(),
    destinationId: text("destination_id").references(() => destinations.id, {
      onDelete: "cascade",
    }),
    sourceKind: text("source_kind").notNull(),
    matchStatus: matchStatus("match_status").notNull(),
    matchRule: text("match_rule").notNull(),
    nameSimilarity: doublePrecision("name_similarity"),
    addressSimilarity: doublePrecision("address_similarity"),
    distanceMeters: doublePrecision("distance_meters"),
  },
  (table) => [
    index("idx_entity_links_destination").on(table.destinationId),
    index("idx_entity_links_status").on(table.matchStatus),
  ],
);

// ============================================================================
// DESTINATION-ASPECT SIGNALS (composite PK: destination_id, aspect)
// ============================================================================
export const destinationSignals = pgTable(
  "destination_signals",
  {
    destinationId: text("destination_id")
      .notNull()
      .references(() => destinations.id, { onDelete: "cascade" }),
    aspect: text("aspect")
      .notNull()
      .references(() => aspects.key),
    mentionCount: integer("mention_count").notNull().default(0),
    negativeCount: integer("negative_count").notNull().default(0),
    severeCount: integer("severe_count"),
    complaintRate: doublePrecision("complaint_rate"),
    smoothedComplaintRate: doublePrecision("smoothed_complaint_rate"),
    meanConfidence: doublePrecision("mean_confidence"),
    persistence: doublePrecision("persistence"),
    freshness: doublePrecision("freshness"),
    uniqueReviewCount: integer("unique_review_count").notNull().default(0),
    textReviewCount: integer("text_review_count").notNull().default(0),
    allReviewCount: integer("all_review_count").notNull().default(0),
    dataConfidence: confidenceLevel("data_confidence")
      .notNull()
      .default("insufficient"),
    severityStatus: severityStatus("severity_status")
      .notNull()
      .default("unavailable_no_supported_model"),

    priority: priorityLevel("priority").notNull().default("Insufficient Data"),
    priorityScore: doublePrecision("priority_score"),
    priorityComponents: jsonb("priority_components").notNull().default({}),
    explanation: text("explanation"),
    recommendedVerification: text("recommended_verification"),
    candidateIntervention: text("candidate_intervention"),

    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    primaryKey({ columns: [table.destinationId, table.aspect] }),
    index("idx_signals_priority").on(table.priority),
    index("idx_signals_aspect").on(table.aspect),
  ],
);

// ============================================================================
// EVIDENCE (restricted)
// ============================================================================
export const evidence = pgTable(
  "evidence",
  {
    id: bigint("id", { mode: "number" })
      .primaryKey()
      .generatedAlwaysAsIdentity(),
    destinationId: text("destination_id")
      .notNull()
      .references(() => destinations.id, { onDelete: "cascade" }),
    aspect: text("aspect")
      .notNull()
      .references(() => aspects.key),
    reviewId: text("review_id").notNull(),
    sourceFile: text("source_file"),
    sourceRow: integer("source_row"),
    text: text("text").notNull(),
    aspectProbability: doublePrecision("aspect_probability").notNull(),
    publishedDateEstimate: date("published_date_estimate"),
    evidenceStatus: evidenceStatus("evidence_status")
      .notNull()
      .default("withheld_pending_privacy_review"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("idx_evidence_dest_aspect").on(table.destinationId, table.aspect),
    index("idx_evidence_review").on(table.reviewId),
  ],
);

// ============================================================================
// REVIEWS (restricted)
// ============================================================================
export const reviews = pgTable(
  "reviews",
  {
    id: text("id").primaryKey(),
    destinationId: text("destination_id")
      .notNull()
      .references(() => destinations.id, { onDelete: "cascade" }),
    reviewTextRaw: text("review_text_raw").notNull(),
    rating: doublePrecision("rating"),
    hasText: boolean("has_text").notNull(),
    reviewKind: reviewKind("review_kind").notNull(),
    publishedDateEstimate: date("published_date_estimate"),
    duplicateGroupId: text("duplicate_group_id"),
    sourceFile: text("source_file"),
    sourceRow: integer("source_row"),
    silverStatus: silverStatus("silver_status"),
    passAgreement: doublePrecision("pass_agreement"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("idx_reviews_destination").on(table.destinationId),
    index("idx_reviews_duplicate").on(table.duplicateGroupId),
  ],
);

// ============================================================================
// REVIEW PREDICTIONS (restricted, composite PK: review_id, aspect)
// ============================================================================
export const reviewPredictions = pgTable(
  "review_predictions",
  {
    reviewId: text("review_id")
      .notNull()
      .references(() => reviews.id, { onDelete: "cascade" }),
    aspect: text("aspect")
      .notNull()
      .references(() => aspects.key),
    aspectProbability: doublePrecision("aspect_probability").notNull(),
    polarity: polarity("polarity").notNull(),
    polarityProbability: doublePrecision("polarity_probability"),
    severity: severityLevel("severity"),
    severityProbability: doublePrecision("severity_probability"),
    modelVersion: text("model_version")
      .notNull()
      .references(() => modelVersions.version),
    generatedAt: timestamp("generated_at", { withTimezone: true }).notNull(),
  },
  (table) => [
    primaryKey({ columns: [table.reviewId, table.aspect] }),
    index("idx_predictions_aspect").on(table.aspect),
  ],
);

// ============================================================================
// ALERTS + VERIFICATION (workflow final round)
// ============================================================================
export const alerts = pgTable(
  "alerts",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    destinationId: text("destination_id")
      .notNull()
      .references(() => destinations.id, { onDelete: "cascade" }),
    aspect: text("aspect")
      .notNull()
      .references(() => aspects.key),
    priority: priorityLevel("priority").notNull(),
    priorityScore: doublePrecision("priority_score"),
    recommendedVerification: text("recommended_verification"),
    candidateIntervention: text("candidate_intervention"),
    status: verificationStatus("status").notNull().default("pending"),
    assignedTo: text("assigned_to"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("idx_alerts_status").on(table.status),
    uniqueIndex("alerts_destination_aspect_key").on(
      table.destinationId,
      table.aspect,
    ),
  ],
);

export const alertVerifications = pgTable(
  "alert_verifications",
  {
    id: bigint("id", { mode: "number" })
      .primaryKey()
      .generatedAlwaysAsIdentity(),
    alertId: uuid("alert_id")
      .notNull()
      .references(() => alerts.id, { onDelete: "cascade" }),
    status: verificationStatus("status").notNull(),
    verdictNote: text("verdict_note"),
    rejectionReason: text("rejection_reason"),
    verifiedBy: text("verified_by"),
    verifiedAt: timestamp("verified_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [index("idx_alert_verifications_alert").on(table.alertId)],
);
