"use client";
import Link from "next/link";
import { useMemo, useState } from "react";
import type { Intervention } from "@/lib/types";
import { num, pct, score } from "@/lib/format";
import { Badge, Card, Empty, Note } from "@/components/ui";
import { AspectIcon } from "@/components/AppIcon";

export default function OpportunityList({
  interventions,
  kabupatenList,
}: {
  interventions: Intervention[];
  kabupatenList: string[];
}) {
  const [kabupaten, setKabupaten] = useState("");
  const [category, setCategory] = useState("");
  const categories = useMemo(
    () =>
      Array.from(new Set(interventions.map((item) => item.category))).sort(),
    [interventions],
  );
  const filtered = useMemo(
    () =>
      interventions.filter(
        (item) =>
          (!kabupaten || item.kabupaten === kabupaten) &&
          (!category || item.category === category),
      ),
    [interventions, kabupaten, category],
  );
  return (
    <div>
      <Card className="mb-4 p-3">
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={kabupaten}
            onChange={(event) => setKabupaten(event.target.value)}
            className="rounded-md border bg-surface px-2 py-1.5 text-[13px]"
            style={{ borderColor: "var(--hairline)" }}
          >
            <option value="">Semua kabupaten</option>
            {kabupatenList.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
          <button
            onClick={() => setCategory("")}
            className="rounded-md border px-2.5 py-1 text-[12px]"
            style={{
              borderColor: category ? "var(--hairline)" : "var(--series-1)",
            }}
          >
            Semua
          </button>
          {categories.map((item) => (
            <button
              key={item}
              onClick={() => setCategory(item === category ? "" : item)}
              className="rounded-md border px-2.5 py-1 text-[12px]"
              style={{
                borderColor:
                  item === category ? "var(--series-1)" : "var(--hairline)",
              }}
            >
              {item}
            </button>
          ))}
          <span className="ml-auto text-[12px] text-muted">
            {num(filtered.length)} dari {num(interventions.length)} kandidat
          </span>
        </div>
      </Card>
      {filtered.length ? (
        <ol className="grid gap-3 md:grid-cols-2">
          {filtered.map((item) => (
            <Card as="li" key={item.id} className="flex flex-col p-4">
              <div className="flex items-start gap-3">
                <AspectIcon aspect={item.aspect} size={18} />
                <div className="min-w-0 flex-1">
                  <h3 className="text-[14px] font-semibold">{item.title}</h3>
                  <p className="mt-0.5 text-[12px] text-muted">
                    <Link
                      href={`/destinasi/${item.placeId}`}
                      className="underline decoration-dotted"
                    >
                      {item.placeName}
                    </Link>{" "}
                    · {item.kabupaten}
                  </p>
                </div>
                <span className="text-[11px] text-muted">#{item.rank}</span>
              </div>
              <div className="mt-2 flex flex-wrap gap-1.5">
                <Badge>{item.aspectLabel}</Badge>
                <Badge>{item.priority}</Badge>
                <Badge>
                  {num(item.mentionCount)} sebutan ·{" "}
                  {pct(item.smoothedComplaintRate, 1)} smoothed
                </Badge>
              </div>
              <p className="mt-3 text-[13px] leading-relaxed text-ink-2">
                {item.explanation}
              </p>
              <div
                className="mt-3 rounded-md border p-3"
                style={{
                  borderColor: "var(--hairline)",
                  background: "var(--surface-2)",
                }}
              >
                <div className="text-[11px] font-semibold uppercase text-muted">
                  Wajib diverifikasi
                </div>
                <p className="mt-1 text-[12px] text-ink-2">
                  {item.verification}
                </p>
              </div>
              <div
                className="mt-3 border-t pt-2 text-[11px] text-muted"
                style={{ borderColor: "var(--hairline)" }}
              >
                priority score {score(item.priorityScore)} · evidence text
                ditahan pending privacy review
              </div>
            </Card>
          ))}
        </ol>
      ) : (
        <Empty>Tidak ada kandidat yang lolos filter.</Empty>
      )}
      <div className="mt-4">
        <Note>
          Kandidat ini bukan rekomendasi investasi, estimasi modal, atau hasil
          studi kelayakan. Ia adalah tindakan awal yang diturunkan deterministik
          dari reported issue SIPATURE Intelligence dan wajib diperiksa di
          lapangan.
        </Note>
      </div>
    </div>
  );
}
