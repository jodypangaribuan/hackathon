import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ClipboardCheck, EyeOff, MapPin, ShieldAlert } from "lucide-react";
import InterventionSim from "@/components/InterventionSim";
import { AspectIcon } from "@/components/AppIcon";
import {
  Badge,
  Card,
  ConfidenceBadge,
  LevelBadge,
  Meter,
  Note,
  SectionTitle,
} from "@/components/ui";
import {
  getCorpus,
  getInterventionsForPlace,
  getPlace,
  KIND_LABEL,
} from "@/lib/data";
import {
  ASPECT_LABEL,
  dateTime,
  levelOfPlace,
  num,
  pct,
  score,
} from "@/lib/format";
interface Props {
  params: Promise<{ id: string }>;
}
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const place = await getPlace(id);
  return {
    title: place
      ? `${place.name} — SIPATURE`
      : "Tempat tidak ditemukan — SIPATURE",
  };
}
export default async function DestinationPage({ params }: Props) {
  const { id } = await params;
  const [place, corpus] = await Promise.all([getPlace(id), getCorpus()]);
  if (!place) notFound();
  const actionable = place.issues.filter(
    (issue) => issue.priority !== "Insufficient Data",
  );
  const maxScore = Math.max(
    ...actionable.map((issue) => issue.priorityScore ?? 0),
    0.01,
  );
  const candidates = await getInterventionsForPlace(place.id);
  return (
    <div className="space-y-5">
      <nav className="text-[12px] text-muted">
        <Link href="/">Kembali ke overview</Link>
      </nav>
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-[22px] font-semibold tracking-tight">
              {place.name}
            </h1>
            <LevelBadge level={levelOfPlace(place)} />
            <ConfidenceBadge confidence={place.dataConfidence} />
          </div>
          <p className="mt-1.5 text-[13px] text-ink-2">
            {KIND_LABEL[place.kind]} · {place.kabupaten}
            {place.kecamatan ? ` · Kec. ${place.kecamatan}` : ""}
          </p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            <Badge>{num(place.textReviewCount)} review berteks</Badge>
            <Badge>{num(place.allReviewCount)} seluruh review</Badge>
            {place.entryFee ? <Badge>Tiket: {place.entryFee}</Badge> : null}
            {place.hours ? <Badge>Jam: {place.hours}</Badge> : null}
          </div>
        </div>
        <div className="text-right">
          <div className="tabular text-[40px] font-semibold leading-none">
            {score(place.priorityScore)}
          </div>
          <div className="mt-1 text-[11px] text-muted">
            priority score (0–100)
          </div>
          <div className="mt-1 text-[12px] text-ink-2">
            {place.rank
              ? `Prioritas #${place.rank} dari ${corpus.actionableDestinations}`
              : "Tidak masuk antrean actionable"}
          </div>
        </div>
      </header>
      {place.canonicalStatus === "unresolved_placeholder" ? (
        <Note>
          <MapPin size={13} className="mr-1 inline" />
          Identitas atau koordinat destinasi belum terselesaikan. Record
          dipertahankan untuk audit tetapi tidak diberi prioritas operasional.
        </Note>
      ) : null}
      <div className="grid gap-4 lg:grid-cols-[1fr_400px]">
        <div className="space-y-4">
          <Card className="p-4 sm:p-5">
            <SectionTitle
              hint={
                actionable.length
                  ? `${actionable.length} isu actionable`
                  : undefined
              }
            >
              Reported Issues
            </SectionTitle>
            {actionable.length ? (
              <ol className="space-y-4">
                {actionable.map((issue) => (
                  <li
                    key={issue.aspect}
                    className="rounded-card border p-3.5"
                    style={{ borderColor: "var(--hairline)" }}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <AspectIcon aspect={issue.aspect} />
                      <span className="text-[14px] font-semibold">
                        {ASPECT_LABEL[issue.aspect]}
                      </span>
                      <LevelBadge
                        level={levelOfPlace({
                          ...place,
                          priority: issue.priority,
                        })}
                        size="sm"
                      />
                      <span className="ml-auto text-[11px] text-muted">
                        confidence {pct(issue.meanConfidence, 1)}
                      </span>
                    </div>
                    <div className="mt-2.5">
                      <Meter
                        value={issue.priorityScore ?? 0}
                        max={maxScore}
                        label={`${num(issue.mentionCount)} sebutan · ${num(issue.negativeCount)} negatif · sinyal keluhan smoothed ${pct(issue.smoothedComplaintRate, 1)}`}
                        valueLabel={score(issue.priorityScore)}
                      />
                    </div>
                    <p className="mt-3 text-[12px] leading-relaxed text-ink-2">
                      {issue.explanation}
                    </p>
                    <div className="mt-3 grid gap-2 sm:grid-cols-2">
                      <div
                        className="rounded-md border p-2.5"
                        style={{ borderColor: "var(--hairline)" }}
                      >
                        <div className="mb-1 flex items-center gap-1.5 text-[11px] font-semibold uppercase text-muted">
                          <ClipboardCheck size={13} />
                          Verifikasi berikutnya
                        </div>
                        <p className="text-[12px] text-ink-2">
                          {issue.recommendedVerification}
                        </p>
                      </div>
                      <div
                        className="rounded-md border p-2.5"
                        style={{ borderColor: "var(--hairline)" }}
                      >
                        <div className="mb-1 flex items-center gap-1.5 text-[11px] font-semibold uppercase text-muted">
                          <ShieldAlert size={13} />
                          Kandidat intervensi
                        </div>
                        <p className="text-[12px] text-ink-2">
                          {issue.candidateIntervention}
                        </p>
                      </div>
                    </div>
                    <div className="mt-3">
                      <Note>
                        <EyeOff size={13} className="mr-1 inline" />
                        Kutipan evidence ditahan dari aplikasi publik sampai
                        privacy review selesai. Evidence gate sudah diverifikasi
                        secara restricted.
                      </Note>
                    </div>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="py-6 text-center text-[13px] text-muted">
                Belum ada isu yang memenuhi support, identity, dan evidence gate
                untuk prioritas operasional.
              </p>
            )}
          </Card>
          <Card className="p-4 sm:p-5">
            <SectionTitle>Explainability & Missing Data</SectionTitle>
            <p className="text-[13px] leading-relaxed text-ink-2">
              Priority score memakai complaint frequency, model confidence,
              persistence, dan visitor exposure. Severity, facility gap, dan
              feasibility tidak tersedia sehingga bobotnya dikeluarkan dan bobot
              tersedia dinormalisasi ulang.
            </p>
            <p className="mt-2 text-[12px] text-muted">
              Health{" "}
              {place.healthScore === null
                ? "tidak tersedia"
                : place.healthScore.toFixed(1).replace(".", ",")}{" "}
              adalah kebalikan rata-rata complaint signal yang sudah di-smooth,
              bukan penilaian kualitas total destinasi.
            </p>
          </Card>
        </div>
        <div className="space-y-4">
          <InterventionSim place={place} />
          <Card className="p-4 sm:p-5">
            <SectionTitle>Metadata & Provenance</SectionTitle>
            <dl className="space-y-2 text-[12px]">
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Canonical ID</dt>
                <dd className="break-all text-right">{place.id}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Status identitas</dt>
                <dd>{place.canonicalStatus}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Alamat</dt>
                <dd className="max-w-[240px] text-right">
                  {place.address ?? "tidak terdata"}
                </dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Model</dt>
                <dd>{corpus.modelVersion}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Generated</dt>
                <dd>{dateTime(corpus.generatedAt)}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Severity</dt>
                <dd>unavailable</dd>
              </div>
            </dl>
          </Card>
          {candidates.length ? (
            <Card className="p-4 sm:p-5">
              <SectionTitle hint={`${candidates.length} kandidat`}>
                Kandidat Tindakan
              </SectionTitle>
              <ul className="space-y-2">
                {candidates.map((item) => (
                  <li key={item.id}>
                    <Link
                      href="/umkm"
                      className="flex items-start gap-2 rounded-md border px-3 py-2"
                      style={{ borderColor: "var(--hairline)" }}
                    >
                      <AspectIcon aspect={item.aspect} />
                      <span>
                        <span className="block text-[13px] font-medium">
                          {item.title}
                        </span>
                        <span className="text-[11px] text-muted">
                          pending verifikasi lapangan
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
