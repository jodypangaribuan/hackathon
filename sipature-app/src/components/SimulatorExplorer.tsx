"use client";

import { useState } from "react";
import type { Place } from "@/lib/types";
import InterventionSim from "@/components/InterventionSim";
import { Card, SectionTitle } from "@/components/ui";

export default function SimulatorExplorer({ places, ladder }: { places: Place[]; ladder: number[] }) {
  const [id, setId] = useState(places[0]?.id ?? "");
  const place = places.find((item) => item.id === id) ?? places[0];
  if (!place) return null;

  return (
    <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
      <Card className="h-fit p-4">
        <SectionTitle>Pilih Destinasi</SectionTitle>
        <label className="text-[12px] text-ink-2" htmlFor="destination">Destinasi berprioritas</label>
        <select
          id="destination"
          value={id}
          onChange={(event) => setId(event.target.value)}
          className="mt-1.5 w-full rounded-md border bg-surface px-2.5 py-2 text-[13px]"
          style={{ borderColor: "var(--hairline)" }}
        >
          {places.map((item) => <option key={item.id} value={item.id}>#{item.rank} · {item.name}</option>)}
        </select>
        <dl className="mt-4 space-y-2 border-t pt-3 text-[12px]" style={{ borderColor: "var(--hairline)" }}>
          <div className="flex justify-between"><dt className="text-muted">Kabupaten</dt><dd>{place.kabupaten}</dd></div>
          <div className="flex justify-between"><dt className="text-muted">Ulasan berteks</dt><dd className="tabular">{place.nReviewsText}</dd></div>
          <div className="flex justify-between"><dt className="text-muted">Indeks saat ini</dt><dd className="tabular font-semibold">{place.frictionScore.toFixed(1)}</dd></div>
        </dl>
      </Card>
      <InterventionSim place={place} ladder={ladder} />
    </div>
  );
}
