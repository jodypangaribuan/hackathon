import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";

export const metadata: Metadata = {
  title: "MARTAHUTA — Toba Retention Intelligence",
  description:
    "Mengubah 22.302 ulasan wisatawan Danau Toba menjadi daftar perbaikan berprioritas bagi pengelola destinasi, pemerintah daerah, dan UMKM.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body className="min-h-screen">
        <Nav />
        <main className="mx-auto max-w-[1400px] px-4 py-6">{children}</main>
        <footer
          className="mx-auto max-w-[1400px] border-t px-4 py-6 text-[11px] leading-relaxed text-muted"
          style={{ borderColor: "var(--hairline)" }}
        >
          <p>
            <strong className="text-ink-2">MARTAHUTA</strong> — <em>Marsipature Hutana Be</em>.
            Prototipe Del AI Hackathon 2026.
          </p>
          <p className="mt-1">
            Nama tempat, koordinat, dan seluruh kutipan ulasan berasal dari dataset panitia
            yang sebenarnya. Skor friksi pada demo ini dihitung dengan baseline
            <em> keyword + rating</em> sebagai pengganti sementara keluaran model IndoBERT.
            Identitas pengulas tidak disimpan maupun ditampilkan.
          </p>
        </footer>
      </body>
    </html>
  );
}
