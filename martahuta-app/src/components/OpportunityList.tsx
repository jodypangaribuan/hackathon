"use client";

/**
 * Layar 3 — daftar Peluang UMKM dengan filter kabupaten & kategori.
 * 35 peluang itu kecil — aman dikirim utuh lewat props.
 */

import Link from "next/link";
import { useMemo, useState } from "react";
import type { Opportunity } from "@/lib/types";
import { km, num, pct } from "@/lib/format";
import { Badge, Card, Empty, Quote } from "@/components/ui";

export default function OpportunityList({
  opportunities,
  kabupatenList,
}: {
  opportunities: Opportunity[];
  kabupatenList: string[];
}) {
  const [kabupaten, setKabupaten] = useState("");
  const [category, setCategory] = useState("");

  const categories = useMemo(
    () => Array.from(new Set(opportunities.map((o) => o.category))).sort(),
    [opportunities],
  );

  const filtered = useMemo(
    () =>
      opportunities
        .filter(
          (o) =>
            (!kabupaten || o.kabupaten === kabupaten) &&
            (!category || o.category === category),
        )
        .sort((a, b) => a.rank - b.rank),
    [opportunities, kabupaten, category],
  );

  const maxScore = Math.max(...opportunities.map((o) => o.score), 0.0001);

  return (
    <div>
      {/* ------------------------------------------------------------ filter */}
      <Card className="mb-4 p-3">
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={kabupaten}
            onChange={(e) => setKabupaten(e.target.value)}
            aria-label="Filter kabupaten"
            className="rounded-md border bg-surface px-2 py-1.5 text-[13px]"
            style={{ borderColor: "var(--hairline)" }}
          >
            <option value="">Semua kabupaten</option>
            {kabupatenList.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
          <div className="flex flex-wrap gap-1">
            <button
              type="button"
              onClick={() => setCategory("")}
              className="rounded-md border px-2.5 py-1 text-[12px] transition-colors"
              style={{
                borderColor: category === "" ? "var(--series-1)" : "var(--hairline)",
                background: category === "" ? "var(--surface-2)" : "transparent",
                fontWeight: category === "" ? 600 : 400,
              }}
            >
              Semua
            </button>
            {categories.map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => setCategory(c === category ? "" : c)}
                className="rounded-md border px-2.5 py-1 text-[12px] transition-colors"
                style={{
                  borderColor: c === category ? "var(--series-1)" : "var(--hairline)",
                  background: c === category ? "var(--surface-2)" : "transparent",
                  fontWeight: c === category ? 600 : 400,
                }}
              >
                {c}
              </button>
            ))}
          </div>
          <span className="tabular ml-auto text-[12px] text-muted">
            {num(filtered.length)} dari {num(opportunities.length)} peluang
          </span>
        </div>
      </Card>

      {/* ------------------------------------------------------------- kartu */}
      {filtered.length === 0 ? (
        <Empty>Tidak ada peluang yang lolos filter.</Empty>
      ) : (
        <ol className="grid gap-3 md:grid-cols-2">
          {filtered.map((o) => (
            <Card as="li" key={o.id} className="flex flex-col p-4">
              <div className="flex items-start gap-3">
                <span aria-hidden className="text-[22px] leading-none">
                  {o.icon}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-baseline gap-2">
                    <h3 className="text-[14px] font-semibold leading-snug">
                      {o.title}
                    </h3>
                    <span className="tabular ml-auto shrink-0 text-[11px] text-muted">
                      #{o.rank}
                    </span>
                  </div>
                  <p className="mt-0.5 text-[12px] text-muted">
                    <Link
                      href={`/destinasi/${o.placeId}`}
                      className="underline decoration-dotted underline-offset-2 hover:text-ink"
                    >
                      {o.placeName}
                    </Link>{" "}
                    · {o.kabupaten}
                  </p>
                </div>
              </div>

              <div className="mt-2 flex flex-wrap gap-1.5">
                <Badge>{o.category}</Badge>
                <Badge>
                  {o.aspectLabel} · {num(o.mentionCount)} sebutan ·{" "}
                  {pct(o.negRate)} negatif
                </Badge>
                {o.gapKm !== null ? (
                  <Badge tone="muted">gap terdekat {km(o.gapKm)}</Badge>
                ) : null}
              </div>

              <p className="mt-2.5 text-[13px] leading-relaxed text-ink-2">
                {o.why}
              </p>

              {o.evidence.length > 0 ? (
                <div className="mt-2.5 space-y-1.5">
                  {o.evidence.slice(0, 2).map((e, i) => (
                    <Quote key={i} text={e} meta="kutipan verbatim ulasan" />
                  ))}
                </div>
              ) : null}

              <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-1.5 text-[11px]">
                <div>
                  <dt className="text-muted">Proksi pasar</dt>
                  <dd className="text-ink-2">{o.marketProxy}</dd>
                </div>
                <div>
                  <dt className="text-muted">Kunjungan kabupaten/thn</dt>
                  <dd className="tabular text-ink-2">{num(o.kabupatenVisits)}</dd>
                </div>
                <div>
                  <dt className="text-muted">Perkiraan modal</dt>
                  <dd className="text-ink-2">{o.investEstimate}</dd>
                </div>
                <div>
                  <dt className="text-muted">Pesaing</dt>
                  <dd className="text-ink-2">{o.competitorNote}</dd>
                </div>
              </dl>

              <div
                className="mt-3 border-t pt-2"
                style={{ borderColor: "var(--hairline)" }}
              >
                <div
                  className="h-1.5 w-full overflow-hidden rounded-full"
                  style={{ background: "var(--gridline)" }}
                  role="img"
                  aria-label={`Skor peluang ${o.score.toFixed(1)}`}
                >
                  <div
                    className="h-full"
                    style={{
                      width: `${Math.min(100, (o.score / maxScore) * 100)}%`,
                      background: "var(--series-3)",
                    }}
                  />
                </div>
                <div className="tabular mt-1 text-[11px] text-muted">
                  skor peluang {o.score.toFixed(1).replace(".", ",")} — volume
                  keluhan × tingkat negatif × gap pasar
                </div>
              </div>
            </Card>
          ))}
        </ol>
      )}
    </div>
  );
}
