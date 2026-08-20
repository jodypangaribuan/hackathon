import type { Metadata } from "next";
import InterventionQueueClient from "@/components/InterventionQueueClient";
import { getRankedPlaces } from "@/lib/data";
import { num } from "@/lib/format";
import { Note } from "@/components/ui";

export const metadata: Metadata = {
  title: "Antrean Tindak Lanjut — SIPATURE",
  description: "Daftar prioritas tugas verifikasi dan penanganan fasilitas destinasi Danau Toba.",
};

export const dynamic = "force-dynamic";

export default async function InterventionsPage() {
  const rankedPlaces = await getRankedPlaces();

  return (
    <div className="space-y-5">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight sm:text-[26px]">
          Antrean Tugas Tindak Lanjut &amp; Verifikasi
        </h1>
        <p className="mt-1.5 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          Daftar <strong>{num(rankedPlaces.length)} destinasi prioritas</strong> yang memiliki keluhan berulang wisatawan. Petugas dan pengelola dapat memeriksa rincian masalah, panduan cek fisik, dan mencatat status konfirmasi lapangan.
        </p>
      </section>

      <InterventionQueueClient rankedPlaces={rankedPlaces} />

      <Note>
        Daftar tugas di atas ditujukan sebagai panduan awal inspeksi lapangan. Penanganan fisik dilakukan secara kolaboratif bersama pengelola destinasi dan dinas terkait.
      </Note>
    </div>
  );
}
