/**
 * Seed database dari bundle aplikasi (`src/data/generated/*.json`).
 *
 * Jalankan:
 *   npm run data:generate   # (bila bundle belum ada)
 *   npm run db:seed
 *
 * Idempotent: truncate dulu lalu insert ulang. Source = privacy-safe JSON
 * yang sama dengan yang dipakai dashboard (bukan artifact review-level).
 */
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { sql } from "drizzle-orm";

import { db, schema } from "../src/db";
import type { AspectKey, Corpus, Place } from "../src/lib/types";

async function readJson<T>(name: string): Promise<T> {
  const raw = await readFile(resolve(process.cwd(), "src/data/generated", name), "utf8");
  return JSON.parse(raw) as T;
}

async function main() {
  const places = await readJson<Place[]>("places.json");
  const corpus = await readJson<Corpus>("corpus.json");

  // Seluruh seed dalam SATU transaksi: app tidak akan melihat kondisi
  // setengah-isi bila di-query di tengah proses seed.
  await db.transaction(async (tx) => {
    await tx.execute(sql`
      TRUNCATE TABLE
        alert_verifications, alerts, review_predictions, reviews, evidence,
        destination_signals, entity_links, destinations, data_exports, aspects
      CASCADE
    `);

    // 1. Taxonomy aspects (dari corpus.aspects).
    await tx.insert(schema.aspects).values(
      corpus.aspects.map((aspect) => ({
        key: aspect.key,
        label: aspect.label,
        aspectGroup: aspect.group,
      })),
    );

    // 2. Destinations.
    await tx.insert(schema.destinations).values(
      places.map((place) => ({
        id: place.id,
        legacyId: place.legacyId,
        name: place.name,
        kind: place.kind,
        canonicalStatus: place.canonicalStatus,
        latitude: place.lat,
        longitude: place.lon,
        address: place.address,
        placeType: place.type,
        entryFee: place.entryFee,
        operationalHours: place.hours,
        gmapsRating: place.gmapsRating,
        operationalStatus: place.status,
        facilities: place.facilities,
        kabupaten: place.kabupaten,
        kecamatan: place.kecamatan,
        priority: place.priority,
        priorityScore: place.priorityScore,
        healthScore: place.healthScore,
        concernScore: place.concernScore,
        dataConfidence: place.dataConfidence,
        textReviewCount: place.textReviewCount,
        allReviewCount: place.allReviewCount,
        rank: place.rank,
      })),
    );

    // 3. Destination-aspect signals (dari place.issues).
    await tx.insert(schema.destinationSignals).values(
      places.flatMap((place) =>
        place.issues.map((issue) => ({
          destinationId: place.id,
          aspect: issue.aspect as AspectKey,
          mentionCount: issue.mentionCount,
          negativeCount: issue.negativeCount,
          textReviewCount: issue.textReviewCount,
          allReviewCount: issue.allReviewCount,
          smoothedComplaintRate: issue.smoothedComplaintRate,
          meanConfidence: issue.meanConfidence,
          dataConfidence: issue.dataConfidence,
          severityStatus: issue.severityStatus,
          priority: issue.priority,
          priorityScore: issue.priorityScore,
          priorityComponents: issue.priorityComponents,
          explanation: issue.explanation,
          recommendedVerification: issue.recommendedVerification,
          candidateIntervention: issue.candidateIntervention,
        })),
      ),
    );

    // 4. Data export snapshot (provenance + corpus).
    await tx.insert(schema.dataExports).values({
      schemaVersion: corpus.schemaVersion,
      modelVersion: corpus.modelVersion,
      generatedAt: new Date(corpus.generatedAt),
      sourceManifest: corpus.sourceManifest,
      exportSha256: corpus.exportSha256,
      totalCleanReviews: corpus.totalCleanReviews,
      textualReviewsAnalyzed: corpus.textualReviewsAnalyzed,
      reviewsWithPredictions: corpus.reviewsWithPredictions,
      aspectPredictions: corpus.aspectPredictions,
      actionableDestinations: corpus.actionableDestinations,
      actionableIssues: corpus.actionableIssues,
      limitations: corpus.limitations,
      corpusJson: corpus as unknown as Record<string, unknown>,
    });
  });

  console.log(
    `Seeded: ${places.length} destinations, ` +
      `${corpus.aspects.length} aspects, ` +
      `${places.reduce((n, p) => n + p.issues.length, 0)} signals.`,
  );
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
