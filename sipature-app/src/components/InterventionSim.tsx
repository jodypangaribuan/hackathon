"use client";

/**
 * Simulasi Intervensi — "bila keluhan ini diselesaikan, indeks jadi berapa?"
 *
 * Client component murni: hanya menerima satu Place + tangga peringkat lewat
 * props. Tidak pernah mengimpor @/lib/data (places.json 892 KB tetap di server).
 * Seluruh matematika ada di simulateFixes(); komponen ini hanya menampilkan.
 */

import { useMemo, useState } from "react";
import type { AspectKey, AspectRow, Place } from "@/lib/types";
import {
  ASPECT_LABEL,
  FRICTION_ASPECTS,
  levelOf,
  num,
} from "@/lib/format";
import { simulateFixes } from "@/lib/simulate";
import { Card, LevelBadge, Meter, Note, SectionTitle } from "@/components/ui";
import { AspectIcon } from "@/components/AppIcon";

/** Desimal gaya Indonesia: 10.9 → "10,9". */
function dec(v: number, digits = 1): string {
  return v.toFixed(digits).replace(".", ",");
}

/** Kontribusi aspek (0–0,35) ditampilkan pada skala skor 0–100. */
function contribPoints(a: AspectRow): number {
  return a.frictionContrib * 100;
}

export default function InterventionSim({
  place,
  ladder,
}: {
  place: Place;
  ladder: number[];
}) {
  const [selected, setSelected] = useState<AspectKey[]>([]);

  // Ganti tempat → kosongkan pilihan (penyesuaian state saat render, tanpa efek).
  const [seenId, setSeenId] = useState(place.id);
  if (seenId !== place.id) {
    setSeenId(place.id);
    setSelected([]);
  }

  /** Hanya aspek friksi yang benar-benar menyumbang indeks. */
  const fixable = useMemo(
    () =>
      place.aspects
        .filter(
          (a) => a.frictionContrib > 0 && FRICTION_ASPECTS.includes(a.aspect),
        )
        .sort((x, y) => x.priorityRank - y.priorityRank),
    [place],
  );

  const result = useMemo(
    () => simulateFixes(place, selected, ladder),
    [place, selected, ladder],
  );

  const beforeLevel = levelOf(result.before.score, place.confidence);
  const afterLevel = levelOf(result.after.score, place.confidence);
  const levelChanged = beforeLevel.key !== afterLevel.key;

  const drop = Math.max(0, result.before.score - result.after.score);
  const dropPct =
    result.before.score > 0 ? Math.round((drop / result.before.score) * 100) : 0;

  const rankShift =
    result.before.rank !== null && result.after.rank !== null
      ? result.after.rank - result.before.rank
      : 0;

  const allSelected = selected.length === fixable.length && fixable.length > 0;

  function toggle(aspect: AspectKey) {
    setSelected((prev) =>
      prev.includes(aspect) ? prev.filter((a) => a !== aspect) : [...prev, aspect],
    );
  }

  return (
    <Card className="p-4 sm:p-5">
      <SectionTitle
        hint={
          fixable.length > 0
            ? `${fixable.length} aspek dapat diintervensi`
            : undefined
        }
      >
        Simulasi Intervensi
      </SectionTitle>

      <p className="mb-4 text-[13px] leading-relaxed text-ink-2">
        Centang keluhan yang dianggap dapat diselesaikan. Indeks friksi dan posisi{" "}
        <span className="font-medium text-ink">{place.name}</span> pada daftar
        prioritas dihitung ulang seketika.
      </p>

      {fixable.length === 0 ? (
        <p className="mb-4 rounded-md border px-3 py-4 text-center text-[13px] text-muted"
           style={{ borderColor: "var(--hairline)" }}>
          Tidak ada aspek friksi dengan kontribusi terukur di tempat ini.
          Tidak ada yang dapat disimulasikan.
        </p>
      ) : (
        <>
          {/* ------------------------------------------------ kendali daftar */}
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => setSelected(fixable.map((a) => a.aspect))}
              disabled={allSelected}
              className="rounded-md border px-2.5 py-1 text-[12px] text-ink-2 transition-colors hover:text-ink disabled:opacity-40"
              style={{ borderColor: "var(--hairline)" }}
            >
              Pilih semua
            </button>
            <button
              type="button"
              onClick={() => setSelected([])}
              disabled={selected.length === 0}
              className="rounded-md border px-2.5 py-1 text-[12px] text-ink-2 transition-colors hover:text-ink disabled:opacity-40"
              style={{ borderColor: "var(--hairline)" }}
            >
              Kosongkan
            </button>
            <span className="tabular ml-auto text-[12px] text-muted">
              {selected.length} dari {fixable.length} dipilih
            </span>
          </div>

          {/* -------------------------------------------------- daftar aspek */}
          <fieldset className="mb-4">
            <legend className="sr-only">
              Aspek friksi yang dianggap diselesaikan
            </legend>
            <ul className="space-y-1.5">
              {fixable.map((a) => {
                const on = selected.includes(a.aspect);
                return (
                  <li key={a.aspect}>
                    <label
                      className="flex cursor-pointer items-center gap-3 rounded-md border px-3 py-2 transition-colors"
                      style={{
                        borderColor: on ? "var(--series-1)" : "var(--hairline)",
                        background: on ? "var(--surface-2)" : "transparent",
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={on}
                        onChange={() => toggle(a.aspect)}
                        className="h-4 w-4 shrink-0"
                        style={{ accentColor: "var(--series-1)" }}
                      />
                       <AspectIcon aspect={a.aspect} className="shrink-0" />
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-[13px] font-medium text-ink">
                          {ASPECT_LABEL[a.aspect]}
                        </span>
                        <span className="tabular block text-[11px] text-muted">
                          {num(a.nMention)} sebutan · {num(a.nNegative)} negatif
                        </span>
                      </span>
                      <span className="tabular shrink-0 text-right text-[13px] font-medium text-ink">
                        −{dec(contribPoints(a), 2)}
                        <span className="ml-1 text-[11px] font-normal text-muted">
                          poin
                        </span>
                      </span>
                    </label>
                  </li>
                );
              })}
            </ul>
          </fieldset>
        </>
      )}

      {/* -------------------------------------------------------- hasil */}
      <div
        aria-live="polite"
        className="rounded-card border p-4"
        style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}
      >
        <div className="grid gap-4 sm:grid-cols-2">
          {/* indeks */}
          <div>
            <div className="text-[11px] uppercase tracking-wide text-muted">
              Indeks friksi
            </div>
            <div className="mt-1.5 flex items-baseline gap-2">
              <span className="sr-only">Sebelum</span>
              <span className="tabular text-[24px] font-semibold leading-none text-muted transition-colors">
                {dec(result.before.score)}
              </span>
              <span aria-hidden className="text-[14px] text-muted">
                →
              </span>
              <span className="sr-only">menjadi</span>
              <span className="tabular text-[32px] font-semibold leading-none text-ink transition-colors">
                {dec(result.after.score)}
              </span>
            </div>
            <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
              <LevelBadge level={beforeLevel} size="sm" />
              <span aria-hidden className="text-[12px] text-muted">
                →
              </span>
              <LevelBadge level={afterLevel} size="sm" />
            </div>
            {levelChanged ? (
              <p className="mt-1.5 text-[11px] text-muted">
                Tingkat friksi turun dari {beforeLevel.label.toLowerCase()} ke{" "}
                {afterLevel.label.toLowerCase()}.
              </p>
            ) : null}
          </div>

          {/* peringkat */}
          <div>
            <div className="text-[11px] uppercase tracking-wide text-muted">
              Peringkat prioritas
            </div>
            {result.before.rank === null || result.after.rank === null ? (
              <p className="mt-1.5 text-[13px] leading-relaxed text-muted">
                Tempat ini belum masuk peringkat publik karena jumlah ulasan
                berteks terlalu sedikit. Simulasi hanya mengubah indeks.
              </p>
            ) : (
              <>
                <div className="mt-1.5 flex items-baseline gap-2">
                  <span className="sr-only">Sebelum</span>
                  <span className="tabular text-[24px] font-semibold leading-none text-muted transition-colors">
                    #{result.before.rank}
                  </span>
                  <span aria-hidden className="text-[14px] text-muted">
                    →
                  </span>
                  <span className="sr-only">menjadi</span>
                  <span className="tabular text-[32px] font-semibold leading-none text-ink transition-colors">
                    #{result.after.rank}
                  </span>
                </div>
                <p className="mt-2.5 text-[11px] leading-relaxed text-muted">
                  {rankShift > 0
                    ? `Bergeser ${num(rankShift)} posisi lebih rendah pada antrean prioritas.`
                    : "Posisi pada antrean prioritas tidak berubah."}{" "}
                  Peringkat 1 = paling mendesak, dari {num(ladder.length)} tempat
                  berperingkat.
                </p>
              </>
            )}
          </div>
        </div>

        {/* batang perbandingan — satu hue, panjang menyandikan besaran */}
        <div className="mt-4 space-y-2.5">
          <Meter
            value={result.before.score}
            max={result.before.score}
            label="Sebelum"
            valueLabel={dec(result.before.score)}
          />
          <Meter
            value={result.after.score}
            max={result.before.score}
            label="Sesudah"
            valueLabel={dec(result.after.score)}
          />
        </div>

        <p className="tabular mt-3 text-[12px] text-ink-2">
          {selected.length === 0 ? (
            <span className="text-muted">
              Belum ada aspek yang dipilih — angka di atas adalah keadaan saat ini.
            </span>
          ) : (
            <>
              Total penurunan{" "}
              <span className="font-semibold text-ink">−{dec(drop)} poin</span>{" "}
              <span className="text-muted">({dropPct}% dari indeks awal)</span>
            </>
          )}
        </p>
      </div>

      {/* ------------------------------------------ peringatan kausalitas */}
      {/* WAJIB permanen: tidak dapat ditutup, tidak dapat disembunyikan. */}
      <div className="mt-3">
        <Note>
          {result.caveat} Indeks dasar dihitung dengan baseline{" "}
          <em>keyword + rating</em>, bukan keluaran model IndoBERT terlatih.
        </Note>
      </div>
    </Card>
  );
}
