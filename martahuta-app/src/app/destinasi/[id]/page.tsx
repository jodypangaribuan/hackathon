/**
 * Layar 2 — Rapor Destinasi.
 * Prioritas perbaikan + kutipan verbatim sebagai bukti + gap infrastruktur +
 * Simulasi Intervensi. Server component; hanya InterventionSim yang client.
 */
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import InterventionSim from "@/components/InterventionSim";
import {
  Badge,
  Card,
  ConfidenceBadge,
  LevelBadge,
  Meter,
  Note,
  Quote,
  SectionTitle,
} from "@/components/ui";
import {
  KIND_LABEL,
  getPlace,
  opportunitiesForPlace,
  rankedPlaces,
} from "@/lib/data";
import {
  ASPECT_ICON,
  ASPECT_LABEL,
  FRICTION_ASPECTS,
  TREND_META,
  km,
  levelOfPlace,
  monthsAgoLabel,
  num,
  pct,
  score,
  severityLabel,
} from "@/lib/format";
import { buildRankLadder } from "@/lib/simulate";

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const place = getPlace(id);
  return {
    title: place
      ? `${place.name} — Rapor Destinasi — MARTAHUTA`
      : "Tempat tidak ditemukan — MARTAHUTA",
  };
}

export default async function DestinasiPage({ params }: Props) {
  const { id } = await params;
  const place = getPlace(id);
  if (!place) notFound();

  const level = levelOfPlace(place);
  const ladder = buildRankLadder(rankedPlaces.map((p) => p.frictionScore));
  const opps = opportunitiesForPlace(place.id);

  const frictionRows = place.aspects
    .filter((a) => a.frictionContrib > 0 && FRICTION_ASPECTS.includes(a.aspect))
    .sort((a, b) => a.priorityRank - b.priorityRank);
  const maxContrib = Math.max(...frictionRows.map((a) => a.frictionContrib), 0.0001);

  const positiveRows = place.aspects.filter(
    (a) => a.aspect === "pemandangan" && a.nMention > 0,
  );

  const gap = place.infraGap;

  return (
    <div className="space-y-5">
      <nav className="text-[12px] text-muted">
        <Link href="/" className="hover:text-ink">
          ← Peta Friksi
        </Link>
      </nav>

      {/* ------------------------------------------------------------ kepala */}
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-[22px] font-semibold tracking-tight">{place.name}</h1>
            <LevelBadge level={level} />
            <ConfidenceBadge confidence={place.confidence} />
          </div>
          <p className="mt-1.5 text-[13px] text-ink-2">
            {KIND_LABEL[place.kind]} · {place.kabupaten}
            {place.kecamatan ? ` · Kec. ${place.kecamatan}` : ""}
          </p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {place.gmapsRating !== null ? (
              <Badge>★ {String(place.gmapsRating).replace(".", ",")} Google Maps</Badge>
            ) : null}
            <Badge>{num(place.nReviewsText)} ulasan berteks</Badge>
            {place.entryFee ? <Badge>Tiket: {place.entryFee}</Badge> : null}
            {place.hours ? <Badge>Jam: {place.hours}</Badge> : null}
            {place.status ? <Badge tone="muted">{place.status}</Badge> : null}
          </div>
        </div>
        <div className="shrink-0 text-right">
          <div className="tabular text-[40px] font-semibold leading-none">
            {score(place.frictionScore)}
          </div>
          <div className="mt-1 text-[11px] text-muted">indeks friksi (0–100)</div>
          {place.rank !== null ? (
            <div className="tabular mt-1 text-[12px] text-ink-2">
              Prioritas <span className="font-semibold">#{place.rank}</span> dari{" "}
              {num(ladder.length)}
            </div>
          ) : (
            <div className="mt-1 max-w-[180px] text-[11px] text-muted">
              Tidak masuk peringkat publik — sampel terlalu kecil
            </div>
          )}
        </div>
      </header>

      {place.nReviewsText === 0 ? (
        <Note>
          Tempat ini belum memiliki ulasan berteks pada dataset. Ia tetap
          ditampilkan sebagai <strong>prioritas survei lapangan</strong> —
          ketiadaan data adalah temuan, bukan alasan menyembunyikan.
        </Note>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-[1fr_400px]">
        {/* --------------------------------------------- kolom kiri: aspek */}
        <div className="min-w-0 space-y-4">
          <Card className="p-4 sm:p-5">
            <SectionTitle
              hint={
                frictionRows.length > 0
                  ? `${frictionRows.length} aspek menyumbang friksi`
                  : undefined
              }
            >
              Prioritas Perbaikan
            </SectionTitle>
            {frictionRows.length === 0 ? (
              <p className="py-6 text-center text-[13px] text-muted">
                Tidak ada aspek friksi dengan kontribusi terukur pada ulasan
                tempat ini.
              </p>
            ) : (
              <ol className="space-y-4">
                {frictionRows.map((a) => {
                  const t = TREND_META[a.trend];
                  return (
                    <li
                      key={a.aspect}
                      className="rounded-card border p-3.5"
                      style={{ borderColor: "var(--hairline)" }}
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <span aria-hidden className="text-[16px]">
                          {ASPECT_ICON[a.aspect]}
                        </span>
                        <span className="text-[14px] font-semibold">
                          {ASPECT_LABEL[a.aspect]}
                        </span>
                        <span
                          className="inline-flex items-center gap-1 text-[11px]"
                          style={{ color: t.tone }}
                        >
                          <span aria-hidden>{t.icon}</span>
                          <span className="text-muted">{t.label}</span>
                        </span>
                        <span className="tabular ml-auto text-[12px] text-muted">
                          dampak {severityLabel(a.severity)}
                        </span>
                      </div>

                      <div className="mt-2.5">
                        <Meter
                          value={a.frictionContrib}
                          max={maxContrib}
                          label={`${num(a.nMention)} sebutan · ${num(a.nNegative)} negatif · tingkat negatif ${pct(a.negRateWilson)} (Wilson 95%)`}
                          valueLabel={`+${(a.frictionContrib * 100).toFixed(2).replace(".", ",")} poin`}
                        />
                      </div>

                      {a.evidence.length > 0 ? (
                        <div className="mt-3 space-y-1.5">
                          {a.evidence.slice(0, 3).map((e, i) => (
                            <Quote
                              key={i}
                              text={e.text}
                              meta={
                                <>
                                  {e.rating !== null ? `★ ${e.rating} · ` : ""}
                                  {monthsAgoLabel(e.monthsAgo)} · kutipan verbatim
                                </>
                              }
                            />
                          ))}
                        </div>
                      ) : null}
                    </li>
                  );
                })}
              </ol>
            )}
          </Card>

          {positiveRows.length > 0 ? (
            <Card className="p-4 sm:p-5">
              <SectionTitle>Yang Sudah Baik</SectionTitle>
              {positiveRows.map((a) => (
                <div key={a.aspect}>
                  <p className="text-[13px] text-ink-2">
                    <span aria-hidden>{ASPECT_ICON[a.aspect]}</span>{" "}
                    <strong>{ASPECT_LABEL[a.aspect]}</strong> disebut{" "}
                    {num(a.nMention)} kali dengan dampak rating{" "}
                    {severityLabel(a.severity)} — kekuatan yang layak dijaga.
                  </p>
                  {a.evidence.length > 0 ? (
                    <div className="mt-2 space-y-1.5">
                      {a.evidence.slice(0, 2).map((e, i) => (
                        <Quote
                          key={i}
                          text={e.text}
                          meta={
                            <>
                              {e.rating !== null ? `★ ${e.rating} · ` : ""}
                              {monthsAgoLabel(e.monthsAgo)}
                            </>
                          }
                        />
                      ))}
                    </div>
                  ) : null}
                </div>
              ))}
            </Card>
          ) : null}
        </div>

        {/* ----------------------------------------- kolom kanan: sim + gap */}
        <div className="min-w-0 space-y-4">
          <InterventionSim place={place} ladder={ladder} />

          <Card className="p-4 sm:p-5">
            <SectionTitle>Gap Infrastruktur</SectionTitle>
            <dl className="space-y-2.5 text-[13px]">
              <div className="flex items-baseline justify-between gap-3">
                <dt className="text-ink-2">🍽️ Kuliner terdekat</dt>
                <dd className="tabular text-right">
                  {gap.nearestFood ? (
                    <>
                      <span className="font-medium">{km(gap.nearestFood.km)}</span>
                      <span className="block text-[11px] text-muted">
                        {gap.nearestFood.name}
                      </span>
                    </>
                  ) : (
                    <span className="text-muted">tidak terdata</span>
                  )}
                </dd>
              </div>
              <div className="flex items-baseline justify-between gap-3">
                <dt className="text-ink-2">🕌 Kuliner halal terdekat</dt>
                <dd className="tabular text-right">
                  {gap.nearestHalalFood ? (
                    <>
                      <span className="font-medium">{km(gap.nearestHalalFood.km)}</span>
                      <span className="block text-[11px] text-muted">
                        {gap.nearestHalalFood.name}
                      </span>
                    </>
                  ) : (
                    <span className="text-muted">tidak terdata</span>
                  )}
                </dd>
              </div>
              <div className="flex items-baseline justify-between gap-3">
                <dt className="text-ink-2">🛏️ Akomodasi terdekat</dt>
                <dd className="tabular text-right">
                  {gap.nearestLodging ? (
                    <>
                      <span className="font-medium">{km(gap.nearestLodging.km)}</span>
                      <span className="block text-[11px] text-muted">
                        {gap.nearestLodging.name}
                      </span>
                    </>
                  ) : (
                    <span className="text-muted">tidak terdata</span>
                  )}
                </dd>
              </div>
              <div className="flex items-baseline justify-between gap-3">
                <dt className="text-ink-2">🚻 Toilet</dt>
                <dd>
                  {gap.hasToilet === null ? (
                    <span className="text-muted">tidak terdata</span>
                  ) : gap.hasToilet ? (
                    "tercatat ada"
                  ) : (
                    <span style={{ color: "var(--status-critical)" }}>
                      ✕ tidak tercatat
                    </span>
                  )}
                </dd>
              </div>
            </dl>

            {gap.publicTransport.length > 0 ? (
              <div className="mt-4">
                <div className="mb-1.5 text-[12px] font-medium text-ink-2">
                  🚌 Angkutan umum tercatat
                </div>
                <ul className="space-y-1.5">
                  {gap.publicTransport.map((r, i) => (
                    <li
                      key={i}
                      className="rounded-md border px-2.5 py-1.5 text-[12px]"
                      style={{ borderColor: "var(--hairline)" }}
                    >
                      <span className="font-medium">{r.name}</span>
                      <span className="block text-[11px] text-muted">
                        via {r.via} · {r.hours} · {r.price}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            <div className="mt-3">
              <Note>
                Jarak dihitung garis lurus antar koordinat dataset. Korelasi gap
                infrastruktur ↔ keluhan bukan kausalitas.
              </Note>
            </div>
          </Card>

          {opps.length > 0 ? (
            <Card className="p-4 sm:p-5">
              <SectionTitle hint={`${opps.length} peluang`}>
                Peluang UMKM di Sini
              </SectionTitle>
              <ul className="space-y-2">
                {opps.map((o) => (
                  <li key={o.id}>
                    <Link
                      href="/umkm"
                      className="flex items-start gap-2.5 rounded-md border px-3 py-2 transition-colors hover:bg-surface-2"
                      style={{ borderColor: "var(--hairline)" }}
                    >
                      <span aria-hidden className="text-[16px]">
                        {o.icon}
                      </span>
                      <span className="min-w-0">
                        <span className="block text-[13px] font-medium text-ink">
                          {o.title}
                        </span>
                        <span className="block text-[11px] text-muted">
                          dari keluhan {o.aspectLabel.toLowerCase()} ·{" "}
                          {num(o.mentionCount)} sebutan
                        </span>
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            </Card>
          ) : null}
        </div>
      </div>
    </div>
  );
}
