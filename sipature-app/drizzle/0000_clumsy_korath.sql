CREATE TYPE "public"."canonical_status" AS ENUM('metadata_anchor', 'unresolved_placeholder');--> statement-breakpoint
CREATE TYPE "public"."confidence_level" AS ENUM('high', 'medium', 'low', 'insufficient');--> statement-breakpoint
CREATE TYPE "public"."evidence_status" AS ENUM('withheld_pending_privacy_review', 'published');--> statement-breakpoint
CREATE TYPE "public"."match_status" AS ENUM('auto_match', 'human_verified_match', 'human_verified_no_match', 'manual_review', 'unresolved');--> statement-breakpoint
CREATE TYPE "public"."place_kind" AS ENUM('wisata', 'kuliner', 'akomodasi', 'layanan');--> statement-breakpoint
CREATE TYPE "public"."polarity" AS ENUM('positive', 'negative', 'neutral');--> statement-breakpoint
CREATE TYPE "public"."priority_level" AS ENUM('Critical', 'High', 'Medium', 'Monitor', 'Insufficient Data');--> statement-breakpoint
CREATE TYPE "public"."review_kind" AS ENUM('text_and_rating', 'text_only', 'rating_only', 'empty_record');--> statement-breakpoint
CREATE TYPE "public"."severity_level" AS ENUM('low', 'medium', 'high');--> statement-breakpoint
CREATE TYPE "public"."severity_status" AS ENUM('unavailable_no_supported_model');--> statement-breakpoint
CREATE TYPE "public"."silver_status" AS ENUM('consensus', 'no_supported_aspect', 'review_recommended');--> statement-breakpoint
CREATE TYPE "public"."verification_status" AS ENUM('pending', 'confirmed', 'rejected', 'uncertain');--> statement-breakpoint
CREATE TABLE "alert_verifications" (
	"id" bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "alert_verifications_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1),
	"alert_id" uuid NOT NULL,
	"status" "verification_status" NOT NULL,
	"verdict_note" text,
	"rejection_reason" text,
	"verified_by" text,
	"verified_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "alerts" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"destination_id" text NOT NULL,
	"aspect" text NOT NULL,
	"priority" "priority_level" NOT NULL,
	"priority_score" double precision,
	"recommended_verification" text,
	"candidate_intervention" text,
	"status" "verification_status" DEFAULT 'pending' NOT NULL,
	"assigned_to" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "aspects" (
	"key" text PRIMARY KEY NOT NULL,
	"label" text NOT NULL,
	"aspect_group" text NOT NULL,
	"definition" text,
	"is_rare" boolean DEFAULT false NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "data_exports" (
	"id" bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "data_exports_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1),
	"schema_version" text NOT NULL,
	"model_version" text NOT NULL,
	"generated_at" timestamp with time zone NOT NULL,
	"source_manifest" text NOT NULL,
	"export_sha256" text NOT NULL,
	"total_clean_reviews" integer,
	"textual_reviews_analyzed" integer,
	"reviews_with_predictions" integer,
	"aspect_predictions" integer,
	"actionable_destinations" integer,
	"actionable_issues" integer,
	"limitations" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "destination_signals" (
	"destination_id" text NOT NULL,
	"aspect" text NOT NULL,
	"mention_count" integer DEFAULT 0 NOT NULL,
	"negative_count" integer DEFAULT 0 NOT NULL,
	"severe_count" integer,
	"complaint_rate" double precision,
	"smoothed_complaint_rate" double precision,
	"mean_confidence" double precision,
	"persistence" double precision,
	"freshness" double precision,
	"unique_review_count" integer DEFAULT 0 NOT NULL,
	"text_review_count" integer DEFAULT 0 NOT NULL,
	"all_review_count" integer DEFAULT 0 NOT NULL,
	"data_confidence" "confidence_level" DEFAULT 'insufficient' NOT NULL,
	"severity_status" "severity_status" DEFAULT 'unavailable_no_supported_model' NOT NULL,
	"priority" "priority_level" DEFAULT 'Insufficient Data' NOT NULL,
	"priority_score" double precision,
	"priority_components" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"explanation" text,
	"recommended_verification" text,
	"candidate_intervention" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "destination_signals_destination_id_aspect_pk" PRIMARY KEY("destination_id","aspect")
);
--> statement-breakpoint
CREATE TABLE "destinations" (
	"id" text PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"kind" "place_kind" NOT NULL,
	"canonical_status" "canonical_status" DEFAULT 'metadata_anchor' NOT NULL,
	"latitude" double precision,
	"longitude" double precision,
	"address" text,
	"category" text,
	"legacy_id" text,
	"place_type" text,
	"entry_fee" text,
	"operational_hours" text,
	"gmaps_rating" double precision,
	"operational_status" text,
	"facilities" text,
	"kabupaten" text,
	"kecamatan" text,
	"priority" "priority_level" DEFAULT 'Insufficient Data' NOT NULL,
	"priority_score" double precision,
	"health_score" double precision,
	"concern_score" double precision,
	"data_confidence" "confidence_level" DEFAULT 'insufficient' NOT NULL,
	"text_review_count" integer DEFAULT 0 NOT NULL,
	"all_review_count" integer DEFAULT 0 NOT NULL,
	"rank" integer,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "entity_links" (
	"source_record_id" text PRIMARY KEY NOT NULL,
	"destination_id" text,
	"source_kind" text NOT NULL,
	"match_status" "match_status" NOT NULL,
	"match_rule" text NOT NULL,
	"name_similarity" double precision,
	"address_similarity" double precision,
	"distance_meters" double precision
);
--> statement-breakpoint
CREATE TABLE "evidence" (
	"id" bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "evidence_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1),
	"destination_id" text NOT NULL,
	"aspect" text NOT NULL,
	"review_id" text NOT NULL,
	"source_file" text,
	"source_row" integer,
	"text" text NOT NULL,
	"aspect_probability" double precision NOT NULL,
	"published_date_estimate" date,
	"evidence_status" "evidence_status" DEFAULT 'withheld_pending_privacy_review' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "model_versions" (
	"version" text PRIMARY KEY NOT NULL,
	"model_type" text NOT NULL,
	"manifest_sha256" text,
	"model_sha256" text,
	"taxonomy_sha256" text,
	"config_sha256" text,
	"reference_label_type" text,
	"is_active" boolean DEFAULT false NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "review_predictions" (
	"review_id" text NOT NULL,
	"aspect" text NOT NULL,
	"aspect_probability" double precision NOT NULL,
	"polarity" "polarity" NOT NULL,
	"polarity_probability" double precision,
	"severity" "severity_level",
	"severity_probability" double precision,
	"model_version" text NOT NULL,
	"generated_at" timestamp with time zone NOT NULL,
	CONSTRAINT "review_predictions_review_id_aspect_pk" PRIMARY KEY("review_id","aspect")
);
--> statement-breakpoint
CREATE TABLE "reviews" (
	"id" text PRIMARY KEY NOT NULL,
	"destination_id" text NOT NULL,
	"review_text_raw" text NOT NULL,
	"rating" double precision,
	"has_text" boolean NOT NULL,
	"review_kind" "review_kind" NOT NULL,
	"published_date_estimate" date,
	"duplicate_group_id" text,
	"source_file" text,
	"source_row" integer,
	"silver_status" "silver_status",
	"pass_agreement" double precision,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "alert_verifications" ADD CONSTRAINT "alert_verifications_alert_id_alerts_id_fk" FOREIGN KEY ("alert_id") REFERENCES "public"."alerts"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "alerts" ADD CONSTRAINT "alerts_destination_id_destinations_id_fk" FOREIGN KEY ("destination_id") REFERENCES "public"."destinations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "alerts" ADD CONSTRAINT "alerts_aspect_aspects_key_fk" FOREIGN KEY ("aspect") REFERENCES "public"."aspects"("key") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "destination_signals" ADD CONSTRAINT "destination_signals_destination_id_destinations_id_fk" FOREIGN KEY ("destination_id") REFERENCES "public"."destinations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "destination_signals" ADD CONSTRAINT "destination_signals_aspect_aspects_key_fk" FOREIGN KEY ("aspect") REFERENCES "public"."aspects"("key") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "entity_links" ADD CONSTRAINT "entity_links_destination_id_destinations_id_fk" FOREIGN KEY ("destination_id") REFERENCES "public"."destinations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "evidence" ADD CONSTRAINT "evidence_destination_id_destinations_id_fk" FOREIGN KEY ("destination_id") REFERENCES "public"."destinations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "evidence" ADD CONSTRAINT "evidence_aspect_aspects_key_fk" FOREIGN KEY ("aspect") REFERENCES "public"."aspects"("key") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "review_predictions" ADD CONSTRAINT "review_predictions_review_id_reviews_id_fk" FOREIGN KEY ("review_id") REFERENCES "public"."reviews"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "review_predictions" ADD CONSTRAINT "review_predictions_aspect_aspects_key_fk" FOREIGN KEY ("aspect") REFERENCES "public"."aspects"("key") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "review_predictions" ADD CONSTRAINT "review_predictions_model_version_model_versions_version_fk" FOREIGN KEY ("model_version") REFERENCES "public"."model_versions"("version") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "reviews" ADD CONSTRAINT "reviews_destination_id_destinations_id_fk" FOREIGN KEY ("destination_id") REFERENCES "public"."destinations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "idx_alert_verifications_alert" ON "alert_verifications" USING btree ("alert_id");--> statement-breakpoint
CREATE INDEX "idx_alerts_status" ON "alerts" USING btree ("status");--> statement-breakpoint
CREATE UNIQUE INDEX "alerts_destination_aspect_key" ON "alerts" USING btree ("destination_id","aspect");--> statement-breakpoint
CREATE UNIQUE INDEX "data_exports_export_sha256_key" ON "data_exports" USING btree ("export_sha256");--> statement-breakpoint
CREATE INDEX "idx_signals_priority" ON "destination_signals" USING btree ("priority");--> statement-breakpoint
CREATE INDEX "idx_signals_aspect" ON "destination_signals" USING btree ("aspect");--> statement-breakpoint
CREATE INDEX "idx_destinations_priority" ON "destinations" USING btree ("priority");--> statement-breakpoint
CREATE INDEX "idx_destinations_geo" ON "destinations" USING btree ("latitude","longitude");--> statement-breakpoint
CREATE INDEX "idx_destinations_kabupaten" ON "destinations" USING btree ("kabupaten");--> statement-breakpoint
CREATE INDEX "idx_entity_links_destination" ON "entity_links" USING btree ("destination_id");--> statement-breakpoint
CREATE INDEX "idx_entity_links_status" ON "entity_links" USING btree ("match_status");--> statement-breakpoint
CREATE INDEX "idx_evidence_dest_aspect" ON "evidence" USING btree ("destination_id","aspect");--> statement-breakpoint
CREATE INDEX "idx_evidence_review" ON "evidence" USING btree ("review_id");--> statement-breakpoint
CREATE INDEX "idx_predictions_aspect" ON "review_predictions" USING btree ("aspect");--> statement-breakpoint
CREATE INDEX "idx_reviews_destination" ON "reviews" USING btree ("destination_id");--> statement-breakpoint
CREATE INDEX "idx_reviews_duplicate" ON "reviews" USING btree ("duplicate_group_id");