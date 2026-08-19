"use client";

import { useState } from "react";
import {
  CheckCircle2,
  ClipboardCheck,
  HelpCircle,
  LoaderCircle,
  XCircle,
} from "lucide-react";

type Verdict = "confirmed" | "rejected" | "uncertain";

const STATUS_STYLE: Record<
  Verdict,
  { label: string; icon: typeof CheckCircle2; color: string }
> = {
  confirmed: { label: "Terkonfirmasi", icon: CheckCircle2, color: "var(--status-good)" },
  rejected: { label: "Ditolak", icon: XCircle, color: "var(--status-serious)" },
  uncertain: { label: "Tidak pasti", icon: HelpCircle, color: "var(--text-muted)" },
};

export default function AlertStatusControl({
  destinationId,
  aspect,
}: {
  destinationId: string;
  aspect: string;
}) {
  const [verdict, setVerdict] = useState<Verdict | null>(null);
  const [busy, setBusy] = useState(false);
  const [rejecting, setRejecting] = useState(false);
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit(next: Verdict, rejectionReason?: string) {
    setBusy(true);
    setError(null);
    try {
      const response = await fetch("/api/alerts/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ destinationId, aspect, status: next, rejectionReason }),
      });
      const payload = (await response.json()) as {
        status?: string;
        error?: string;
      };
      if (!response.ok) {
        setError(payload.error ?? "Gagal menyimpan verifikasi.");
        return;
      }
      setVerdict(next);
      setRejecting(false);
      setReason("");
    } catch {
      setError("Gagal menyimpan verifikasi.");
    } finally {
      setBusy(false);
    }
  }

  const activeStatus = verdict ? STATUS_STYLE[verdict] : null;
  const StatusIcon = activeStatus?.icon;

  return (
    <div className="mt-3 rounded-md border p-2.5" style={{ borderColor: "var(--hairline)" }}>
      <div className="mb-1.5 flex items-center gap-1.5 text-[11px] font-semibold uppercase text-muted">
        <ClipboardCheck size={13} />
        Verifikasi lapangan
      </div>
      {verdict && activeStatus && StatusIcon ? (
        <div className="flex items-center gap-2 text-[12px]">
          <span
            className="inline-flex items-center gap-1.5 font-medium"
            style={{ color: activeStatus.color }}
          >
            <StatusIcon size={13} />
            {activeStatus.label}
          </span>
          {verdict === "rejected" && reason ? (
            <span className="text-muted">· {reason}</span>
          ) : null}
        </div>
      ) : (
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            disabled={busy}
            onClick={() => void submit("confirmed")}
            className="inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-[12px] disabled:opacity-50"
            style={{ borderColor: "var(--hairline)" }}
          >
            {busy ? <LoaderCircle className="animate-spin" size={13} /> : <CheckCircle2 size={13} />}
            Konfirmasi
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => void submit("uncertain")}
            className="inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-[12px] disabled:opacity-50"
            style={{ borderColor: "var(--hairline)" }}
          >
            <HelpCircle size={13} />
            Tidak pasti
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => setRejecting((value) => !value)}
            className="inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-[12px] disabled:opacity-50"
            style={{ borderColor: "var(--hairline)", color: "var(--status-serious)" }}
          >
            <XCircle size={13} />
            Tolak (false positive)
          </button>
        </div>
      )}
      {rejecting && !verdict ? (
        <div className="mt-2 space-y-2">
          <input
            type="text"
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            placeholder="Alasan penolakan (mis. tarif sudah jelas di lapangan)"
            className="w-full rounded-md border bg-transparent px-3 py-2 text-[12px] outline-none focus:ring-2"
            style={{ borderColor: "var(--hairline)" }}
          />
          <button
            type="button"
            disabled={busy || !reason.trim()}
            onClick={() => void submit("rejected", reason.trim())}
            className="inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-[12px] font-semibold text-white disabled:opacity-40"
            style={{ background: "var(--status-serious)" }}
          >
            {busy ? <LoaderCircle className="animate-spin" size={13} /> : <XCircle size={13} />}
            Simpan penolakan
          </button>
        </div>
      ) : null}
      {error ? (
        <p className="mt-2 text-[11px]" style={{ color: "var(--status-critical)" }}>
          {error}
        </p>
      ) : null}
    </div>
  );
}
