"use client";

import { useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  MessageSquareQuote,
  Quote,
} from "lucide-react";
import type { EvidenceSnippet } from "@/lib/types";
import { num } from "@/lib/format";

interface Props {
  snippets: EvidenceSnippet[];
  negativeCount: number;
  mentionCount: number;
}

export default function EvidenceQuotesList({
  snippets,
  negativeCount,
  mentionCount,
}: Props) {
  const [expanded, setExpanded] = useState(false);

  if (!snippets || snippets.length === 0) {
    return null;
  }

  const initialCount = 3;
  const displayed = expanded ? snippets : snippets.slice(0, initialCount);
  const hasMore = snippets.length > initialCount;

  return (
    <div
      className="mt-3.5 rounded-lg border p-3.5 transition-all"
      style={{
        borderColor: "var(--hairline)",
        background: "var(--surface-2)",
      }}
    >
      <div className="mb-2.5 flex flex-wrap items-center justify-between gap-2 border-b pb-2" style={{ borderColor: "var(--hairline)" }}>
        <div className="flex items-center gap-1.5 text-[11.5px] font-semibold uppercase tracking-wider text-muted">
          <MessageSquareQuote size={14} className="text-accent" />
          <span>
            Suara / Kutipan Asli Wisatawan ({num(snippets.length)} ulasan)
          </span>
        </div>
        <span className="text-[11.5px] text-muted">
          Terdeteksi <strong className="text-ink">{num(negativeCount)} keluhan</strong> dari {num(mentionCount)} sebutan
        </span>
      </div>

      <div className="space-y-2">
        {displayed.map((quote, idx) => (
          <div
            key={idx}
            className="group rounded-md border p-3 text-[12.5px] leading-relaxed transition-colors hover:border-ink/30"
            style={{
              borderColor: "var(--hairline)",
              background: "var(--surface-1)",
            }}
          >
            <div className="flex items-start gap-2">
              <Quote size={13} className="shrink-0 mt-0.5 text-accent opacity-60" />
              <div className="min-w-0 flex-1">
                <p className="italic text-ink leading-relaxed">
                  “{quote.text}”
                </p>
                {quote.date ? (
                  <span className="mt-1.5 inline-block text-[11px] not-italic text-muted font-mono">
                    Tanggal ulasan: {quote.date}
                  </span>
                ) : null}
              </div>
            </div>
          </div>
        ))}
      </div>

      {hasMore && (
        <div className="mt-2.5 pt-2 text-center border-t" style={{ borderColor: "var(--hairline)" }}>
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-[12px] font-medium text-ink transition-colors hover:bg-surface-1 hover:border-ink"
            style={{ borderColor: "var(--hairline)", background: "var(--surface-1)" }}
          >
            {expanded ? (
              <>
                <span>Sembunyikan Sebagian</span>
                <ChevronUp size={13} />
              </>
            ) : (
              <>
                <span>Buka &amp; Baca Semua ({snippets.length} Ulasan)</span>
                <ChevronDown size={13} />
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
