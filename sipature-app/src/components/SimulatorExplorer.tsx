"use client";
import { useState } from "react";
import type { Place } from "@/lib/types";
import InterventionSim from "@/components/InterventionSim";
import { Card, SectionTitle } from "@/components/ui";
import { score } from "@/lib/format";

export default function SimulatorExplorer({ places }: { places: Place[] }) {
  const [id, setId] = useState(places[0]?.id ?? "");
  const place = places.find((item) => item.id === id) ?? places[0];
  if (!place) return null;
  return (
    <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
      <Card className="h-fit p-4">
        <SectionTitle>Pilih Destinasi</SectionTitle>
        <select
          value={id}
          onChange={(event) => setId(event.target.value)}
          className="w-full rounded-md border bg-surface px-2.5 py-2 text-[13px]"
          style={{ borderColor: "var(--hairline)" }}
        >
          {places.map((item) => (
            <option key={item.id} value={item.id}>
              #{item.rank} · {item.name}
            </option>
          ))}
        </select>
        <dl
          className="mt-4 space-y-2 border-t pt-3 text-[12px]"
          style={{ borderColor: "var(--hairline)" }}
        >
          <div className="flex justify-between">
            <dt className="text-muted">Kabupaten</dt>
            <dd>{place.kabupaten}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-muted">Review bersih</dt>
            <dd>{place.allReviewCount}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-muted">Priority score</dt>
            <dd className="font-semibold">{score(place.priorityScore)}</dd>
          </div>
        </dl>
      </Card>
      <InterventionSim place={place} />
    </div>
  );
}
