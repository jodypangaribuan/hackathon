"use client";

import { useRef, useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  Clock3,
  Eraser,
  FlaskConical,
  LoaderCircle,
  LockKeyhole,
  RotateCcw,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
import type { AnalyzeResult } from "@/lib/types";
import { Card, Empty, Meter, Note, SectionTitle } from "@/components/ui";
import { AspectIcon } from "@/components/AppIcon";

const MAX_CHARS = 5000;
const SAMPLES = [
  "Toiletnya kotor dan air sering mati, tetapi pemandangannya sangat indah.",
  "Harga tiket tidak jelas dan petugas kurang ramah saat kami bertanya.",
  "Akses jalannya rusak, parkir sempit, dan antreannya cukup panjang.",
];
const SENTIMENT_STYLE = {
  positif: { icon: CheckCircle2, color: "var(--status-good)" },
  negatif: { icon: TriangleAlert, color: "var(--status-serious)" },
  netral: { icon: Clock3, color: "var(--text-muted)" },
} as const;

export default function AnalyzerClient() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const requestRef = useRef<AbortController | null>(null);

  async function analyze(input: string) {
    const clean = input.trim();
    if (!clean || busy) return;

    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    setBusy(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: clean }),
        cache: "no-store",
        signal: controller.signal,
      });
      const payload = (await response.json()) as AnalyzeResult | { error?: string };
      if (!response.ok) {
        throw new Error(
          "error" in payload && payload.error
            ? payload.error
            : "Analisis gagal diproses.",
        );
      }
      setResult(payload as AnalyzeResult);
    } catch (value) {
      if (value instanceof DOMException && value.name === "AbortError") return;
      setError(
        value instanceof Error ? value.message : "Analisis gagal diproses.",
      );
    } finally {
      if (requestRef.current === controller) {
        requestRef.current = null;
        setBusy(false);
      }
    }
  }

  function clear() {
    requestRef.current?.abort();
    requestRef.current = null;
    setText("");
    setResult(null);
    setError(null);
    setBusy(false);
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_460px]">
      <div className="min-w-0 space-y-3">
        <Card className="overflow-hidden">
          <div
            className="flex flex-wrap items-center justify-between gap-2 border-b px-4 py-3 sm:px-5"
            style={{ borderColor: "var(--hairline)" }}
          >
            <div>
              <h2 className="text-[14px] font-semibold">Masukkan review</h2>
              <p className="mt-0.5 text-[11px] text-muted">
                Bahasa Indonesia · satu review per analisis
              </p>
            </div>
            <span
              className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] text-ink-2"
              style={{ borderColor: "var(--hairline)" }}
            >
              <FlaskConical size={12} /> Baseline aktif
            </span>
          </div>

          <form
            className="p-4 sm:p-5"
            onSubmit={(event) => {
              event.preventDefault();
              void analyze(text);
            }}
          >
            <label htmlFor="review-text" className="sr-only">
              Teks review
            </label>
            <textarea
              id="review-text"
              value={text}
              onChange={(event) => setText(event.target.value)}
              rows={8}
              maxLength={MAX_CHARS}
              placeholder="Contoh: Pemandangannya indah, tetapi toilet kotor dan harga parkir tidak jelas."
              className="w-full resize-y rounded-md border bg-transparent px-3.5 py-3 text-[14px] leading-relaxed outline-none transition-shadow focus:ring-2"
              style={{
                borderColor: error
                  ? "var(--status-critical)"
                  : "var(--hairline)",
              }}
              aria-describedby="review-help"
            />
            <div
              id="review-help"
              className="mt-2 flex items-center justify-between gap-3 text-[11px] text-muted"
            >
              <span>Jangan masukkan nama, nomor telepon, atau data pribadi.</span>
              <span className="tabular shrink-0">
                {text.length.toLocaleString("id-ID")}/
                {MAX_CHARS.toLocaleString("id-ID")}
              </span>
            </div>

            {error ? (
              <div
                role="alert"
                className="mt-3 flex items-start gap-2 rounded-md border px-3 py-2 text-[12px]"
                style={{
                  borderColor: "var(--status-critical)",
                  color: "var(--status-critical)",
                }}
              >
                <TriangleAlert className="mt-0.5 shrink-0" size={14} />
                <span>{error}</span>
              </div>
            ) : null}

            <div className="mt-4 flex flex-wrap items-center gap-2">
              <button
                type="submit"
                disabled={busy || !text.trim()}
                className="inline-flex items-center gap-2 rounded-md px-4 py-2 text-[13px] font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
                style={{ background: "var(--series-1)" }}
              >
                {busy ? (
                  <LoaderCircle className="animate-spin" size={14} />
                ) : (
                  <Sparkles size={14} />
                )}
                {busy ? "Menganalisis..." : "Analisis review"}
              </button>
              {text ? (
                <button
                  type="button"
                  onClick={clear}
                  className="inline-flex items-center gap-1.5 rounded-md border px-3 py-2 text-[12px] text-ink-2"
                  style={{ borderColor: "var(--hairline)" }}
                >
                  <Eraser size={13} /> Bersihkan
                </button>
              ) : null}
            </div>
          </form>
        </Card>

        <Card className="p-4 sm:p-5">
          <SectionTitle hint="teks sintetis">Coba Contoh</SectionTitle>
          <div className="grid gap-2">
            {SAMPLES.map((sample) => (
              <button
                type="button"
                key={sample}
                disabled={busy}
                onClick={() => {
                  setText(sample);
                  void analyze(sample);
                }}
                className="group flex items-center gap-3 rounded-md border px-3 py-2.5 text-left text-[12px] leading-relaxed transition-colors disabled:opacity-50"
                style={{ borderColor: "var(--hairline)" }}
              >
                <span className="min-w-0 flex-1">{sample}</span>
                <ArrowRight
                  className="shrink-0 text-muted transition-transform group-hover:translate-x-0.5"
                  size={14}
                />
              </button>
            ))}
          </div>
        </Card>

        <Note>
          <span className="inline-flex items-center gap-1.5">
            <LockKeyhole size={12} /> Input tidak disimpan dan tidak mengubah
            skor, peringkat, atau data dashboard.
          </span>
        </Note>
      </div>

      <Card className="h-fit min-h-[430px] overflow-hidden">
        <div
          className="flex items-start justify-between gap-3 border-b px-4 py-3 sm:px-5"
          style={{ borderColor: "var(--hairline)" }}
        >
          <div>
            <h2 className="text-[14px] font-semibold">Hasil analisis</h2>
            <p className="mt-0.5 text-[11px] text-muted">
              Aspek dan sentimen per review
            </p>
          </div>
          {result ? (
            <span className="tabular inline-flex items-center gap-1 text-[11px] text-muted">
              <Clock3 size={12} /> {result.latencyMs} ms
            </span>
          ) : null}
        </div>

        <div aria-live="polite" aria-busy={busy} className="p-4 sm:p-5">
          {busy ? (
            <div className="flex min-h-[320px] flex-col items-center justify-center text-center">
              <LoaderCircle className="animate-spin text-muted" size={24} />
              <p className="mt-3 text-[13px] font-medium">
                Menganalisis review
              </p>
              <p className="mt-1 text-[11px] text-muted">
                Mendeteksi aspek dan indikasi sentimen...
              </p>
            </div>
          ) : !result ? (
            <div className="flex min-h-[320px] flex-col items-center justify-center text-center">
              <div
                className="rounded-full border p-3 text-muted"
                style={{ borderColor: "var(--hairline)" }}
              >
                <Sparkles size={20} />
              </div>
              <p className="mt-3 text-[13px] font-medium">Belum ada hasil</p>
              <p className="mt-1 max-w-[270px] text-[11px] leading-relaxed text-muted">
                Masukkan satu review atau pilih contoh aman untuk memulai
                analisis.
              </p>
            </div>
          ) : result.hits.length === 0 ? (
            <div>
              <Empty>Tidak ada aspek yang dapat dideteksi dari teks ini.</Empty>
              <button
                type="button"
                onClick={() => setResult(null)}
                className="mx-auto flex items-center gap-1.5 text-[12px] text-ink-2"
              >
                <RotateCcw size={13} /> Ubah review
              </button>
            </div>
          ) : (
            <div>
              <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                <span className="text-[12px] text-ink-2">
                  <strong>{result.hits.length}</strong> aspek terdeteksi
                </span>
                <span
                  className="rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-wide text-muted"
                  style={{ borderColor: "var(--hairline)" }}
                >
                  {result.mode === "production"
                    ? result.modelVersion ?? "Model production"
                    : "Baseline leksikal"}
                </span>
              </div>
              <ul className="space-y-2.5">
                {result.hits.map((hit) => {
                  const sentiment = SENTIMENT_STYLE[hit.sentiment];
                  const SentimentIcon = sentiment.icon;
                  const metric =
                    result.scoreType === "model_confidence"
                      ? hit.confidence ?? hit.matchScore
                      : hit.matchScore;
                  return (
                    <li
                      key={hit.aspect}
                      className="rounded-card border p-3.5"
                      style={{ borderColor: "var(--hairline)" }}
                    >
                      <div className="flex items-start gap-2.5">
                        <span className="mt-0.5 rounded-md bg-surface-2 p-1.5">
                          <AspectIcon aspect={hit.aspect} />
                        </span>
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <span className="text-[13px] font-semibold">
                              {hit.label}
                            </span>
                            <span
                              className="inline-flex items-center gap-1 text-[11px] font-medium capitalize"
                              style={{ color: sentiment.color }}
                            >
                              <SentimentIcon size={12} /> {hit.sentiment}
                            </span>
                          </div>
                          <div className="mt-2.5">
                            <Meter
                              value={metric}
                              max={1}
                              label={
                                result.scoreType === "model_confidence"
                                  ? "Confidence model"
                                  : "Kekuatan kecocokan baseline"
                              }
                              valueLabel={`${Math.round(metric * 100)}%`}
                            />
                          </div>
                        </div>
                      </div>
                      {hit.snippets.length ? (
                        <div
                          className="mt-3 border-t pt-2.5"
                          style={{ borderColor: "var(--hairline)" }}
                        >
                          <p className="mb-1 text-[10px] uppercase tracking-wide text-muted">
                            Potongan pendukung
                          </p>
                          {hit.snippets.slice(0, 2).map((snippet, index) => (
                            <p
                              key={index}
                              className="text-[11px] leading-relaxed text-ink-2"
                            >
                              “{snippet}”
                            </p>
                          ))}
                        </div>
                      ) : null}
                    </li>
                  );
                })}
              </ul>
              <p className="mt-4 text-[11px] leading-relaxed text-muted">
                {result.note}
              </p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
