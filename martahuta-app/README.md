# MARTAHUTA — Toba Retention Intelligence

> *Marsipature Hutana Be* — setiap orang membangun kampungnya sendiri.
> Contoh aplikasi final Del AI Hackathon 2026.

Toba menerima **751.225** kunjungan wisatawan nusantara namun rata-rata tinggal hanya
**1,31 hari**. Simalungun dan Karo masing-masing menarik 2,3–2,6 juta. Toba berfungsi
sebagai koridor transit, bukan destinasi menginap.

Aplikasi ini membalik arah pertanyaan yang biasa diajukan. Alih-alih membantu wisatawan
menemukan tempat, ia menjawab: **apa persisnya yang membuat mereka pergi cepat, diurutkan
menurut besar kerugiannya, per destinasi** — untuk Dinas Pariwisata, BPODT, pengelola
destinasi, dan UMKM.

---

## Menjalankan

```bash
npm install
npm run dev          # http://localhost:3000
```

Produksi / DGX B200:

```bash
docker compose up -d --build
curl http://localhost:3000/api/health
```

---

## Empat layar

| Rute | Layar | Isi |
|---|---|---|
| `/` | **Peta Friksi** | 320 tempat berkoordinat, diwarnai tingkat friksi, dengan filter dan peringkat |
| `/destinasi/[id]` | **Rapor Destinasi** | Prioritas perbaikan + kutipan verbatim sebagai bukti + gap infrastruktur + Simulasi Intervensi |
| `/umkm` | **Peluang UMKM** | Peluang usaha yang diturunkan dari keluhan nyata, bukan survei pasar |
| `/analyzer` | **Live Analyzer** | Tempel ulasan apa pun, lihat ekstraksi aspek + sentimen berjalan |
| `/metode` | **Metode & Keterbatasan** | Rumus, bias audit, deklarasi pemakaian dataset, etika |

---

## API

| Endpoint | Method | Keterangan |
|---|---|---|
| `/api/health` | GET | Status layanan |
| `/api/places` | GET | Daftar tempat; `?kabupaten=&kind=&aspect=&confidence=&q=&limit=` |
| `/api/places/[id]` | GET | Detail satu tempat beserta aspek dan bukti |
| `/api/opportunities` | GET | Peluang UMKM; `?kabupaten=&category=&limit=` |
| `/api/analyze` | POST | `{ text }` → aspek + sentimen + bukti + latensi |
| `/api/simulate` | POST | `{ placeId, fixes[] }` → indeks & peringkat baru |

---

## Dari mana angkanya

`scripts/gen_seed.py` membaca **15 file CSV dataset panitia** lalu menghasilkan empat berkas
JSON di `src/data/`. Regenerasi:

```bash
python3 scripts/gen_seed.py src/data
```

Yang dihitung:

```
mention_rate  = review menyebut aspek / total review berteks di tempat itu
neg_rate      = Wilson lower bound 95% dari (negatif / disebut)
severity      = mean(rating | aspek disebut) − mean(rating global 4,441)
FrictionIndex = Σ  mention_rate × neg_rate × |severity|          (ditampilkan × 100)
```

**Wilson lower bound wajib.** 72% ulasan berbintang 5 sehingga kelas negatif langka; tanpa
koreksi ini, tempat dengan 5 ulasan akan tampak lebih bermasalah daripada tempat dengan 800
ulasan. Ini sekaligus cara menjawab bias popularitas secara matematis.

Severity yang keluar dari data — bukan ditentukan manual:

| Aspek | Dampak rating |
|---|---:|
| Keamanan & sikap warga | −2,54★ |
| Harga & pungutan | −1,21★ |
| Jam operasional | −0,84★ |
| Toilet & sanitasi | −0,56★ |
| Parkir | −0,30★ |
| Kebersihan | −0,27★ |
| Akses jalan | −0,21★ |
| **Pemandangan** | **+0,19★** |

Baris terakhir adalah uji kewarasan: aspek positif keluar positif. Metodenya bukan sekadar
penghitung kata negatif.

---

## ⚠ Batas kejujuran demo ini

- **Skor friksi berasal dari baseline keyword + rating, BUKAN model IndoBERT terlatih.**
  Lapisan itu diganti setelah model tahap preliminary selesai, dan macro-F1-nya dilaporkan.
- **Nama tempat, koordinat, dan seluruh kutipan ulasan adalah data asli** dataset panitia.
  Tidak ada kutipan karangan.
- 64 tempat tidak punya ulasan sama sekali. Mereka **ditampilkan** sebagai "prioritas survei
  lapangan", bukan disembunyikan.
- Tempat dengan < 20 ulasan berteks ditandai kepercayaan rendah dan **dikeluarkan dari
  peringkat publik**.
- Korelasi gap infrastruktur ↔ tingkat keluhan **bukan** kausalitas. Simulasi Intervensi
  menampilkan batas atas perbaikan, bukan prediksi.
- Identitas pengulas tidak disimpan maupun ditampilkan di mana pun.
- Bias platform: seluruh ulasan berasal dari pengguna Google Maps — condong ke wisatawan
  muda dan melek digital. Wisatawan lansia dan lokal non-digital tidak terwakili.

---

## Keputusan teknis

| Pilihan | Alasan |
|---|---|
| **Leaflet + tile raster**, bukan MapLibre vektor | Tile vektor menuntut WebGL plus tiga jenis permintaan tambahan (style JSON, glyph, sprite). Raster hanya PNG. Di ruang lockdown dengan perangkat dan jaringan tak terjamin, lebih sedikit titik gagal lebih berharga daripada zoom yang mulus |
| Basemap **CARTO Positron / Dark Matter**, gratis tanpa API key | Basemap sengaja muted agar tidak berebut perhatian dengan warna data di atasnya; tersedia versi terang **dan** gelap sehingga toggle tema ikut benar |
| Cadangan **peta SVG luring** otomatis | Bila enam tile berturut-turut gagal, aplikasi beralih sendiri ke peta ringkas nol-jaringan. Ini jawaban atas pertanyaan juri "bagaimana kalau ruang demo tidak ada internet?" |
| Data **precomputed** dari CSV | Peta muncul seketika; bila GPU bermasalah, 4 dari 5 layar tetap hidup |
| Inferensi live **hanya** di `/analyzer` | Satu-satunya tempat juri perlu melihat model bekerja |
| CSV/JSON, bukan Postgres | 320 tempat dan 22 ribu ulasan itu kecil; basis data hanya menambah kerumitan |
| Status palette 4 tingkat, bukan gradasi pelangi | Tingkat friksi adalah *state*, dan warna tidak pernah menjadi satu-satunya pembawa makna |

---

## Struktur

```
src/
├── app/            # halaman + route handler API
├── components/     # TobaMap, panel, kartu, primitif UI
├── lib/
│   ├── types.ts      # skema data
│   ├── format.ts     # tingkat friksi, proyeksi peta, formatter
│   ├── data.ts       # loader (server-only)
│   ├── simulate.ts   # simulasi intervensi (murni)
│   └── absa-sim.ts   # simulasi inferensi ABSA (murni)
└── data/           # JSON hasil scripts/gen_seed.py
```

---

Dokumen pendamping: `../IDEAS.md` (analisis dataset & ide) ·
`../IDE-1-MARTAHUTA-Detail.md` (spesifikasi model) · `../EKSEKUSI.md` (rencana eksekusi).
