# SIPATURE Annotation Guideline

**Version:** `1.0.0-rc1`
**Status:** Pilot locked
**Taxonomy:** `ml/configs/taxonomy.yaml`
**Schema:** `ml/contracts/annotation.schema.json`

## 1. Tujuan dan Unit Annotation

Satu unit annotation adalah satu clean textual review yang telah memiliki `review_id` dan `destination_id`. Annotator memberi semua aspek yang eksplisit atau jelas tersirat, polarity per aspek, dan severity hanya untuk aspek negatif.

Review boleh memiliki nol, satu, atau beberapa aspek. Rating hanya konteks sekunder dan tidak boleh menggantikan isi teks.

## 2. Prinsip Umum

1. Label berdasarkan teks, bukan asumsi tentang destinasi.
2. Label semua aspek yang didukung, bukan hanya aspek dominan.
3. Tentukan polarity pada clause yang merujuk aspek tersebut.
4. Positive clause tidak membatalkan negative clause pada aspek lain.
5. Jangan membuat evidence; salin span verbatim dari teks.
6. Jangan menyimpulkan fasilitas tidak ada hanya karena tidak disebut.
7. Jika dua label sama-sama masuk akal dan boundary rule tidak menyelesaikan, tandai `needs_adjudication`.
8. Tidak ada nama/ID reviewer dalam annotation file.

## 3. Output Example

```json
{
  "review_id": "review_abc",
  "destination_id": "dest_xyz",
  "text": "Pemandangannya indah tetapi toiletnya kotor dan tidak ada air.",
  "rating_context": 5,
  "labels": [
    {
      "aspect": "scenery",
      "polarity": "positive",
      "severity": null,
      "evidence_text": "Pemandangannya indah",
      "notes": null
    },
    {
      "aspect": "sanitation",
      "polarity": "negative",
      "severity": "high",
      "evidence_text": "toiletnya kotor dan tidak ada air",
      "notes": null
    }
  ],
  "annotator_id": "A1",
  "annotation_version": "1.0.0-rc1",
  "annotation_status": "completed",
  "review_notes": null
}
```

## 4. Aspect Definitions

### 4.1 `cleanliness`

**Definition:** Kebersihan umum area, permukaan, kamar, meja, alat, atau lingkungan layanan.
**In scope:** kotor, jorok, bau karena kebersihan, debu, serangga/jaring laba-laba, area bersih.
**Out of scope:** sampah spesifik (`waste`), toilet/air/drainase (`sanitation`), kerusakan (`maintenance`).
**Positive:** “Kamarnya bersih dan rapi.”
**Negative:** “Meja dan lantainya sangat kotor.”
**Neutral:** “Petugas sedang membersihkan area.”

### 4.2 `waste`

**Definition:** Sampah/limbah dan pengelolaan atau pembuangannya.
**In scope:** sampah berserakan, plastik, limbah, tempat sampah, pengangkutan sampah.
**Out of scope:** area kotor tanpa penyebutan sampah (`cleanliness`), air toilet (`sanitation`).
**Positive:** “Tempat sampah tersedia dan rutin dikosongkan.”
**Negative:** “Sampah plastik berserakan di tepi pantai.”
**Neutral:** “Ada beberapa tempat sampah di pintu masuk.”

### 4.3 `sanitation`

**Definition:** Toilet, WC, kamar mandi, MCK, air bersih, drainase, dan kondisi sanitasi.
**In scope:** toilet kotor/rusak, tidak ada air, bau toilet, drainase, kamar mandi bersih.
**Out of scope:** kebersihan kamar umum (`cleanliness`), fasilitas duduk/lampu (`public_facilities`).
**Positive:** “Toilet bersih dan airnya lancar.”
**Negative:** “WC tidak bisa dipakai dan tidak ada air.”
**Neutral:** “Toilet berada dekat area parkir.”

### 4.4 `crowding`

**Definition:** Kepadatan, antrean, atau keramaian yang memengaruhi pengalaman/operasi.
**In scope:** terlalu padat, antre panjang, sepi/tenang dalam konteks crowd level.
**Out of scope:** bising tanpa kaitan keramaian (`comfort`), parkir penuh (`parking`; tambahkan crowding jika kerumunan disebut).
**Positive:** “Ramai tetapi antreannya teratur.”
**Negative:** “Terlalu penuh sampai sulit bergerak.”
**Neutral:** “Biasanya ramai saat akhir pekan.”

### 4.5 `access`

**Definition:** Jalan, rute, medan, transport access, signage, atau kemudahan mencapai lokasi.
**In scope:** jalan rusak/terjal, rute mudah, petunjuk arah, sulit dijangkau.
**Out of scope:** licin/berbahaya di dalam lokasi tanpa akses context (`safety`), parking (`parking`).
**Positive:** “Jalannya sudah bagus dan mudah ditemukan.”
**Negative:** “Jalan menuju lokasi rusak, gelap, dan terjal.”
**Neutral:** “Lokasi dapat dicapai dengan sepeda motor.”

### 4.6 `parking`

**Definition:** Ketersediaan, kapasitas, keamanan, biaya, dan pengelolaan parkir.
**In scope:** parkiran luas/sempit, biaya parkir, kendaraan tidak aman di parkiran.
**Out of scope:** pungutan tiket masuk (`price_transparency`), jalan menuju tempat (`access`).
**Positive:** “Parkir luas dan dijaga.”
**Negative:** “Parkir sempit dan tarifnya tidak jelas.”
**Neutral:** “Parkir tersedia di depan lokasi.”

### 4.7 `public_facilities`

**Definition:** Fasilitas publik selain sanitation/parking, seperti gazebo, tempat duduk, penerangan, aksesibilitas, dan tempat ibadah.
**In scope:** fasilitas tersedia/tidak memadai, lampu, kursi, gazebo, mushola, akses kursi roda.
**Out of scope:** toilet (`sanitation`), parkir (`parking`), kerusakan fasilitas (`maintenance`; label keduanya bila fasilitas dan kondisi rusaknya disebut).
**Positive:** “Gazebo dan tempat duduknya cukup.”
**Negative:** “Tidak ada penerangan dan fasilitas untuk lansia.”
**Neutral:** “Terdapat mushola di dekat pintu masuk.”

### 4.8 `scenery`

**Definition:** Pemandangan, panorama, keindahan alam/visual, sunrise, atau sunset.
**In scope:** view indah/biasa/tertutup, panorama, suasana visual.
**Out of scope:** nyaman/sejuk tanpa visual (`comfort`), atraksi menarik tanpa visual yang jelas.
**Positive:** “Pemandangan Danau Toba sangat indah.”
**Negative:** “Pemandangannya tertutup bangunan.”
**Neutral:** “Dari sini terlihat Danau Toba.”

### 4.9 `comfort`

**Definition:** Kenyamanan fisik/atmosfer yang tidak lebih spesifik pada fasilitas, crowding, atau safety.
**In scope:** nyaman, sejuk, panas, pengap, bising, tenang.
**Out of scope:** kepadatan (`crowding`), kursi/fasilitas (`public_facilities`), rasa aman (`safety`).
**Positive:** “Suasananya sejuk dan nyaman.”
**Negative:** “Kamarnya pengap dan sangat bising.”
**Neutral:** “Area ini lebih tenang pada pagi hari.”

### 4.10 `safety`

**Definition:** Risiko cedera, kriminalitas, ancaman, kondisi berbahaya, atau rasa aman.
**In scope:** rawan, licin berbahaya, preman, maling, ancaman, pengunjung merasa aman.
**Out of scope:** staf kasar tanpa ancaman (`staff_service`), jalan rusak tanpa risk statement (`access`). Label access+safety bila jalan disebut berbahaya.
**Positive:** “Tempatnya aman dan ada penjaga.”
**Negative:** “Jalannya gelap dan sangat berbahaya untuk mobil.”
**Neutral:** “Ada petugas keamanan di pintu masuk.”

### 4.11 `price_transparency`

**Definition:** Kejelasan/kewajaran relatif biaya, pungutan, perubahan harga, tiket, atau biaya yang tidak diinformasikan.
**In scope:** pungli, biaya tersembunyi, tarif berbeda, harga terlalu mahal relatif layanan, harga jelas.
**Out of scope:** menyebut angka harga tanpa evaluasi (neutral masih boleh jika informatif); preferensi “mahal bagi saya” tanpa masalah transparansi diberi negative low, bukan high.
**Positive:** “Harga tiket jelas dan sesuai fasilitas.”
**Negative:** “Diminta biaya tambahan yang tidak diinformasikan.”
**Neutral:** “Tiket masuknya Rp10.000.”

### 4.12 `staff_service`

**Definition:** Sikap, respons, komunikasi, kecepatan, atau profesionalitas staf/petugas/pengelola.
**In scope:** ramah, kasar, lambat, tidak responsif, membantu.
**Out of scope:** perilaku pengunjung/warga tanpa peran operasional; ancaman/kriminalitas (`safety`).
**Positive:** “Petugasnya ramah dan membantu.”
**Negative:** “Staf kasar dan tidak mau menjelaskan.”
**Neutral:** “Petugas memeriksa tiket di pintu masuk.”

### 4.13 `maintenance`

**Definition:** Kondisi perawatan, kerusakan, keusangan, atau objek/fasilitas terbengkalai.
**In scope:** tidak terawat, rusak, usang, cat mengelupas, fasilitas terbengkalai.
**Out of scope:** jalan rusak menuju lokasi (`access`); toilet rusak label `sanitation` + `maintenance` bila kedua konsep penting.
**Positive:** “Bangunannya terawat dengan baik.”
**Negative:** “Gazebo rusak dan dibiarkan terbengkalai.”
**Neutral:** “Sebagian fasilitas sedang diperbaiki.”

### 4.14 `opening_hours`

**Definition:** Kesesuaian informasi dan realisasi jam/hari buka atau tutup.
**In scope:** tutup sebelum jadwal, belum buka, informasi jam akurat, buka 24 jam.
**Out of scope:** destinasi tutup permanen tanpa pengalaman kunjungan dapat diberi neutral bila hanya informasi; status operasi metadata bukan label review.
**Positive:** “Buka tepat waktu sesuai informasi.”
**Negative:** “Di internet tertulis buka tetapi saat datang masih tutup.”
**Neutral:** “Lokasi buka pukul delapan.”

## 5. Polarity Rules

### Positive

Aspek dinilai baik, memuaskan, tersedia dengan kualitas baik, atau meningkat secara jelas.

### Negative

Aspek berisi keluhan, kekurangan, risiko, ketidaksesuaian, atau pengalaman buruk.

### Neutral

Aspek disebut faktual tanpa evaluasi jelas. Neutral bukan “tidak tahu”; jika aspek tidak didukung, jangan beri label.

### Negation

- “Tidak kotor” = `cleanliness: positive` bila jelas menyatakan bersih; bila hanya menyangkal tuduhan dan konteks ambigu, adjudicate.
- “Tidak terlalu bersih” = `cleanliness: negative`.
- “Belum rusak” = `maintenance: positive/neutral` sesuai konteks, bukan negative.
- Negasi tidak otomatis berlaku melewati clause marker.

### Contrast

Pada “pemandangan bagus tetapi jalan rusak”, label `scenery: positive` dan `access: negative`. Jangan memilih hanya clause setelah “tetapi”.

### Sarcasm

Label sarcasm hanya jika intent negatif cukup jelas dari lexical/context cue, misalnya “Bagus sekali, datang jauh-jauh ternyata tutup.” Beri `opening_hours: negative`; tulis `sarcasm` pada notes. Jika intent tidak jelas, `needs_adjudication`.

### Implicit Complaint

Keluhan tersirat boleh dilabel jika implikasinya operasional dan tidak membutuhkan asumsi jauh: “Harus dorong motor sampai atas” mendukung `access: negative`. “Lumayan” tanpa objek tidak cukup.

## 6. Multi-Aspect Boundaries

- “Toilet kotor” = `sanitation`; tambahkan `cleanliness` hanya bila kebersihan area umum juga disebut.
- “Jalan rusak dan berbahaya” = `access` + `safety`.
- “Parkir mahal dan tidak ada karcis” = `parking` + `price_transparency`.
- “Gazebo rusak” = `public_facilities` + `maintenance` bila fasilitas dan kondisi perawatannya sama-sama relevan.
- “Petugas mengancam” = `staff_service` + `safety`; “petugas kasar” = `staff_service` saja.
- “Terlalu ramai dan bising” = `crowding` + `comfort`.

## 7. Severity Rules

Severity hanya untuk polarity `negative`. Rating tidak menentukan severity.

### Low

Gangguan ringan, preferensi, atau keluhan terbatas tanpa hambatan berarti. Contoh: “Harga agak mahal”, “parkir sedikit sempit”, “toilet kurang wangi tetapi bisa dipakai”.

### Medium

Masalah jelas yang mengurangi pengalaman atau memerlukan tindakan operasional, tetapi tidak menunjukkan bahaya serius atau fungsi utama gagal total. Contoh: “Jalan rusak cukup panjang”, “staf kasar”, “toilet kotor”, “antre satu jam”.

### High

Risiko keselamatan/kriminalitas, pungutan/pemaksaan serius, kegagalan fungsi dasar, atau masalah yang membuat layanan tidak dapat digunakan. Contoh: “Jalan sangat berbahaya untuk mobil”, “dipalak/pungli”, “toilet tidak bisa dipakai dan tidak ada air”, “kamar membuat keracunan makanan” jika dinyatakan sebagai pengalaman pelapor.

Jika severity bergantung pada fakta yang tidak ada di teks, pilih tingkat lebih rendah atau adjudicate.

## 8. Annotation Workflow

1. Baca seluruh review tanpa melihat candidate suggestion terlebih dahulu bila tool memungkinkan.
2. Tentukan semua aspek.
3. Tentukan polarity per aspek.
4. Isi severity hanya untuk negative.
5. Salin evidence span verbatim.
6. Validasi constraint dan tandai completed/needs_adjudication.
7. Jangan berkomunikasi dengan annotator lain sebelum double-annotation pilot selesai.

## 9. Adjudication

Adjudication record memuat review ID, dua label, jenis disagreement, final label, rationale, guideline section/change, adjudicator ID, dan timestamp. Perubahan taxonomy setelah pilot menghasilkan versi baru; label lama tidak ditimpa tanpa migration log.

## 10. Pilot Gate

- Aspect set Jaccard >=0,70.
- Polarity agreement pada matched aspects >=0,75.
- Severity weighted kappa >=0,60.
- Jika gate gagal, revisi guideline/taxonomy dan ulangi pilot sebelum main annotation.
