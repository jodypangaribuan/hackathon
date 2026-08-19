"""SIPATURE adjudicator — web tool untuk adjudikasi label gold yang berselisih.

Membaca `adjudication_queue.json` (review berselisih + label tiap annotator)
dan `adjudicated_auto.jsonl` (hasil majority-vote 2/3) dari folder gold, lalu
menyajikan satu per satu agar adjudicator memilih/menyunting label final.

Progress disimpan ke `data/adjudicator.json` (server-side, atomic). Export
menggabungkan hasil auto + manual menjadi `adjudicated.jsonl` yang siap untuk
`sipature-ml freeze-gold`.

Jalankan:
    cd tools/adjudicator
    pip install -r requirements.txt
    uvicorn app:app --host 0.0.0.0 --port 8002
"""

from __future__ import annotations

import base64
import json
import os
import secrets
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

_GOLD_DIR = os.environ.get("GOLD_DIR")
if _GOLD_DIR:
    GOLD_DIR = Path(_GOLD_DIR).resolve()
else:
    base = Path(__file__).resolve().parent
    GOLD_DIR = None
    for parent in base.parents:
        candidate = parent / "ml" / "data" / "annotations" / "gold"
        if candidate.is_dir():
            GOLD_DIR = candidate.resolve()
            break
    if GOLD_DIR is None:
        GOLD_DIR = (base / "gold").resolve()

STATE_DIR = Path(os.environ.get("STATE_DIR", str(Path(__file__).parent / "data"))).resolve()
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR = Path(__file__).parent / "static"

QUEUE_PATH = Path(os.environ.get("ADJUDICATION_QUEUE", str(GOLD_DIR / "adjudication_queue.json")))
AUTO_PATH = Path(os.environ.get("ADJUDICATED_AUTO", str(GOLD_DIR / "adjudicated_auto.jsonl")))
OUTPUT_PATH = Path(os.environ.get("ADJUDICATED_OUTPUT", str(GOLD_DIR / "adjudicated.jsonl")))

SEED_DIR = Path(__file__).parent / "seed"


def seed_gold() -> None:
    """Salin queue + auto-adjudikasi bawaan ke GOLD_DIR setiap startup.

    Queue dan auto adalah input statis (bukan state pengguna), jadi selalu
    ditimpa agar seed terbaru dari image terpakai. Progress pengguna tersimpan
    terpisah di STATE_DIR.
    """
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    if not SEED_DIR.is_dir():
        return
    for name in ("adjudication_queue.json", "adjudicated_auto.jsonl"):
        src = SEED_DIR / name
        target = GOLD_DIR / name
        if src.is_file():
            shutil.copy2(src, target)


seed_gold()

AUTH_USERNAME = os.environ.get("ADJUDICATOR_USERNAME", "")
AUTH_PASSWORD = os.environ.get("ADJUDICATOR_PASSWORD", "")

ASPECTS = [
    "cleanliness", "waste", "sanitation", "crowding", "access", "parking",
    "public_facilities", "scenery", "comfort", "safety", "price_transparency",
    "staff_service", "maintenance", "opening_hours",
]
POLARITIES = ["positive", "negative", "neutral"]
SEVERITIES = ["low", "medium", "high"]

ASPECT_META = {
    "cleanliness": {"label": "Kebersihan", "definition": "Kebersihan umum area, permukaan, kamar, meja, atau lingkungan layanan.", "hint": "bersih, kotor, jorok, kumuh, bau, serangga"},
    "waste": {"label": "Sampah & Limbah", "definition": "Sampah, limbah, plastik, atau pengelolaan/pembuangan sampah.", "hint": "sampah, limbah, plastik, berserakan, tempat sampah"},
    "sanitation": {"label": "Toilet & Sanitasi", "definition": "Toilet, WC, kamar mandi, MCK, air bersih, drainase, atau kondisi sanitasi.", "hint": "toilet, wc, kamar mandi, mck, air mati, air bersih"},
    "crowding": {"label": "Kepadatan & Antrean", "definition": "Kepadatan, antrean, atau keramaian yang memengaruhi pengalaman/operasi.", "hint": "ramai, padat, penuh sesak, antre, antri"},
    "access": {"label": "Akses & Kondisi Rute", "definition": "Jalan, rute, akses transportasi, medan, penunjuk arah, atau kemudahan mencapai lokasi.", "hint": "akses, jalan, rusak, berlubang, terjal, berbatu"},
    "parking": {"label": "Parkir", "definition": "Ketersediaan, kapasitas, keamanan, biaya, atau pengelolaan parkir.", "hint": "parkir, parkiran, lahan parkir"},
    "public_facilities": {"label": "Fasilitas Publik & Aksesibilitas", "definition": "Fasilitas publik selain sanitasi/parkir: tempat duduk, gazebo, penerangan, aksesibilitas, tempat ibadah.", "hint": "fasilitas, gazebo, kursi, penerangan, mushola, difabel"},
    "scenery": {"label": "Pemandangan", "definition": "Pemandangan, panorama, keindahan alam/visual, sunrise, atau sunset.", "hint": "pemandangan, panorama, view, indah, sunrise, sunset"},
    "comfort": {"label": "Kenyamanan", "definition": "Kenyamanan fisik/atmosfer yang tidak lebih spesifik pada fasilitas, crowding, atau safety.", "hint": "nyaman, panas, sejuk, bising, tenang"},
    "safety": {"label": "Keselamatan & Keamanan", "definition": "Risiko cedera, kriminalitas, ancaman, kondisi berbahaya, atau rasa aman.", "hint": "aman, bahaya, rawan, licin, preman, maling"},
    "price_transparency": {"label": "Harga & Transparansi Pungutan", "definition": "Kejelasan/kewajaran relatif biaya, tiket, pungutan, perubahan harga.", "hint": "harga, tarif, tiket, pungli, pungutan, mahal"},
    "staff_service": {"label": "Pelayanan Petugas", "definition": "Sikap, respons, komunikasi, kecepatan, atau profesionalitas staf/petugas/pengelola.", "hint": "pelayanan, petugas, staf, ramah, kasar, lambat"},
    "maintenance": {"label": "Perawatan & Kerusakan", "definition": "Kondisi perawatan, kerusakan, keusangan, atau fasilitas/objek terbengkalai.", "hint": "terawat, perawatan, rusak, usang, terbengkalai"},
    "opening_hours": {"label": "Jam Operasional", "definition": "Kesesuaian informasi dan realisasi jam/hari buka atau tutup.", "hint": "jam buka, jam operasional, tutup, belum buka"},
}

POLARITY_META = {
    "positive": "review memuji / menyebut kelebihan",
    "negative": "review mengeluh / menyebut masalah",
    "neutral": "menyebut aspek tanpa penilaian jelas",
}

SEVERITY_META = {
    "low": "gangguan kecil, tidak menghambat",
    "medium": "masalah nyata, mengurangi kenyamanan",
    "high": "berbahaya / menghalangi operasional",
}

app = FastAPI(title="SIPATURE Adjudicator", version="1.0.0")


@app.middleware("http")
async def basic_auth_middleware(request: Request, call_next):
    if AUTH_USERNAME and AUTH_PASSWORD and request.url.path != "/health":
        authorization = request.headers.get("Authorization", "")
        expected = "Basic " + base64.b64encode(
            f"{AUTH_USERNAME}:{AUTH_PASSWORD}".encode()
        ).decode()
        if not secrets.compare_digest(authorization, expected):
            return Response(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="SIPATURE"'},
            )
    return await call_next(request)


def load_queue() -> List[dict]:
    if not QUEUE_PATH.is_file():
        return []
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


def load_auto() -> List[dict]:
    if not AUTO_PATH.is_file():
        return []
    records: List[dict] = []
    for line in AUTO_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def load_state() -> Dict[str, dict]:
    path = STATE_DIR / "adjudicator.json"
    if not path.is_file():
        return {}
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        result: Dict[str, dict] = {}
        decoder = json.JSONDecoder()
        idx = 0
        length = len(raw)
        while idx < length:
            while idx < length and raw[idx] in " \t\r\n":
                idx += 1
            if idx >= length:
                break
            try:
                obj, end = decoder.raw_decode(raw, idx)
            except json.JSONDecodeError:
                break
            if isinstance(obj, dict):
                result.update(obj)
            idx = end
        return result


def save_state(state: Dict[str, dict]) -> None:
    path = STATE_DIR / "adjudicator.json"
    tmp = path.with_name(f"{path.name}.tmp.{secrets.token_hex(6)}")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


class LabelIn(BaseModel):
    aspect: str
    polarity: str
    severity: Optional[str] = None
    evidence_text: str = ""


class SaveIn(BaseModel):
    labels: List[LabelIn] = Field(default_factory=list)


def validate_labels(labels: List[LabelIn]) -> None:
    seen: set[str] = set()
    for label in labels:
        if label.aspect not in ASPECTS:
            raise HTTPException(400, f"Unknown aspect: {label.aspect}")
        if label.aspect in seen:
            raise HTTPException(400, f"Duplicate aspect: {label.aspect}")
        seen.add(label.aspect)
        if label.polarity not in POLARITIES:
            raise HTTPException(400, f"Unknown polarity: {label.polarity}")
        if label.polarity == "negative" and label.severity not in SEVERITIES:
            raise HTTPException(400, "Negative label requires severity")
        if label.polarity != "negative" and label.severity is not None:
            raise HTTPException(400, "Non-negative label must have null severity")


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


@app.get("/api/meta")
def meta() -> Dict[str, Any]:
    return {
        "aspects": [{"key": k, **ASPECT_META[k]} for k in ASPECTS],
        "polarities": [{"key": p, "desc": POLARITY_META[p]} for p in POLARITIES],
        "severities": [{"key": s, "desc": SEVERITY_META[s]} for s in SEVERITIES],
    }


@app.get("/api/reviews")
def reviews() -> Dict[str, Any]:
    queue = load_queue()
    state = load_state()
    items: List[dict] = []
    for item in queue:
        review_id = item["review_id"]
        entry = state.get(review_id, {})
        items.append(
            {
                "review_id": review_id,
                "destination_id": item.get("destination_id"),
                "destination_name": item.get("destination_name"),
                "destination_kind": item.get("destination_kind"),
                "destination_category": item.get("destination_category"),
                "text": item.get("text", ""),
                "rating_context": item.get("rating_context"),
                "annotators": item.get("annotators", {}),
                "labels": entry.get("labels", []),
                "status": entry.get("status", "pending"),
            }
        )
    done = sum(1 for i in items if i["status"] == "adjudicated")
    return {"total": len(items), "done": done, "reviews": items}


@app.post("/api/reviews/{review_id}")
def save_review(review_id: str, payload: SaveIn) -> Dict[str, Any]:
    queue = {item["review_id"]: item for item in load_queue()}
    if review_id not in queue:
        raise HTTPException(404, "Unknown review")
    validate_labels(payload.labels)
    text = queue[review_id]["text"]
    for label in payload.labels:
        if label.evidence_text and label.evidence_text not in text:
            raise HTTPException(400, f"Evidence bukan substring verbatim: {label.evidence_text}")
    state = load_state()
    state[review_id] = {
        "labels": [label.model_dump() for label in payload.labels],
        "status": "adjudicated",
    }
    save_state(state)
    return {"ok": True}


@app.get("/api/export")
def export() -> FileResponse:
    queue = {item["review_id"]: item for item in load_queue()}
    state = load_state()
    missing = [rid for rid in queue if state.get(rid, {}).get("status") != "adjudicated"]
    if missing:
        raise HTTPException(400, f"{len(missing)} reviews belum diadjudikasi: {missing[:5]}...")

    adjudicated: Dict[str, dict] = {}
    for rec in load_auto():
        adjudicated[rec["review_id"]] = rec
    for rid, item in queue.items():
        entry = state[rid]
        adjudicated[rid] = {
            "review_id": rid,
            "annotator_id": "ADJ",
            "destination_id": item["destination_id"],
            "text": item["text"],
            "rating_context": item.get("rating_context"),
            "labels": entry["labels"],
            "annotation_version": item.get("annotation_version", "1.0.0-rc1"),
            "annotation_status": "adjudicated",
            "review_notes": "manual adjudication",
        }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        for rid in sorted(adjudicated):
            handle.write(json.dumps(adjudicated[rid], ensure_ascii=False, sort_keys=True) + "\n")
    return FileResponse(OUTPUT_PATH, filename="adjudicated.jsonl")


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
