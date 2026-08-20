"use client";

import { useMemo, useState } from "react";
import { ArrowRight, CheckCircle2, RotateCcw, Sparkles, TrendingDown, TrendingUp } from "lucide-react";
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

  const isSimulating = selected.length > 0;

  const toggle = (aspect: AspectKey) =>
    setSelected((current) =>
      current.includes(aspect)
        ? current.filter((item) => item !== aspect)
        : [...current, aspect],
    );

  const reset = () => setSelected([]);

  const beforeScore = result.before.priorityScore ?? 0;
  const afterScore = result.after.priorityScore ?? 0;
  const scoreDiff = beforeScore - afterScore;

  const beforeHealth = result.before.healthScore !== null ? Math.round(result.before.healthScore) : null;
  const afterHealth = result.after.healthScore !== null ? Math.round(result.after.healthScore) : null;
  const healthDiff = (afterHealth ?? 0) - (beforeHealth ?? 0);

  return (
    <Card className="p-4 sm:p-5">
      <div className="flex items-center justify-between">
        <SectionTitle hint={`${fixable.length} isu dapat dipilih`}>
          Simulasi Dampak Perbaikan
        </SectionTitle>
        {isSimulating ? (
          <button
            type="button"
            onClick={reset}
            className="mb-3 inline-flex items-center gap-1 text-[11.5px] font-medium text-accent hover:underline"
          >
            <RotateCcw size={12} />
            <span>Reset</span>
          </button>
        ) : null}
      </div>

      <p className="mb-3 text-[12.5px] leading-relaxed text-ink-2">
        Centang masalah yang akan ditangani untuk melihat estimasi penurunan tingkat urgensi dan peningkatan kenyamanan wisatawan.
      </p>

      {/* Checkboxes List */}
      {fixable.length ? (
        <fieldset className="space-y-2">
          <legend className="sr-only">Masalah yang diasumsikan selesai</legend>
          {fixable.map((issue) => {
            const isChecked = selected.includes(issue.aspect);
            return (
              <label
                key={issue.aspect}
                className="flex cursor-pointer items-center gap-3 rounded-lg border p-2.5 transition-all"
                style={{
                  borderColor: isChecked ? "var(--accent)" : "var(--hairline)",
                  background: isChecked ? "rgba(235,108,54,0.06)" : "transparent",
                }}
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => toggle(issue.aspect)}
                  className="h-4 w-4 rounded"
                  style={{ accentColor: "var(--accent)" }}
                />
                <AspectIcon aspect={issue.aspect} size={15} />
                <span className="min-w-0 flex-1 text-[13px] font-medium text-ink">
                  {ASPECT_LABEL[issue.aspect]}
                </span>
                <span className="tabular text-[11px] text-muted">
                  {num(issue.negativeCount)} keluhan
                </span>
              </label>
            );
          })}
        </fieldset>
      ) : (
        <p className="py-4 text-center text-[12.5px] text-muted">
          Tidak ada isu yang perlu disimulasikan.
        </p>
      )}

      {/* Impact Result Card */}
      <div
        className="mt-4 space-y-3.5 rounded-xl border p-4"
        style={{
          borderColor: isSimulating ? "var(--accent)" : "var(--hairline)",
          background: "var(--surface-2)",
        }}
      >
        {isSimulating ? (
          <>
            <div className="flex items-center justify-between border-b pb-2.5" style={{ borderColor: "var(--hairline)" }}>
              <div className="inline-flex items-center gap-1.5 text-[11.5px] font-semibold text-accent">
                <Sparkles size={13} />
                <span>Proyeksi Skenario ({selected.length} Isu Ditangani)</span>
              </div>
            </div>

            {/* Score Comparison */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[12px] font-medium text-muted">Skor Urgensi</span>
                {scoreDiff > 0 ? (
                  <span className="inline-flex items-center gap-1 rounded bg-green-500/10 px-1.5 py-0.5 text-[11px] font-semibold text-green-600 dark:text-green-400">
                    <TrendingDown size={12} /> Turun {scoreDiff.toFixed(1)} poin
                  </span>
                ) : null}
              </div>
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="tabular text-[20px] text-muted line-through">
                    {score(beforeScore)}
                  </span>
                  <ArrowRight size={14} className="text-muted" />
                  <span className="tabular text-[26px] font-bold text-accent">
                    {score(afterScore)}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <LevelBadge level={levelOf(result.before.priority)} size="sm" />
                  <span className="text-[10px] text-muted">→</span>
                  <LevelBadge level={levelOf(result.after.priority)} size="sm" />
                </div>
              </div>
            </div>

            {/* Tourist Comfort Comparison */}
            {beforeHealth !== null && afterHealth !== null ? (
              <div className="space-y-2 border-t pt-2.5" style={{ borderColor: "var(--hairline)" }}>
                <div className="flex items-center justify-between">
                  <span className="text-[12px] font-medium text-muted">Kenyamanan Wisatawan</span>
                  {healthDiff > 0 ? (
                    <span className="inline-flex items-center gap-1 rounded bg-green-500/10 px-1.5 py-0.5 text-[11px] font-semibold text-green-600 dark:text-green-400">
                      <TrendingUp size={12} /> Naik +{healthDiff}%
                    </span>
                  ) : null}
                </div>
                <div className="flex items-center gap-2">
                  <span className="tabular text-[20px] text-muted">
                    {beforeHealth}%
                  </span>
                  <ArrowRight size={14} className="text-muted" />
                  <span className="tabular text-[26px] font-bold text-ink">
                    {afterHealth}%
                  </span>
                </div>
                <Meter
                  value={afterHealth}
                  max={100}
                  label="Proyeksi Tingkat Kepuasan"
                  valueLabel={`${afterHealth}%`}
                />
              </div>
            ) : null}
          </>
        ) : (
          /* Baseline Clean State (No Checkbox Selected) */
          <>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wider text-muted">
                  Kondisi Saat Ini
                </div>
                <div className="mt-1 flex items-baseline gap-2">
                  <span className="tabular text-[28px] font-bold text-accent">
                    {score(beforeScore)}
                  </span>
                  <span className="text-[12px] text-muted">Skor Urgensi</span>
                </div>
              </div>
              <LevelBadge level={levelOf(result.before.priority)} />
            </div>

            {beforeHealth !== null ? (
              <div className="border-t pt-2.5" style={{ borderColor: "var(--hairline)" }}>
                <div className="mb-1 flex items-center justify-between text-[12px]">
                  <span className="text-muted">Indeks Kepuasan Pengunjung:</span>
                  <strong className="text-ink">{beforeHealth}%</strong>
                </div>
                <Meter
                  value={beforeHealth}
                  max={100}
                  label="Kepuasan Berdasarkan Ulasan"
                  valueLabel={`${beforeHealth}%`}
                />
              </div>
            ) : null}

            <p className="text-[11.5px] italic text-muted">
              Pilih satu atau lebih masalah di atas untuk melihat simulasi perbaikan.
            </p>
          </>
        )}
      </div>

      <div className="mt-3">
        <Note>
          Simulasi ini adalah estimasi matematis untuk membantu perencanaan perbaikan dan bukan jaminan mutlak kepuasan wisatawan.
        </Note>
      </div>
    </Card>
  );
}
