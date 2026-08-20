"use client";

import { useMemo, useState } from "react";
import type { AspectKey, Place } from "@/lib/types";
import { ASPECT_LABEL, levelOf, num, score } from "@/lib/format";
import { simulateFixes } from "@/lib/simulate";
import { AspectIcon } from "@/components/AppIcon";
import { Card, LevelBadge, Meter, Note, SectionTitle } from "@/components/ui";

export default function InterventionSim({ place }: { place: Place }) {
  const [selected, setSelected] = useState<AspectKey[]>([]);
  const fixable = useMemo(
    () =>
      place.issues.filter((issue) => issue.priority !== "Insufficient Data"),
    [place],
  );
  const result = useMemo(
    () => simulateFixes(place, selected),
    [place, selected],
  );
  const toggle = (aspect: AspectKey) =>
    setSelected((current) =>
      current.includes(aspect)
        ? current.filter((item) => item !== aspect)
        : [...current, aspect],
    );

  return (
    <Card className="p-4 sm:p-5">
      <SectionTitle hint={`${fixable.length} isu dapat diperbaiki`}>
        Simulasi Dampak Perbaikan
      </SectionTitle>
      <p className="mb-3.5 text-[12.5px] leading-relaxed text-ink-2">
        Centang masalah yang akan ditangani untuk melihat estimasi penurunan tingkat urgensi dan peningkatan kenyamanan wisatawan.
      </p>
      {fixable.length ? (
        <fieldset className="space-y-2">
          <legend className="sr-only">Masalah yang diasumsikan selesai</legend>
          {fixable.map((issue) => (
            <label
              key={issue.aspect}
              className="flex cursor-pointer items-center gap-3 rounded-md border p-2.5 transition-colors"
              style={{
                borderColor: selected.includes(issue.aspect)
                  ? "var(--accent)"
                  : "var(--hairline)",
                background: selected.includes(issue.aspect)
                  ? "rgba(235,108,54,0.05)"
                  : "transparent",
              }}
            >
              <input
                type="checkbox"
                checked={selected.includes(issue.aspect)}
                onChange={() => toggle(issue.aspect)}
                className="h-4 w-4 rounded"
                style={{ accentColor: "var(--accent)" }}
              />
              <AspectIcon aspect={issue.aspect} />
              <span className="min-w-0 flex-1 text-[13px] font-medium text-ink">
                {ASPECT_LABEL[issue.aspect]}
              </span>
              <span className="tabular text-[11px] text-muted">
                {num(issue.negativeCount)} keluhan
              </span>
            </label>
          ))}
        </fieldset>
      ) : (
        <p className="py-4 text-center text-[12.5px] text-muted">
          Tidak ada isu yang perlu disimulasikan.
        </p>
      )}
      <div
        className="mt-4 rounded-xl border p-4"
        style={{
          borderColor: "var(--hairline)",
          background: "var(--surface-2)",
        }}
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <div className="text-[10.5px] font-semibold uppercase tracking-wider text-muted">
              Skor Urgensi
            </div>
            <div className="mt-1 flex items-center gap-2">
              <span className="tabular text-[20px] text-muted line-through">
                {score(result.before.priorityScore)}
              </span>
              <span className="text-muted">→</span>
              <span className="tabular text-[26px] font-bold text-accent">
                {score(result.after.priorityScore)}
              </span>
            </div>
            <div className="mt-1.5 flex items-center gap-1.5">
              <LevelBadge level={levelOf(result.before.priority)} size="sm" />
              <span className="text-xs text-muted">→</span>
              <LevelBadge level={levelOf(result.after.priority)} size="sm" />
            </div>
          </div>
          <div>
            <div className="text-[10.5px] font-semibold uppercase tracking-wider text-muted">
              Kenyamanan Wisatawan
            </div>
            <div className="mt-1 flex items-center gap-2">
              <span className="tabular text-[20px] text-muted">
                {result.before.healthScore !== null ? `${result.before.healthScore.toFixed(0)}%` : "–"}
              </span>
              <span className="text-muted">→</span>
              <span className="tabular text-[26px] font-bold text-ink">
                {result.after.healthScore !== null ? `${result.after.healthScore.toFixed(0)}%` : "–"}
              </span>
            </div>
            <p className="mt-1 text-[11px] text-muted">
              Estimasi indeks kepuasan
            </p>
          </div>
        </div>
        {result.before.healthScore !== null &&
        result.after.healthScore !== null ? (
          <div className="mt-3.5 border-t pt-3" style={{ borderColor: "var(--hairline)" }}>
            <Meter
              value={result.after.healthScore}
              max={100}
              label="Proyeksi Kepuasan Pasca Perbaikan"
              valueLabel={`${result.after.healthScore.toFixed(0)}%`}
            />
          </div>
        ) : null}
      </div>
      <div className="mt-3">
        <Note>
          Simulasi ini adalah estimasi matematis untuk membantu perencanaan anggaran dan bukan jaminan mutlak kepuasan wisatawan.
        </Note>
      </div>
    </Card>
  );
}
