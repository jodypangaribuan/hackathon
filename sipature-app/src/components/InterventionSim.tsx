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
      <SectionTitle hint={`${fixable.length} isu actionable`}>
        Simulasi Skenario
      </SectionTitle>
      <p className="mb-4 text-[13px] leading-relaxed text-ink-2">
        Centang isu yang diasumsikan hilang sepenuhnya. Health dan prioritas
        dihitung ulang dari isu intelligence lain yang tersisa.
      </p>
      {fixable.length ? (
        <fieldset className="space-y-1.5">
          <legend className="sr-only">Isu yang diasumsikan selesai</legend>
          {fixable.map((issue) => (
            <label
              key={issue.aspect}
              className="flex cursor-pointer items-center gap-3 rounded-md border px-3 py-2"
              style={{
                borderColor: selected.includes(issue.aspect)
                  ? "var(--series-1)"
                  : "var(--hairline)",
              }}
            >
              <input
                type="checkbox"
                checked={selected.includes(issue.aspect)}
                onChange={() => toggle(issue.aspect)}
                style={{ accentColor: "var(--series-1)" }}
              />
              <AspectIcon aspect={issue.aspect} />
              <span className="min-w-0 flex-1 text-[13px] font-medium">
                {ASPECT_LABEL[issue.aspect]}
              </span>
              <span className="tabular text-[11px] text-muted">
                {num(issue.mentionCount)} sebutan
              </span>
            </label>
          ))}
        </fieldset>
      ) : (
        <p className="py-5 text-center text-[13px] text-muted">
          Tidak ada isu actionable untuk disimulasikan.
        </p>
      )}
      <div
        className="mt-4 rounded-card border p-4"
        style={{
          borderColor: "var(--hairline)",
          background: "var(--surface-2)",
        }}
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <div className="text-[11px] uppercase text-muted">
              Priority score
            </div>
            <div className="mt-2 flex items-center gap-2">
              <span className="tabular text-[22px] text-muted">
                {score(result.before.priorityScore)}
              </span>
              <span>→</span>
              <span className="tabular text-[30px] font-semibold">
                {score(result.after.priorityScore)}
              </span>
            </div>
            <div className="mt-2 flex gap-2">
              <LevelBadge level={levelOf(result.before.priority)} size="sm" />
              <span>→</span>
              <LevelBadge level={levelOf(result.after.priority)} size="sm" />
            </div>
          </div>
          <div>
            <div className="text-[11px] uppercase text-muted">
              Complaint-derived health
            </div>
            <div className="mt-2 flex items-center gap-2">
              <span className="tabular text-[22px] text-muted">
                {result.before.healthScore?.toFixed(1).replace(".", ",") ?? "–"}
              </span>
              <span>→</span>
              <span className="tabular text-[30px] font-semibold">
                {result.after.healthScore?.toFixed(1).replace(".", ",") ?? "–"}
              </span>
            </div>
            <p className="mt-2 text-[11px] text-muted">
              Kosong berarti tidak ada isu tersisa, bukan health sempurna.
            </p>
          </div>
        </div>
        {result.before.healthScore !== null &&
        result.after.healthScore !== null ? (
          <div className="mt-4">
            <Meter
              value={result.after.healthScore}
              max={100}
              label="Health setelah skenario"
              valueLabel={result.after.healthScore.toFixed(1).replace(".", ",")}
            />
          </div>
        ) : null}
      </div>
      <div className="mt-3">
        <Note>{result.caveat}</Note>
      </div>
    </Card>
  );
}
