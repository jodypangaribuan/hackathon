import type { AspectKey, Place, Priority, SimulateResult } from "./types";
import { ASPECT_LABEL } from "./format";

const ORDER: Priority[] = [
  "Critical",
  "High",
  "Medium",
  "Monitor",
  "Insufficient Data",
];

export function simulateFixes(
  place: Place,
  fixes: AspectKey[],
): SimulateResult {
  const selected = new Set(fixes);
  const remaining = place.issues.filter(
    (issue) =>
      issue.priority !== "Insufficient Data" && !selected.has(issue.aspect),
  );
  const top = [...remaining].sort(
    (a, b) =>
      ORDER.indexOf(a.priority) - ORDER.indexOf(b.priority) ||
      (b.priorityScore ?? -1) - (a.priorityScore ?? -1),
  )[0];
  const healthScore = remaining.length
    ? 100 *
      (1 -
        remaining.reduce((sum, issue) => sum + issue.smoothedComplaintRate, 0) /
          remaining.length)
    : null;
  return {
    placeId: place.id,
    placeName: place.name,
    before: {
      healthScore: place.healthScore,
      priority: place.priority,
      priorityScore: place.priorityScore,
    },
    after: {
      healthScore,
      priority: top?.priority ?? "Insufficient Data",
      priorityScore: top?.priorityScore ?? null,
    },
    removed: place.issues
      .filter(
        (issue) =>
          selected.has(issue.aspect) && issue.priority !== "Insufficient Data",
      )
      .map((issue) => ({
        aspect: issue.aspect,
        label: ASPECT_LABEL[issue.aspect],
      })),
    caveat:
      "Analisis skenario, bukan prediksi kausal. Aspek terpilih diasumsikan hilang sepenuhnya sementara seluruh sinyal lain tetap. Hasil tidak mengestimasi efektivitas intervensi, dampak lanjutan, atau ulasan masa depan.",
  };
}
