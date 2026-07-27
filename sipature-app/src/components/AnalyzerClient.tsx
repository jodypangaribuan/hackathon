"use client";

/**
 * Layar 4 — Live Analyzer. Satu-satunya inferensi live di aplikasi:
 * teks dikirim ke POST /api/analyze, hasil aspek + sentimen ditampilkan
 * beserta latensi nyata. Contoh ulasan berasal dari lexicon.json (props).
 */

import { useState } from "react";
import type { AnalyzeResult } from "@/lib/types";
import { severityLabel } from "@/lib/format";
import { Card, Meter, Note, Quote, SectionTitle } from "@/components/ui";
import { AspectIcon } from "@/components/AppIcon";
import { Circle, Lightbulb, TriangleAlert } from "lucide-react";

const SENTIMENT_META = {
  negatif: { icon: "▼", color: "var(--status-critical)", label: "Negatif" },
  netral: { icon: "—", color: "var(--text-muted)", label: "Netral" },
  positif: { icon: "▲", color: "var(--status-good)", label: "Positif" },
} as const;

export default function AnalyzerClient({ samples }: { samples: string[] }) {
  const [text, setText] = useState("");
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function analyze(input: string) {
    const t = input.trim();
    if (!t) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: t }),
      });
      if (!res.ok) {
        const body = (await res.json().catch(() => null)) as { error?: string } | null;
        throw new Error(body?.error ?? `HTTP ${res.status}`);
      }
      setResult((await res.json()) as AnalyzeResult);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Permintaan gagal.");
    } finally {
      setBusy(false);
    }
  }

  function runSample(s: string) {
    setText(s);
    void analyze(s);
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_420px]">
      {/* ------------------------------------------------------------ input */}
      <div className="min-w-0">
        <Card className="p-4 sm:p-5">
          <SectionTitle>Tempel Ulasan</SectionTitle>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void analyze(text);
            }}
          >
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={7}
              maxLength={5000}
              placeholder="Tempel ulasan wisatawan apa pun di sini — bahasa Indonesia informal, singkatan, dan typo tidak masalah…"
              aria-label="Teks ulasan untuk dianalisis"
              className="w-full resize-y rounded-md border bg-transparent px-3 py-2.5 text-[13px] leading-relaxed outline-none placeholder:text-muted"
              style={{ borderColor: "var(--hairline)" }}
            />
            <div className="mt-2 flex items-center gap-3">
              <button
                type="submit"
                disabled={busy || text.trim().length === 0}
                className="rounded-md px-4 py-2 text-[13px] font-semibold text-white transition-opacity disabled:opacity-40"
                style={{ background: "var(--series-1)" }}
              >
                {busy ? "Menganalisis…" : "Analisis"}
              </button>
              <span className="tabular text-[11px] text-muted">
                {text.length}/5000 karakter
              </span>
              {result ? (
                <span className="tabular ml-auto text-[11px] text-muted">
                  latensi {result.latencyMs} ms
                </span>
              ) : null}
            </div>
          </form>
          {error ? (
            <p className="mt-2 text-[12px]" style={{ color: "var(--status-critical)" }}>
              {error}
            </p>
          ) : null}
        </Card>

        <Card className="mt-3 p-4">
          <SectionTitle hint="klik untuk langsung dianalisis">
            Contoh dari Dataset
          </SectionTitle>
          <ul className="space-y-1.5">
            {samples.map((s, i) => (
              <li key={i}>
                <button
                  type="button"
                  onClick={() => runSample(s)}
                  className="w-full rounded-md border px-3 py-2 text-left text-[12px] leading-relaxed text-ink-2 transition-colors hover:bg-surface-2"
                  style={{ borderColor: "var(--hairline)" }}
                >
                  “{s}”
                </button>
              </li>
            ))}
          </ul>
        </Card>

        <div className="mt-3">
          <Note>
             <TriangleAlert size={13} className="mr-1 inline" /> Lapisan analisis pada demo ini adalah{" "}
            <strong>baseline leksikon + isyarat sentimen</strong>, bukan model
            IndoBERT terlatih. Pada produk final, lapisan ini diganti IndoBERT
            hasil fine-tuning tahap preliminary dan macro-F1-nya dilaporkan.
          </Note>
        </div>
      </div>

      {/* ------------------------------------------------------------ hasil */}
      <div className="min-w-0">
        <Card className="p-4 sm:p-5">
          <SectionTitle
            hint={result ? `${result.hits.length} aspek terdeteksi` : undefined}
          >
            Hasil Ekstraksi
          </SectionTitle>

          {!result ? (
            <p className="py-10 text-center text-[13px] text-muted">
              Hasil akan muncul di sini — aspek yang disebut, sentimennya, dan
              potongan kalimat sebagai bukti.
            </p>
          ) : result.hits.length === 0 ? (
            <p className="py-10 text-center text-[13px] text-muted">
              Tidak ada aspek yang dikenali pada teks ini.
            </p>
          ) : (
            <ul className="space-y-3">
              {result.hits.map((h) => {
                const s = SENTIMENT_META[h.sentiment];
                return (
                  <li
                    key={h.aspect}
                    className="rounded-card border p-3"
                    style={{ borderColor: "var(--hairline)" }}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                       <AspectIcon aspect={h.aspect} />
                      <span className="text-[13px] font-semibold">{h.label}</span>
                      <span
                        className="inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[11px] font-medium"
                        style={{ borderColor: "var(--hairline)", color: s.color }}
                      >
                         <Circle size={8} fill="currentColor" /> {s.label}
                      </span>
                      <span className="tabular ml-auto text-[11px] text-muted">
                        dampak korpus {severityLabel(h.severity)}
                      </span>
                    </div>
                    <div className="mt-2">
                      <Meter
                        value={h.score}
                        max={1}
                        label="keyakinan"
                        valueLabel={h.score.toFixed(2).replace(".", ",")}
                      />
                    </div>
                    {h.evidence.length > 0 ? (
                      <div className="mt-2 space-y-1.5">
                        {h.evidence.map((e, i) => (
                          <Quote key={i} text={e} />
                        ))}
                      </div>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          )}

          {result?.keywordBaselineWouldMiss ? (
            <p
              className="mt-3 rounded-md border px-3 py-2 text-[12px] leading-relaxed"
              style={{ borderColor: "var(--series-2)", color: "var(--text-secondary)" }}
            >
               <Lightbulb size={14} className="mr-1 inline" /> Teks ini memuat keluhan <em>implisit</em> (mis. “bayar lagi”,
              “air mati”) tanpa kata kunci eksplisit — kasus yang menjadi alasan
              memakai model bahasa, bukan sekadar pencocokan kata.
            </p>
          ) : null}
        </Card>
      </div>
    </div>
  );
}
