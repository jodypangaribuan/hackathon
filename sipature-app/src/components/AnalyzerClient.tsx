"use client";
import { useState } from "react";
import type { AnalyzeResult } from "@/lib/types";
import { Card, Meter, Note, SectionTitle } from "@/components/ui";
import { AspectIcon } from "@/components/AppIcon";
const SAMPLES = [
  "Contoh sintetis: toilet kotor dan air mati, tetapi pemandangannya indah.",
  "Contoh sintetis: harga tiket tidak jelas dan petugas kurang ramah.",
  "Contoh sintetis: akses jalan rusak, parkir sempit, dan antreannya panjang.",
];
export default function AnalyzerClient() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function analyze(input: string) {
    if (!input.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
        cache: "no-store",
      });
      if (!response.ok) throw new Error("Analisis gagal");
      setResult(await response.json());
    } catch (value) {
      setError(value instanceof Error ? value.message : "Analisis gagal");
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_420px]">
      <div>
        <Card className="p-4 sm:p-5">
          <SectionTitle>Sandbox Teks</SectionTitle>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              void analyze(text);
            }}
          >
            <textarea
              value={text}
              onChange={(event) => setText(event.target.value)}
              rows={7}
              maxLength={5000}
              placeholder="Tempel teks untuk demo leksikal…"
              className="w-full rounded-md border bg-transparent px-3 py-2.5 text-[13px]"
              style={{ borderColor: "var(--hairline)" }}
            />
            <div className="mt-2 flex items-center gap-3">
              <button
                disabled={busy || !text.trim()}
                className="rounded-md px-4 py-2 text-[13px] font-semibold text-white disabled:opacity-40"
                style={{ background: "var(--series-1)" }}
              >
                {busy ? "Menganalisis…" : "Analisis"}
              </button>
              <span className="text-[11px] text-muted">{text.length}/5000</span>
              {result ? (
                <span className="ml-auto text-[11px] text-muted">
                  {result.latencyMs} ms
                </span>
              ) : null}
            </div>
          </form>
          {error ? <p className="mt-2 text-[12px]">{error}</p> : null}
        </Card>
        <Card className="mt-3 p-4">
          <SectionTitle hint="seluruhnya sintetis">Contoh Aman</SectionTitle>
          {SAMPLES.map((sample) => (
            <button
              key={sample}
              onClick={() => {
                setText(sample);
                void analyze(sample);
              }}
              className="mb-1.5 w-full rounded-md border px-3 py-2 text-left text-[12px]"
              style={{ borderColor: "var(--hairline)" }}
            >
              {sample}
            </button>
          ))}
        </Card>
        <div className="mt-3">
          <Note>
            Sandbox ini memakai aturan leksikal deterministik 14 aspek, bukan
            model intelligence utama. Input tidak disimpan dan hasil tidak mengubah
            dashboard.
          </Note>
        </div>
      </div>
      <Card className="h-fit p-4 sm:p-5">
        <SectionTitle hint={result ? `${result.hits.length} aspek` : undefined}>
          Hasil Sandbox
        </SectionTitle>
        {!result ? (
          <p className="py-10 text-center text-[13px] text-muted">
            Hasil lexical match akan muncul di sini.
          </p>
        ) : result.hits.length === 0 ? (
          <p className="py-10 text-center text-[13px] text-muted">
            Tidak ada pola leksikal yang cocok.
          </p>
        ) : (
          <ul className="space-y-3">
            {result.hits.map((hit) => (
              <li
                key={hit.aspect}
                className="rounded-card border p-3"
                style={{ borderColor: "var(--hairline)" }}
              >
                <div className="flex items-center gap-2">
                  <AspectIcon aspect={hit.aspect} />
                  <span className="text-[13px] font-semibold">{hit.label}</span>
                  <span className="ml-auto text-[11px] text-muted">
                    {hit.sentiment}
                  </span>
                </div>
                <div className="mt-2">
                  <Meter
                    value={hit.matchScore}
                    max={1}
                    label="lexical match score"
                    valueLabel={hit.matchScore.toFixed(2).replace(".", ",")}
                  />
                </div>
                {hit.snippets.map((snippet, index) => (
                  <p
                    key={index}
                    className="mt-2 rounded-md bg-surface-2 px-3 py-2 text-[12px] text-ink-2"
                  >
                    “{snippet}”
                  </p>
                ))}
              </li>
            ))}
          </ul>
        )}
        {result ? (
          <p className="mt-3 text-[11px] text-muted">{result.note}</p>
        ) : null}
      </Card>
    </div>
  );
}
