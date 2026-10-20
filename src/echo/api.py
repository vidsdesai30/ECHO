"""FastAPI application around the real ECHO core."""

from __future__ import annotations

import time
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import __version__
from .evaluation import timed_evaluation
from .ingestion import ingest_records
from .models import EventValidationError
from .persistence import database_url
from .reconstruction import ReconstructionConfig, reconstruct
from .scenarios.generator import DegradationConfig, generate_scenario


class InvestigationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)


class EventImport(BaseModel):
    events: list[dict[str, Any]] = Field(min_length=1, max_length=10000)


class ExperimentCreate(BaseModel):
    seed: int = Field(default=7, ge=0, le=2**31 - 1)
    scenario_id: str = Field(default="experiment-scenario", min_length=1, max_length=200)
    noise_count: int = Field(default=1, ge=0, le=1000)
    missing_event_rate: float = Field(default=0.0, ge=0.0, le=1.0)


class MemoryStore:
    """Explicit local fallback used only when DATABASE_URL is absent."""

    def __init__(self) -> None:
        self.investigations: dict[str, dict[str, Any]] = {}
        self.experiments: dict[str, dict[str, Any]] = {}


def create_app() -> FastAPI:
    app = FastAPI(title="ECHO API", version=__version__)
    app.state.store = MemoryStore()
    app.state.persistence_mode = "postgresql-configured-unverified" if database_url() else "memory-development-fallback"
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            origin.strip()
            for origin in os.getenv(
                "ECHO_FRONTEND_ORIGIN",
                "http://localhost:5173,http://127.0.0.1:5173",
            ).split(",")
            if origin.strip()
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "persistence": app.state.persistence_mode}

    @app.get("/api/version")
    def version() -> dict[str, str]:
        return {"version": __version__}

    @app.get("/api/investigations")
    def list_investigations() -> list[dict[str, Any]]:
        return list(app.state.store.investigations.values())

    @app.post("/api/investigations", status_code=status.HTTP_201_CREATED)
    def create_investigation(payload: InvestigationCreate) -> dict[str, Any]:
        investigation_id = f"inv-{len(app.state.store.investigations) + 1:04d}"
        result = {"id": investigation_id, "name": payload.name, "description": payload.description, "events": [], "graph": None, "created_at": datetime.now(timezone.utc).isoformat()}
        app.state.store.investigations[investigation_id] = result
        return result

    def get_investigation(investigation_id: str) -> dict[str, Any]:
        result = app.state.store.investigations.get(investigation_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Investigation not found")
        return result

    @app.get("/api/investigations/{investigation_id}")
    def investigation(investigation_id: str) -> dict[str, Any]:
        return get_investigation(investigation_id)

    @app.post("/api/investigations/{investigation_id}/events")
    def import_events(investigation_id: str, payload: EventImport) -> dict[str, Any]:
        target = get_investigation(investigation_id)
        report = ingest_records(payload.events)
        if report.invalid_records:
            raise HTTPException(status_code=422, detail=report.to_mapping())
        existing_ids = {event["event_id"] for event in target["events"]}
        new_events = [event for event in report.events if event.event_id not in existing_ids]
        target["events"].extend(event.to_mapping(include_original=True) for event in new_events)
        target["ingestion"] = report.to_mapping()
        return {
            "investigation_id": investigation_id,
            "ingestion": report.to_mapping(),
            "stored_count": len(new_events),
            "idempotent_duplicate_count": len(report.events) - len(new_events),
        }

    @app.get("/api/investigations/{investigation_id}/events")
    def events(investigation_id: str) -> list[dict[str, Any]]:
        return get_investigation(investigation_id).get("events", [])

    @app.get("/api/investigations/{investigation_id}/timeline")
    def timeline(investigation_id: str) -> list[dict[str, Any]]:
        return sorted(events(investigation_id), key=lambda event: (event["event_time"], event["event_id"]))

    @app.post("/api/investigations/{investigation_id}/reconstruct")
    def run_reconstruction(investigation_id: str) -> dict[str, Any]:
        target = get_investigation(investigation_id)
        report = ingest_records(target.get("events", []))
        if report.invalid_records:
            raise HTTPException(status_code=422, detail=report.to_mapping())
        graph = reconstruct(report.events, ReconstructionConfig())
        target["graph"] = graph.to_mapping()
        return target["graph"]

    @app.get("/api/investigations/{investigation_id}/graph")
    def graph(investigation_id: str) -> dict[str, Any]:
        target = get_investigation(investigation_id)
        return target.get("graph") or {"version": 0, "nodes": [], "edges": [], "rejected_candidates": [], "missing_evidence": []}

    @app.get("/api/investigations/{investigation_id}/relationships")
    def relationships(investigation_id: str) -> list[dict[str, Any]]:
        return graph(investigation_id).get("edges", [])

    @app.post("/api/experiments")
    def create_experiment(payload: ExperimentCreate) -> dict[str, Any]:
        experiment_id = f"exp-{len(app.state.store.experiments) + 1:04d}"
        scenario = generate_scenario(payload.seed, payload.scenario_id, DegradationConfig(missing_event_rate=payload.missing_event_rate, noise_count=payload.noise_count))
        start = time.perf_counter()
        graph_result = reconstruct(scenario.observed_events)
        metrics = timed_evaluation(graph_result, scenario.ground_truth, len(scenario.observed_events))
        metrics["runtime_seconds"] = time.perf_counter() - start
        result = {"id": experiment_id, "status": "completed", "scenario_id": payload.scenario_id, "seed": payload.seed, "configuration": payload.model_dump(), "metrics": metrics, "created_at": datetime.now(timezone.utc).isoformat()}
        app.state.store.experiments[experiment_id] = result
        return result

    @app.get("/api/experiments")
    def experiments() -> list[dict[str, Any]]:
        return list(app.state.store.experiments.values())

    @app.get("/api/experiments/{experiment_id}")
    def experiment(experiment_id: str) -> dict[str, Any]:
        result = app.state.store.experiments.get(experiment_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Experiment not found")
        return result

    @app.get("/api/experiments/{experiment_id}/results")
    def experiment_results(experiment_id: str) -> dict[str, Any]:
        return experiment(experiment_id).get("metrics", {})

    @app.post("/api/synthetic-scenarios")
    def synthetic_scenario(payload: ExperimentCreate) -> dict[str, Any]:
        scenario = generate_scenario(payload.seed, payload.scenario_id, DegradationConfig(missing_event_rate=payload.missing_event_rate, noise_count=payload.noise_count))
        return {"scenario_id": scenario.scenario_id, "seed": scenario.seed, "events": [event.to_mapping() for event in scenario.observed_events], "ground_truth_count": len(scenario.ground_truth)}

    return app


app = create_app()