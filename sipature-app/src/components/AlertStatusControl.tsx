"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertCircle,
  CheckCircle2,
  ClipboardCheck,
  HelpCircle,
  LoaderCircle,
  RotateCcw,
  Sparkles,
  X,
  XCircle,
} from "lucide-react";

export type Verdict = "pending" | "confirmed" | "rejected" | "uncertain";

const REJECTION_PRESETS = [
  "Fasilitas sudah bersih / diperbaiki",
  "Tarif & tiket sudah resmi dan transparan",
  "Akses jalan sudah diaspal / diperbaiki",
  "Ulasan lama tidak menggambarkan kondisi sekarang",
  "Bukan kewenangan pengelola destinasi",
];

interface Props {
  destinationId: string;
  aspect: string;
  initialStatus?: Verdict;
  initialReason?: string | null;
}

export default function AlertStatusControl({
  destinationId,
  aspect,
  initialStatus = "pending",
  initialReason = null,
}: Props) {
  const router = useRouter();
  const [verdict, setVerdict] = useState<Verdict>(initialStatus);
  const [savedReason, setSavedReason] = useState<string | null>(initialReason);
  const [busy, setBusy] = useState(false);
  const [rejecting, setRejecting] = useState(false);
  const [rejectionInput, setRejectionInput] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit(next: Verdict, reasonText?: string) {
    setBusy(true);
    setError(null);
    setFeedback(null);

    try {
      const response = await fetch("/api/alerts/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          destinationId,
          aspect,
          status: next,
          rejectionReason: next === "rejected" ? reasonText : undefined,
        }),
      });

      const payload = (await response.json()) as {
        status?: string;
        error?: string;
      };

      if (!response.ok) {
        setError(payload.error ?? "Gagal menyimpan status verifikasi.");
        return;
      }

      setVerdict(next);
      if (next === "rejected") {
        setSavedReason(reasonText ?? null);
      } else {
        setSavedReason(null);
      }
      setRejecting(false);
      setRejectionInput("");
      router.refresh();

      if (next === "confirmed") {
        setFeedback("Status berhasil dikonfirmasi sebagai masalah nyata di lapangan.");
      } else if (next === "uncertain") {
        setFeedback("Status ditandai 'Tidak Pasti' (memerlukan pengecekan berkala lanjutan).");
      } else if (next === "rejected") {
        setFeedback(`Status ditolak sebagai False Positive (${reasonText}).`);
      } else {
        setFeedback("Status verifikasi berhasil direset ke antrean awal.");
      }
    } catch {
      setError("Terjadi kesalahan jaringan saat menyimpan status.");
    } finally {
      setBusy(false);
    }
  }

  const isConfirmed = verdict === "confirmed";
  const isUncertain = verdict === "uncertain";
  const isRejected = verdict === "rejected";

  return (
    <div
      className="mt-3 rounded-lg border p-3.5 transition-all"
      style={{
        borderColor: isConfirmed
          ? "rgba(34, 197, 94, 0.4)"
          : isRejected
            ? "rgba(239, 68, 68, 0.4)"
            : isUncertain
              ? "rgba(245, 158, 11, 0.4)"
              : "var(--hairline)",
        background: isConfirmed
          ? "rgba(34, 197, 94, 0.03)"
          : isRejected
            ? "rgba(239, 68, 68, 0.03)"
            : isUncertain
              ? "rgba(245, 158, 11, 0.03)"
              : "var(--surface-1)",
      }}
    >
      <div className="flex flex-wrap items-center justify-between gap-2 border-b pb-2.5" style={{ borderColor: "var(--hairline)" }}>
        <div className="flex items-center gap-1.5 text-[11.5px] font-semibold uppercase tracking-wider text-muted">
          <ClipboardCheck size={14} className="text-accent" />
          <span>Status Verifikasi Lapangan</span>
        </div>

        {verdict !== "pending" && (
          <button
            type="button"
            disabled={busy}
            onClick={() => void submit("pending")}
            className="inline-flex items-center gap-1 text-[11.5px] text-muted hover:text-ink hover:underline disabled:opacity-50"
            title="Kembalikan ke status belum diverifikasi"
          >
            <RotateCcw size={12} />
            <span>Reset Verifikasi</span>
          </button>
        )}
      </div>

      {/* 3 Action Buttons */}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {/* 1. Konfirmasi */}
        <button
          type="button"
          disabled={busy}
          onClick={() => {
            setRejecting(false);
            void submit("confirmed");
          }}
          className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-[12px] font-semibold transition-all active:scale-[0.98] disabled:opacity-50 ${
            isConfirmed
              ? "border-green-600 bg-green-500/15 text-green-700 dark:text-green-400 shadow-sm"
              : "border-hairline bg-surface-2 text-ink hover:border-green-500/50 hover:bg-green-500/5"
          }`}
          style={{ borderColor: isConfirmed ? "rgba(34,197,94,0.6)" : undefined }}
        >
          {busy && isConfirmed ? (
            <LoaderCircle className="animate-spin" size={13} />
          ) : (
            <CheckCircle2 size={14} className={isConfirmed ? "text-green-600 dark:text-green-400" : "text-muted"} />
          )}
          <span>Konfirmasi (Valid)</span>
        </button>

        {/* 2. Tidak Pasti */}
        <button
          type="button"
          disabled={busy}
          onClick={() => {
            setRejecting(false);
            void submit("uncertain");
          }}
          className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-[12px] font-semibold transition-all active:scale-[0.98] disabled:opacity-50 ${
            isUncertain
              ? "border-amber-600 bg-amber-500/15 text-amber-700 dark:text-amber-400 shadow-sm"
              : "border-hairline bg-surface-2 text-ink hover:border-amber-500/50 hover:bg-amber-500/5"
          }`}
          style={{ borderColor: isUncertain ? "rgba(245,158,11,0.6)" : undefined }}
        >
          {busy && isUncertain ? (
            <LoaderCircle className="animate-spin" size={13} />
          ) : (
            <HelpCircle size={14} className={isUncertain ? "text-amber-600 dark:text-amber-400" : "text-muted"} />
          )}
          <span>Tidak Pasti</span>
        </button>

        {/* 3. Tolak */}
        <button
          type="button"
          disabled={busy}
          onClick={() => {
            if (isRejected) {
              setRejecting((val) => !val);
            } else {
              setRejecting(true);
            }
          }}
          className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-[12px] font-semibold transition-all active:scale-[0.98] disabled:opacity-50 ${
            isRejected
              ? "border-red-600 bg-red-500/15 text-red-700 dark:text-red-400 shadow-sm"
              : "border-hairline bg-surface-2 text-ink hover:border-red-500/50 hover:bg-red-500/5"
          }`}
          style={{ borderColor: isRejected ? "rgba(239,68,68,0.6)" : undefined }}
        >
          <XCircle size={14} className={isRejected ? "text-red-600 dark:text-red-400" : "text-muted"} />
          <span>Tolak (False Positive)</span>
        </button>
      </div>

      {/* Rejecting Form with Quick Preset Chips */}
      {rejecting && (
        <div className="mt-3 rounded-lg border bg-surface-2 p-3 space-y-2.5" style={{ borderColor: "var(--hairline)" }}>
          <div className="flex items-center justify-between">
            <span className="text-[11.5px] font-medium text-ink">
              Pilih atau tuliskan alasan penolakan keluhan:
            </span>
            <button
              type="button"
              onClick={() => setRejecting(false)}
              className="text-muted hover:text-ink"
            >
              <X size={14} />
            </button>
          </div>

          {/* Quick preset chips */}
          <div className="flex flex-wrap gap-1.5">
            {REJECTION_PRESETS.map((preset) => (
              <button
                key={preset}
                type="button"
                onClick={() => setRejectionInput(preset)}
                className="rounded-full border bg-surface-1 px-2.5 py-1 text-[11px] text-ink-2 transition-colors hover:border-ink hover:text-ink"
                style={{ borderColor: "var(--hairline)" }}
              >
                {preset}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={rejectionInput}
              onChange={(e) => setRejectionInput(e.target.value)}
              placeholder="Tulis alasan spesifik di lapangan..."
              className="flex-1 rounded-md border bg-surface-1 px-3 py-1.5 text-[12px] outline-none placeholder:text-muted focus:border-ink"
              style={{ borderColor: "var(--hairline)" }}
            />
            <button
              type="button"
              disabled={busy || !rejectionInput.trim()}
              onClick={() => void submit("rejected", rejectionInput.trim())}
              className="inline-flex items-center gap-1.5 rounded-md bg-red-600 px-3 py-1.5 text-[12px] font-semibold text-white transition-opacity hover:bg-red-700 disabled:opacity-40"
            >
              {busy ? <LoaderCircle className="animate-spin" size={13} /> : <CheckCircle2 size={13} />}
              <span>Simpan Penolakan</span>
            </button>
          </div>
        </div>
      )}

      {/* Current Active Status Info / Feedback Banner */}
      {verdict !== "pending" && !rejecting && (
        <div className="mt-2.5 flex items-center justify-between text-[11.5px]">
          <div className="flex items-center gap-1.5">
            {isConfirmed && (
              <span className="font-semibold text-green-700 dark:text-green-400">
                ✓ Terkonfirmasi oleh petugas lapangan
              </span>
            )}
            {isUncertain && (
              <span className="font-semibold text-amber-700 dark:text-amber-400">
                ? Ditandai tidak pasti — butuh inspeksi ulang
              </span>
            )}
            {isRejected && (
              <span className="font-semibold text-red-700 dark:text-red-400">
                ✕ Ditolak sebagai False Positive {savedReason ? `· "${savedReason}"` : ""}
              </span>
            )}
          </div>
        </div>
      )}

      {feedback && (
        <p className="mt-2 text-[11.5px] text-accent animate-fade-in">
          {feedback}
        </p>
      )}

      {error && (
        <p className="mt-2 text-[11.5px] text-red-600 dark:text-red-400 flex items-center gap-1">
          <AlertCircle size={12} />
          {error}
        </p>
      )}
    </div>
  );
}
