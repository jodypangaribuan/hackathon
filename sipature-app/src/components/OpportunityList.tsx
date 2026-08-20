"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { Intervention } from "@/lib/types";
import { num, pct, score } from "@/lib/format";
import { Badge, Card, Empty, Note } from "@/components/ui";
import { AspectIcon } from "@/components/AppIcon";

const CATEGORY_LABEL: Record<string, string> = {
  environmental: "Lingkungan & Sanitasi",
  infrastructure: "Akses & Infrastruktur",
  visitor_experience: "Kenyamanan & Nilai",
  operations: "Tata Kelola & Layanan",
};

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
            className="rounded-md border bg-surface px-2.5 py-1.5 text-[12.5px] outline-none"
            style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}
          >
            <option value="">Semua Kabupaten</option>
            {kabupatenList.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
          <button
            onClick={() => setCategory("")}
            className="rounded-md border px-2.5 py-1.5 text-[12px] font-medium transition-colors"
            style={{
              borderColor: category ? "var(--hairline)" : "var(--accent)",
              background: category ? "transparent" : "rgba(235,108,54,0.08)",
              color: category ? "var(--text-secondary)" : "var(--accent)",
            }}
          >
            Semua Pilar
          </button>
          {categories.map((item) => (
            <button
              key={item}
              onClick={() => setCategory(item === category ? "" : item)}
              className="rounded-md border px-2.5 py-1.5 text-[12px] font-medium transition-colors"
              style={{
                borderColor: item === category ? "var(--accent)" : "var(--hairline)",
                background: item === category ? "rgba(235,108,54,0.08)" : "transparent",
                color: item === category ? "var(--accent)" : "var(--text-secondary)",
              }}
            >
              {CATEGORY_LABEL[item] ?? item}
            </button>
          ))}
          <span className="ml-auto text-[12px] text-muted">
            Menampilkan <strong className="text-ink">{num(filtered.length)}</strong> dari {num(interventions.length)} usulan
          </span>
        </div>
      </Card>
      {filtered.length ? (
        <ol className="grid gap-3 md:grid-cols-2">
          {filtered.map((item) => (
            <Card as="li" key={item.id} className="flex flex-col justify-between p-4">
              <div>
                <div className="flex items-start gap-3">
                  <span className="mt-0.5 rounded-md bg-surface-2 p-1.5">
                    <AspectIcon aspect={item.aspect} size={16} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-[14px] font-semibold leading-snug">{item.title}</h3>
                    <p className="mt-1 text-[12px] text-ink-2">
                      <Link
                        href={`/destinasi/${item.placeId}`}
                        className="font-medium hover:text-accent hover:underline"
                      >
                        {item.placeName}
                      </Link>{" "}
                      · <span className="text-muted">{item.kabupaten}</span>
                    </p>
                  </div>
                  <span className="rounded bg-ink/10 px-1.5 py-0.5 text-[10.5px] font-bold text-ink">
                    #{item.rank}
                  </span>
                </div>
                <div className="mt-2.5 flex flex-wrap gap-1.5">
                  <Badge>{item.aspectLabel}</Badge>
                  <Badge>{item.priority}</Badge>
                  <Badge>
                    {num(item.negativeCount)} negatif / {num(item.mentionCount)} sebutan
                  </Badge>
                </div>
                <div
                  className="mt-3 rounded-md border p-2.5 text-[12px] leading-relaxed"
                  style={{
                    borderColor: "var(--hairline)",
                    background: "var(--surface-2)",
                  }}
                >
                  <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                    Protokol Verifikasi Lapangan
                  </div>
                  <p className="mt-1 text-ink-2">{item.verification}</p>
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between border-t pt-2.5 text-[11px] text-muted" style={{ borderColor: "var(--hairline)" }}>
                <span>Skor prioritas {score(item.priorityScore)}</span>
                <span className="italic">Evidence restricted (privacy-safe)</span>
              </div>
            </Card>
          ))}
        </ol>
      ) : (
        <Empty>Tidak ada kandidat untuk filter yang dipilih.</Empty>
      )}
    </div>
  );
}
