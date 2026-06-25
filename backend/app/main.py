from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.app.services.imagineer_system import ImagineerSystem


ROOT_DIR = Path(__file__).resolve().parents[2]
PAPER_PDF = ROOT_DIR / "imagineer-autonomous-position-system.pdf"
PAPER_TEX = ROOT_DIR / "manuscripts" / "imagineer_nature_style" / "main.tex"
PAPER_BIB = ROOT_DIR / "manuscripts" / "imagineer_nature_style" / "references.bib"
SYSTEM = ImagineerSystem()


class ImagineerEvent(BaseModel):
    kind: str = Field(default="proof", max_length=40)
    title: str | None = Field(default=None, max_length=140)
    notes: str | None = Field(default=None, max_length=4000)
    link: str | None = Field(default=None, max_length=800)
    tags: list[str] = Field(default_factory=list, max_length=12)
    impact: int = Field(default=1, ge=1, le=5)


class ProofCapture(BaseModel):
    note: str | None = Field(default=None, max_length=4000)
    measurement: str | None = Field(default=None, max_length=1200)
    changed: str | None = Field(default=None, max_length=280)
    failure: str | None = Field(default=None, max_length=1200)
    next_update: str | None = Field(default=None, max_length=1200)
    link: str | None = Field(default=None, max_length=800)
    artifact_name: str | None = Field(default=None, max_length=180)
    artifact_type: str | None = Field(default=None, max_length=80)
    artifact_mime: str | None = Field(default=None, max_length=120)
    artifact_data: str | None = Field(default=None, max_length=18_000_000)


def _cors_origins() -> list[str]:
    defaults = [
        "https://aolabs.io",
        "https://www.aolabs.io",
        "https://imagineer.aolabs.io",
        "https://www.imagineer.aolabs.io",
        "https://nalalalan.github.io",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    configured = [
        origin.strip()
        for origin in os.getenv("IMAGINEER_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]
    merged: list[str] = []
    for origin in configured + defaults:
        if origin not in merged:
            merged.append(origin)
    return merged


app = FastAPI(title="ao-imagineer-position-system")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ao-imagineer-position-system"}


@app.get("/api/imagineer/ops-check")
def ops_check() -> dict[str, Any]:
    return SYSTEM.ops_check()


@app.get("/api/imagineer/research-journal")
def research_journal() -> dict[str, Any]:
    return SYSTEM.research_journal()


@app.get("/api/imagineer/paper-outline")
def paper_outline() -> dict[str, Any]:
    return SYSTEM.paper_outline()


@app.get("/api/imagineer/weekly-paper")
def weekly_paper() -> dict[str, Any]:
    return SYSTEM.weekly_paper()


@app.post("/api/imagineer/weekly-paper/run")
def weekly_paper_run() -> dict[str, Any]:
    return SYSTEM.run_weekly_paper_update()


@app.get("/api/imagineer/ai-review")
def ai_review() -> dict[str, Any]:
    return SYSTEM.reviewer_report()


@app.post("/api/imagineer/ai-review/run")
def ai_review_run() -> dict[str, Any]:
    return SYSTEM.run_ai_review()


@app.post("/api/imagineer/events")
def record_event(event: ImagineerEvent) -> dict[str, Any]:
    return SYSTEM.record_event(event.model_dump())


@app.post("/api/imagineer/proofs")
def record_proof(proof: ProofCapture) -> dict[str, Any]:
    try:
        return SYSTEM.record_proof_capture(proof.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/imagineer/proofs/{filename}")
def proof_artifact(filename: str) -> FileResponse:
    path = SYSTEM.proof_artifact_path(filename)
    if path is None:
        raise HTTPException(status_code=404, detail="proof artifact not found")
    return FileResponse(path)


@app.post("/api/imagineer/lead-check/run")
def lead_check_run() -> dict[str, Any]:
    return SYSTEM.run_lead_check()


@app.post("/api/imagineer/daily-cycle")
def daily_cycle() -> dict[str, Any]:
    return SYSTEM.run_daily_cycle()


@app.get("/")
def index() -> FileResponse:
    index_path = ROOT_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)


def _paper_file_response(path: Path, *, media_type: str, filename: str | None = None) -> FileResponse:
    if not path.exists():
        raise HTTPException(status_code=404, detail="paper file not found")
    return FileResponse(path, media_type=media_type, filename=filename)


@app.get("/paper")
def paper_index() -> FileResponse:
    paper_path = ROOT_DIR / "paper.html"
    if not paper_path.exists():
        raise HTTPException(status_code=404, detail="paper.html not found")
    return FileResponse(paper_path)


@app.get("/paper/")
def paper_index_slash() -> FileResponse:
    return paper_index()


@app.get("/paper.pdf")
def paper_pdf() -> FileResponse:
    return _paper_file_response(
        PAPER_PDF,
        media_type="application/pdf",
        filename="An autonomous career system for embodied creative research and development.pdf",
    )


@app.get("/paper/source.tex")
def paper_tex() -> FileResponse:
    return _paper_file_response(PAPER_TEX, media_type="text/plain; charset=utf-8")


@app.get("/paper/references.bib")
def paper_bib() -> FileResponse:
    return _paper_file_response(PAPER_BIB, media_type="text/plain; charset=utf-8")


@app.get("/{asset_path:path}")
def static_asset(asset_path: str) -> FileResponse:
    allowed_suffixes = {".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".ico", ".webmanifest", ".html", ".pdf"}
    path = (ROOT_DIR / asset_path).resolve()
    if ROOT_DIR not in path.parents and path != ROOT_DIR:
        raise HTTPException(status_code=404, detail="not found")
    if path.exists() and path.is_file() and path.suffix.lower() in allowed_suffixes:
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="not found")
