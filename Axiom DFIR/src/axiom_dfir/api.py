"""AXIOM DFIR - Production FastAPI REST API Server.

Comprehensive OpenAPI-compliant REST API serving the React/Vite/TypeScript frontend
and external forensic integration pipelines.

Endpoints:
  - /api/health
  - /api/config
  - /api/cases
  - /api/cases/{case_id}
  - /api/cases/{case_id}/evidence
  - /api/cases/{case_id}/investigate/start
  - /api/cases/{case_id}/investigate/step
  - /api/cases/{case_id}/hypotheses
  - /api/cases/{case_id}/findings
  - /api/cases/{case_id}/findings/{finding_id}
  - /api/cases/{case_id}/atomic_claims
  - /api/cases/{case_id}/graph
  - /api/cases/{case_id}/timeline
  - /api/cases/{case_id}/custody
  - /api/cases/{case_id}/reports/{fmt}
  - /api/models/observatory
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from axiom_dfir.atomic_claims import AtomicClaim, AtomicClaimValidator
from axiom_dfir.cas import ContentAddressedStorage
from axiom_dfir.chain_of_custody import ChainOfCustodyLedger
from axiom_dfir.hypothesis import Hypothesis, HypothesisStatus, InvestigationLedger
from axiom_dfir.nebius import GLOBAL_METRICS, NebiusClient, NebiusModelRouter
from axiom_dfir.orchestrator import AxiomOrchestrator, InvestigationStage, STAGE_ORDER
from axiom_dfir.reporting import generate_full_report
from axiom_dfir.validation import ValidationStatus

logger = logging.getLogger("axiom_dfir.api")

app = FastAPI(
    title="AXIOM DFIR API",
    description="Autonomous Evidence-Verified Digital Forensics & Incident Response Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Case Registry ──────────────────────────────────────────────────────
CASE_REGISTRY: Dict[str, AxiomOrchestrator] = {}
DATA_ROOT = Path(os.environ.get("AXIOM_DATA_DIR") or Path(os.environ.get("TEMP", "/tmp")) / "axiom-dfir").resolve()
DATA_ROOT.mkdir(parents=True, exist_ok=True)


def get_or_create_orchestrator(case_id: str, evidence_path: Optional[str] = None) -> AxiomOrchestrator:
    if case_id in CASE_REGISTRY:
        return CASE_REGISTRY[case_id]

    case_state_dir = DATA_ROOT / case_id
    case_state_dir.mkdir(parents=True, exist_ok=True)

    fallback_ev = Path(__file__).resolve().parent.parent.parent / "yara_rules"
    if not fallback_ev.is_dir():
        fallback_ev = Path(__file__).resolve().parent.parent.parent / "Axiom DFIR" / "yara_rules"

    ev_path = evidence_path or (str(fallback_ev) if fallback_ev.is_dir() else str(case_state_dir / "evidence"))
    orch = AxiomOrchestrator(
        case_id=case_id,
        evidence_path=ev_path,
        state_dir=case_state_dir,
    )
    CASE_REGISTRY[case_id] = orch
    return orch


# Initialize default demonstration case on startup
DEFAULT_CASE_ID = "CASE-DEMO-2026"
default_orch = get_or_create_orchestrator(DEFAULT_CASE_ID)
if not os.environ.get("NEBIUS_API_KEY"):
    os.environ["AXIOM_MOCK_NEBIUS"] = "1"
# Pre-run stages for demo so rich forensic state is immediately ready
try:
    default_orch.execute_all_stages()
except Exception as exc:
    logger.warning("Default demo case startup: %s", exc)


# ── Pydantic Request & Response Schemas ────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "HEALTHY"
    product: str = "AXIOM DFIR"
    version: str = "2.0.0"
    uptime_seconds: float
    timestamp: str


class ConfigResponse(BaseModel):
    environment: str
    demo_mode: bool
    nebius_configured: bool
    nebius_endpoint: str
    fast_model: str
    balanced_model: str
    deep_model: str


class CreateCaseRequest(BaseModel):
    case_id: str = Field(..., description="Unique identifier for the case")
    evidence_path: str = Field(..., description="Local path to evidence files or disk image")
    description: Optional[str] = Field(default="", description="Case notes or incident summary")


class CaseSummary(BaseModel):
    case_id: str
    status: str
    current_stage: str
    integrity_status: str
    evidence_items_count: int
    verified_findings_count: int
    total_findings_count: int
    updated_at: str


class EvidenceItemSchema(BaseModel):
    evidence_id: str
    original_filename: str
    artifact_type: str
    sha256_hash: str
    size_bytes: int
    is_read_only: bool
    provenance: str


class HypothesisSchema(BaseModel):
    hypothesis_id: str
    title: str
    description: str
    entities: List[str]
    confidence_score: float
    status: str
    resolution_reason: Optional[str] = None
    supporting_count: int
    contradicting_count: int


class FindingDetailSchema(BaseModel):
    finding_id: str
    title: str
    validation_status: str
    confidence: float
    checks: List[Dict[str, Any]]
    corroborating_evidence_refs: List[str]
    contradicting_evidence_refs: List[str]
    rejection_reason: Optional[str] = None


class ModelObservatoryResponse(BaseModel):
    nebius_configured: bool
    status_label: str
    base_url: str
    models: Dict[str, str]
    metrics: Dict[str, Any]
    routing_decisions: List[Dict[str, Any]]


_START_TIME = time.time()


# ── API Routes ────────────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def get_health() -> HealthResponse:
    return HealthResponse(
        uptime_seconds=round(time.time() - _START_TIME, 2),
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )


@app.get("/api/config", response_model=ConfigResponse, tags=["System"])
def get_config() -> ConfigResponse:
    router = NebiusModelRouter()
    has_key = bool(os.environ.get("NEBIUS_API_KEY", "").strip())
    return ConfigResponse(
        environment=os.environ.get("AXIOM_ENV", "production"),
        demo_mode=os.environ.get("AXIOM_DEMO_MODE", "true").lower() == "true",
        nebius_configured=has_key,
        nebius_endpoint=os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"),
        fast_model=router.fast_model,
        balanced_model=router.balanced_model,
        deep_model=router.deep_model,
    )


@app.get("/api/models/observatory", response_model=ModelObservatoryResponse, tags=["Model Observatory"])
def get_model_observatory() -> ModelObservatoryResponse:
    router = NebiusModelRouter()
    has_key = bool(os.environ.get("NEBIUS_API_KEY", "").strip())
    summary = GLOBAL_METRICS.summary()

    return ModelObservatoryResponse(
        nebius_configured=has_key,
        status_label="ACTIVE (LIVE INFERENCE)" if has_key else "NOT CONFIGURED (SYNTHETIC REASONING ONLY)",
        base_url=os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"),
        models={
            "FAST": router.fast_model,
            "BALANCED": router.balanced_model,
            "DEEP": router.deep_model,
        },
        metrics=summary,
        routing_decisions=GLOBAL_METRICS.routing_decisions,
    )


@app.get("/api/cases", response_model=List[CaseSummary], tags=["Case Management"])
def list_cases() -> List[CaseSummary]:
    summaries = []
    for cid, orch in CASE_REGISTRY.items():
        ctx = orch.context
        manifest = ctx.manifest or {}
        items = manifest.get("items", [])
        v_count = sum(1 for f in ctx.validated_findings if f.get("validation_status") == "VERIFIED")

        summaries.append(
            CaseSummary(
                case_id=cid,
                status=ctx.status,
                current_stage=ctx.current_stage.value,
                integrity_status=ctx.integrity_status,
                evidence_items_count=len(items),
                verified_findings_count=v_count,
                total_findings_count=len(ctx.validated_findings),
                updated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )
        )
    return summaries


@app.post("/api/cases", response_model=CaseSummary, status_code=status.HTTP_201_CREATED, tags=["Case Management"])
def create_case(req: CreateCaseRequest) -> CaseSummary:
    if req.case_id in CASE_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Case ID '{req.case_id}' already exists")

    orch = get_or_create_orchestrator(req.case_id, req.evidence_path)
    ctx = orch.context
    return CaseSummary(
        case_id=req.case_id,
        status=ctx.status,
        current_stage=ctx.current_stage.value,
        integrity_status=ctx.integrity_status,
        evidence_items_count=0,
        verified_findings_count=0,
        total_findings_count=0,
        updated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )


@app.get("/api/cases/{case_id}", tags=["Case Management"])
def get_case(case_id: str) -> Dict[str, Any]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    return CASE_REGISTRY[case_id].context.to_dict()


@app.get("/api/cases/{case_id}/evidence", tags=["Evidence"])
def get_case_evidence(case_id: str) -> Dict[str, Any]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    ctx = CASE_REGISTRY[case_id].context
    return ctx.manifest or {"items": [], "total_bytes": 0, "item_count": 0}


@app.post("/api/cases/{case_id}/investigate/start", tags=["Investigation"])
def start_investigation(case_id: str) -> Dict[str, Any]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    orch = CASE_REGISTRY[case_id]
    success = orch.execute_all_stages()
    return {"case_id": case_id, "success": success, "status": orch.context.status, "current_stage": orch.context.current_stage.value}


@app.post("/api/cases/{case_id}/investigate/step", tags=["Investigation"])
def step_investigation(case_id: str) -> Dict[str, Any]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    orch = CASE_REGISTRY[case_id]
    curr = orch.context.current_stage
    idx = STAGE_ORDER.index(curr) if curr in STAGE_ORDER else -1

    if idx < len(STAGE_ORDER) - 1:
        next_stage = STAGE_ORDER[idx + 1]
        success = orch.run_stage(next_stage)
        return {"advanced_to": next_stage.value, "success": success}
    return {"message": "Investigation already at terminal stage", "stage": curr.value}


@app.get("/api/cases/{case_id}/hypotheses", tags=["Hypotheses"])
def get_hypotheses(case_id: str) -> List[Dict[str, Any]]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    ctx = CASE_REGISTRY[case_id].context
    return ctx.hypotheses or []


@app.get("/api/cases/{case_id}/findings", tags=["Findings"])
def get_findings(case_id: str) -> List[Dict[str, Any]]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    ctx = CASE_REGISTRY[case_id].context
    return ctx.validated_findings or []


@app.get("/api/cases/{case_id}/findings/{finding_id}", tags=["Findings"])
def get_finding_detail(case_id: str, finding_id: str) -> Dict[str, Any]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    ctx = CASE_REGISTRY[case_id].context
    for f in ctx.validated_findings:
        if f.get("finding_id") == finding_id:
            return f
    raise HTTPException(status_code=404, detail=f"Finding '{finding_id}' not found")


@app.get("/api/cases/{case_id}/atomic_claims", tags=["Findings"])
def get_atomic_claims(case_id: str) -> List[Dict[str, Any]]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    ctx = CASE_REGISTRY[case_id].context
    return ctx.atomic_claims or []


@app.get("/api/cases/{case_id}/graph", tags=["Reconstruction"])
def get_attack_graph(case_id: str) -> Dict[str, Any]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    orch = CASE_REGISTRY[case_id]
    from axiom_dfir.correlation import reconstruct_incident_from_artifacts
    graph = reconstruct_incident_from_artifacts(
        findings=orch.context.validated_findings,
        tool_records=orch.context.tool_results,
        manifest=orch.context.manifest,
    )
    return graph.to_dict()


@app.get("/api/cases/{case_id}/timeline", tags=["Reconstruction"])
def get_timeline(case_id: str) -> List[Dict[str, Any]]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    return CASE_REGISTRY[case_id].context.timeline or []


@app.get("/api/cases/{case_id}/custody", tags=["Chain of Custody"])
def get_chain_of_custody(case_id: str) -> Dict[str, Any]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    orch = CASE_REGISTRY[case_id]
    is_valid, reason = orch.chain_of_custody.verify_chain()
    d = orch.chain_of_custody.to_dict()
    d["verified"] = is_valid
    d["verification_error"] = reason
    return d


@app.get("/api/cases/{case_id}/reports/html", response_class=HTMLResponse, tags=["Reports"])
def download_html_report(case_id: str) -> HTMLResponse:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    orch = CASE_REGISTRY[case_id]
    html_path = orch.state_dir / "investigation_report.html"
    if not html_path.is_file():
        generate_full_report(orch.context, orch.state_dir)
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/api/cases/{case_id}/reports/markdown", response_class=PlainTextResponse, tags=["Reports"])
def download_markdown_report(case_id: str) -> PlainTextResponse:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    orch = CASE_REGISTRY[case_id]
    md_path = orch.state_dir / "investigation_report.md"
    if not md_path.is_file():
        generate_full_report(orch.context, orch.state_dir)
    return PlainTextResponse(content=md_path.read_text(encoding="utf-8"))


@app.get("/api/cases/{case_id}/reports/json", tags=["Reports"])
def download_json_report(case_id: str) -> Dict[str, Any]:
    if case_id not in CASE_REGISTRY:
        raise HTTPException(status_code=404, detail="Case not found")
    orch = CASE_REGISTRY[case_id]
    json_path = orch.state_dir / "investigation_report.json"
    if not json_path.is_file():
        generate_full_report(orch.context, orch.state_dir)
    import json
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Mount Built React Frontend if dist exists
candidate_dists = [
    Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist",
    Path(__file__).resolve().parent.parent.parent / "frontend" / "dist",
    Path.cwd() / "frontend" / "dist",
]
frontend_dist = next((d for d in candidate_dists if d.is_dir()), None)
if frontend_dist:
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    # Serve self-contained dashboard on root if React build is not yet produced
    @app.get("/", response_class=HTMLResponse, tags=["Web Interface"])
    def serve_dashboard():
        from axiom_dfir.web import AxiomAPIHandler
        handler = AxiomAPIHandler(None, None, None)  # type: ignore
        html = handler._serve_dashboard_html.__doc__ or "<html><body><h1>AXIOM DFIR</h1><p>Visit /docs for OpenAPI</p></body></html>"
        return HTMLResponse(content="<html><body><script>window.location.href='/docs';</script></body></html>")
