#!/usr/bin/env python3
"""
Generator data seed MARTAHUTA.

Menghasilkan JSON untuk aplikasi Next.js dari dataset asli panitia.
Angka friksi dihitung dengan BASELINE KEYWORD + rating (bukan model terlatih) —
ini berdiri sebagai pengganti output IndoBERT sampai model preliminary selesai.
Nama tempat, koordinat, dan seluruh kutipan review adalah DATA ASLI.
"""
import csv, json, re, math, os, sys, collections, unicodedata

DS = "/Users/jody/Documents/Hackathon/Datasets"
OUT = sys.argv[1] if len(sys.argv) > 1 else "./out"
os.makedirs(OUT, exist_ok=True)

def load(f):
    p = f"{DS}/Dataset HackathonTourism - IT DEL.xlsx - {f}.csv"
    return list(csv.DictReader(open(p, encoding="utf-8")))

def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return re.sub(r"[^a-z0-9]", "", s)

def slug(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60]

def latlon(s):
    try:
        a, b = (s or "").split(",")
        la, lo = float(a), float(b)
        if 1.5 < la < 3.5 and 98.0 < lo < 100.0:
            return la, lo
    except Exception:
        pass
    return None

def hav(a, b):
    (la1, lo1), (la2, lo2) = a, b
    R = 6371.0
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = math.radians(la2 - la1), math.radians(lo2 - lo1)
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return round(2*R*math.asin(math.sqrt(h)), 2)

def wilson_lb(pos, n, z=1.96):
    """Wilson lower bound 95% — menghukum sampel kecil."""
    if n == 0:
        return 0.0
    p = pos / n
    d = 1 + z*z/n
    c = p + z*z/(2*n)
    m = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return round(max(0.0, (c - m) / d), 4)

# ---------------------------------------------------------------- tanggal
def months_ago(pub, scraped):
    """'a year ago' / '2 tahun lalu di' / 'Edited 3 months ago' -> bulan (int)."""
    if not pub:
        return None
    t = pub.lower().replace("edited", "").strip()
    t = t.replace("setahun", "1 tahun").replace("sebulan", "1 bulan")
    t = t.replace("seminggu", "1 minggu").replace("sehari", "1 hari")
    if t.startswith("a ") or t.startswith("an "):
        t = "1 " + t.split(" ", 1)[1]
    m = re.search(r"(\d+)", t)
    n = int(m.group(1)) if m else 1
    if re.search(r"year|tahun", t):   return n * 12
    if re.search(r"month|bulan", t):  return n
    if re.search(r"week|minggu", t):  return 0
    if re.search(r"day|hari|jam|hour|menit|minute", t): return 0
    return None

# ---------------------------------------------------------------- aspek
ASPECTS = [
    ("kebersihan",      "Kebersihan",            "🧹", r"sampah|kotor|jorok|bau busuk|bau\b|bersih|kebersihan|kumuh"),
    ("harga_pungli",    "Harga & Pungutan",      "💰", r"pungli|pungutan|dipalak|mahal|retribusi|karcis|bayar lagi|serba bayar|harga tiket|htm"),
    ("toilet_sanitasi", "Toilet & Sanitasi",     "🚻", r"toilet|wc\b|kamar mandi|sanitasi|air mati|mck"),
    ("parkir",          "Parkir",                "🅿️", r"parkir|parkiran"),
    ("akses_jalan",     "Akses Jalan",           "🛣️", r"jalan rusak|jalanan rusak|akses jalan|berlubang|jalan sempit|jalan berbatu|akses menuju|jalan menuju"),
    ("ramah_keluarga",  "Ramah Keluarga & Lansia", "👨‍👩‍👧", r"anak|balita|lansia|orang tua|stroller|difabel|kursi roda|keluarga"),
    ("halal_muslim",    "Halal & Muslim-Friendly", "🕌", r"halal|muslim|babi|b2\b|bpk\b|saksang|non halal|nonhalal"),
    ("rumah_ibadah",    "Rumah Ibadah",          "🛐", r"mushola|musholla|masjid|sholat|shalat|gereja|tempat ibadah"),
    ("jam_operasional", "Jam Operasional",       "🕐", r"sudah tutup|udah tutup|tutup jam|jam buka|belum buka|masih tutup|tutup lebih awal"),
    ("keamanan_sikap",  "Keamanan & Sikap Warga", "🛡️", r"preman|tidak aman|gak aman|dimarahi|di marahi|marah|maling|copet|kehilangan|galak|kasar"),
    ("pemandangan",     "Pemandangan",           "🏞️", r"pemandangan|view|indah|cantik|bagus banget|panorama|sunset|sunrise|asri|sejuk"),
]
ASPECT_RE = {k: re.compile(p) for k, _, _, p in ASPECTS}
ASPECT_META = {k: {"key": k, "label": lab, "icon": ic} for k, lab, ic, _ in ASPECTS}

# aspek yang diperlakukan sebagai friksi (pemandangan tidak)
FRICTION_ASPECTS = [k for k, _, _, _ in ASPECTS if k != "pemandangan"]

print("→ memuat dataset…")
wisata_md = load("wisata-metadata")
resto_md  = load("resto-metadata")
hotel_md  = load("hotel-metadata")
wisata_rv = load("wisata-v2")
rh_rv     = load("resto-hotel-v2")
wo        = load("waktu operasional destinasi")
transport = load("transportasi")
kuliner   = load("kuliner")
artikel   = load("Artikel Danau Toba")

# ---------------------------------------------------------------- tempat
places = {}

def add_place(name, kind, coord, extra):
    if not coord:
        return
    key = norm(name)
    if key in places:
        return
    places[key] = dict(
        id=slug(name), name=name.strip(), kind=kind,
        lat=coord[0], lon=coord[1], **extra
    )

for r in wisata_md:
    add_place(r["place-name"], "wisata", latlon(r["lat-long"]), dict(
        type=(r["place-type"] or "").strip() or "Wisata Alam",
        entryFee=(r["entry-fee"] or "").strip() or None,
        hours=(r["operational-hour"] or "").strip() or None,
        address=(r["address"] or "").strip() or None,
        gmapsRating=float((r["place-rating"] or "0").replace(",", ".") or 0) or None,
        status=(r["status"] or "").strip() or None,
    ))
for r in resto_md:
    add_place(r["place-name"], "kuliner", latlon(r["lat-long"]), dict(
        type="Restoran",
        entryFee=(r["price-per-head"] or "").strip() or None,
        hours=None,
        address=(r["address"] or "").strip() or None,
        gmapsRating=float((r["place-rating"] or "0").replace(",", ".") or 0) or None,
        status=(r["status"] or "").strip() or None,
        menu=(r["recommend-menu"] or "").strip() or None,
    ))
for r in hotel_md:
    add_place(r["place-name"], "akomodasi", latlon(r["lat-long"]), dict(
        type=(r["place-type"] or "").strip() or "Hotel",
        entryFee=(r["price-per-head"] or "").strip() or None,
        hours=None,
        address=(r["address"] or "").strip() or None,
        gmapsRating=float((r["place-rating"] or "0").replace(",", ".") or 0) or None,
        status=(r["status"] or "").strip() or None,
        facilities=(r["Fasilitas"] or "").strip() or None,
    ))
print(f"  tempat berkoordinat: {len(places)}")

# ---------------------------------------------------------------- kabupaten
def kabupaten_of(addr, name):
    a = (addr or "").lower()
    for k, lab in [("humbang", "Humbang Hasundutan"), ("samosir", "Samosir"),
                   ("simalungun", "Simalungun"), ("karo", "Karo"),
                   ("dairi", "Dairi"), ("pakpak", "Pakpak Bharat"),
                   ("tapanuli utara", "Tapanuli Utara"), ("tarutung", "Tapanuli Utara"),
                   ("toba", "Toba")]:
        if k in a:
            return lab
    return "Toba"

for p in places.values():
    p["kabupaten"] = kabupaten_of(p.get("address"), p["name"])

def kecamatan_of(addr):
    m = re.search(r"kec\.?\s*([A-Za-z ]+)", addr or "", re.I)
    return m.group(1).strip().title() if m else None

for p in places.values():
    p["kecamatan"] = kecamatan_of(p.get("address"))

# ---------------------------------------------------------------- review
print("→ memproses review…")
all_reviews = []
for r in wisata_rv:
    all_reviews.append((r["place-name"], r.get("review-text") or "", r.get("reviewer-rating") or "",
                        r.get("published-at") or "", r.get("scraped-at-date") or ""))
for r in rh_rv:
    all_reviews.append((r["place-name"], r.get("review-text") or "", r.get("reviewer-rating") or "",
                        r.get("published-at") or "", r.get("scraped-at-date") or ""))

def to_rating(s):
    try:
        v = float(str(s).replace(",", "."))
        return v if 1 <= v <= 5 else None
    except Exception:
        return None

by_place = collections.defaultdict(list)
global_ratings = []
for pname, text, rat, pub, scr in all_reviews:
    rv = to_rating(rat)
    if rv is not None:
        global_ratings.append(rv)
    t = text.strip()
    if not t:
        continue
    by_place[norm(pname)].append(dict(
        text=re.sub(r"\s+", " ", t), rating=rv, months=months_ago(pub, scr),
    ))

GLOBAL_MEAN = sum(global_ratings) / len(global_ratings)
print(f"  review berteks: {sum(len(v) for v in by_place.values())} · rata-rata rating global: {GLOBAL_MEAN:.3f}")

# severity global per aspek  = mean(rating | aspek disebut) - mean(rating global)
sev_acc = collections.defaultdict(list)
for revs in by_place.values():
    for rv in revs:
        low = rv["text"].lower()
        for k in ASPECT_RE:
            if ASPECT_RE[k].search(low) and rv["rating"] is not None:
                sev_acc[k].append(rv["rating"])
SEVERITY = {k: round((sum(v)/len(v)) - GLOBAL_MEAN, 3) for k, v in sev_acc.items() if v}
print("  severity per aspek:", {k: SEVERITY[k] for k in sorted(SEVERITY, key=SEVERITY.get)})

# ---------------------------------------------------------------- agregasi
def clean_quote(t, maxlen=180):
    t = re.sub(r"\s+", " ", t).strip().strip('"')
    return (t[:maxlen].rsplit(" ", 1)[0] + "…") if len(t) > maxlen else t

def snippet(text, rx, width=170):
    """Potong kutipan DI SEKITAR kata kunci aspek, bukan dari awal review."""
    t = re.sub(r"\s+", " ", text).strip().strip('"')
    m = rx.search(t.lower())
    if not m:
        return clean_quote(t, width)
    if len(t) <= width:
        return t
    lead = width // 3
    start = max(0, m.start() - lead)
    end = min(len(t), start + width)
    if start > 0:
        sp = t.find(" ", start)
        start = sp + 1 if 0 <= sp < start + 15 else start
    if end < len(t):
        sp = t.rfind(" ", start, end)
        end = sp if sp > start + 40 else end
    s = t[start:end].strip()
    return ("…" if start > 0 else "") + s + ("…" if end < len(t) else "")

def pick_evidence(hits, rx, k=3):
    """Urutkan bukti: paling banyak kata kunci aspek, lalu rating terendah."""
    def hitcount(r):
        return len(rx.findall(r["text"].lower()))
    ranked = sorted(hits, key=lambda r: (-hitcount(r), r["rating"] if r["rating"] else 5, -len(r["text"])))
    return ranked[:k]

place_aspects = {}
for key, p in places.items():
    revs = by_place.get(key, [])
    n_text = len(revs)
    rows = []
    for k in ASPECT_RE:
        hits = [r for r in revs if ASPECT_RE[k].search(r["text"].lower())]
        if not hits:
            continue
        neg = [r for r in hits if r["rating"] is not None and r["rating"] <= 3]
        n_m, n_n = len(hits), len(neg)
        wl = wilson_lb(n_n, n_m)
        sev = SEVERITY.get(k, 0.0)
        mention_rate = n_m / n_text if n_text else 0.0
        contrib = round(mention_rate * wl * abs(sev), 4) if k in FRICTION_ASPECTS else 0.0
        # tren: bandingkan <=12 bulan vs >12 bulan
        recent = [r for r in neg if r["months"] is not None and r["months"] <= 12]
        older  = [r for r in neg if r["months"] is not None and r["months"] > 12]
        rc = len([r for r in hits if r["months"] is not None and r["months"] <= 12]) or 1
        oc = len([r for r in hits if r["months"] is not None and r["months"] > 12]) or 1
        rr, orr = len(recent)/rc, len(older)/oc
        trend = "naik" if rr > orr + 0.08 else ("turun" if rr < orr - 0.08 else "stabil")
        rx = ASPECT_RE[k]
        ev = pick_evidence(neg, rx, 3) if neg else pick_evidence(hits, rx, 2)
        rows.append(dict(
            aspect=k, nMention=n_m, nNegative=n_n,
            negRateRaw=round(n_n/n_m, 4), negRateWilson=wl,
            severity=sev, mentionRate=round(mention_rate, 4),
            frictionContrib=contrib, trend=trend,
            evidence=[dict(text=snippet(r["text"], rx), rating=r["rating"],
                           monthsAgo=r["months"]) for r in ev],
        ))
    rows.sort(key=lambda x: -x["frictionContrib"])
    for i, row in enumerate(rows, 1):
        row["priorityRank"] = i
    fi = round(sum(r["frictionContrib"] for r in rows), 3)
    place_aspects[key] = dict(rows=rows, frictionIndex=fi, nReviewsText=n_text)

# ---------------------------------------------------------------- infra gap
print("→ menghitung gap infrastruktur…")
food   = [(p["lat"], p["lon"], p["name"]) for p in places.values() if p["kind"] == "kuliner"]
lodge  = [(p["lat"], p["lon"], p["name"]) for p in places.values() if p["kind"] == "akomodasi"]
HALAL_HINT = re.compile(r"islam|minang|padang|muslim|halal|aceh|bakso|mie ayam|ayam penyet|soto|rahayu", re.I)
PORK_HINT  = re.compile(r"\bbabi\b|\bb2\b|\bbpk\b|saksang|panggang karo|na?niura", re.I)
halal = []
for p in places.values():
    if p["kind"] != "kuliner":
        continue
    blob = f"{p['name']} {p.get('menu') or ''}"
    if HALAL_HINT.search(blob) and not PORK_HINT.search(blob):
        halal.append((p["lat"], p["lon"], p["name"]))

def nearest(p, pool):
    if not pool:
        return None
    best = min(pool, key=lambda q: hav((p["lat"], p["lon"]), (q[0], q[1])))
    d = hav((p["lat"], p["lon"]), (best[0], best[1]))
    return dict(km=d, name=best[2])

# toilet dari 'waktu operasional destinasi'
toilet_map = {}
for r in wo:
    nm = (r.get("OBJEK / DESTINASI WISATA") or "").strip()
    if not nm:
        continue
    blob = f"{r.get('FASILITAS UMUM') or ''} {r.get('FASILITAS PENUNJANG') or ''}".lower()
    toilet_map[norm(nm)] = bool(re.search(r"toilet|sanitasi|wc|mck", blob))

def toilet_lookup(name):
    k = norm(name)
    if k in toilet_map:
        return toilet_map[k]
    for tk, tv in toilet_map.items():
        if len(tk) > 6 and (tk in k or k in tk):
            return tv
    return None

# angkutan umum dari transportasi.csv
routes = []
for r in transport:
    cities = [c.strip().lower() for c in (r.get("direction") or "").split(",") if c.strip()]
    routes.append(dict(name=(r.get("transport-name") or "").strip(),
                       cities=cities, hours=(r.get("operational-hour") or "").strip(),
                       price=(r.get("price") or "").strip()))

def transport_for(p):
    hay = f"{p.get('kecamatan') or ''} {p.get('address') or ''}".lower()
    found = []
    for rt in routes:
        for c in rt["cities"]:
            if len(c) > 4 and c in hay:
                found.append(dict(name=rt["name"], hours=rt["hours"], price=rt["price"], via=c.title()))
                break
    return found[:3]

for key, p in places.items():
    p["infraGap"] = dict(
        nearestFood=nearest(p, food),
        nearestHalalFood=nearest(p, halal),
        nearestLodging=nearest(p, lodge),
        hasToilet=toilet_lookup(p["name"]),
        publicTransport=transport_for(p),
    )

# ---------------------------------------------------------------- rakit output
print("→ merakit output…")
CONF_MIN = 20
out_places = []
for key, p in places.items():
    pa = place_aspects.get(key, dict(rows=[], frictionIndex=0.0, nReviewsText=0))
    n = pa["nReviewsText"]
    conf = "high" if n >= 60 else ("medium" if n >= CONF_MIN else ("low" if n > 0 else "none"))
    q = dict(p)
    q.pop("menu", None)
    q.update(
        frictionIndex=pa["frictionIndex"],
        frictionScore=round(pa["frictionIndex"] * 100, 1),   # skala 0–100 untuk tampilan
        nReviewsText=n,
        confidence=conf,
        aspects=pa["rows"],
        topAspects=[r["aspect"] for r in pa["rows"] if r["aspect"] in FRICTION_ASPECTS][:3],
    )
    out_places.append(q)

ranked = sorted([p for p in out_places if p["confidence"] in ("high", "medium")],
                key=lambda x: -x["frictionIndex"])
for i, p in enumerate(ranked, 1):
    p["rank"] = i
for p in out_places:
    p.setdefault("rank", None)
out_places.sort(key=lambda x: (x["rank"] is None, x["rank"] or 0))

# ---------------------------------------------------------------- peluang UMKM
print("→ menurunkan peluang UMKM…")
BUDGET = {"Toba": "Rp 500.000 – >1.000.000", "Samosir": "Rp 400.000 – >800.000",
          "Simalungun": "Rp 600.000 – >1.200.000", "Karo": "Rp 400.000 – >800.000",
          "Humbang Hasundutan": "Rp 300.000 – >500.000", "Dairi": "Rp 400.000 – >750.000",
          "Pakpak Bharat": "Rp 300.000 – >600.000", "Tapanuli Utara": "Rp 600.000 – >1.000.000"}
VISITS = {"Toba": 751225, "Samosir": 1506208, "Simalungun": 2595069, "Karo": 2305891,
          "Humbang Hasundutan": 463475, "Dairi": 719807, "Pakpak Bharat": 116321}

RULES = [
    dict(aspect="halal_muslim", icon="🍽️", title="Warung nasi & lauk halal",
         why="Kuliner unggulan kawasan berbasis babi (saksang, BPK, B2) — wisatawan muslim tidak terlayani.",
         gapField="nearestHalalFood", gapMin=2.0,
         invest="Rp 15 – 35 juta", cat="Kuliner"),
    dict(aspect="toilet_sanitasi", icon="🚻", title="Pengelolaan toilet berbayar yang layak",
         why="Keluhan toilet berbarengan dengan keluhan pungutan — wisatawan bersedia bayar bila fasilitasnya layak.",
         gapField=None, gapMin=0,
         invest="Rp 20 – 50 juta", cat="Fasilitas"),
    dict(aspect="kebersihan", icon="♻️", title="Jasa kebersihan & bank sampah wisata",
         why="Sampah adalah keluhan bervolume tertinggi di korpus dan menurunkan rating lintas destinasi.",
         gapField=None, gapMin=0,
         invest="Rp 10 – 25 juta", cat="Lingkungan"),
    dict(aspect="parkir", icon="🅿️", title="Penataan parkir resmi bertarif jelas",
         why="Parkir liar bertarif tidak jelas memicu keluhan pungutan.",
         gapField=None, gapMin=0,
         invest="Rp 8 – 20 juta", cat="Fasilitas"),
    dict(aspect="ramah_keluarga", icon="👨‍👩‍👧", title="Area bermain anak & fasilitas ramah lansia",
         why="Segmen keluarga adalah pembelanja terbesar namun fasilitasnya paling jarang disebut.",
         gapField=None, gapMin=0,
         invest="Rp 25 – 60 juta", cat="Fasilitas"),
]

opportunities = []
for p in out_places:
    if p["confidence"] not in ("high", "medium"):
        continue
    amap = {a["aspect"]: a for a in p["aspects"]}
    for rule in RULES:
        a = amap.get(rule["aspect"])
        if not a or a["nNegative"] < 3 or a["negRateWilson"] < 0.10:
            continue
        gap_km = None
        if rule["gapField"]:
            g = p["infraGap"].get(rule["gapField"])
            gap_km = g["km"] if g else None
            if gap_km is not None and gap_km < rule["gapMin"]:
                continue
        score = round(a["negRateWilson"] * a["nMention"] * (1 + (gap_km or 0) / 5), 2)
        opportunities.append(dict(
            id=f"{p['id']}--{rule['aspect']}",
            title=rule["title"], icon=rule["icon"], category=rule["cat"],
            placeId=p["id"], placeName=p["name"], kabupaten=p["kabupaten"],
            lat=p["lat"], lon=p["lon"],
            evidenceCount=a["nNegative"], mentionCount=a["nMention"],
            negRate=a["negRateWilson"], why=rule["why"],
            gapKm=gap_km,
            competitorNote=(f"Warung halal terdekat {gap_km} km" if rule["gapField"] and gap_km
                            else "Belum ada pengelola resmi"),
            marketProxy=f"{p['nReviewsText']} review berteks/korpus",
            kabupatenVisits=VISITS.get(p["kabupaten"]),
            budgetBand=BUDGET.get(p["kabupaten"]),
            investEstimate=rule["invest"],
            score=score,
            evidence=[e["text"] for e in a["evidence"][:2]],
            aspect=rule["aspect"],
            aspectLabel=ASPECT_META[rule["aspect"]]["label"],
        ))
opportunities.sort(key=lambda x: -x["score"])
for i, o in enumerate(opportunities, 1):
    o["rank"] = i
opportunities = opportunities[:40]

# ---------------------------------------------------------------- leksikon analyzer
lexicon = {
    k: dict(label=ASPECT_META[k]["label"], icon=ASPECT_META[k]["icon"],
            pattern=p, severity=SEVERITY.get(k, 0.0),
            isFriction=(k in FRICTION_ASPECTS))
    for k, _, _, p in ASPECTS
}

samples = [
    "Tempatnya bagus tapi kamar mandinya udah pakai air danau minta bayar lagi, terus parkirnya 10 ribu padahal di luar.",
    "Pantainya bersih, pemandangan indah sekali, anak-anak puas main air. Cuma warung makannya monoton.",
    "Harga tiket naik 10x lipat dari sebelumnya, tidak ada perubahan apa pun di dalam lokasi wisata.",
    "Tidak ada yang jual warung makanan nasi dan lauk, semua jualan cuma kopi dan gorengan, warung muslim pun tidak jualan.",
    "Toilet airnya mati, sayang sekali padahal tempatnya bagus dan pemandangannya luar biasa.",
]

kabupaten_stats = [
    dict(name="Simalungun", visits=2595069, intl=0,  duration=None,   budget=BUDGET["Simalungun"]),
    dict(name="Karo",       visits=2305891, intl=0,  duration=None,   budget=BUDGET["Karo"]),
    dict(name="Samosir",    visits=1506208, intl=0,  duration=None,   budget=BUDGET["Samosir"]),
    dict(name="Toba",       visits=751225,  intl=379, duration=1.31,  budget=BUDGET["Toba"]),
    dict(name="Dairi",      visits=719807,  intl=0,  duration=None,   budget=BUDGET["Dairi"]),
    dict(name="Humbang Hasundutan", visits=463475, intl=0, duration=None, budget=BUDGET["Humbang Hasundutan"]),
    dict(name="Pakpak Bharat", visits=116321, intl=0, duration=None, budget=BUDGET["Pakpak Bharat"]),
]

corpus = dict(
    totalReviews=len(all_reviews),
    reviewsWithText=sum(len(v) for v in by_place.values()),
    placesGeocoded=len(places),
    globalMeanRating=round(GLOBAL_MEAN, 3),
    ratingDistribution=dict(collections.Counter(
        int(to_rating(r[2])) for r in all_reviews if to_rating(r[2]) is not None)),
    severity=SEVERITY,
    aspects=[ASPECT_META[k] for k, _, _, _ in ASPECTS],
    kabupaten=kabupaten_stats,
    generatedFrom="Dataset HackathonTourism - IT DEL.xlsx (15 file)",
    method="Baseline keyword + rating (pengganti sementara output IndoBERT)",
    maxFrictionScore=0.0,   # diisi di bawah
)

corpus["maxFrictionScore"] = max((p["frictionScore"] for p in out_places), default=0.0)
corpus["rankedCount"] = len(ranked)

def dump(name, obj):
    p = os.path.join(OUT, name)
    json.dump(obj, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  ✓ {name}  ({os.path.getsize(p)/1024:.0f} KB)")

dump("places.json", out_places)
dump("opportunities.json", opportunities)
dump("corpus.json", corpus)
dump("lexicon.json", dict(aspects=lexicon, samples=samples))

print(f"\n=== RINGKASAN ===")
print(f"tempat            : {len(out_places)}  (ranked: {len(ranked)})")
print(f"peluang UMKM      : {len(opportunities)}")
print(f"friksi tertinggi  :")
for p in ranked[:12]:
    tops = ", ".join(p["topAspects"][:3])
    print(f"  {p['rank']:2d}. {p['name'][:42]:44s} FI={p['frictionIndex']:.3f}  n={p['nReviewsText']:4d}  [{tops}]")
