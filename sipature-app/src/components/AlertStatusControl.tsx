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
      className="mt-3.5 rounded-lg border p-4 transition-all"
      style={{
        borderColor: isConfirmed
          ? "rgba(16, 185, 129, 0.45)"
          : isRejected
            ? "rgba(244, 63, 94, 0.45)"
            : isUncertain
              ? "rgba(245, 158, 11, 0.45)"
              : "var(--hairline)",
        background: isConfirmed
          ? "rgba(16, 185, 129, 0.04)"
          : isRejected
            ? "rgba(244, 63, 94, 0.04)"
            : isUncertain
              ? "rgba(245, 158, 11, 0.04)"
              : "var(--surface-1)",
      }}
    >
      <div className="flex flex-wrap items-center justify-between gap-2 border-b pb-2.5" style={{ borderColor: "var(--hairline)" }}>
        <div className="flex items-center gap-2">
          <div className="flex h-5 w-5 items-center justify-center rounded bg-accent/10 text-accent">
            <ClipboardCheck size={13} />
          </div>
          <span className="text-[12px] font-semibold uppercase tracking-wider text-ink">
            Status Verifikasi Lapangan
          </span>
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

      {/* 3 Distinct Bold Action Buttons */}
      <div className="mt-3.5 flex flex-wrap items-center gap-2.5">
        {/* 1. Konfirmasi (Emerald / Green) */}
        <button
          type="button"
          disabled={busy}
          onClick={() => {
            setRejecting(false);
            void submit("confirmed");
          }}
          className={`inline-flex items-center gap-2 rounded-lg border px-3.5 py-2 text-[12.5px] font-semibold transition-all active:scale-[0.98] disabled:opacity-50 ${
            isConfirmed
              ? "border-emerald-600 bg-emerald-600 text-white shadow-md ring-2 ring-emerald-500/30"
              : "border-emerald-600/40 bg-emerald-500/10 text-emerald-800 hover:bg-emerald-500/20 hover:border-emerald-600/70 dark:text-emerald-300 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:hover:bg-emerald-500/20"
          }`}
        >
          {busy && isConfirmed ? (
            <LoaderCircle className="animate-spin" size={14} />
          ) : (
            <CheckCircle2 size={15} className={isConfirmed ? "text-white" : "text-emerald-600 dark:text-emerald-400"} />
          )}
          <span>Konfirmasi (Valid)</span>
        </button>

        {/* 2. Tidak Pasti (Amber / Yellow) */}
        <button
          type="button"
          disabled={busy}
          onClick={() => {
            setRejecting(false);
            void submit("uncertain");
          }}
          className={`inline-flex items-center gap-2 rounded-lg border px-3.5 py-2 text-[12.5px] font-semibold transition-all active:scale-[0.98] disabled:opacity-50 ${
            isUncertain
              ? "border-amber-600 bg-amber-600 text-white shadow-md ring-2 ring-amber-500/30"
              : "border-amber-600/40 bg-amber-500/10 text-amber-800 hover:bg-amber-500/20 hover:border-amber-600/70 dark:text-amber-300 dark:border-amber-500/30 dark:bg-amber-500/10 dark:hover:bg-amber-500/20"
          }`}
        >
          {busy && isUncertain ? (
            <LoaderCircle className="animate-spin" size={14} />
          ) : (
            <HelpCircle size={15} className={isUncertain ? "text-white" : "text-amber-600 dark:text-amber-400"} />
          )}
          <span>Tidak Pasti</span>
        </button>

        {/* 3. Tolak (Rose / Crimson Red) */}
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
          className={`inline-flex items-center gap-2 rounded-lg border px-3.5 py-2 text-[12.5px] font-semibold transition-all active:scale-[0.98] disabled:opacity-50 ${
            isRejected
              ? "border-rose-600 bg-rose-600 text-white shadow-md ring-2 ring-rose-500/30"
              : "border-rose-600/40 bg-rose-500/10 text-rose-800 hover:bg-rose-500/20 hover:border-rose-600/70 dark:text-rose-300 dark:border-rose-500/30 dark:bg-rose-500/10 dark:hover:bg-rose-500/20"
          }`}
        >
          <XCircle size={15} className={isRejected ? "text-white" : "text-rose-600 dark:text-rose-400"} />
          <span>Tolak (False Positive)</span>
        </button>
      </div>

      {/* Rejection Form with Quick Preset Chips */}
      {rejecting && (
        <div className="mt-3.5 rounded-lg border border-rose-500/30 bg-rose-500/[0.04] p-3.5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[12px] font-semibold text-rose-700 dark:text-rose-300">
              Pilih atau tuliskan alasan penolakan keluhan di lapangan:
            </span>
            <button
              type="button"
              onClick={() => setRejecting(false)}
              className="text-muted hover:text-ink"
            >
              <X size={15} />
            </button>
          </div>

          {/* Quick preset chips */}
          <div className="flex flex-wrap gap-1.5">
            {REJECTION_PRESETS.map((preset) => (
              <button
                key={preset}
                type="button"
                onClick={() => setRejectionInput(preset)}
                className="rounded-full border border-hairline bg-surface-1 px-3 py-1 text-[11.5px] text-ink transition-all hover:border-rose-500 hover:bg-rose-500/10"
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
              placeholder="Tuliskan catatan alasan penolakan spesifik..."
              className="flex-1 rounded-md border bg-surface-1 px-3 py-2 text-[12.5px] outline-none placeholder:text-muted focus:border-rose-500"
              style={{ borderColor: "var(--hairline)" }}
            />
            <button
              type="button"
              disabled={busy || !rejectionInput.trim()}
              onClick={() => void submit("rejected", rejectionInput.trim())}
              className="inline-flex items-center gap-1.5 rounded-md bg-rose-600 px-3.5 py-2 text-[12.5px] font-semibold text-white shadow-sm transition-all hover:bg-rose-700 disabled:opacity-40"
            >
              {busy ? <LoaderCircle className="animate-spin" size={13} /> : <CheckCircle2 size={14} />}
              <span>Simpan Penolakan</span>
            </button>
          </div>
        </div>
      )}

      {/* Current Active Status Info / Feedback Banner */}
      {verdict !== "pending" && !rejecting && (
        <div className="mt-3 flex items-center justify-between rounded-md border px-3 py-2 text-[12px]"
          style={{
            borderColor: isConfirmed
              ? "rgba(16, 185, 129, 0.4)"
              : isRejected
                ? "rgba(244, 63, 94, 0.4)"
                : "rgba(245, 158, 11, 0.4)",
            background: isConfirmed
              ? "rgba(16, 185, 129, 0.08)"
              : isRejected
                ? "rgba(244, 63, 94, 0.08)"
                : "rgba(245, 158, 11, 0.08)",
          }}
        >
          <div className="flex items-center gap-2">
            {isConfirmed && (
              <>
                <CheckCircle2 size={14} className="text-emerald-600 dark:text-emerald-400 shrink-0" />
                <span className="font-semibold text-emerald-800 dark:text-emerald-300">
                  Status: Terkonfirmasi oleh petugas lapangan (Isu Valid)
                </span>
              </>
            )}
            {isUncertain && (
              <>
                <HelpCircle size={14} className="text-amber-600 dark:text-amber-400 shrink-0" />
                <span className="font-semibold text-amber-800 dark:text-amber-300">
                  Status: Ditandai Tidak Pasti — Memerlukan inspeksi fisik berkala
                </span>
              </>
            )}
            {isRejected && (
              <>
                <XCircle size={14} className="text-rose-600 dark:text-rose-400 shrink-0" />
                <span className="font-semibold text-rose-800 dark:text-rose-300">
                  Status: Ditolak sebagai False Positive {savedReason ? `· "${savedReason}"` : ""}
                </span>
              </>
            )}
          </div>
        </div>
      )}

      {feedback && (
        <p className="mt-2.5 text-[11.5px] text-accent animate-fade-in font-medium">
          {feedback}
        </p>
      )}

      {error && (
        <p className="mt-2 text-[11.5px] text-rose-600 dark:text-rose-400 flex items-center gap-1">
          <AlertCircle size={13} />
          {error}
        </p>
      )}
    </div>
  );
}
