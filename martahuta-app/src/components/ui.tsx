/**
 * Primitif UI bersama. Semua halaman memakai komponen ini agar tampilan
 * konsisten satu sistem. Tidak ada warna hex mentah di sini — semuanya token.
 */
import type { ReactNode } from "react";
import type { Confidence, LevelSpec, Trend } from "@/lib/types";
import { CONFIDENCE_LABEL, TREND_META } from "@/lib/format";

/* --------------------------------------------------------------- layout */

export function Card({
  children,
  className = "",
  as: As = "div",
}: {
  children: ReactNode;
  className?: string;
  as?: "div" | "section" | "article" | "li";
}) {
  return (
    <As
      className={`rounded-card border bg-surface ${className}`}
      style={{ borderColor: "var(--hairline)" }}
    >
      {children}
    </As>
  );
}

export function SectionTitle({
  children,
  hint,
}: {
  children: ReactNode;
  hint?: ReactNode;
}) {
  return (
    <div className="mb-3 flex items-baseline justify-between gap-3">
      <h2 className="text-[13px] font-semibold uppercase tracking-wide text-ink-2">
        {children}
      </h2>
      {hint ? <span className="text-[12px] text-muted">{hint}</span> : null}
    </div>
  );
}

/* ---------------------------------------------------------------- badges */

/**
 * Lencana tingkat friksi. Warna status SELALU disertai ikon + label teks —
 * ini mitigasi wajib karena warning/serious berada di bawah 3:1 pada
 * permukaan terang.
 */
export function LevelBadge({
  level,
  size = "md",
  showLabel = true,
}: {
  level: LevelSpec;
  size?: "sm" | "md";
  showLabel?: boolean;
}) {
  const pad = size === "sm" ? "px-1.5 py-0.5 text-[11px]" : "px-2 py-1 text-[12px]";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border font-medium ${pad}`}
      style={{ borderColor: "var(--hairline)", color: "var(--text-primary)" }}
    >
      <span aria-hidden style={{ color: level.colorVar }}>
        {level.icon}
      </span>
      {showLabel ? level.label : null}
    </span>
  );
}

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "muted";
}) {
  return (
    <span
      className="inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[11px]"
      style={{
        borderColor: "var(--hairline)",
        color: tone === "muted" ? "var(--text-muted)" : "var(--text-secondary)",
      }}
    >
      {children}
    </span>
  );
}

export function ConfidenceBadge({ confidence }: { confidence: Confidence }) {
  const weak = confidence === "low" || confidence === "none";
  return (
    <span
      className="inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[11px]"
      style={{
        borderColor: "var(--hairline)",
        color: weak ? "var(--text-muted)" : "var(--text-secondary)",
      }}
      title={
        weak
          ? "Sampel terlalu kecil — tidak dimasukkan ke peringkat publik."
          : "Sampel cukup untuk masuk peringkat."
      }
    >
      {weak ? "⚠" : "✓"} {CONFIDENCE_LABEL[confidence]}
    </span>
  );
}

export function TrendTag({ trend }: { trend: Trend }) {
  const t = TREND_META[trend];
  return (
    <span className="inline-flex items-center gap-1 text-[11px]" style={{ color: t.tone }}>
      <span aria-hidden>{t.icon}</span>
      <span className="text-muted">{t.label}</span>
    </span>
  );
}

/* ----------------------------------------------------------------- marks */

/**
 * Meter batang tunggal. Nominal — SEMUA batang memakai satu hue (slot-1),
 * karena panjang batang sudah menyandikan besarannya. Jangan mewarnai
 * batang menurut nilainya.
 */
export function Meter({
  value,
  max = 1,
  label,
  valueLabel,
  colorVar = "var(--series-1)",
}: {
  value: number;
  max?: number;
  label?: string;
  valueLabel?: string;
  colorVar?: string;
}) {
  const w = Math.max(0, Math.min(1, max === 0 ? 0 : value / max));
  return (
    <div>
      {(label || valueLabel) && (
        <div className="mb-1 flex items-baseline justify-between gap-2">
          {label ? <span className="text-[12px] text-ink-2">{label}</span> : <span />}
          {valueLabel ? (
            <span className="tabular text-[12px] font-medium text-ink">{valueLabel}</span>
          ) : null}
        </div>
      )}
      <div
        className="h-2 w-full overflow-hidden rounded-full"
        style={{ background: "var(--gridline)" }}
        role="img"
        aria-label={`${label ?? "nilai"}: ${valueLabel ?? w.toFixed(2)}`}
      >
        <div
          className="h-full rounded-r-[4px]"
          style={{ width: `${w * 100}%`, background: colorVar }}
        />
      </div>
    </div>
  );
}

/** Angka utama satu kartu. Tanpa plot → tidak perlu hover. */
export function StatTile({
  value,
  label,
  sub,
  accent,
}: {
  value: ReactNode;
  label: string;
  sub?: ReactNode;
  accent?: string;
}) {
  return (
    <Card className="p-4">
      <div
        className="text-[28px] font-semibold leading-none"
        style={accent ? { color: accent } : undefined}
      >
        {value}
      </div>
      <div className="mt-2 text-[12px] font-medium text-ink-2">{label}</div>
      {sub ? <div className="mt-1 text-[11px] leading-snug text-muted">{sub}</div> : null}
    </Card>
  );
}

/** Kutipan verbatim review — lapisan explainability. */
export function Quote({
  text,
  meta,
}: {
  text: string;
  meta?: ReactNode;
}) {
  return (
    <figure
      className="rounded-md border-l-2 py-1.5 pl-3 pr-2"
      style={{ borderColor: "var(--baseline)", background: "var(--surface-2)" }}
    >
      <blockquote className="text-[12px] leading-relaxed text-ink-2">“{text}”</blockquote>
      {meta ? <figcaption className="mt-1 text-[11px] text-muted">{meta}</figcaption> : null}
    </figure>
  );
}

export function Note({ children }: { children: ReactNode }) {
  return (
    <p
      className="rounded-md border px-3 py-2 text-[11px] leading-relaxed text-muted"
      style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}
    >
      {children}
    </p>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return (
    <div className="py-10 text-center text-[13px] text-muted">{children}</div>
  );
}
