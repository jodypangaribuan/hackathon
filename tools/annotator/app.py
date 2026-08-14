"""SIPATURE annotator — web tool anotasi gold untuk 3 anggota tim.

Membaca template anotasi (`pilot_*` + `main_*` JSONL) dari `ml/data/annotations/`,
menyajikannya per annotator, menyimpan progres ke `data/<annotator>.json`, dan
mengekspor JSONL yang siap untuk `sipature-ml annotation-agreement` / `freeze-gold`.

Jalankan:
    cd tools/annotator
    pip install -r requirements.txt
    uvicorn app:app --host 0.0.0.0 --port 8001
"""

from __future__ import annotations

import base64
import json
import os
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ANNOTATION_DIR = Path(
    os.environ.get("ANNOTATION_DIR", str(Path(__file__).resolve().parents[2] / "ml" / "data" / "annotations"))
).resolve()
STATE_DIR = Path(os.environ.get("STATE_DIR", str(Path(__file__).parent / "data"))).resolve()
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR = Path(__file__).parent / "static"

AUTH_USERNAME = os.environ.get("ANNOTATOR_USERNAME", "")
AUTH_PASSWORD = os.environ.get("ANNOTATOR_PASSWORD", "")

ANNOTATORS = ["A1", "A2", "A3"]
PHASES = ["pilot", "main"]

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

app = FastAPI(title="SIPATURE Annotator", version="1.0.0")


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


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


def load_template(annotator_id: str) -> List[dict]:
    records: List[dict] = []
    for phase in PHASES:
        path = ANNOTATION_DIR / f"{phase}_{annotator_id}_annotations.jsonl"
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    return records


_TEMPLATE_CACHE: Dict[str, List[dict]] = {}


def get_template(annotator_id: str) -> List[dict]:
    if annotator_id not in _TEMPLATE_CACHE:
        _TEMPLATE_CACHE[annotator_id] = load_template(annotator_id)
    return _TEMPLATE_CACHE[annotator_id]


def load_state(annotator_id: str) -> Dict[str, dict]:
    path = STATE_DIR / f"{annotator_id}.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_state(annotator_id: str, state: Dict[str, dict]) -> None:
    path = STATE_DIR / f"{annotator_id}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(tmp, path)  # atomic: mencegah korupsi bila crash di tengah tulis


class LabelIn(BaseModel):
    aspect: str
    polarity: str
    severity: Optional[str] = None
    evidence_text: str = ""


class SaveIn(BaseModel):
    labels: List[LabelIn] = Field(default_factory=list)
    status: str = "pending"


def validate_labels(labels: List[LabelIn]) -> None:
    for label in labels:
        if label.aspect not in ASPECTS:
            raise HTTPException(400, f"Unknown aspect: {label.aspect}")
        if label.polarity not in POLARITIES:
            raise HTTPException(400, f"Unknown polarity: {label.polarity}")
        if label.polarity == "negative" and label.severity not in SEVERITIES:
            raise HTTPException(400, "Negative label requires severity")
        if label.polarity != "negative" and label.severity is not None:
            raise HTTPException(400, "Non-negative label must have null severity")


@app.get("/api/annotators")
def annotators() -> Dict[str, Any]:
    return {
        "annotators": ANNOTATORS,
        "aspects": [{"key": k, **ASPECT_META[k]} for k in ASPECTS],
        "polarities": [{"key": p, "desc": POLARITY_META[p]} for p in POLARITIES],
        "severities": [{"key": s, "desc": SEVERITY_META[s]} for s in SEVERITIES],
    }


@app.get("/api/annotator/{annotator_id}/reviews")
def reviews(annotator_id: str) -> Dict[str, Any]:
    if annotator_id not in ANNOTATORS:
        raise HTTPException(404, "Unknown annotator")
    records = load_template(annotator_id)
    state = load_state(annotator_id)
    items: List[dict] = []
    for record in records:
        review_id = record["review_id"]
        entry = state.get(review_id, {})
        items.append(
            {
                "review_id": review_id,
                "destination_id": record.get("destination_id"),
                "text": record.get("text", ""),
                "rating_context": record.get("rating_context"),
                "labels": entry.get("labels", []),
                "status": entry.get("status", "pending"),
            }
        )
    done = sum(1 for item in items if item["status"] == "completed")
    return {
        "annotator_id": annotator_id,
        "total": len(items),
        "done": done,
        "reviews": items,
    }


@app.get("/api/progress")
def progress() -> Dict[str, Any]:
    result = {}
    for aid in ANNOTATORS:
        records = get_template(aid)
        state = load_state(aid)
        done = sum(
            1 for r in records if state.get(r["review_id"], {}).get("status") == "completed"
        )
        result[aid] = {"done": done, "total": len(records)}
    return result


@app.post("/api/annotator/{annotator_id}/reviews/{review_id}")
def save_review(annotator_id: str, review_id: str, payload: SaveIn) -> Dict[str, Any]:
    if annotator_id not in ANNOTATORS:
        raise HTTPException(404, "Unknown annotator")
    validate_labels(payload.labels)
    state = load_state(annotator_id)
    state[review_id] = {
        "labels": [label.model_dump() for label in payload.labels],
        "status": payload.status,
    }
    save_state(annotator_id, state)
    return {"ok": True}


@app.get("/api/annotator/{annotator_id}/export")
def export(annotator_id: str) -> FileResponse:
    if annotator_id not in ANNOTATORS:
        raise HTTPException(404, "Unknown annotator")
    records = load_template(annotator_id)
    state = load_state(annotator_id)
    output_path = STATE_DIR / f"{annotator_id}_completed.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            review_id = record["review_id"]
            entry = state.get(review_id, {})
            handle.write(
                json.dumps(
                    {
                        **record,
                        "labels": entry.get("labels", []),
                        "annotation_status": entry.get("status", "pending"),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )
    return FileResponse(output_path, filename=f"{annotator_id}_completed.jsonl")


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
