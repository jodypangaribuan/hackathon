import type { Metadata } from "next";
import DestinationDirectoryClient from "@/components/DestinationDirectoryClient";
import { getKabupatenList, getPlaces } from "@/lib/data";
import { num } from "@/lib/format";

export const metadata: Metadata = {
  title: "Katalog Destinasi — SIPATURE",
  description: "Direktori lengkap 388 destinasi kanonikal kawasan Danau Toba dengan skor prioritas.",
};

export const dynamic = "force-dynamic";

export default async function DestinationsPage() {
  const [places, kabupatenList] = await Promise.all([
    getPlaces(),
    getKabupatenList(),
  ]);

  return (
    <div className="space-y-5">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Katalog Destinasi Pariwisata Toba
        </h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          Eksplorasi seluruh {num(places.length)} destinasi kanonikal Danau Toba
          yang telah diintegrasikan melalui proses pembersihan data dan resolusi entitas.
          Gunakan filter untuk meninjau sinyal isu dan tingkat keyakinan data per lokasi.
        </p>
      </section>

      <DestinationDirectoryClient
        places={places}
        kabupatenList={kabupatenList}
      />
    </div>
  );
}
