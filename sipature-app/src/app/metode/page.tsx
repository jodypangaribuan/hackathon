import type { Metadata } from "next";
import { Check, Circle, EyeOff, ShieldCheck, TriangleAlert } from "lucide-react";
import { AspectIcon } from "@/components/AppIcon";
import { Card, Note, SectionTitle } from "@/components/ui";
import { getCorpus } from "@/lib/data";
import { dateTime, num } from "@/lib/format";

export const metadata: Metadata = {
  title: "Model & Metodologi — SIPATURE",
  description: "Kontrak model SIPATURE Intelligence, formula prioritas, benchmark gold-v1, dan Responsible AI.",
};

export const dynamic = "force-dynamic";

export default async function MethodPage() {
  const corpus = await getCorpus();

  const pipeline = [
    "12.234 ulasan berteks (NLP Corpus)",
    `Ekstraksi 14 Aspek (${corpus.aspectModel})`,
    `Klasifikasi Polaritas Sentimen (${corpus.polarityModel})`,
    "Pembobotan Kebaruan & Deduplikasi Hash",
    "Normalisasi Bayesian-smoothed Complaint Rate",
    "Support Gate & Resolusi Entitas (388 Kanonikal)",
    "Missing-Aware Priority Scoring",
    "Human Field Verification (Confirmed / Rejected / Uncertain)",
  ].join("\n→ ");

  const formula = [
    "priority = 0,3333 × complaint_frequency",
    "         + 0,2500 × model_confidence",
    "         + 0,2500 × persistence",
    "         + 0,1667 × visitor_exposure",
    "",
    "severity, facility_gap, feasibility = unavailable (missing-aware)",
  ].join("\n");

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Model, Metodologi, &amp; Keterbatasan
        </h1>
        <p className="mt-1 text-[13px] text-ink-2">
          Dashboard memuat keluaran model produksi <code>{corpus.modelVersion}</code>,
          dihasilkan pada {dateTime(corpus.generatedAt)}.
        </p>
      </section>

      {/* Benchmark Table Card */}
      <Card className="p-4 sm:p-5">
        <SectionTitle hint="Evaluasi Independen Human Gold-v1">
          Perbandingan Benchmark Model (1.320 Ulasan)
        </SectionTitle>
        <div className="mt-3 thin-scroll overflow-x-auto">
          <table className="w-full text-left text-[12.5px]">
            <thead
              className="border-y text-[11px] uppercase text-muted"
              style={{
                borderColor: "var(--hairline)",
                background: "var(--surface-2)",
              }}
            >
              <tr>
                <th className="px-3 py-2">Model yang Diuji</th>
                <th className="px-3 py-2 text-center">Silver Test (Locked)</th>
                <th className="px-3 py-2 text-center">Gold-v1 (Human Test)</th>
                <th className="px-3 py-2">Status &amp; Keputusan</th>
              </tr>
            </thead>
            <tbody className="divide-y" style={{ borderColor: "var(--hairline)" }}>
              <tr>
                <td className="px-3 py-2.5 font-medium">Keyword (Lexicon Rule)</td>
                <td className="px-3 py-2.5 text-center font-mono">0,9768 (sirkular)</td>
                <td className="px-3 py-2.5 text-center font-mono font-semibold">0,7056</td>
                <td className="px-3 py-2.5 text-muted">Batas atas leksikal (bukan model ML)</td>
              </tr>
              <tr style={{ background: "rgba(235,108,54,0.06)" }}>
                <td className="px-3 py-2.5 font-medium text-accent">
                  TF-IDF + Logistic Regression
                </td>
                <td className="px-3 py-2.5 text-center font-mono font-medium text-accent">0,7201</td>
                <td className="px-3 py-2.5 text-center font-mono font-bold text-accent">0,5777</td>
                <td className="px-3 py-2.5 font-medium text-accent">
                  ★ Model Produksi Terpilih (Data-Driven, CPU-only)
                </td>
              </tr>
              <tr>
                <td className="px-3 py-2.5 font-medium">IndoBERT Base (Aspect)</td>
                <td className="px-3 py-2.5 text-center font-mono">0,5247</td>
                <td className="px-3 py-2.5 text-center font-mono">0,4254</td>
                <td className="px-3 py-2.5 text-muted">Ditolak (underfit pada data kecil)</td>
              </tr>
              <tr>
                <td className="px-3 py-2.5 font-medium">IndoBERT Base (Polarity)</td>
                <td className="px-3 py-2.5 text-center font-mono">0,7459</td>
                <td className="px-3 py-2.5 text-center font-mono">0,5077</td>
                <td className="px-3 py-2.5 text-muted">Ditolak (akurasi setara chance level)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <Card className="p-4 sm:p-5">
        <SectionTitle>Rantai Pemrosesan End-to-End</SectionTitle>
        <pre
          className="thin-scroll overflow-x-auto rounded-md border p-3 text-[12px] leading-relaxed font-mono"
          style={{
            borderColor: "var(--hairline)",
            background: "var(--surface-2)",
          }}
        >
          {pipeline}
        </pre>
      </Card>

      <Card className="p-4 sm:p-5">
        <SectionTitle>Formula Skor Prioritas (Missing-Aware)</SectionTitle>
        <pre
          className="thin-scroll overflow-x-auto rounded-md border p-3 text-[12px] leading-relaxed font-mono"
          style={{
            borderColor: "var(--hairline)",
            background: "var(--surface-2)",
          }}
        >
          {formula}
        </pre>
        <p className="mt-3 text-[13px] text-ink-2">
          Bobot original komponen yang tersedia dinormalisasi menjadi 1,00. Komponen data yang belum tersedia tidak pernah diisi angka nol atau diasumsikan dalam kondisi baik.
        </p>
      </Card>

      <Card className="p-4 sm:p-5">
        <SectionTitle hint={`${corpus.aspects.length} aspek dalam 4 pilar`}>
          Struktur Taksonomi Pariwisata Toba
        </SectionTitle>
        <div className="grid gap-2 sm:grid-cols-2">
          {corpus.aspects.map((aspect) => (
            <div
              key={aspect.key}
              className="flex items-center gap-2 rounded-md border px-3 py-2 text-[13px]"
              style={{ borderColor: "var(--hairline)" }}
            >
              <AspectIcon aspect={aspect.key} />
              <span className="font-medium">{aspect.label}</span>
              <span className="ml-auto text-[10.5px] font-mono text-muted">
                {aspect.key}
              </span>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-4 sm:p-5">
        <SectionTitle>Keterlacakan Artefak (Traceability)</SectionTitle>
        <dl className="space-y-2 text-[12px]">
          <div className="flex justify-between gap-3">
            <dt className="text-muted">Total Ulasan Bersih</dt>
            <dd className="font-mono font-medium">{num(corpus.totalCleanReviews)}</dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-muted">Prediksi Aspek Terdeteksi</dt>
            <dd className="font-mono font-medium">{num(corpus.aspectPredictions)}</dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-muted">Destinasi Kanonikal</dt>
            <dd className="font-mono font-medium">{num(corpus.canonicalDestinations)}</dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-muted">Destinasi / Isu Actionable</dt>
            <dd className="font-mono font-medium">
              {num(corpus.actionableDestinations)} destinasi / {num(corpus.actionableIssues)} isu
            </dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-muted">Export Hash SHA-256</dt>
            <dd className="max-w-[480px] break-all text-right font-mono text-[11px]">
              {corpus.exportSha256}
            </dd>
          </div>
        </dl>
      </Card>

      <Card className="p-4 sm:p-5">
        <SectionTitle>Prinsip Responsible AI &amp; Batas Kejujuran</SectionTitle>
        <ul className="space-y-2.5 text-[13px] leading-relaxed text-ink-2">
          <li>
            <ShieldCheck size={14} className="mr-1.5 inline text-accent" />
            <strong>Privasi Reviewer:</strong> Identitas personal, nama akun, ID reviewer, dan baris mentah tidak pernah masuk ke dalam bundle aplikasi publik.
          </li>
          <li>
            <TriangleAlert size={14} className="mr-1.5 inline text-muted" />
            <strong>Sinyal Triase:</strong> Skor prioritas adalah alat bantu penentuan titik inspeksi awal, bukan vonis mutlak bahwa suatu destinasi berbahaya atau tidak layak.
          </li>
          <li>
            <Check size={14} className="mr-1.5 inline text-accent" />
            <strong>Human-in-the-Loop:</strong> Setiap rekomendasi operasional berstatus pending verifikasi lapangan dengan alur konfirmasi atau penolakan bersyarat.
          </li>
          <li>
            <EyeOff size={14} className="mr-1.5 inline text-muted" />
            <strong>Perlindungan Bukti Verbatim:</strong> Teks kutipan verbatim ulasan ditahan pada lingkungan audit internal berstatus <em>restricted</em> demi kepatuhan privasi.
          </li>
        </ul>
      </Card>

      <Note>
        Keluaran sistem diverifikasi otomatis dengan generator kriptografis: <code>npm run data:generate</code> untuk memastikan integritas hash, koordinat wilayah, dan penegakan aturan privasi.
      </Note>
    </div>
  );
}
