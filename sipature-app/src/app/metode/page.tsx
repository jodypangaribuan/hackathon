/**
 * Layar 5 — Metode & Keterbatasan.
 * Rumus, audit bias, deklarasi pemakaian dataset, dan etika — semua angka
 * diambil dari corpus.json, bukan diketik ulang.
 */
import type { Metadata } from "next";
import { Card, Meter, Note, SectionTitle } from "@/components/ui";
import { corpus, places } from "@/lib/data";
import { ASPECT_LABEL, num, severityLabel } from "@/lib/format";
import type { AspectKey } from "@/lib/types";
import { AspectIcon } from "@/components/AppIcon";
import { Check, Circle, TriangleAlert } from "lucide-react";

export const metadata: Metadata = {
  title: "Model & Keterbatasan — SIPATURE",
  description:
    "Rumus indeks friksi, audit bias, deklarasi dataset, dan batas kejujuran demo.",
};

export default function MetodePage() {
  const severityRows = (Object.entries(corpus.severity) as [AspectKey, number][])
    .sort((a, b) => a[1] - b[1]);

  const dist = corpus.ratingDistribution;
  const distTotal = Object.values(dist).reduce((s, v) => s + v, 0);
  const noReview = places.filter((p) => p.confidence === "none").length;
  const lowConf = places.filter((p) => p.confidence === "low").length;

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Metode &amp; Keterbatasan
        </h1>
        <p className="mt-1 text-[13px] leading-relaxed text-ink-2">
          Semua angka pada halaman ini dihitung dari dataset panitia (
          {corpus.generatedFrom}) oleh <code className="text-[12px]">scripts/gen_seed.py</code>{" "}
          — tidak ada yang diketik manual.
        </p>
      </section>

      {/* ------------------------------------------------------------ rumus */}
      <Card className="p-4 sm:p-5">
        <SectionTitle>Rumus Indeks Friksi</SectionTitle>
        <pre
          className="thin-scroll overflow-x-auto rounded-md border p-3 text-[12px] leading-relaxed"
          style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}
        >
{`mention_rate  = review menyebut aspek / total review berteks di tempat itu
neg_rate      = Wilson lower bound 95% dari (negatif / disebut)
severity      = mean(rating | aspek disebut) − mean(rating global ${String(corpus.globalMeanRating).replace(".", ",")})
FrictionIndex = Σ  mention_rate × neg_rate × |severity|   (ditampilkan × 100)`}
        </pre>
        <p className="mt-3 text-[13px] leading-relaxed text-ink-2">
          <strong>Wilson lower bound wajib.</strong>{" "}
          {Math.round(((dist["5"] ?? 0) / Math.max(distTotal, 1)) * 100)}% ulasan
          berbintang 5 sehingga kelas negatif langka; tanpa koreksi ini, tempat
          dengan 5 ulasan akan tampak lebih bermasalah daripada tempat dengan
          800 ulasan. Ini sekaligus jawaban matematis terhadap bias popularitas.
        </p>
      </Card>

      {/* ------------------------------------------------- distribusi rating */}
      <Card className="p-4 sm:p-5">
        <SectionTitle hint={`${num(distTotal)} ulasan berbintang`}>
          Distribusi Rating Korpus
        </SectionTitle>
        <div className="space-y-2">
          {(["5", "4", "3", "2", "1"] as const).map((star) => (
            <Meter
              key={star}
              value={dist[star] ?? 0}
              max={distTotal}
              label={`★ ${star}`}
              valueLabel={`${num(dist[star] ?? 0)} (${Math.round(((dist[star] ?? 0) / Math.max(distTotal, 1)) * 100)}%)`}
            />
          ))}
        </div>
        <p className="mt-3 text-[12px] leading-relaxed text-muted">
          Ketimpangan ini alasan kelas negatif diperlakukan hati-hati: sinyal
          keluhan harus dicari pada minoritas ulasan, bukan diasumsikan merata.
        </p>
      </Card>

      {/* ---------------------------------------------------------- severity */}
      <Card className="p-4 sm:p-5">
        <SectionTitle>Severity Keluar dari Data — Bukan Ditentukan Manual</SectionTitle>
        <p className="mb-3 text-[13px] leading-relaxed text-ink-2">
          Severity tiap aspek = rata-rata rating saat aspek disebut dikurangi
          rata-rata global. Aspek yang benar-benar menyakitkan menyeret rating
          paling dalam:
        </p>
        <div className="thin-scroll overflow-x-auto">
          <table className="w-full text-[13px]">
            <thead>
              <tr className="text-left text-[11px] uppercase tracking-wide text-muted">
                <th className="pb-2 font-medium">Aspek</th>
                <th className="pb-2 text-right font-medium">Dampak rating</th>
              </tr>
            </thead>
            <tbody>
              {severityRows.map(([key, sev]) => {
                const positive = sev > 0;
                return (
                  <tr
                    key={key}
                    className="border-t"
                    style={{ borderColor: "var(--hairline)" }}
                  >
                    <td className="py-1.5">
                       <AspectIcon aspect={key} className="mr-1.5 inline" />
                      {positive ? (
                        <strong>{ASPECT_LABEL[key]}</strong>
                      ) : (
                        ASPECT_LABEL[key]
                      )}
                    </td>
                    <td
                      className="tabular py-1.5 text-right font-medium"
                      style={positive ? { color: "var(--success-text)" } : undefined}
                    >
                      {severityLabel(sev)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-[12px] leading-relaxed text-muted">
          Baris positif adalah uji kewarasan: aspek yang memang disukai
          (pemandangan) keluar bernilai positif. Metode ini bukan sekadar
          penghitung kata negatif.
        </p>
      </Card>

      {/* ---------------------------------------------------- batas kejujuran */}
      <Card className="p-4 sm:p-5">
        <SectionTitle>Batas Kejujuran Demo Ini</SectionTitle>
        <ul className="space-y-2.5 text-[13px] leading-relaxed text-ink-2">
          <li>
             <TriangleAlert size={14} className="mr-1 inline" /> <strong>Skor friksi berasal dari baseline keyword + rating, BUKAN
            model IndoBERT terlatih.</strong>{" "}
            Lapisan itu diganti setelah model tahap preliminary selesai, dan
            macro-F1-nya dilaporkan.
          </li>
          <li>
             <Check size={14} className="mr-1 inline" /> <strong>Nama tempat, koordinat, dan seluruh kutipan ulasan adalah
            data asli</strong>{" "}
            dataset panitia. Tidak ada kutipan karangan.
          </li>
          <li>
             <Circle size={12} className="mr-1 inline" /> {num(noReview)} tempat tidak punya ulasan sama sekali. Mereka{" "}
            <strong>ditampilkan</strong> sebagai prioritas survei lapangan,
            bukan disembunyikan.
          </li>
          <li>
             <Circle size={12} className="mr-1 inline" /> {num(lowConf)} tempat dengan &lt; 20 ulasan berteks ditandai
            kepercayaan rendah dan <strong>dikeluarkan dari peringkat publik</strong>{" "}
            — hanya {num(corpus.rankedCount)} dari {num(places.length)} tempat
            yang diperingkat.
          </li>
          <li>
             <TriangleAlert size={14} className="mr-1 inline" /> Korelasi gap infrastruktur ↔ tingkat keluhan <strong>bukan</strong>{" "}
            kausalitas. Simulasi Intervensi menampilkan <em>batas atas</em>{" "}
            perbaikan, bukan prediksi. Uji kausal memerlukan pilot terkendali di
            satu kecamatan.
          </li>
          <li>
             <TriangleAlert size={14} className="mr-1 inline" /> Bias platform: seluruh ulasan berasal dari pengguna Google Maps —
            condong ke wisatawan muda dan melek digital. Wisatawan lansia dan
            lokal non-digital tidak terwakili.
          </li>
        </ul>
      </Card>

      {/* -------------------------------------------------------------- etika */}
      <Card className="p-4 sm:p-5">
        <SectionTitle>Etika &amp; Privasi</SectionTitle>
        <ul className="space-y-2 text-[13px] leading-relaxed text-ink-2">
          <li>
            Identitas pengulas <strong>tidak disimpan maupun ditampilkan</strong>{" "}
            di mana pun pada aplikasi ini — kutipan dipotong di sekitar kata
            kunci aspek tanpa nama, foto, atau tautan profil.
          </li>
          <li>
            Skor friksi menilai <em>pengelolaan tempat</em>, bukan warga atau
            komunitas. Aspek “keamanan &amp; sikap” dilaporkan agregat, tidak
            pernah menunjuk individu.
          </li>
          <li>
            Metode: {corpus.method}.
          </li>
        </ul>
      </Card>

      <Note>
        Regenerasi data:{" "}
        <code className="text-[11px]">python3 scripts/gen_seed.py src/data</code>{" "}
        membaca 15 file CSV dataset panitia dan menulis ulang empat berkas JSON
        di <code className="text-[11px]">src/data/</code>.
      </Note>
    </div>
  );
}
