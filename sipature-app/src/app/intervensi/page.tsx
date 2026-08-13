import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, ClipboardCheck, EyeOff } from "lucide-react";
import { getRankedPlaces } from "@/lib/data";
import { ASPECT_LABEL, levelOfPlace, num, score } from "@/lib/format";
import { AspectIcon } from "@/components/AppIcon";
import { Card, LevelBadge, Note, SectionTitle } from "@/components/ui";
export const metadata: Metadata = { title: "Antrean Intervensi — SIPATURE" };
export const dynamic = "force-dynamic";
export default async function InterventionsPage() {
  const rankedPlaces = await getRankedPlaces();
  return (
    <div className="space-y-5">
      <section className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight">
            Antrean Verifikasi & Intervensi
          </h1>
          <p className="mt-1 max-w-3xl text-[13px] text-ink-2">
            Destinasi diurutkan berdasarkan priority score SIPATURE Intelligence
            yang transparan.
            Tindakan tetap memerlukan verifikasi manusia.
          </p>
        </div>
        <span className="text-[12px] text-muted">
          {num(rankedPlaces.length)} destinasi actionable
        </span>
      </section>
      <Card className="overflow-hidden">
        <div className="p-4">
          <SectionTitle hint="Peringkat 1 paling mendesak">
            Prioritas Verifikasi Lapangan
          </SectionTitle>
        </div>
        <div className="thin-scroll overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-[12px]">
            <thead
              className="border-y text-[11px] uppercase text-muted"
              style={{
                borderColor: "var(--hairline)",
                background: "var(--surface-2)",
              }}
            >
              <tr>
                <th className="px-4 py-2">Prioritas</th>
                <th className="px-3 py-2">Destinasi</th>
                <th className="px-3 py-2">Sinyal utama</th>
                <th className="px-3 py-2">Support</th>
                <th className="px-3 py-2">Langkah berikutnya</th>
                <th className="px-4 py-2" />
              </tr>
            </thead>
            <tbody>
              {rankedPlaces.map((place) => {
                const issue = place.issues.find(
                  (item) => item.priority !== "Insufficient Data",
                );
                return (
                  <tr
                    key={place.id}
                    className="border-b"
                    style={{ borderColor: "var(--hairline)" }}
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">#{place.rank}</span>
                        <LevelBadge level={levelOfPlace(place)} size="sm" />
                      </div>
                    </td>
                    <td className="px-3 py-3">
                      <Link
                        href={`/destinasi/${place.id}`}
                        className="font-medium hover:underline"
                      >
                        {place.name}
                      </Link>
                      <span className="block text-[11px] text-muted">
                        {place.kabupaten} · skor {score(place.priorityScore)}
                      </span>
                    </td>
                    <td className="px-3 py-3">
                      {issue ? (
                        <span className="inline-flex items-center gap-1.5">
                          <AspectIcon aspect={issue.aspect} />
                          {ASPECT_LABEL[issue.aspect]}
                        </span>
                      ) : (
                        "–"
                      )}
                    </td>
                    <td className="px-3 py-3">
                      {issue
                        ? `${num(issue.negativeCount)} negatif / ${num(issue.mentionCount)} sebutan`
                        : "–"}
                      <span className="mt-1 block text-[10px] text-muted">
                        <EyeOff size={11} className="mr-1 inline" />
                        evidence restricted
                      </span>
                    </td>
                    <td className="max-w-[300px] px-3 py-3 text-ink-2">
                      {issue ? (
                        <span className="inline-flex gap-1.5">
                          <ClipboardCheck
                            size={14}
                            className="mt-0.5 shrink-0"
                          />
                          {issue.recommendedVerification}
                        </span>
                      ) : (
                        "–"
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <Link href={`/destinasi/${place.id}`}>
                        <ArrowRight size={15} />
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
      <Note>
        Reported issue bukan vonis kualitas atau kondisi lapangan. Expert
        judgments masih 0/25 dan evidence text belum dilepas ke aplikasi publik.
      </Note>
    </div>
  );
}
