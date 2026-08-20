import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  CheckCircle2,
  ClipboardCheck,
  Compass,
  EyeOff,
  HelpCircle,
  Info,
  MapPin,
  MessageSquareQuote,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import InterventionSim from "@/components/InterventionSim";
import AlertStatusControl from "@/components/AlertStatusControl";
import EvidenceQuotesList from "@/components/EvidenceQuotesList";
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
  CONFIDENCE_LABEL,
  dateTime,
  levelOfPlace,
  num,
  pct,
  score,
} from "@/lib/format";

export const dynamic = "force-dynamic";

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

  return (
    <div className="space-y-6">
      {/* Breadcrumbs */}
      <nav className="flex items-center gap-2 text-[12.5px] text-muted">
        <Link href="/" className="hover:text-ink hover:underline">← Overview</Link>
        <span>/</span>
        <Link href="/destinasi" className="hover:text-ink hover:underline">Katalog Destinasi</Link>
        <span>/</span>
        <span className="truncate font-medium text-ink">{place.name}</span>
      </nav>

      {/* Destination Header Card */}
      <Card className="p-5 sm:p-6">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <h1 className="text-[24px] font-semibold tracking-tight sm:text-[28px]">
                {place.name}
              </h1>
              <LevelBadge level={levelOfPlace(place)} />
              <ConfidenceBadge confidence={place.dataConfidence} />
            </div>

            <p className="mt-1.5 flex items-center gap-1.5 text-[13px] text-ink-2">
              <MapPin size={13} className="text-muted" />
              <span>{KIND_LABEL[place.kind]}</span>
              <span>·</span>
              <strong className="text-ink">{place.kabupaten}</strong>
              {place.kecamatan ? <span>(Kec. {place.kecamatan})</span> : null}
            </p>

            <div className="mt-3 flex flex-wrap gap-2">
              <Badge>{num(place.textReviewCount)} ulasan berteks dianalisis</Badge>
              <Badge>{num(place.allReviewCount)} total ulasan wisatawan</Badge>
              {place.entryFee ? <Badge>Tiket: {place.entryFee}</Badge> : null}
              {place.hours ? <Badge>Jam Operasional: {place.hours}</Badge> : null}
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-4 rounded-xl border bg-surface-2 p-4 lg:text-right" style={{ borderColor: "var(--hairline)" }}>
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-wider text-muted">
                Skor Urgensi Perbaikan
              </div>
              <div className="mt-0.5 tabular text-[36px] font-bold leading-none text-accent">
                {score(place.priorityScore)}
              </div>
              <div className="mt-1 text-[11.5px] text-ink-2">
                {place.rank
                  ? `Peringkat #${place.rank} dari ${corpus.actionableDestinations} lokasi`
                  : "Kondisi stabil / Tidak mendesak"}
              </div>
            </div>
          </div>
        </div>
      </Card>

      {place.canonicalStatus === "unresolved_placeholder" ? (
        <Note>
          <MapPin size={13} className="mr-1 inline text-accent" />
          <strong>Catatan Lokasi:</strong> Koordinat spesifik destinasi ini masih dalam proses sinkronisasi lapangan. Data ulasan tetap tercatat untuk kebutuhan evaluasi.
        </Note>
      ) : null}

      {/* Main Grid: Left Issues & Action, Right Scenario Simulator */}
      <div className="grid gap-5 lg:grid-cols-[1fr_400px]">
        {/* Left Column: Issues & Work Orders */}
        <div className="space-y-5">
          <Card className="p-4 sm:p-5">
            <SectionTitle
              hint={
                actionable.length
                  ? `${actionable.length} masalah teridentifikasi`
                  : "Tidak ada keluhan kritis"
              }
            >
              Daftar Masalah &amp; Rekomendasi Tindak Lanjut
            </SectionTitle>

            {actionable.length ? (
              <ol className="space-y-4">
                {actionable.map((issue) => (
                  <li
                    key={issue.aspect}
                    className="rounded-card border p-4 transition-all"
                    style={{ borderColor: "var(--hairline)" }}
                  >
                    {/* Aspect Title & Status */}
                    <div className="flex flex-wrap items-center gap-2 border-b pb-3" style={{ borderColor: "var(--hairline)" }}>
                      <span className="rounded-md bg-surface-2 p-1.5">
                        <AspectIcon aspect={issue.aspect} size={16} />
                      </span>
                      <span className="text-[15px] font-semibold">
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
                        Keyakinan AI: {pct(issue.meanConfidence, 1)}
                      </span>
                    </div>

                    {/* Complaint Summary */}
                    <div className="mt-3">
                      <Meter
                        value={issue.priorityScore ?? 0}
                        max={maxScore}
                        label={`${num(issue.negativeCount)} keluhan dari ${num(issue.mentionCount)} sebutan wisatawan`}
                        valueLabel={`Urgensi ${score(issue.priorityScore)}`}
                      />
                    </div>

                    <p className="mt-2.5 text-[12.5px] leading-relaxed text-ink-2">
                      {issue.explanation}
                    </p>

                    {/* Action Cards: Inspection & Solution */}
                    <div className="mt-3.5 grid gap-2.5 sm:grid-cols-2">
                      <div
                        className="rounded-md border p-3"
                        style={{
                          borderColor: "var(--hairline)",
                          background: "var(--surface-2)",
                        }}
                      >
                        <div className="mb-1 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted">
                          <ClipboardCheck size={13} className="text-accent" />
                          Panduan Cek Fisik Lapangan
                        </div>
                        <p className="text-[12px] leading-relaxed text-ink">
                          {issue.recommendedVerification}
                        </p>
                      </div>

                      <div
                        className="rounded-md border p-3"
                        style={{
                          borderColor: "var(--hairline)",
                          background: "var(--surface-2)",
                        }}
                      >
                        <div className="mb-1 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted">
                          <ShieldAlert size={13} className="text-accent" />
                          Rekomendasi Tindakan Perbaikan
                        </div>
                        <p className="text-[12px] leading-relaxed text-ink">
                          {issue.candidateIntervention}
                        </p>
                      </div>
                    </div>

                    {/* Verbatim Evidence / Suara Ulasan Wisatawan */}
                    <EvidenceQuotesList
                      snippets={issue.evidenceSnippets ?? []}
                      negativeCount={issue.negativeCount}
                      mentionCount={issue.mentionCount}
                    />

                    {/* Field Officer Verification Control */}
                    <AlertStatusControl
                      destinationId={place.id}
                      aspect={issue.aspect}
                      initialStatus={issue.verificationStatus}
                      initialReason={issue.rejectionReason}
                    />
                  </li>
                ))}
              </ol>
            ) : (
              <div className="py-8 text-center">
                <CheckCircle2 size={32} className="mx-auto text-muted opacity-60" />
                <p className="mt-2 text-[13.5px] font-medium text-ink">
                  Kondisi Destinasi Terpantau Baik
                </p>
                <p className="mt-1 text-[12px] text-muted">
                  Tidak ditemukan pola keluhan berulang yang membutuhkan penanganan darurat.
                </p>
              </div>
            )}
          </Card>
        </div>

        {/* Right Column: Interactive Impact Simulator */}
        <div className="space-y-5">
          <InterventionSim place={place} />

          <Card className="p-4 sm:p-5">
            <SectionTitle>Petunjuk Verifikator Lapangan</SectionTitle>
            <ol className="space-y-2 text-[12px] leading-relaxed text-ink-2">
              <li className="flex gap-2">
                <strong className="text-ink">1.</strong>
                <span>Kunjungi lokasi dan periksa fisik fasilitas sesuai panduan.</span>
              </li>
              <li className="flex gap-2">
                <strong className="text-ink">2.</strong>
                <span>Tekan tombol <strong>Konfirmasi</strong> jika masalah memang benar terjadi di lapangan.</span>
              </li>
              <li className="flex gap-2">
                <strong className="text-ink">3.</strong>
                <span>Gunakan hasil verifikasi untuk mengalokasikan anggaran perbaikan.</span>
              </li>
            </ol>
          </Card>
        </div>
      </div>
    </div>
  );
}
