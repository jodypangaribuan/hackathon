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

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ANNOTATION_DIR = Path(
    os.environ.get("ANNOTATION_DIR", str(Path(__file__).resolve().parents[2] / "ml" / "data" / "annotations"))
).resolve()
STATE_DIR = Path(__file__).parent / "data"
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR = Path(__file__).parent / "static"

ANNOTATORS = ["A1", "A2", "A3"]
PHASES = ["pilot", "main"]

ASPECTS = [
    "cleanliness", "waste", "sanitation", "crowding", "access", "parking",
    "public_facilities", "scenery", "comfort", "safety", "price_transparency",
    "staff_service", "maintenance", "opening_hours",
]
POLARITIES = ["positive", "negative", "neutral"]
SEVERITIES = ["low", "medium", "high"]

app = FastAPI(title="SIPATURE Annotator", version="1.0.0")


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


def load_state(annotator_id: str) -> Dict[str, dict]:
    path = STATE_DIR / f"{annotator_id}.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_state(annotator_id: str, state: Dict[str, dict]) -> None:
    (STATE_DIR / f"{annotator_id}.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


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
    return {"annotators": ANNOTATORS, "aspects": ASPECTS, "polarities": POLARITIES, "severities": SEVERITIES}


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
