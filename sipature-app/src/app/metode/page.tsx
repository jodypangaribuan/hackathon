import type { Metadata } from "next";
import { Check, Circle, EyeOff, TriangleAlert } from "lucide-react";
import { AspectIcon } from "@/components/AppIcon";
import { Card, Note, SectionTitle } from "@/components/ui";
import { corpus } from "@/lib/data";
import { dateTime, num } from "@/lib/format";

export const metadata: Metadata = {
  title: "Model & Keterbatasan — SIPATURE",
  description: "Kontrak model A9, formula prioritas, dan Responsible AI.",
};

const pipeline = [
  "12.234 review berteks",
  `TF-IDF multilabel aspect (${corpus.aspectModel})`,
  `Lexical polarity fallback (${corpus.polarityModel})`,
  "Duplicate + freshness weights",
  "Bayesian-smoothed complaint rate",
  "Support / identity / evidence gate",
  "Missing-aware priority",
  "Human field verification",
].join("\n→ ");

const formula = [
  "priority = 0,3333 × complaint_frequency",
  "         + 0,2500 × model_confidence",
  "         + 0,2500 × persistence",
  "         + 0,1667 × visitor_exposure",
  "",
  "severity, facility_gap, feasibility = unavailable",
].join("\n");

export default function MethodPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Model &amp; Keterbatasan
        </h1>
        <p className="mt-1 text-[13px] text-ink-2">
          Dashboard memuat batch output <code>{corpus.modelVersion}</code>,
          generated {dateTime(corpus.generatedAt)}.
        </p>
      </section>

      <Card className="p-4 sm:p-5">
        <SectionTitle>Rantai A9</SectionTitle>
        <pre
          className="thin-scroll overflow-x-auto rounded-md border p-3 text-[12px] leading-relaxed"
          style={{
            borderColor: "var(--hairline)",
            background: "var(--surface-2)",
          }}
        >
          {pipeline}
        </pre>
      </Card>

      <Card className="p-4 sm:p-5">
        <SectionTitle>Formula Priority</SectionTitle>
        <pre
          className="thin-scroll overflow-x-auto rounded-md border p-3 text-[12px] leading-relaxed"
          style={{
            borderColor: "var(--hairline)",
            background: "var(--surface-2)",
          }}
        >
          {formula}
        </pre>
        <p className="mt-3 text-[13px] text-ink-2">
          Bobot original komponen tersedia berjumlah 0,60 dan dinormalisasi
          menjadi 1,00. Missing data tidak pernah diisi nol atau dianggap
          kondisi baik.
        </p>
      </Card>

      <Card className="p-4 sm:p-5">
        <SectionTitle hint={`${corpus.aspects.length} aspek`}>
          Taxonomy {corpus.taxonomyVersion}
        </SectionTitle>
        <div className="grid gap-2 sm:grid-cols-2">
          {corpus.aspects.map((aspect) => (
            <div
              key={aspect.key}
              className="flex items-center gap-2 rounded-md border px-3 py-2 text-[13px]"
              style={{ borderColor: "var(--hairline)" }}
            >
              <AspectIcon aspect={aspect.key} />
              <span>{aspect.label}</span>
              <span className="ml-auto text-[10px] text-muted">
                {aspect.group}
              </span>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-4 sm:p-5">
        <SectionTitle>Traceability</SectionTitle>
        <dl className="space-y-2 text-[12px]">
          <div className="flex justify-between gap-3">
            <dt className="text-muted">Clean reviews</dt>
            <dd>{num(corpus.totalCleanReviews)}</dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-muted">Prediksi aspek</dt>
            <dd>{num(corpus.aspectPredictions)}</dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-muted">Canonical destinations</dt>
            <dd>{num(corpus.canonicalDestinations)}</dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-muted">Actionable destinations/issues</dt>
            <dd>
              {num(corpus.actionableDestinations)} /{" "}
              {num(corpus.actionableIssues)}
            </dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-muted">Export SHA-256</dt>
            <dd className="max-w-[480px] break-all text-right">
              {corpus.exportSha256}
            </dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-muted">Expert judgments</dt>
            <dd>{corpus.expertJudgmentsCompleted}/25</dd>
          </div>
        </dl>
      </Card>

      <Card className="p-4 sm:p-5">
        <SectionTitle>Batas Kejujuran</SectionTitle>
        <ul className="space-y-2.5 text-[13px] leading-relaxed text-ink-2">
          <li>
            <TriangleAlert size={14} className="mr-1 inline" />
            TF-IDF Macro F1 0,7201 diukur terhadap held-out weak-supervision
            silver labels, bukan human gold.
          </li>
          <li>
            <Circle size={12} className="mr-1 inline" />
            Polarity memakai fallback leksikal dan tidak mengeluarkan
            probability.
          </li>
          <li>
            <Circle size={12} className="mr-1 inline" />
            Severity model tidak tersedia karena support kelas high tidak
            melewati gate.
          </li>
          <li>
            <EyeOff size={14} className="mr-1 inline" />
            Evidence text ditahan sampai privacy review selesai; aplikasi publik
            hanya membawa agregat.
          </li>
          <li>
            <TriangleAlert size={14} className="mr-1 inline" />
            Priority adalah sinyal triase, bukan bukti destinasi buruk,
            berbahaya, atau tidak layak.
          </li>
          <li>
            <Check size={14} className="mr-1 inline" />
            Unresolved identity dan insufficient data tidak diberi operational
            priority.
          </li>
        </ul>
      </Card>

      <Card className="p-4 sm:p-5">
        <SectionTitle>Responsible AI</SectionTitle>
        <ul className="space-y-2 text-[13px] text-ink-2">
          <li>
            Identitas reviewer, review ID, source file, dan source row tidak
            masuk bundle aplikasi.
          </li>
          <li>
            Setiap kandidat tindakan tampil sebagai kandidat pending field
            verification.
          </li>
          <li>Simulator adalah analisis skenario non-kausal.</li>
          <li>
            Analyzer adalah sandbox leksikal terpisah dan tidak mengaku sebagai
            A9.
          </li>
        </ul>
      </Card>

      <Note>
        Regenerasi bundle: <code>npm run data:a9</code>. Generator memverifikasi
        hash r5, taxonomy, count, identity, coordinates, missing semantics, dan
        forbidden privacy keys.
      </Note>
    </div>
  );
}
