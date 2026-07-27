import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, ClipboardCheck } from "lucide-react";
import { rankedPlaces } from "@/lib/data";
import { ASPECT_LABEL, levelOfPlace, num, score } from "@/lib/format";
import { AspectIcon } from "@/components/AppIcon";
import { Card, LevelBadge, Note, SectionTitle } from "@/components/ui";

export const metadata: Metadata = { title: "Antrean Intervensi — SIPATURE" };

export default function IntervensiPage() {
  return (
    <div className="space-y-5">
      <section className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight">Antrean Intervensi</h1>
          <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
            Destinasi dan masalah yang harus diverifikasi lebih dulu, diurutkan dari bukti,
            keparahan, frekuensi, dan kepercayaan data.
          </p>
        </div>
        <span className="tabular text-[12px] text-muted">{num(rankedPlaces.length)} destinasi berperingkat</span>
      </section>
      <Card className="overflow-hidden">
        <div className="p-4"><SectionTitle hint="Peringkat 1 paling mendesak">Prioritas Verifikasi Lapangan</SectionTitle></div>
        <div className="thin-scroll overflow-x-auto">
          <table className="w-full min-w-[820px] text-left text-[12px]">
            <thead className="border-y text-[11px] uppercase tracking-wide text-muted" style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}>
              <tr><th className="px-4 py-2 font-medium">Prioritas</th><th className="px-3 py-2 font-medium">Destinasi</th><th className="px-3 py-2 font-medium">Sinyal utama</th><th className="px-3 py-2 font-medium">Bukti</th><th className="px-3 py-2 font-medium">Langkah berikutnya</th><th className="px-4 py-2" /></tr>
            </thead>
            <tbody>
              {rankedPlaces.slice(0, 100).map((place) => {
                const aspect = place.aspects.find((row) => row.aspect === place.topAspects[0]);
                return (
                  <tr key={place.id} className="border-b last:border-0" style={{ borderColor: "var(--hairline)" }}>
                    <td className="px-4 py-3"><div className="flex items-center gap-2"><span className="tabular font-semibold">#{place.rank}</span><LevelBadge level={levelOfPlace(place)} size="sm" /></div></td>
                    <td className="px-3 py-3"><Link href={`/destinasi/${place.id}`} className="font-medium hover:underline">{place.name}</Link><span className="block text-[11px] text-muted">{place.kabupaten} · indeks {score(place.frictionScore)}</span></td>
                    <td className="px-3 py-3">{aspect ? <span className="inline-flex items-center gap-1.5"><AspectIcon aspect={aspect.aspect} />{ASPECT_LABEL[aspect.aspect]}</span> : <span className="text-muted">Belum cukup sinyal</span>}</td>
                    <td className="tabular px-3 py-3 text-ink-2">{aspect ? `${num(aspect.nNegative)} negatif / ${num(aspect.nMention)} sebutan` : "—"}</td>
                    <td className="px-3 py-3 text-ink-2"><span className="inline-flex items-center gap-1.5"><ClipboardCheck size={14} />Verifikasi kondisi dan metadata di lapangan</span></td>
                    <td className="px-4 py-3 text-right"><Link href={`/destinasi/${place.id}`} aria-label={`Buka bukti ${place.name}`}><ArrowRight size={15} /></Link></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
      <Note>Sinyal ulasan bukan vonis kualitas. Setiap item harus diverifikasi manusia sebelum intervensi atau komunikasi publik.</Note>
    </div>
  );
}
