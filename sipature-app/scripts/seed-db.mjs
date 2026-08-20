/**
 * SIPATURE — Database Seeder (Pure Node.js / PostgreSQL)
 * Dapat dijalankan langsung dengan: node scripts/seed-db.mjs
 */

import { readFile } from "node:fs/promises";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import pg from "pg";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const databaseUrl =
  process.env.DATABASE_URL ||
  `postgresql://${process.env.POSTGRES_USER || "sipature"}:${
    process.env.POSTGRES_PASSWORD || "sipature_dev_password"
  }@${process.env.POSTGRES_HOST || "localhost"}:${
    process.env.POSTGRES_PORT || "5432"
  }/${process.env.POSTGRES_DB || "sipature"}`;

async function readJson(name) {
  const possiblePaths = [
    resolve(process.cwd(), "src/data/generated", name),
    resolve(__dirname, "../src/data/generated", name),
    resolve(__dirname, "data/generated", name),
  ];

  for (const p of possiblePaths) {
    try {
      const raw = await readFile(p, "utf8");
      return JSON.parse(raw);
    } catch {
      // try next path
    }
  }
  throw new Error(`File ${name} tidak ditemukan di lokasi data generated.`);
}

async function main() {
  console.log(`Connecting to database at ${databaseUrl.replace(/:[^:@]+@/, ":****@")}...`);
  const pool = new pg.Pool({ connectionString: databaseUrl });
  const client = await pool.connect();

  try {
    const places = await readJson("places.json");
    const corpus = await readJson("corpus.json");

    await client.query("BEGIN");

    // Truncate tables
    await client.query(`
      TRUNCATE TABLE
        alert_verifications, alerts, review_predictions, reviews, evidence,
        destination_signals, entity_links, destinations, data_exports, aspects
      CASCADE;
    `);

    // 1. Aspects
    for (const aspect of corpus.aspects) {
      await client.query(
        `INSERT INTO aspects (key, label, aspect_group) VALUES ($1, $2, $3) ON CONFLICT (key) DO NOTHING;`,
        [aspect.key, aspect.label, aspect.group]
      );
    }

    // 2. Destinations
    for (const place of places) {
      await client.query(
        `INSERT INTO destinations (
          id, legacy_id, name, kind, canonical_status,
          latitude, longitude, address, place_type, entry_fee,
          operational_hours, gmaps_rating, operational_status, facilities,
          kabupaten, kecamatan, priority, priority_score, health_score,
          concern_score, data_confidence, text_review_count, all_review_count, rank
        ) VALUES (
          $1, $2, $3, $4, $5,
          $6, $7, $8, $9, $10,
          $11, $12, $13, $14,
          $15, $16, $17, $18, $19,
          $20, $21, $22, $23, $24
        );`,
        [
          place.id,
          place.legacyId,
          place.name,
          place.kind,
          place.canonicalStatus,
          place.lat,
          place.lon,
          place.address,
          place.type,
          place.entryFee,
          place.hours,
          place.gmapsRating,
          place.status,
          place.facilities,
          place.kabupaten,
          place.kecamatan,
          place.priority,
          place.priorityScore,
          place.healthScore,
          place.concernScore,
          place.dataConfidence,
          place.textReviewCount,
          place.allReviewCount,
          place.rank,
        ]
      );
    }

    // 3. Destination Signals
    for (const place of places) {
      for (const issue of place.issues) {
        await client.query(
          `INSERT INTO destination_signals (
            destination_id, aspect, mention_count, negative_count,
            text_review_count, all_review_count, smoothed_complaint_rate,
            mean_confidence, data_confidence, severity_status, priority,
            priority_score, priority_components, explanation,
            recommended_verification, candidate_intervention
          ) VALUES (
            $1, $2, $3, $4,
            $5, $6, $7,
            $8, $9, $10, $11,
            $12, $13, $14,
            $15, $16
          );`,
          [
            place.id,
            issue.aspect,
            issue.mentionCount,
            issue.negativeCount,
            issue.textReviewCount,
            issue.allReviewCount,
            issue.smoothedComplaintRate,
            issue.meanConfidence,
            issue.dataConfidence,
            issue.severityStatus,
            issue.priority,
            issue.priorityScore,
            JSON.stringify(issue.priorityComponents || {}),
            issue.explanation,
            issue.recommendedVerification,
            issue.candidateIntervention,
          ]
        );
      }
    }

    // 4. Evidence verbatim ulasan wisatawan
    try {
      const evidenceList = await readJson("evidence.json");
      if (evidenceList && evidenceList.length > 0) {
        for (let i = 0; i < evidenceList.length; i += 200) {
          const chunk = evidenceList.slice(i, i + 200);
          const values = [];
          const params = [];
          let pIdx = 1;

          for (const item of chunk) {
            values.push(
              `($${pIdx}, $${pIdx + 1}, $${pIdx + 2}, $${pIdx + 3}, $${pIdx + 4}, $${pIdx + 5}, $${pIdx + 6}, $${pIdx + 7}, $${pIdx + 8})`
            );
            params.push(
              item.destination_id,
              item.aspect,
              item.review_id,
              item.source_file,
              item.source_row,
              item.text,
              item.aspect_probability,
              item.published_date_estimate,
              "published"
            );
            pIdx += 9;
          }

          await client.query(
            `INSERT INTO evidence (
              destination_id, aspect, review_id, source_file, source_row,
              text, aspect_probability, published_date_estimate, evidence_status
            ) VALUES ${values.join(", ")};`,
            params
          );
        }
        console.log(`Seeded: ${evidenceList.length} evidence quotes.`);
      }
    } catch (e) {
      console.warn("Evidence seed skipped:", e.message);
    }

    // 5. Data export snapshot
    await client.query(
      `INSERT INTO data_exports (
        schema_version, model_version, generated_at, source_manifest, export_sha256,
        total_clean_reviews, textual_reviews_analyzed, reviews_with_predictions,
        aspect_predictions, actionable_destinations, actionable_issues,
        limitations, corpus_json
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
      ON CONFLICT (export_sha256) DO NOTHING;`,
      [
        corpus.schemaVersion,
        corpus.modelVersion,
        new Date(corpus.generatedAt),
        corpus.sourceManifest,
        corpus.exportSha256,
        corpus.totalCleanReviews,
        corpus.textualReviewsAnalyzed,
        corpus.reviewsWithPredictions,
        corpus.aspectPredictions,
        corpus.actionableDestinations,
        corpus.actionableIssues,
        JSON.stringify(corpus.limitations || []),
        JSON.stringify(corpus || {}),
      ]
    );

    await client.query("COMMIT");

    const totalSignals = places.reduce((n, p) => n + p.issues.length, 0);
    console.log(
      `Database Seeding Berhasil: ${places.length} destinasi, ${corpus.aspects.length} aspek, ${totalSignals} sinyal.`
    );
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

main().catch((err) => {
  console.error("Gagal melakukan database seed:", err);
  process.exit(1);
});
