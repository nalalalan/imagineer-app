from __future__ import annotations

import base64
import binascii
import copy
import html
import json
import os
import re
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


POSITIONING_LINE = (
    "Mechanical PhD + soft robotics + creative prototyping + AI-assisted tools "
    "for physical interaction systems."
)
PROFILE_UPDATED_AT = "2026-05-09T16:06:25+00:00"
DISNEY_JOB_SEARCH_URL = (
    "https://www.disneycareers.com/en/search-jobs?"
    "k=Imagineering%20mechanical&l=Glendale%2C%20CA%2C%20United%20States"
)
VERIFIED_DISNEY_JOB_URL = (
    "https://www.disneycareers.com/en/job/glendale/"
    "principal-ride-development-engineer-design-assurance/391/87268384416"
)
A3_QUEUE_SNAPSHOT_URL = "https://a3.aolabs.io/api/queue-snapshot"
EXPIRED_DISNEY_JOB_IDS = {"10146734", "93733641696"}
MAX_PROOF_UPLOAD_BYTES = 12 * 1024 * 1024
PROOF_SYNC_TARGETS = ["profile", "CV", "paper", "Progress"]
PROOF_TAGS = ["proof", "fluxcell", "mechanical_depth", "leadership_network", "paper_system", "reviewer_ready"]
PROOF_MIME_EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "application/pdf": ".pdf",
    "text/plain": ".txt",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


DEFAULT_STATE: dict[str, Any] = {
    "active_experiment_id": "autonomous-ai-reviewer-v0",
    "target": {
        "north_star_title": "Principal R&D Imagineer - Mechanical Engineer",
        "active_rung_title": "Principal Ride Development Engineer, Design Assurance",
        "company": "Walt Disney Imagineering",
        "location": "Glendale, California",
        "active_listing_job_id": "10134485",
        "active_listing_posted": "2026-06-01",
        "active_listing_url": VERIFIED_DISNEY_JOB_URL,
        "active_listing_state": "verified_live_listing",
        "active_listing_last_checked_at": "2026-06-18T16:00:32+00:00",
        "active_listing_last_status_code": 200,
        "active_listing_note": "Disney Careers destination verified live on 2026-06-18 at 12:00 PM ET: Principal Ride Development Engineer, Design Assurance, Walt Disney Imagineering, Glendale. This is a lead only; no application, outreach, referral, relationship, or hiring claim is created.",
        "north_star_note": "Use the WDI R&D principal title as the north-star profile; the active verified Disney lead is ride-development design assurance, not proof of R&D hiring fit.",
    },
    "positioning": POSITIONING_LINE,
    "profile_record": {
        "updated_at": PROFILE_UPDATED_AT,
        "scope": "whole_public_ao_labs_graph",
        "basis": (
            "AO Labs home, CV, public project surfaces, papers, dashboards, progress ledger, "
            "review state, and role-specific profile."
        ),
        "source_policy": (
            "General AO Labs work counts as profile context; role-fit credit stays bounded by "
            "direct relevance to mechanical R&D, physical interaction, prototypes, systems, and principal-scope ownership."
        ),
    },
    "guardrails": [
        "No fabricated credentials, projects, relationships, recommendations, or outcomes.",
        "No spam or fake outreach. Human approval is required before applications, direct referrals, sensitive messages, or external requests.",
        "Optimize for truthful public work: working prototypes, clear figures, test logs, concise writing, and real conversations.",
        "Respect Disney and third-party intellectual property; focus on Alan-owned public work and general role-fit signals.",
    ],
    "reviewer": {
        "mode": "autonomous_ai",
        "model": "gpt-5-mini",
        "scope": "whole_public_ao_labs_graph",
        "approval_boundary": "The system can review, score, rewrite internal surfaces, and update public AO Labs pages. Human approval is required before applications, referral asks, direct outreach, or anything person-facing.",
        "source_urls": [
            "https://aolabs.io/",
            DISNEY_JOB_SEARCH_URL,
            "https://imagineer.aolabs.io/profile.html",
            "https://imagineer.aolabs.io/imagineer-autonomous-position-system.pdf",
            "https://cv.aolabs.io",
            "https://cv.aolabs.io/alan-nguyen-pham-cv.pdf",
            "https://sarrus.aolabs.io",
            "https://sarrus.aolabs.io/mechanism.html",
            "https://sarrus.aolabs.io/paper/",
            "https://fluxcell.aolabs.io",
            "https://relay.aolabs.io",
            "https://relaylive.aolabs.io",
            "https://progress.aolabs.io",
            "https://progress.aolabs.io/api/progress/summary",
            "https://docs.google.com/document/d/1Ffi51WavVvaFBUQX37AbFQ4ZKGEkRlGl-NRcOVQP03c/export?format=txt",
            "https://www.youtube.com/@nalalan",
            "https://curtis.aolabs.io",
            "https://curtis.aolabs.io/api/curtis/media-status",
            "https://curtis.aolabs.io/api/curtis/daily-records",
            "https://curtis.aolabs.io/paper",
            "https://ocean.aolabs.io",
            "https://talk.aolabs.io",
            "https://nerve.aolabs.io",
            "https://duet.aolabs.io/hello",
            "https://violin.aolabs.io",
            "https://yum.aolabs.io",
            "https://lily.aolabs.io",
            "https://la.disneyresearch.com/researchers/",
            "https://la.disneyresearch.com/publication/design-and-control-of-a-bipedal-robotic-character/",
        ],
    },
    "identity_profile": {
        "summary": (
            "Alan Pham is a mechanical engineering PhD candidate building soft robotic materials, "
            "reconfigurable mechanisms, motion prototypes, human-facing physical systems, public project surfaces, "
            "research papers, and autonomous systems across AO Labs."
        ),
        "current_role": "Mechanical engineering PhD candidate at Worcester Polytechnic Institute; expected 2027.",
        "technical_pattern": [
            "Soft robotics, compliant mechanisms, continuum robots, modular soft robots, morphing surfaces, haptics, and human-robot interaction.",
            "First-author Sarrus work on monolithically printed pneumatic cells that reconfigure into surfaces and robot bodies.",
            "FluxCell work exploring actuator-less linkage validation before pneumatic and electropermanent actuation integration.",
            "Mechanical design experience spanning CAD, prototype fabrication, testing, dynamics, sensors, and physical systems.",
        ],
        "builder_pattern": [
            "AO Labs turns projects into public surfaces, papers, dashboards, media walls, and autonomous loops.",
            "Relay shows the user's preference for operational systems with metrics, state, experiments, logs, and money/result tracking.",
            "Imagineer should use the same operational style for career conversion: source intake, critique, state updates, and logged progress.",
        ],
        "wdi_relevance": [
            "Strongest fit is embodied creative R&D: mechanisms that produce readable physical motion, shape change, responsiveness, surprise, or believable object behavior.",
            "The gap is not motivation; the gap is source-backed public work that makes mechanical credibility and physical interaction obvious.",
        ],
    },
    "portfolio": [
        {
            "name": "Sarrus",
            "url": "https://sarrus.aolabs.io",
            "summary": "Programmable soft robotic surfaces and bodies.",
            "tags": ["soft_robotics", "physical_experience", "creative_prototyping", "mechanical_depth"],
        },
        {
            "name": "FluxCell",
            "url": "https://fluxcell.aolabs.io",
            "summary": "Current prototype path: actuator-less linkage validation before pneumatic and electropermanent actuation integration.",
            "tags": ["actuation", "mechanical_depth", "creative_prototyping", "paper_system"],
        },
        {
            "name": "Ocean",
            "url": "https://ocean.aolabs.io",
            "summary": "Creative R&D, tangible media, WDI, robotics, and technical taste map.",
            "tags": ["physical_experience", "creative_strategy", "application_packet"],
        },
        {
            "name": "CV",
            "url": "https://cv.aolabs.io/alan-nguyen-pham-cv.pdf",
            "summary": "Research, engineering, tools, prototypes, and publications.",
            "tags": ["application_packet", "mechanical_depth"],
        },
    ],
    "dimensions": [
        {
            "key": "mechanical_depth",
            "label": "Mechanical depth",
            "score": 74,
            "target_signal": "SolidWorks-level mechanism work, loads, tolerances, FEA/GD&T, machine design, and manufacturable parts.",
        },
        {
            "key": "creative_prototyping",
            "label": "Creative prototyping",
            "score": 78,
            "target_signal": "Fast physical demonstrators that explain an unfamiliar effect in less than one minute.",
        },
        {
            "key": "physical_experience",
            "label": "Human-facing motion",
            "score": 68,
            "target_signal": "Guest-facing motion: believability, surprise, touch, repeatability, safety, and readable behavior.",
        },
        {
            "key": "leadership_network",
            "label": "Principal-level network",
            "score": 34,
            "target_signal": "Real conversations, referrals, project collaborators, and visible technical leadership.",
        },
        {
            "key": "application_packet",
            "label": "Glendale profile",
            "score": 46,
            "target_signal": "Role-specific portfolio page, two-minute demo reel, CV bullets, and tailored project narrative.",
        },
        {
            "key": "paper_system",
            "label": "Autonomous career system",
            "score": 42,
            "target_signal": "A logged adaptive loop with state, experiments, outcomes, metrics, guardrails, and publishable methods.",
        },
    ],
    "experiments": [
        {
            "id": "autonomous-ai-reviewer-v0",
            "name": "Autonomous career loop v0",
            "status": "active",
            "hypothesis": (
                "Repeated source reads against live WDI R&D signals produce one system-owned update."
            ),
            "variable": "Public-source depth and critique specificity.",
            "success_metric": "One autonomous review run, one short state readout, and one system-owned profile, portfolio, or paper improvement selected from the review.",
            "started_at": "2026-05-06",
        },
        {
            "id": "wdi-profile-v0",
            "name": "WDI R&D profile v0",
            "status": "supporting",
            "hypothesis": (
                "If Alan converts existing soft-robotics work into a concise WDI R&D profile, "
                "the gap shifts from unclear fit to visible studio relevance."
            ),
            "variable": "Translation quality from technical result to physical interaction.",
            "success_metric": "Five logged updates, one public portfolio profile, and one AI critique cycle inside seven days.",
            "started_at": "2026-05-06",
        },
        {
            "id": "principal-signal-map-v0",
            "name": "Principal signal map",
            "status": "queued",
            "hypothesis": "A principal-track map exposes which missing signals matter most: leadership, autonomy, vendor work, or shop-floor depth.",
            "variable": "Gap priority order.",
            "success_metric": "A ranked 12-signal map with source links and clear system-owned status for each signal.",
            "started_at": None,
        },
        {
            "id": "nature-methods-v0",
            "name": "Adaptive career methods paper",
            "status": "queued",
            "hypothesis": "The same machinery used for autonomous revenue can become a publishable career-conversion system if sources and ethics are first-class.",
            "variable": "Outcome metric design.",
            "success_metric": "A methods outline with state schema, decision policy, intervention log, and evaluation metrics.",
            "started_at": None,
        },
    ],
    "events": [],
    "reviews": [],
    "lead_checks": [],
    "journal": [
        {
            "id": "seed-001",
            "created_at": "2026-05-06T12:00:00+00:00",
            "title": "Target locked",
            "body": "Aim the system at WDI R&D in Glendale, with the mechanical Imagineering search lane as the immediate role-shape reference and Principal R&D Imagineer as the north star.",
            "tags": ["target", "application_packet"],
        },
        {
            "id": "seed-002",
            "created_at": "2026-05-06T12:05:00+00:00",
            "title": "Positioning line",
            "body": POSITIONING_LINE,
            "tags": ["target", "physical_experience"],
        },
    ],
    "weekly_papers": [],
}


class ImagineerSystem:
    def __init__(self, state_path: str | Path | None = None) -> None:
        if state_path is None:
            configured = os.getenv("IMAGINEER_STATE_PATH", "").strip()
            state_path = configured or Path.cwd() / ".runtime" / "imagineer_state.json"
        self.state_path = Path(state_path)
        self.proof_upload_dir = self.state_path.parent / "proof_uploads"
        self._state_lock = threading.RLock()

    def ops_check(self) -> dict[str, Any]:
        state = self._load_state()
        dimensions = self._score_dimensions(state)
        weakest = min(dimensions, key=lambda item: item["score"])
        step_decision = self._step_decision(state, dimensions, weakest)
        next_action = self._next_action(state, weakest)
        personal_step = step_decision["step"]
        active_experiment = self._active_experiment(state)
        proof_events = [event for event in state["events"] if event.get("kind") == "proof"]
        outreach_events = [event for event in state["events"] if event.get("kind") == "outreach"]
        cycle_events = [event for event in state["events"] if event.get("kind") == "daily_cycle"]
        reviewer_ready_events = [event for event in state["events"] if "reviewer_ready" in event.get("tags", [])]
        reviewer_ready_portfolio = [item for item in state["portfolio"] if "reviewer_ready" in item.get("tags", [])]
        ai_reviews = state.get("reviews", [])
        fit_score = round(sum(item["score"] for item in dimensions) / max(len(dimensions), 1))
        generated_at = _utc_now()
        a3_snapshot = self._a3_queue_snapshot()
        life_loop = self._life_loop(
            state=state,
            dimensions=dimensions,
            weakest=weakest,
            step=personal_step,
            fit_score=fit_score,
            a3_snapshot=a3_snapshot,
        )
        reviewer = self._reviewer_report_from_state(state, compact=True)
        lead_verification = self._lead_verification_state(state)

        return {
            "status": "building_position_machine_v1",
            "generated_at": generated_at,
            "target": state["target"],
            "positioning": state["positioning"],
            "fit_score": fit_score,
            "confidence": self._confidence_label(fit_score),
            "current_bottleneck": weakest,
            "next_action": next_action,
            "personal_step": personal_step,
            "life_loop": life_loop,
            "proof_capture": self._proof_capture_state(state),
            "lead_verification": lead_verification,
            "decision_system": step_decision["system"],
            "reviewer": reviewer,
            "reviewer_state": reviewer.get("review_state"),
            "active_experiment": self._experiment_view(active_experiment, state),
            "dimensions": dimensions,
            "evidence": {
                "proof_events": len(proof_events),
                "outreach_events": len(outreach_events),
                "daily_cycles": len(cycle_events),
                "ai_reviews": len(ai_reviews),
                "portfolio_items": len(state["portfolio"]),
                "reviewer_ready_artifacts": len(reviewer_ready_events) + len(reviewer_ready_portfolio),
                "journal_entries": len(state["journal"]),
            },
            "portfolio": state["portfolio"],
            "journal": state["journal"][:8],
            "guardrails": state["guardrails"],
            "profile": self._profile_view(state, read_at=generated_at),
            "paper": self.paper_outline(compact=True),
            "weekly_paper": self.weekly_paper(compact=True),
            "artifacts": {
                "paper_pdf": "https://aolabs.io/imagineer/imagineer-autonomous-position-system.pdf",
                "paper_pdf_custom_domain": "https://imagineer.aolabs.io/imagineer-autonomous-position-system.pdf",
                "live_backend": "https://imagineer-app-production.up.railway.app/api/imagineer/ops-check",
            },
            "system_health": {
                "state_path": str(self.state_path),
                "proof_upload_dir": str(self.proof_upload_dir),
                "openai_planner": bool(os.getenv("OPENAI_API_KEY")),
                "openai_model": self._openai_model() if os.getenv("OPENAI_API_KEY") else None,
                "storage": "json_runtime_state",
                "write_surface": "events_proofs_lead_checks_and_ai_reviews",
            },
        }

    def research_journal(self) -> dict[str, Any]:
        state = self._load_state()
        return {
            "generated_at": _utc_now(),
            "journal": state["journal"],
            "events": state["events"][:100],
            "experiments": state["experiments"],
        }

    def weekly_paper(self, compact: bool = False) -> dict[str, Any]:
        state = self._load_state()
        current_week = self._week_id()
        paper = next(
            (item for item in state["weekly_papers"] if item.get("week_id") == current_week),
            None,
        )
        if paper is None:
            paper = self._build_weekly_paper(state, persisted=False)

        if compact:
            return {
                "week_id": paper["week_id"],
                "title": paper["title"],
                "status": paper["status"],
                "updated_at": paper["updated_at"],
                "next_update_due": paper["next_update_due"],
                "abstract": paper["sections"][0]["body"],
                "headline_result": paper["headline_result"],
            }
        return paper

    def paper_outline(self, compact: bool = False) -> dict[str, Any]:
        sections = [
            {
                "title": "Abstract",
                "claim": "An adaptive, guardrailed agent system can convert an ambiguous career target into daily source-backed interventions.",
            },
            {
                "title": "System Architecture",
                "claim": "The loop maintains target-role state, role-signal dimensions, event logs, experiments, and a policy for choosing the next action.",
            },
            {
                "title": "Decision Policy",
                "claim": "Actions are chosen by failure-cost evidence ROI: role alignment, bottleneck relief, evidence created, compounding value, urgency, friction, and approval-gate penalty.",
            },
            {
                "title": "Evaluation",
                "claim": "The system tracks logged work, public artifacts, review runs, application readiness, and conversion milestones.",
            },
            {
                "title": "Guardrails",
                "claim": "The system forbids fabrication, spam, credential inflation, and unapproved applications or sensitive outreach.",
            },
            {
                "title": "Case Study",
                "claim": "The first deployment targets WDI R&D mechanical roles using Alan-owned soft robotics, actuation, and creative prototyping work.",
            },
        ]
        if compact:
            return {
                "working_title": "Adaptive Career Systems for Embodied Creative R&D",
                "thesis": "Career progress becomes optimizable when sources, decisions, experiments, and ethics are logged as a closed-loop system.",
                "section_count": len(sections),
            }
        return {
            "working_title": "Adaptive Career Systems for Embodied Creative R&D",
            "thesis": "Career progress becomes optimizable when sources, decisions, experiments, and ethics are logged as a closed-loop system.",
            "sections": sections,
        }

    def reviewer_report(self, compact: bool = False) -> dict[str, Any]:
        state = self._load_state()
        return self._reviewer_report_from_state(state, compact=compact)

    def run_ai_review(self) -> dict[str, Any]:
        with self._state_lock:
            state = self._load_state()
            ops = self.ops_check_without_weekly(state)
            sources = self._collect_review_sources(state, ops)
            review, review_error = self._openai_review(state, ops, sources)
            review_model = self._openai_model()
            if review is None:
                review = self._fallback_review(state, ops, sources)
                review_model = "deterministic_fallback"
                review["fallback_reason"] = review_error or "openai_unavailable"

            review["id"] = str(uuid.uuid4())
            review["created_at"] = _utc_now()
            review["model"] = review_model
            review["source_count"] = len(sources)
            review["sources"] = [
                {
                    "name": source["name"],
                    "url": source.get("url", ""),
                    "status": source["status"],
                    "chars": len(source.get("text", "")),
                }
                for source in sources
            ]

            state.setdefault("reviews", []).insert(0, review)
            state["reviews"] = state["reviews"][:50]

            event = {
                "id": str(uuid.uuid4()),
                "created_at": review["created_at"],
                "date": _today(),
                "kind": "ai_review",
                "title": "AI reviewer critique generated",
                "notes": f"{review['verdict']} Top issue: {review['top_issue']}",
                "link": "https://imagineer.aolabs.io/profile.html",
                "tags": ["ai_reviewer", "paper_system", "application_packet", "mechanical_depth"],
                "impact": 2,
            }
            state["events"].insert(0, event)
            state["events"] = state["events"][:300]
            self._append_journal_from_event(state, event)
            self._touch_profile_record(state, review["created_at"], source_count=len(sources))
            self._save_state(state)
            return {"ok": True, "review": self._compact_review(review), "ops": self.ops_check()}

    def run_weekly_paper_update(self) -> dict[str, Any]:
        with self._state_lock:
            state = self._load_state()
            current_week = self._week_id()
            paper = self._build_weekly_paper(state, persisted=True)
            state["weekly_papers"] = [
                item for item in state.get("weekly_papers", []) if item.get("week_id") != current_week
            ]
            state["weekly_papers"].insert(0, paper)
            state["weekly_papers"] = state["weekly_papers"][:26]
            state["journal"].insert(
                0,
                {
                    "id": str(uuid.uuid4()),
                    "created_at": paper["updated_at"],
                    "title": "Progress paper updated",
                    "body": paper["headline_result"],
                    "tags": ["weekly_paper", "paper_system", "application_packet"],
                },
            )
            state["journal"] = state["journal"][:120]
            self._touch_profile_record(state, paper["updated_at"])
            self._save_state(state)
            return {"ok": True, "paper": paper, "ops": self.ops_check()}

    def record_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._state_lock:
            state = self._load_state()
            event = self._event_from_payload(payload)
            state["events"].insert(0, event)
            state["events"] = state["events"][:300]
            self._append_journal_from_event(state, event)
            self._touch_profile_record(state, event["created_at"])
            self._save_state(state)
            return {"ok": True, "event": event, "ops": self.ops_check()}

    def record_proof_capture(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._state_lock:
            state = self._load_state()
            artifact = self._save_proof_artifact(payload)
            proof_fields = self._proof_fields(payload)
            event_payload = {
                "kind": "proof",
                "title": "FluxCell proof captured",
                "notes": self._proof_notes(proof_fields, artifact),
                "link": artifact.get("route") if artifact else str(payload.get("link") or "").strip(),
                "tags": PROOF_TAGS,
                "impact": 4,
            }
            event = self._event_from_payload(event_payload)
            event["proof_capture"] = {
                "fields": proof_fields,
                "sync_targets": PROOF_SYNC_TARGETS,
                "sync_state": "runtime_profile_journal_updated",
            }
            if artifact:
                event["artifact"] = artifact
            state["events"].insert(0, event)
            state["events"] = state["events"][:300]
            self._append_journal_from_event(state, event)
            self._touch_profile_record(state, event["created_at"])
            self._save_state(state)
            return {
                "ok": True,
                "proof": event,
                "sync": self._proof_sync_plan(event),
                "ops": self.ops_check(),
            }

    def proof_artifact_path(self, filename: str) -> Path | None:
        clean = self._safe_filename(filename)
        if not clean or clean != filename:
            return None
        path = (self.proof_upload_dir / clean).resolve()
        try:
            path.relative_to(self.proof_upload_dir.resolve())
        except ValueError:
            return None
        if not path.exists() or not path.is_file():
            return None
        return path

    def run_lead_check(self) -> dict[str, Any]:
        with self._state_lock:
            state = self._load_state()
            result = self._check_active_listing_destination(state)
            state.setdefault("lead_checks", []).insert(0, result)
            state["lead_checks"] = state["lead_checks"][:40]
            if result.get("listing_state") in {"verified_live_listing", "unavailable_on_last_check"}:
                target = state.setdefault("target", {})
                target["active_listing_state"] = result["listing_state"]
                target["active_listing_last_checked_at"] = result["checked_at"]
                target["active_listing_last_status_code"] = result.get("status_code")
                target["active_listing_note"] = result.get("note", "")
            self._save_state(state)
            return {
                "ok": bool(result.get("ok")),
                "lead_check": result,
                "lead_verification": self._lead_verification_state(state),
                "ops": self.ops_check(),
            }

    def run_daily_cycle(self) -> dict[str, Any]:
        with self._state_lock:
            state = self._load_state()
            today = _today()
            existing = next(
                (
                    event
                    for event in state["events"]
                    if event.get("kind") == "daily_cycle" and event.get("date") == today
                ),
                None,
            )
            dimensions = self._score_dimensions(state)
            weakest = min(dimensions, key=lambda item: item["score"])
            action = self._next_action(state, weakest, allow_openai=True)

            if existing:
                return {
                    "ok": True,
                    "already_ran": True,
                    "event": existing,
                    "next_action": action,
                    "ops": self.ops_check(),
                }

            event = {
                "id": str(uuid.uuid4()),
                "created_at": _utc_now(),
                "date": today,
                "kind": "daily_cycle",
                "title": action["title"],
                "notes": action["body"],
                "link": "",
                "tags": [action["lane"], weakest["key"], "daily_cycle"],
                "impact": 1,
            }
            state["events"].insert(0, event)
            state["events"] = state["events"][:300]
            state["journal"].insert(
                0,
                {
                    "id": str(uuid.uuid4()),
                    "created_at": event["created_at"],
                    "title": "Daily cycle selected",
                    "body": f"{action['title']} {action['body']}",
                    "tags": event["tags"],
                },
            )
            state["journal"] = state["journal"][:120]
            self._touch_profile_record(state, event["created_at"])
            self._save_state(state)
            return {"ok": True, "already_ran": False, "event": event, "next_action": action, "ops": self.ops_check()}

    def _build_weekly_paper(self, state: dict[str, Any], persisted: bool) -> dict[str, Any]:
        ops = self.ops_check_without_weekly(state)
        week_id = self._week_id()
        week_start, next_update = self._week_bounds()
        recent_events = [
            event
            for event in state["events"]
            if self._event_in_current_week(event, week_start)
        ]
        active_experiment = self._experiment_view(self._active_experiment(state), state)
        weakest = ops["current_bottleneck"]
        next_action = ops["next_action"]
        headline = (
            f"Fit score is {ops['fit_score']} with {weakest['label']} as the current bottleneck; "
            f"the next intervention is: {next_action['title']}"
        )
        sections = [
            {
                "heading": "Abstract",
                "body": (
                    "This continuous paper reports the progress of an autonomous, guardrailed career-conversion system "
                    "targeting WDI R&D mechanical Imagineering roles. The system converts Alan-owned work, "
                    "daily actions, experiments, and guardrails into an adaptive decision loop."
                ),
            },
            {
                "heading": "Methods Update",
                "body": (
                    "The system scores six role-fit dimensions, then selects the next step by failure-cost evidence ROI: "
                    "role alignment, bottleneck relief, current evidence created, compounding value, urgency, friction, and approval-gate penalty. "
                    "It records logged work, runs daily cycles, and maintains a research journal. OpenAI planning is used only when configured; "
                    "otherwise the local deterministic policy chooses the next ethical action."
                ),
            },
            {
                "heading": "Current Results",
                "body": (
                    f"This week has {len(recent_events)} logged events, {ops['evidence']['proof_events']} total work logs, "
                    f"{ops['evidence']['daily_cycles']} daily cycles, {ops['evidence']['reviewer_ready_artifacts']} public artifacts, "
                    f"and {ops['evidence']['portfolio_items']} portfolio anchors. "
                    f"{headline}."
                ),
            },
            {
                "heading": "Active Experiment",
                "body": (
                    f"{active_experiment['name']}: {active_experiment['hypothesis']} "
                    f"Success metric: {active_experiment['success_metric']}"
                ),
            },
            {
                "heading": "Next Intervention",
                "body": f"{next_action['title']} {next_action['body']} Why: {next_action['why']}",
            },
            {
                "heading": "Ethics And Guardrails",
                "body": (
                    "The system forbids fabricated credentials, fake outreach, spam, and unapproved applications. "
                    "Progress must come from truthful public work, real artifacts, useful relationships, and visible technical work."
                ),
            },
        ]
        return {
            "id": str(uuid.uuid4()),
            "week_id": week_id,
            "title": "Progress Paper: Autonomous Imagineer Position System",
            "status": "published_paper_snapshot" if persisted else "live_preview_until_paper_snapshot",
            "updated_at": _utc_now(),
            "week_start": week_start.isoformat(),
            "next_update_due": next_update.isoformat(),
            "headline_result": headline,
            "target": state["target"],
            "positioning": state["positioning"],
            "metrics": ops["evidence"],
            "fit_score": ops["fit_score"],
            "current_bottleneck": weakest,
            "next_action": next_action,
            "active_experiment": active_experiment,
            "sections": sections,
        }

    def ops_check_without_weekly(self, state: dict[str, Any]) -> dict[str, Any]:
        dimensions = self._score_dimensions(state)
        weakest = min(dimensions, key=lambda item: item["score"])
        step_decision = self._step_decision(state, dimensions, weakest)
        next_action = self._next_action(state, weakest)
        personal_step = step_decision["step"]
        active_experiment = self._active_experiment(state)
        proof_events = [event for event in state["events"] if event.get("kind") == "proof"]
        outreach_events = [event for event in state["events"] if event.get("kind") == "outreach"]
        cycle_events = [event for event in state["events"] if event.get("kind") == "daily_cycle"]
        reviewer_ready_events = [event for event in state["events"] if "reviewer_ready" in event.get("tags", [])]
        reviewer_ready_portfolio = [item for item in state["portfolio"] if "reviewer_ready" in item.get("tags", [])]
        ai_reviews = state.get("reviews", [])
        fit_score = round(sum(item["score"] for item in dimensions) / max(len(dimensions), 1))
        return {
            "target": state["target"],
            "fit_score": fit_score,
            "confidence": self._confidence_label(fit_score),
            "current_bottleneck": weakest,
            "next_action": next_action,
            "personal_step": personal_step,
            "decision_system": step_decision["system"],
            "reviewer": self._reviewer_report_from_state(state, compact=True),
            "active_experiment": self._experiment_view(active_experiment, state),
            "dimensions": dimensions,
            "profile": self._profile_view(state),
            "evidence": {
                "proof_events": len(proof_events),
                "outreach_events": len(outreach_events),
                "daily_cycles": len(cycle_events),
                "ai_reviews": len(ai_reviews),
                "portfolio_items": len(state["portfolio"]),
                "reviewer_ready_artifacts": len(reviewer_ready_events) + len(reviewer_ready_portfolio),
                "journal_entries": len(state["journal"]),
            },
        }

    def _profile_view(self, state: dict[str, Any], read_at: str | None = None) -> dict[str, Any]:
        profile = state.get("profile_record") if isinstance(state.get("profile_record"), dict) else {}
        latest_review = next(iter(state.get("reviews", [])), None)
        source_count = self._profile_source_count(state)
        recorded_source_count = int(profile.get("source_count") or 0)
        latest_source_count = 0
        if isinstance(latest_review, dict):
            latest_source_count = int(latest_review.get("source_count") or 0)
        source_updated_at = self._latest_profile_timestamp(state)
        updated_at = read_at or source_updated_at
        return {
            "updated_at": updated_at,
            "read_at": read_at,
            "source_updated_at": source_updated_at,
            "latest_review_at": latest_review.get("created_at") if isinstance(latest_review, dict) else None,
            "source_count": max(source_count, latest_source_count, recorded_source_count),
            "scope": profile.get("scope") or "whole_public_ao_labs_graph",
            "basis": profile.get("basis") or DEFAULT_STATE["profile_record"]["basis"],
            "source_policy": profile.get("source_policy") or DEFAULT_STATE["profile_record"]["source_policy"],
        }

    def _profile_source_count(self, state: dict[str, Any]) -> int:
        reviewer_urls = state.get("reviewer", {}).get("source_urls", [])
        portfolio_urls = [item.get("url") for item in state.get("portfolio", []) if isinstance(item, dict) and item.get("url")]
        urls = [str(url).strip() for url in [*reviewer_urls, *portfolio_urls] if str(url).strip()]
        return len(set(urls))

    def _latest_profile_timestamp(self, state: dict[str, Any]) -> str:
        candidates = [
            state.get("profile_record", {}).get("updated_at") if isinstance(state.get("profile_record"), dict) else "",
            state.get("target", {}).get("active_listing_last_checked_at") if isinstance(state.get("target"), dict) else "",
        ]
        for collection in ("reviews", "events", "journal"):
            items = state.get(collection, [])
            if isinstance(items, list) and items:
                first = items[0]
                if isinstance(first, dict):
                    candidates.append(str(first.get("created_at") or ""))

        parsed: list[datetime] = []
        for value in candidates:
            try:
                text = str(value or "").replace("Z", "+00:00")
                item = datetime.fromisoformat(text)
            except (TypeError, ValueError):
                continue
            if item.tzinfo is None:
                item = item.replace(tzinfo=timezone.utc)
            parsed.append(item.astimezone(timezone.utc))
        if not parsed:
            return PROFILE_UPDATED_AT
        return max(parsed).isoformat()

    def _touch_profile_record(self, state: dict[str, Any], updated_at: str, *, source_count: int | None = None) -> None:
        profile = state.get("profile_record")
        if not isinstance(profile, dict):
            profile = copy.deepcopy(DEFAULT_STATE["profile_record"])
            state["profile_record"] = profile
        profile["updated_at"] = updated_at
        if source_count is not None:
            profile["source_count"] = max(int(profile.get("source_count") or 0), source_count)

    def _reviewer_report_from_state(self, state: dict[str, Any], compact: bool = False) -> dict[str, Any]:
        latest = next(iter(state.get("reviews", [])), None)
        review_state = self._review_public_state(latest)
        report = {
            "mode": state.get("reviewer", {}).get("mode", "autonomous_ai"),
            "scope": state.get("reviewer", {}).get("scope", "whole_public_ao_labs_graph"),
            "status": review_state["status"],
            "review_state": review_state,
            "approval_boundary": state.get("reviewer", {}).get("approval_boundary", ""),
            "latest": self._compact_review(latest) if latest else None,
            "review_count": len(state.get("reviews", [])),
            "source_count": self._profile_source_count(state),
        }
        if compact:
            return report
        return {
            **report,
            "reviews": [self._compact_review(review) for review in state.get("reviews", [])[:10]],
            "source_urls": state.get("reviewer", {}).get("source_urls", []),
        }

    def _compact_review(self, review: dict[str, Any] | None) -> dict[str, Any] | None:
        if not review:
            return None
        next_actions = review.get("next_actions") or []
        compact = {
            "id": review.get("id"),
            "created_at": review.get("created_at"),
            "score": review.get("score"),
            "verdict": self._review_display_text(
                review.get("verdict"),
                review.get("reviewer_summary"),
                "Credible WDI R&D direction; the public profile still needs denser mechanical validation.",
            ),
            "top_issue": self._review_display_text(
                review.get("top_issue"),
                None,
                (
                    "The current public profile still needs one mechanism-centered Sarrus or FluxCell artifact with "
                    "geometry, travel, load path, constraints, actuation margin, prototype build, test result, and iteration."
                ),
            ),
            "why_it_matters": review.get("why_it_matters"),
            "best_existing_evidence": self._string_list(review.get("best_existing_evidence"), 5, 1200),
            "evidence_gaps": self._string_list(review.get("evidence_gaps"), 6, 1200),
            "packet_edits": self._string_list(review.get("packet_edits"), 5, 1200),
            "reviewer_summary": self._review_summary_text(
                review.get("reviewer_summary"),
                review.get("why_it_matters"),
            ),
            "next_action": next_actions[0] if next_actions else None,
            "source_count": review.get("source_count"),
            "model": review.get("model"),
        }
        fallback_state = self._fallback_state(review.get("fallback_reason"))
        if fallback_state:
            compact["fallback_state"] = fallback_state
            compact["fallback_note"] = "AI review did not complete; deterministic fallback used."
        return compact

    def _review_public_state(self, latest: dict[str, Any] | None) -> dict[str, Any]:
        if not latest:
            return {
                "status": "not_run",
                "label": "Review not run",
                "action": "Run review after proof capture.",
                "last_review_at": None,
                "age_days": None,
            }
        created = self._parse_timestamp(latest.get("created_at"))
        age_days = None
        if created:
            age_days = max(0, (datetime.now(timezone.utc) - created).days)
        fallback_state = self._fallback_state(latest.get("fallback_reason"))
        stale = age_days is None or age_days > 30
        if stale and fallback_state:
            status = "stale_fallback"
            label = "Review stale; fallback used"
            action = "Capture current FluxCell proof before another review."
        elif stale:
            status = "stale"
            label = "Review stale"
            action = "Run review after the current proof changes."
        elif fallback_state:
            status = "fallback"
            label = "Fallback review"
            action = "Retry review after proof capture."
        else:
            status = "review_ready"
            label = "Review current"
            action = "Use review as current critique."
        return {
            "status": status,
            "label": label,
            "action": action,
            "last_review_at": latest.get("created_at"),
            "age_days": age_days,
            "fallback_state": fallback_state,
        }

    def _fallback_state(self, reason: Any) -> str | None:
        text = str(reason or "").strip().lower()
        if not text:
            return None
        if "quota" in text or "rate" in text or "429" in text:
            return "quota_or_rate_limit"
        if "timeout" in text:
            return "timeout"
        if "api" in text or "openai" in text or "provider" in text:
            return "provider_unavailable"
        return "fallback_used"

    def _collect_review_sources(self, state: dict[str, Any], ops: dict[str, Any]) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []

        system_snapshot = {
            "target": state["target"],
            "positioning": state["positioning"],
            "fit_score": ops["fit_score"],
            "current_bottleneck": ops["current_bottleneck"],
            "next_action": ops["next_action"],
            "personal_step": ops.get("personal_step"),
            "active_experiment": ops["active_experiment"],
            "dimensions": ops["dimensions"],
            "profile": ops.get("profile") or self._profile_view(state),
            "portfolio": state["portfolio"],
            "identity_profile": state.get("identity_profile", {}),
            "recent_journal": state["journal"][:8],
            "guardrails": state["guardrails"],
        }
        sources.append(
            {
                "name": "Live Imagineer state",
                "url": "internal://ops-check",
                "status": "ok",
                "text": json.dumps(system_snapshot, ensure_ascii=True, indent=2)[:7000],
            }
        )

        urls: list[str] = []
        reviewer_urls = state.get("reviewer", {}).get("source_urls", [])
        target_url = state.get("target", {}).get("active_listing_url")
        if target_url:
            urls.append(str(target_url))
            if "www.disneycareers.com/en/job/" in str(target_url):
                urls.append(str(target_url).replace("www.disneycareers.com/en/job/", "jobs.disneycareers.com/job/"))
        urls.extend(str(url) for url in reviewer_urls)
        urls.extend(str(item.get("url")) for item in state.get("portfolio", []) if item.get("url"))
        urls.extend(self._discover_aolabs_links())

        seen: set[str] = set()
        for url in urls:
            clean_url = url.strip()
            if not clean_url or clean_url in seen:
                continue
            seen.add(clean_url)
            sources.append(self._fetch_url_source(clean_url))
        return sources[:44]

    def _discover_aolabs_links(self) -> list[str]:
        try:
            request = Request(
                "https://aolabs.io/",
                headers={
                    "User-Agent": "AO-Labs-Imagineer-AI-Reviewer/1.0",
                    "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.3",
                },
            )
            with urlopen(request, timeout=7) as response:
                root_html = response.read(220_000).decode("utf-8", errors="ignore")
        except (HTTPError, URLError, OSError, TimeoutError, ValueError):
            return []
        urls = re.findall(r'href=["\']([^"\']+)["\']', root_html)
        if not urls:
            urls = re.findall(r"https://[a-z0-9.-]+\.aolabs\.io[^\s<>\"]*", root_html, flags=re.I)
        discovered: list[str] = []
        for url in urls:
            clean = url.strip()
            if clean.startswith("//"):
                clean = "https:" + clean
            if clean.startswith("/"):
                clean = "https://aolabs.io" + clean
            if not clean.startswith("https://"):
                continue
            if ".aolabs.io" not in clean and "aolabs.io" not in clean:
                continue
            clean = clean.split("#", 1)[0]
            if clean not in discovered:
                discovered.append(clean)
        return discovered[:20]

    def _fetch_url_source(self, url: str) -> dict[str, Any]:
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": "AO-Labs-Imagineer-AI-Reviewer/1.0",
                    "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.3",
                },
            )
            with urlopen(request, timeout=7) as response:
                content_type = response.headers.get("content-type", "")
                raw = response.read(220_000)
            if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
                text = "PDF source detected. Public artifact exists, but this reviewer run only extracts HTML/text sources."
            else:
                decoded = raw.decode("utf-8", errors="ignore")
                text = self._html_to_text(decoded)
            return {
                "name": self._source_name_from_url(url),
                "url": url,
                "status": "ok",
                "text": text[:5000],
            }
        except (HTTPError, URLError, OSError, TimeoutError, ValueError) as exc:
            return {
                "name": self._source_name_from_url(url),
                "url": url,
                "status": f"unavailable:{type(exc).__name__}",
                "text": "",
            }

    def _html_to_text(self, value: str) -> str:
        value = re.sub(r"(?is)<(script|style|svg|noscript).*?</\1>", " ", value)
        value = re.sub(r"(?s)<[^>]+>", " ", value)
        value = html.unescape(value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    def _source_name_from_url(self, url: str) -> str:
        lowered = url.lower()
        if "jobs.disneycareers.com" in lowered or "disneycareers.com" in lowered:
            return "Disney Careers role listing"
        if lowered.rstrip("/") == "https://aolabs.io":
            return "AO Labs home"
        if "imagineer.aolabs.io/profile" in lowered or "imagineer.aolabs.io/proof-packet" in lowered:
            return "WDI R&D profile"
        if "imagineer.aolabs.io/imagineer-autonomous-position-system" in lowered:
            return "Imagineer paper PDF"
        if "sarrus.aolabs.io" in lowered:
            return "Sarrus portfolio"
        if "fluxcell.aolabs.io" in lowered:
            return "FluxCell portfolio"
        if "relaylive.aolabs.io" in lowered:
            return "Relay Live dashboard"
        if "relay.aolabs.io" in lowered:
            return "Relay dashboard"
        if "progress.aolabs.io" in lowered:
            return "AO Labs progress ledger"
        if "curtis.aolabs.io" in lowered:
            return "Curtis practice system"
        if "ocean.aolabs.io" in lowered:
            return "Ocean portfolio"
        if "talk.aolabs.io" in lowered:
            return "Talk app"
        if "nerve.aolabs.io" in lowered:
            return "Nerve app"
        if "duet.aolabs.io" in lowered:
            return "Duet app"
        if "violin.aolabs.io" in lowered:
            return "Violin portfolio"
        if "yum.aolabs.io" in lowered:
            return "Yum app"
        if "lily.aolabs.io" in lowered:
            return "Lily app"
        if "la.disneyresearch.com/researchers" in lowered:
            return "Disney Research roster"
        if "bipedal-robotic-character" in lowered:
            return "Disney Research bipedal character paper"
        if "cv.aolabs.io" in lowered:
            return "CV artifact"
        return url

    def _openai_review(
        self,
        state: dict[str, Any],
        ops: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> tuple[dict[str, Any] | None, str | None]:
        if not os.getenv("OPENAI_API_KEY"):
            return None, "missing_openai_api_key"
        try:
            from openai import OpenAI

            source_payload = [
                {
                    "name": source["name"],
                    "url": source.get("url", ""),
                    "status": source["status"],
                    "text": source.get("text", "")[:2600],
                }
                for source in sources
            ]
            prompt = {
                "review_goal": "Produce a short operational readout: current WDI R&D alignment, active principal-scope gap, system-owned work, approval boundary, and source-backed status.",
                "target": state["target"],
                "positioning": state["positioning"],
                "current_ops": ops,
                "guardrails": state["guardrails"],
                "sources": source_payload,
            }
            client = OpenAI(timeout=90)
            response = client.responses.create(
                model=self._openai_model(),
                instructions=(
                    "You are an evidence-only autonomous career operator for a WDI R&D mechanical Imagineering target. "
                    "Use only the supplied sources. Do not invent credentials, contacts, referrals, or outcomes. "
                    "The user is Alan. Write for a serious researcher/operator, not for an imaginary reviewer. "
                    "State the actual condition. Do not explain why the page exists, narrate system intent, describe how the output should make Alan feel, or talk down to the reader. "
                    "Do not write sentences whose only function is to say that the system is helping, reducing burden, avoiding notes, or moving automatically. "
                    "If the issue is page/profile/paper quality, route it into system-owned work without making it Alan-facing commentary. "
                    "Only person-facing steps, applications, referral asks, or sensitive outreach require Alan approval. "
                    "Write like a concise technical status surface, not a checklist, homework prompt, motivational page, or reviewer-prep worksheet. "
                    "Avoid these terms and close variants in displayed strings: proof packet, evidence packet, reviewer-facing, reviewer-visible, "
                    "reviewer-proof, best evidence, evidence gaps, evidence to create, next evidence, best next move, action items, homework, "
                    "show-value, source coverage, and what a reviewer can inspect. "
                    "Prefer short, plain phrases: current, signals, system, approval boundary, source depth, measurements, geometry, actuation, motion, constraints. "
                    "Return strict JSON with keys: verdict, score, top_issue, why_it_matters, "
                    "best_existing_evidence, evidence_gaps, next_actions, packet_edits, reviewer_summary. "
                    "next_actions must be an array of objects with title, body, expected_signal, and source. "
                    "The first next_actions item must be the best system-owned move unless the only safe next step requires Alan approval. "
                    "Every displayed string must be a complete sentence or complete phrase. Do not end any field "
                    "mid-word, mid-name, or mid-sentence."
                ),
                input="Return json only.\n" + json.dumps(prompt, ensure_ascii=True),
                text={"format": {"type": "json_object"}},
                max_output_tokens=6000,
            )
            raw = self._response_output_text(response) or "{}"
            return self._normalize_review(json.loads(raw)), None
        except Exception as exc:
            return None, f"{type(exc).__name__}: {str(exc)[:240]}"

    def _response_output_text(self, response: Any) -> str:
        direct = getattr(response, "output_text", None)
        if direct:
            return str(direct)
        chunks: list[str] = []
        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                text = getattr(content, "text", None)
                if text:
                    chunks.append(str(text))
        return "".join(chunks)

    def _normalize_review(self, parsed: dict[str, Any]) -> dict[str, Any]:
        next_actions = []
        for item in parsed.get("next_actions") or []:
            if not isinstance(item, dict):
                continue
            next_actions.append(
                {
                    "title": self._bounded_display_text(item.get("title") or "Improve one public artifact.", 220),
                    "body": self._bounded_display_text(item.get("body") or "", 1200),
                    "expected_signal": self._bounded_display_text(item.get("expected_signal") or "", 700),
                    "source": self._bounded_display_text(item.get("source") or "", 500),
                }
            )
            if len(next_actions) >= 5:
                break

        return {
            "verdict": self._bounded_display_text(
                parsed.get("verdict") or "Review completed; profile needs sharper source backing.",
                500,
            ),
            "score": max(0, min(int(parsed.get("score") or 0), 100)),
            "top_issue": self._bounded_display_text(
                parsed.get("top_issue") or "The profile needs one concrete mechanical validation artifact.",
                800,
            ),
            "why_it_matters": self._review_summary_text(parsed.get("why_it_matters"), "", max_chars=1600),
            "best_existing_evidence": self._string_list(parsed.get("best_existing_evidence"), 5, 1200),
            "evidence_gaps": self._string_list(parsed.get("evidence_gaps"), 6, 1200),
            "next_actions": next_actions,
            "packet_edits": self._string_list(parsed.get("packet_edits"), 6, 1200),
            "reviewer_summary": self._review_summary_text(
                parsed.get("reviewer_summary"),
                parsed.get("why_it_matters"),
                max_chars=1600,
            ),
        }

    def _fallback_review(
        self,
        state: dict[str, Any],
        ops: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        source_names = ", ".join(source["name"] for source in sources if source["status"] == "ok")[:500]
        return {
            "verdict": "Credible core, not inevitable yet.",
            "score": max(0, min(int(ops.get("fit_score") or 0), 100)),
            "top_issue": "Sarrus makes the mechanical case credible; Principal-level ownership is not visible enough yet.",
            "why_it_matters": (
                "Current state: credible mechanism depth; developing Disney motion signal; thin principal-scope ownership signal."
            ),
            "best_existing_evidence": [
                "Sarrus establishes mechanism geometry, pneumatic actuation, modular assembly, and measured behavior.",
                "FluxCell establishes an actuation direction for moving beyond tethered pneumatic demos.",
                "The profile targets WDI R&D language instead of generic academic robotics framing.",
            ],
            "evidence_gaps": [
                "Principal-level ownership is not yet visible through led design reviews, integrated systems, collaborators, budget, schedule, or comparable responsibility.",
                "The strongest motion example still needs to read as a human-facing motion sequence, not only as a robotics result.",
                "The Sarrus quantitative record still needs cleaner digitized curves, uncertainty, sample count, and test conditions.",
            ],
            "next_actions": [
                {
                    "title": "Update the state surface.",
                    "body": "Replace raw critique sections with current signal, principal gap, system-owned work, and approval boundary.",
                    "expected_signal": "The dashboard reads as operational state.",
                    "source": source_names or "Live Imagineer state",
                },
                {
                    "title": "Clarify Disney motion.",
                    "body": "Use Sarrus as the anchor and turn one object-motion sequence into a concise human-facing motion sequence.",
                    "expected_signal": "The work reads as WDI physical interaction R&D, not only as soft robotics research.",
                    "source": "Sarrus and profile sources",
                },
            ],
            "packet_edits": [
                "Make Sarrus the primary technical anchor.",
                "Remove long critique lists from the main dashboard.",
                "Keep external outreach and applications behind approval.",
            ],
            "reviewer_summary": (
                "Available sources show credible mechanism depth, developing motion translation, and thin principal-scope ownership."
            ),
        }

    def _string_list(self, value: Any, limit: int, max_chars: int) -> list[str]:
        if not isinstance(value, list):
            return []
        items: list[str] = []
        for item in value:
            text = self._review_list_item_text(item)
            if text:
                items.append(self._bounded_display_text(text, max_chars))
            if len(items) >= limit:
                break
        return items

    def _review_list_item_text(self, item: Any) -> str:
        if isinstance(item, dict):
            source = str(item.get("source") or "").strip()
            evidence = str(item.get("evidence") or "").strip()
            gap = str(item.get("gap") or "").strip()
            detail = str(item.get("detail") or "").strip()
            section = str(item.get("section") or "").strip()
            edit = str(item.get("edit") or "").strip()
            title = str(item.get("title") or "").strip()
            body = str(item.get("body") or "").strip()
            if source and evidence:
                return self._label_detail(source, evidence)
            if gap and detail:
                return self._label_detail(gap, detail)
            if gap:
                return self._clean_inline_text(gap)
            if section and edit:
                return self._label_detail(section, edit)
            if title and body:
                return self._clean_inline_text(f"{title}: {body}")
            if edit:
                return self._clean_inline_text(edit)
            if evidence:
                return self._clean_inline_text(evidence)
            return self._clean_inline_text(json.dumps(item, ensure_ascii=True, sort_keys=True))
        text = self._clean_inline_text(str(item or ""))
        if text.startswith("{") and ":" in text:
            legacy = self._legacy_review_item_text(text)
            if legacy:
                return legacy
        return text

    def _legacy_review_item_text(self, text: str) -> str:
        source = self._legacy_review_value(text, "source")
        evidence = self._legacy_review_value(text, "evidence")
        gap = self._legacy_review_value(text, "gap")
        detail = self._legacy_review_value(text, "detail")
        section = self._legacy_review_value(text, "section")
        edit = self._legacy_review_value(text, "edit")
        if source and evidence:
            return self._label_detail(source, evidence)
        if gap and detail:
            return self._label_detail(gap, detail)
        if gap:
            return self._clean_inline_text(gap)
        if section and edit:
            return self._label_detail(section, edit)
        if edit:
            return self._clean_inline_text(edit)
        return ""

    def _legacy_review_value(self, text: str, key: str) -> str:
        match = re.search(rf"['\"]{re.escape(key)}['\"]\s*:\s*(['\"])", text)
        if not match:
            return ""
        quote = match.group(1)
        start = match.end()
        rest = text[start:]
        next_field = re.search(rf"{re.escape(quote)}\s*,\s*['\"][A-Za-z_]+['\"]\s*:", rest)
        value = rest[: next_field.start()] if next_field else rest
        return self._clean_inline_text(value.strip().rstrip("}").strip().strip("\"'"))

    def _label_detail(self, label: str, detail: str) -> str:
        clean_label = self._clean_inline_text(label).rstrip(".:;")
        clean_detail = self._clean_inline_text(detail)
        return f"{clean_label}: {clean_detail}"

    def _review_display_text(self, primary: Any, fallback: Any, default: str) -> str:
        text = self._clean_inline_text(str(primary or ""))
        if text and text[-1] in ".!?":
            return text
        fallback_text = self._clean_inline_text(str(fallback or ""))
        if fallback_text:
            return self._first_sentence(fallback_text)
        return default

    def _review_summary_text(self, primary: Any, fallback: Any = "", max_chars: int = 1600) -> str:
        text = self._clean_inline_text(str(primary or ""))
        if not text:
            text = self._clean_inline_text(str(fallback or ""))
        if not text:
            return ""

        text = self._strip_incomplete_next_move(text)
        if len(text) > max_chars:
            text = self._complete_prefix(text, max_chars)
        return text

    def _bounded_display_text(self, value: Any, limit: int) -> str:
        text = self._strip_incomplete_next_move(self._clean_inline_text(str(value or "")))
        if len(text) <= limit:
            return text
        return self._complete_prefix(text, limit)

    def _strip_incomplete_next_move(self, text: str) -> str:
        patterns = (
            r"\s+The current move is to\s*$",
            r"\s+The selected next move is to\s*$",
        )
        cleaned = text
        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.I).rstrip()
        return cleaned

    def _complete_prefix(self, text: str, limit: int) -> str:
        prefix = text[:limit].rstrip()
        if not prefix:
            return ""
        if prefix[-1] in ".!?":
            return prefix
        stops = [prefix.rfind(marker) for marker in (". ", "! ", "? ")]
        last_stop = max(stops)
        if last_stop > 0:
            return prefix[: last_stop + 1]
        last_space = prefix.rfind(" ")
        if last_space > 0:
            return prefix[:last_space].rstrip(" ,;:") + "."
        return prefix.rstrip(" ,;:")

    def _first_sentence(self, text: str) -> str:
        for marker in (". ", "! ", "? "):
            index = text.find(marker)
            if index > 0:
                return text[: index + 1]
        return text

    def _clean_inline_text(self, text: str) -> str:
        return self._alan_facing_text(" ".join(text.strip().split()))

    def _alan_facing_text(self, text: str) -> str:
        replacements = (
            ("Sarrus mechanism proof", "Sarrus record"),
            ("sarrus mechanism proof", "Sarrus record"),
            ("mechanism proof", "mechanical record"),
            ("proof packet", "profile"),
            ("Proof packet", "Profile"),
            ("evidence packet", "profile"),
            ("Evidence packet", "Profile"),
            ("reviewer-facing", "public"),
            ("Reviewer-facing", "Public"),
            ("reviewer-visible", "public"),
            ("Reviewer-visible", "Public"),
            ("reviewer-proof", "source-backed"),
            ("Reviewer-proof", "Source-backed"),
            ("best evidence", "current signals"),
            ("Best evidence", "Current signals"),
            ("evidence gaps", "open signals"),
            ("Evidence gaps", "Open signals"),
            ("evidence to create", "unresolved"),
            ("Evidence to create", "Unresolved"),
            ("next evidence", "unresolved signal"),
            ("Next evidence", "Unresolved signal"),
            ("best next move", "current move"),
            ("Best next move", "Current move"),
            ("show-value", "motion"),
            ("Show-value", "Motion"),
            ("source coverage", "source depth"),
            ("Source coverage", "Source depth"),
            ("what a reviewer can inspect", "public sources"),
            ("What a reviewer can inspect", "Public sources"),
        )
        for old, new in replacements:
            text = text.replace(old, new)
        return text

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            state = copy.deepcopy(DEFAULT_STATE)
            self._save_state(state)
            return state

        try:
            with self.state_path.open("r", encoding="utf-8") as handle:
                state = json.load(handle)
        except (json.JSONDecodeError, OSError):
            state = copy.deepcopy(DEFAULT_STATE)
            self._save_state(state)
        return self._merge_defaults(state)

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.state_path.with_name(f"{self.state_path.name}.{uuid.uuid4().hex}.tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, sort_keys=True)
        tmp_path.replace(self.state_path)

    def _merge_defaults(self, state: dict[str, Any]) -> dict[str, Any]:
        merged = copy.deepcopy(DEFAULT_STATE)
        for key, value in state.items():
            merged[key] = value
        for list_key in ("dimensions", "experiments", "portfolio", "guardrails", "events", "reviews", "lead_checks", "journal", "weekly_papers"):
            merged.setdefault(list_key, copy.deepcopy(DEFAULT_STATE[list_key]))
        existing_reviewer = state.get("reviewer", {})
        if not isinstance(existing_reviewer, dict):
            existing_reviewer = {}
        default_reviewer = copy.deepcopy(DEFAULT_STATE["reviewer"])
        merged["reviewer"] = {**default_reviewer, **existing_reviewer}
        merged["reviewer"]["source_urls"] = self._merge_unique_strings(
            default_reviewer.get("source_urls", []),
            existing_reviewer.get("source_urls", []),
        )
        existing_profile = state.get("profile_record", {})
        if not isinstance(existing_profile, dict):
            existing_profile = {}
        merged["profile_record"] = {**copy.deepcopy(DEFAULT_STATE["profile_record"]), **existing_profile}
        existing_target = state.get("target", {})
        if not isinstance(existing_target, dict):
            existing_target = {}
        merged["target"] = {**copy.deepcopy(DEFAULT_STATE["target"]), **existing_target}
        self._refresh_active_listing_target(merged)
        self._merge_list_by_key(merged, "portfolio", "name")
        self._merge_list_by_key(merged, "experiments", "id")
        self._sanitize_expired_job_target(merged)
        return merged

    def _refresh_active_listing_target(self, state: dict[str, Any]) -> None:
        target = state.setdefault("target", {})
        default_target = DEFAULT_STATE["target"]
        if target.get("active_listing_job_id") != default_target.get("active_listing_job_id"):
            return
        if target.get("active_listing_url") != default_target.get("active_listing_url"):
            return
        target_checked = self._parse_timestamp(target.get("active_listing_last_checked_at"))
        default_checked = self._parse_timestamp(default_target.get("active_listing_last_checked_at"))
        if default_checked and (target_checked is None or default_checked > target_checked):
            for key in (
                "active_listing_state",
                "active_listing_last_checked_at",
                "active_listing_last_status_code",
                "active_listing_note",
                "active_listing_posted",
                "active_rung_title",
                "company",
                "location",
            ):
                target[key] = copy.deepcopy(default_target[key])

    def _parse_timestamp(self, value: Any) -> datetime | None:
        try:
            text = str(value or "").replace("Z", "+00:00")
            item = datetime.fromisoformat(text)
        except (TypeError, ValueError):
            return None
        if item.tzinfo is None:
            item = item.replace(tzinfo=timezone.utc)
        return item.astimezone(timezone.utc)

    def _sanitize_expired_job_target(self, state: dict[str, Any]) -> None:
        target = state.setdefault("target", {})
        target_text = " ".join(
            str(target.get(key, ""))
            for key in ("active_listing_job_id", "active_listing_url", "active_rung_title")
        ).lower()
        if any(job_id in target_text for job_id in EXPIRED_DISNEY_JOB_IDS) or target.get("active_listing_state") == "unavailable_on_last_check":
            target.update(copy.deepcopy(DEFAULT_STATE["target"]))
        reviewer = state.setdefault("reviewer", {})
        source_urls = reviewer.get("source_urls", [])
        if isinstance(source_urls, list):
            clean_urls = [
                str(url)
                for url in source_urls
                if not any(job_id in str(url) for job_id in EXPIRED_DISNEY_JOB_IDS)
            ]
            reviewer["source_urls"] = self._merge_unique_strings([DISNEY_JOB_SEARCH_URL], clean_urls)

    def _merge_unique_strings(self, *values: list[Any]) -> list[str]:
        merged: list[str] = []
        seen: set[str] = set()
        for value_list in values:
            for value in value_list:
                text = str(value).strip()
                if not text or text in seen:
                    continue
                seen.add(text)
                merged.append(text)
        return merged

    def _merge_list_by_key(self, state: dict[str, Any], list_key: str, item_key: str) -> None:
        existing_values = {
            item.get(item_key)
            for item in state.get(list_key, [])
            if isinstance(item, dict)
        }
        for item in DEFAULT_STATE[list_key]:
            if item.get(item_key) not in existing_values:
                state[list_key].append(copy.deepcopy(item))

    def _week_id(self) -> str:
        year, week, _ = datetime.now(timezone.utc).isocalendar()
        return f"{year}-W{week:02d}"

    def _week_bounds(self) -> tuple[datetime, datetime]:
        now = datetime.now(timezone.utc)
        week_start = datetime.combine((now - timedelta(days=now.weekday())).date(), datetime.min.time(), tzinfo=timezone.utc)
        return week_start, week_start + timedelta(days=7, hours=8, minutes=30)

    def _event_in_current_week(self, event: dict[str, Any], week_start: datetime) -> bool:
        try:
            created = datetime.fromisoformat(str(event.get("created_at")).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return False
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return created >= week_start

    def _event_from_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        raw_tags = payload.get("tags") or []
        tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()]
        kind = str(payload.get("kind") or "proof").strip().lower()[:40]
        return {
            "id": str(uuid.uuid4()),
            "created_at": _utc_now(),
            "date": _today(),
            "kind": kind,
            "title": str(payload.get("title") or self._title_for_kind(kind)).strip()[:140],
            "notes": str(payload.get("notes") or "").strip()[:4000],
            "link": str(payload.get("link") or "").strip()[:800],
            "tags": tags[:12],
            "impact": max(1, min(int(payload.get("impact") or 1), 5)),
        }

    def _append_journal_from_event(self, state: dict[str, Any], event: dict[str, Any]) -> None:
        if event["kind"] == "daily_cycle":
            return
        body = event["notes"] or event["link"] or "Work logged."
        state["journal"].insert(
            0,
            {
                "id": str(uuid.uuid4()),
                "created_at": event["created_at"],
                "title": event["title"],
                "body": body,
                "tags": event["tags"] or [event["kind"]],
            },
        )
        state["journal"] = state["journal"][:120]

    def _score_dimensions(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        events = state["events"]
        portfolio_tags = [
            tag
            for item in state["portfolio"]
            for tag in item.get("tags", [])
        ]
        ai_review_count = len(state.get("reviews", []))
        scored: list[dict[str, Any]] = []
        for dimension in state["dimensions"]:
            key = dimension["key"]
            calibration = self._dimension_calibration(key)
            event_points = sum(
                int(event.get("impact") or 1)
                for event in events
                if key in event.get("tags", [])
            )
            portfolio_points = portfolio_tags.count(key)
            daily_points = sum(1 for event in events if event.get("kind") == "daily_cycle" and key in event.get("tags", []))
            base_score = int(dimension["score"])
            event_score = min(
                int(round(event_points * calibration["event_weight"])),
                calibration["event_cap"],
            )
            portfolio_score = min(
                portfolio_points * calibration["portfolio_weight"],
                calibration["portfolio_cap"],
            )
            daily_score = min(daily_points, calibration["daily_cap"])
            loop_score = self._dimension_loop_bonus(key, ai_review_count)
            ceiling = calibration["ceiling"]
            raw_score = base_score + event_score + portfolio_score + daily_score + loop_score
            score = min(ceiling, raw_score)
            scored.append(
                {
                    "key": key,
                    "label": self._dimension_label(key, dimension["label"]),
                    "score": score,
                    "gap": max(0, 100 - score),
                    "target_signal": self._dimension_target_signal(key, dimension["target_signal"]),
                    "next_signal": self._signal_action_for_dimension(key),
                    "score_basis": (
                        f"Base {base_score}; +{event_score} calibrated event bonus from {event_points} raw logged-impact points; "
                        f"+{portfolio_score} portfolio bonus; +{daily_score} daily-cycle bonus; "
                        f"+{loop_score} reviewer-loop bonus; readiness ceiling {ceiling} because {calibration['ceiling_reason']} "
                        "A score of 100 is reserved for no known blocker, not just accumulated activity."
                    ),
                }
            )
        return scored

    def _dimension_calibration(self, key: str) -> dict[str, Any]:
        calibrations: dict[str, dict[str, Any]] = {
            "mechanical_depth": {
                "event_weight": 0.30,
                "event_cap": 8,
                "portfolio_weight": 2,
                "portfolio_cap": 4,
                "daily_cap": 1,
                "ceiling": 86,
                "ceiling_reason": "raw digitized curves, uncertainty, and formal test conditions are still missing.",
            },
            "creative_prototyping": {
                "event_weight": 0.25,
                "event_cap": 4,
                "portfolio_weight": 2,
                "portfolio_cap": 4,
                "daily_cap": 1,
                "ceiling": 84,
                "ceiling_reason": "the public record still needs a tighter visible prototype-iteration story.",
            },
            "physical_experience": {
                "event_weight": 0.70,
                "event_cap": 10,
                "portfolio_weight": 2,
                "portfolio_cap": 4,
                "daily_cap": 1,
                "ceiling": 82,
                "ceiling_reason": "motion is visible, but the profile still needs a concise guest-facing demo sequence.",
            },
            "leadership_network": {
                "event_weight": 0.20,
                "event_cap": 3,
                "portfolio_weight": 1,
                "portfolio_cap": 2,
                "daily_cap": 1,
                "ceiling": 58,
                "ceiling_reason": "the review loop works, but visible principal-level ownership and external validation remain weak.",
            },
            "application_packet": {
                "event_weight": 0.50,
                "event_cap": 22,
                "portfolio_weight": 2,
                "portfolio_cap": 4,
                "daily_cap": 1,
                "ceiling": 76,
                "ceiling_reason": "the profile is credible for the active rung, but a demo reel, final CV bullets, and principal-scope signals are still open.",
            },
            "paper_system": {
                "event_weight": 0.45,
                "event_cap": 20,
                "portfolio_weight": 2,
                "portfolio_cap": 2,
                "daily_cap": 1,
                "ceiling": 74,
                "ceiling_reason": "the autonomous loop is early and still needs scheduled runs, stronger evaluations, and longer outcome history.",
            },
        }
        return calibrations.get(
            key,
            {
                "event_weight": 0.25,
                "event_cap": 5,
                "portfolio_weight": 1,
                "portfolio_cap": 2,
                "daily_cap": 1,
                "ceiling": 75,
                "ceiling_reason": "the lane has unresolved signals.",
            },
        )

    def _dimension_loop_bonus(self, key: str, ai_review_count: int) -> int:
        if key == "leadership_network":
            return min(ai_review_count * 2, 20)
        if key == "paper_system":
            return min(ai_review_count, 8)
        return 0

    def _active_experiment(self, state: dict[str, Any]) -> dict[str, Any]:
        active_id = state.get("active_experiment_id")
        if active_id:
            selected = next((item for item in state["experiments"] if item.get("id") == active_id), None)
            if selected:
                return selected
        return next((item for item in state["experiments"] if item.get("status") == "active"), state["experiments"][0])

    def _experiment_view(self, experiment: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        start = experiment.get("started_at")
        proof_count = sum(1 for event in state["events"] if event.get("kind") == "proof")
        cycle_count = sum(1 for event in state["events"] if event.get("kind") == "daily_cycle")
        reviewer_ready = sum(1 for event in state["events"] if "reviewer_ready" in event.get("tags", []))
        reviewer_ready += sum(1 for item in state["portfolio"] if "reviewer_ready" in item.get("tags", []))
        warm_review = sum(1 for event in state["events"] if "warm_review" in event.get("tags", []))
        ai_reviews = len(state.get("reviews", []))
        progress = {
            "proof_logs": proof_count,
            "daily_cycles": cycle_count,
            "reviewer_ready_artifacts": reviewer_ready,
            "ai_reviews": ai_reviews,
            "warm_review_requests": warm_review,
            "target_proof_logs": 5,
            "target_reviewer_ready_artifacts": 1,
            "target_ai_reviews": 1,
            "target_warm_review_requests": 1,
        }
        return {**experiment, "started_at": start, "progress": progress}

    def _a3_queue_snapshot(self) -> dict[str, Any]:
        try:
            request = Request(
                A3_QUEUE_SNAPSHOT_URL,
                headers={
                    "User-Agent": "AO-Labs-Imagineer-Life-Loop/1.0",
                    "Accept": "application/json,text/plain;q=0.8,*/*;q=0.3",
                },
            )
            with urlopen(request, timeout=5) as response:
                raw = response.read(80_000).decode("utf-8", errors="ignore")
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except (HTTPError, URLError, OSError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            return {
                "ok": False,
                "available": False,
                "source": A3_QUEUE_SNAPSHOT_URL,
                "error": f"{type(exc).__name__}",
            }
        return {"ok": False, "available": False, "source": A3_QUEUE_SNAPSHOT_URL, "error": "invalid_payload"}

    def _proof_capture_state(self, state: dict[str, Any]) -> dict[str, Any]:
        proofs = [
            event
            for event in state.get("events", [])
            if event.get("kind") == "proof" and ("fluxcell" in event.get("tags", []) or "FluxCell" in str(event.get("title", "")))
        ]
        latest = proofs[0] if proofs else None
        return {
            "title": "FluxCell proof capture",
            "status": "proof_logged" if latest else "ready_for_capture",
            "endpoint": "/api/imagineer/proofs",
            "current_step": "Add one note, measurement, route, photo, video, PDF, or text file from the FluxCell linkage test.",
            "artifact_types": ["note", "measurement", "route", "photo", "video", "PDF", "text file"],
            "sync_targets": PROOF_SYNC_TARGETS,
            "latest": self._compact_proof(latest),
        }

    def _compact_proof(self, event: dict[str, Any] | None) -> dict[str, Any] | None:
        if not event:
            return None
        artifact = event.get("artifact") if isinstance(event.get("artifact"), dict) else {}
        fields = {}
        capture = event.get("proof_capture") if isinstance(event.get("proof_capture"), dict) else {}
        if isinstance(capture.get("fields"), dict):
            fields = capture["fields"]
        return {
            "id": event.get("id"),
            "created_at": event.get("created_at"),
            "title": event.get("title"),
            "notes": event.get("notes"),
            "link": event.get("link"),
            "artifact_route": artifact.get("route"),
            "artifact_type": artifact.get("type"),
            "measurement": fields.get("measurement"),
            "changed": fields.get("changed"),
        }

    def _proof_fields(self, payload: dict[str, Any]) -> dict[str, str]:
        fields = {
            "note": str(payload.get("note") or "").strip(),
            "measurement": str(payload.get("measurement") or "").strip(),
            "changed": str(payload.get("changed") or "").strip(),
            "failure": str(payload.get("failure") or "").strip(),
            "next_update": str(payload.get("next_update") or "").strip(),
            "link": str(payload.get("link") or "").strip(),
        }
        return {key: value for key, value in fields.items() if value}

    def _proof_notes(self, fields: dict[str, str], artifact: dict[str, Any] | None) -> str:
        parts = []
        if fields.get("changed"):
            parts.append(f"Changed: {fields['changed']}.")
        if fields.get("measurement"):
            parts.append(f"Measurement/result: {fields['measurement']}.")
        if fields.get("note"):
            parts.append(f"Note: {fields['note']}")
        if fields.get("failure"):
            parts.append(f"Failure/limit: {fields['failure']}.")
        if fields.get("next_update"):
            parts.append(f"Next update: {fields['next_update']}.")
        if fields.get("link"):
            parts.append(f"Source route: {fields['link']}.")
        if artifact:
            parts.append(f"Artifact: {artifact.get('name')} ({artifact.get('type')}).")
        if not parts:
            raise ValueError("Add a note, measurement, link, or file before logging proof.")
        parts.append("Runtime profile and journal state updated; next public sync targets: profile, CV, paper, Progress.")
        return " ".join(parts)[:4000]

    def _proof_sync_plan(self, event: dict[str, Any]) -> dict[str, Any]:
        return {
            "state": "runtime_profile_journal_updated",
            "event_id": event.get("id"),
            "targets": PROOF_SYNC_TARGETS,
            "remaining": ["static CV PDF", "static paper PDF", "Progress public event"],
        }

    def _save_proof_artifact(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        data_url = str(payload.get("artifact_data") or "").strip()
        if not data_url:
            return None
        if ";base64," not in data_url:
            raise ValueError("Proof artifact must be a base64 data URL.")
        header, encoded = data_url.split(";base64,", 1)
        mime = str(payload.get("artifact_mime") or header.replace("data:", "") or "application/octet-stream").strip().lower()
        if mime not in PROOF_MIME_EXTENSIONS:
            raise ValueError("Unsupported proof artifact type.")
        try:
            content = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("Proof artifact could not be decoded.") from exc
        if not content:
            raise ValueError("Proof artifact is empty.")
        if len(content) > MAX_PROOF_UPLOAD_BYTES:
            raise ValueError("Proof artifact is over the 12 MB limit.")

        original_name = self._safe_filename(str(payload.get("artifact_name") or "proof-artifact"))
        suffix = PROOF_MIME_EXTENSIONS[mime]
        stem = original_name.rsplit(".", 1)[0] if "." in original_name else original_name
        stem = stem or "proof-artifact"
        filename = self._safe_filename(f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}-{stem}{suffix}")
        self.proof_upload_dir.mkdir(parents=True, exist_ok=True)
        path = self.proof_upload_dir / filename
        path.write_bytes(content)
        artifact_type = str(payload.get("artifact_type") or "").strip() or self._artifact_type_from_mime(mime)
        route = f"/api/imagineer/proofs/{filename}"
        return {
            "name": original_name,
            "filename": filename,
            "route": route,
            "type": artifact_type,
            "mime": mime,
            "bytes": len(content),
        }

    def _safe_filename(self, value: str) -> str:
        name = Path(str(value or "")).name
        name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-_")
        return name[:140]

    def _artifact_type_from_mime(self, mime: str) -> str:
        if mime.startswith("image/"):
            return "photo"
        if mime.startswith("video/"):
            return "video"
        if mime == "application/pdf":
            return "PDF"
        return "text file"

    def _lead_verification_state(self, state: dict[str, Any]) -> dict[str, Any]:
        target = state.get("target") if isinstance(state.get("target"), dict) else {}
        checked_at = self._parse_timestamp(target.get("active_listing_last_checked_at"))
        now = datetime.now(timezone.utc)
        age_days = None
        if checked_at:
            age_days = max(0, (now - checked_at).days)
        is_current = checked_at is not None and age_days is not None and age_days <= 7 and target.get("active_listing_state") == "verified_live_listing"
        status = "current" if is_current else "stale"
        latest_check = next(iter(state.get("lead_checks", [])), None)
        if target.get("active_listing_state") == "unavailable_on_last_check":
            status = "unavailable"
        action = "Verify the clicked Disney destination before lead-facing use."
        effective_listing_state = target.get("active_listing_state")
        latest_checked_at = self._parse_timestamp(latest_check.get("checked_at")) if isinstance(latest_check, dict) else None
        if isinstance(latest_check, dict) and latest_checked_at and (checked_at is None or latest_checked_at >= checked_at):
            latest_state = str(latest_check.get("listing_state") or "")
            effective_listing_state = latest_state or effective_listing_state
            if latest_state == "verified_live_listing":
                status = "current"
                action = "Clicked Disney destination verified."
            elif latest_state == "verification_mismatch":
                status = "mismatch"
                action = "Fresh destination check did not match title/company/location; do not use as a lead yet."
            elif latest_state == "verification_unavailable":
                status = "unverified"
                action = "Fresh destination check did not complete; do not use as a lead yet."
            elif latest_state == "unavailable_on_last_check":
                status = "unavailable"
                action = "Fresh destination check found the lead unavailable."
        return {
            "status": status,
            "listing_state": effective_listing_state,
            "title": target.get("active_rung_title"),
            "company": target.get("company"),
            "location": target.get("location"),
            "url": target.get("active_listing_url"),
            "last_checked_at": target.get("active_listing_last_checked_at"),
            "age_days": age_days,
            "last_status_code": target.get("active_listing_last_status_code"),
            "action": action,
            "latest_check": latest_check,
        }

    def _check_active_listing_destination(self, state: dict[str, Any]) -> dict[str, Any]:
        target = state.get("target") if isinstance(state.get("target"), dict) else {}
        url = str(target.get("active_listing_url") or VERIFIED_DISNEY_JOB_URL).strip()
        checked_at = _utc_now()
        status_code = 0
        body = ""
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": "AO-Labs-Imagineer-Lead-Verifier/1.0",
                    "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.3",
                },
            )
            with urlopen(request, timeout=10) as response:
                status_code = int(getattr(response, "status", 200) or 200)
                body = response.read(260_000).decode("utf-8", errors="ignore")
        except HTTPError as exc:
            status_code = int(exc.code or 0)
            try:
                body = exc.read(120_000).decode("utf-8", errors="ignore")
            except Exception:
                body = ""
        except (URLError, OSError, TimeoutError, ValueError) as exc:
            return {
                "ok": False,
                "checked_at": checked_at,
                "url": url,
                "status_code": status_code,
                "listing_state": "verification_unavailable",
                "note": f"Destination verification did not complete: {type(exc).__name__}.",
            }

        text = self._html_to_text(body)
        lowered = text.lower()
        unavailable = status_code == 404 or "job not found" in lowered or "no longer available" in lowered
        matched = self._lead_destination_match(text, target)
        if matched and not unavailable:
            return {
                "ok": True,
                "checked_at": checked_at,
                "url": url,
                "status_code": status_code,
                "listing_state": "verified_live_listing",
                "note": "Disney Careers destination verified live with matching title, company, and location. Lead only; no application, outreach, referral, relationship, or hiring claim.",
            }
        if unavailable:
            return {
                "ok": False,
                "checked_at": checked_at,
                "url": url,
                "status_code": status_code,
                "listing_state": "unavailable_on_last_check",
                "note": "Disney Careers destination is unavailable or says Job Not Found.",
            }
        return {
            "ok": False,
            "checked_at": checked_at,
            "url": url,
            "status_code": status_code,
            "listing_state": "verification_mismatch",
            "note": "Destination loaded, but title/company/location did not all match the tracked lead.",
        }

    def _lead_destination_match(self, text: str, target: dict[str, Any]) -> bool:
        lowered = text.lower()
        title = str(target.get("active_rung_title") or "Principal Ride Development Engineer, Design Assurance").lower()
        title_parts = [part.strip() for part in re.split(r"[,;-]", title) if part.strip()]
        company = str(target.get("company") or "Walt Disney Imagineering").lower()
        location = str(target.get("location") or "Glendale").lower()
        title_ok = title in lowered or all(part in lowered for part in title_parts[:2])
        company_ok = company in lowered or "walt disney imagineering" in lowered
        location_ok = "glendale" in lowered or location in lowered
        return bool(title_ok and company_ok and location_ok)

    def _life_loop(
        self,
        *,
        state: dict[str, Any],
        dimensions: list[dict[str, Any]],
        weakest: dict[str, Any],
        step: dict[str, Any],
        fit_score: int,
        a3_snapshot: dict[str, Any],
    ) -> dict[str, Any]:
        car = a3_snapshot.get("car") if isinstance(a3_snapshot.get("car"), dict) else {}
        car_path = a3_snapshot.get("carPath") if isinstance(a3_snapshot.get("carPath"), dict) else {}
        finance = a3_snapshot.get("financeRead") if isinstance(a3_snapshot.get("financeRead"), dict) else {}
        readiness = car_path.get("readiness") if isinstance(car_path.get("readiness"), dict) else {}

        car_name = str(car.get("name") or "A3 car target")
        car_price = self._text_value(car.get("priceAsBuilt")) or self._text_value(car_path.get("purchasePrice"))
        car_value = f"{car_name} {car_price}".strip()
        cash = self._text_value(finance.get("currentCash"))
        debt = self._text_value(finance.get("cardLoanBalance"))
        flexible = self._text_value(finance.get("flexible14"))
        monthly_room = self._text_value(car_path.get("monthlyRoom"))
        finance_parts = [
            f"cash {cash}" if cash else "",
            f"card/loan {debt}" if debt else "",
            f"flexible 14d {flexible}" if flexible else "",
            f"monthly room {monthly_room}" if monthly_room else "",
        ]
        finance_line = "; ".join(part for part in finance_parts if part)
        if readiness.get("label") and readiness.get("reason"):
            finance_line = f"{readiness['label']}: {readiness['reason']}. {finance_line}".strip()
        if not finance_line:
            finance_line = "A3 queue snapshot unavailable; keep the career proof as the main controllable lever."

        bottleneck_label = weakest.get("label") or "Current bottleneck"
        bottleneck_score = int(weakest.get("score") or 0)
        target = state.get("target") if isinstance(state.get("target"), dict) else {}
        role = target.get("north_star_title") or "WDI mechanical R&D"
        artifact_name = str(step.get("title") or "Make one proof artifact.").rstrip(".")
        artifact_body = str(step.get("body") or "Create source-backed public proof.").rstrip(".")

        return {
            "title": "Career proof, income path, car",
            "summary": (
                "Current proof artifact first; public career signal next; A3 car path downstream."
            ),
            "source": "Imagineer ops + Progress source graph + PhD queue + A3 queue snapshot.",
            "updated_at": a3_snapshot.get("generatedAt") or a3_snapshot.get("checkedAt") or _utc_now(),
            "primary_action_id": step.get("decision_id"),
            "items": [
                {
                    "label": "Career",
                    "value": f"{role}; fit {fit_score}/100",
                    "detail": f"{bottleneck_label} {bottleneck_score}/100 is the current live gap.",
                },
                {
                    "label": "Proof",
                    "value": artifact_name,
                    "detail": f"{artifact_body}; then update the public profile, CV, paper, and Progress record.",
                },
                {
                    "label": "Money",
                    "value": "Higher-income R&D path",
                    "detail": "The controllable lever is stronger inspectable ownership proof, not another profile rewrite.",
                },
                {
                    "label": "Car",
                    "value": car_value,
                    "detail": finance_line,
                },
            ],
            "a3": {
                "available": bool(a3_snapshot.get("available", False) or a3_snapshot.get("ok", False)),
                "source": A3_QUEUE_SNAPSHOT_URL,
                "generated_at": a3_snapshot.get("generatedAt"),
                "latest_transaction_date": finance.get("latestTransactionDate"),
                "car": car_name,
                "price": car_price,
                "finance": finance_line,
            },
        }

    def _text_value(self, value: Any) -> str:
        if isinstance(value, dict):
            text = str(value.get("text") or "").strip()
            if text:
                return text
            raw = value.get("value")
            if isinstance(raw, (int, float)):
                return f"${raw:,.0f}"
        if isinstance(value, (int, float)):
            return f"${value:,.0f}"
        return str(value or "").strip()

    def _step_decision(
        self,
        state: dict[str, Any],
        dimensions: list[dict[str, Any]],
        weakest: dict[str, Any],
    ) -> dict[str, Any]:
        candidates = self._step_candidates(state, dimensions, weakest)
        selected = max(candidates, key=lambda item: item["score"])
        step = {
            "lane": selected["lane"],
            "title": selected["title"],
            "body": selected["body"],
            "why": selected["why"],
            "time": selected["time"],
            "href": selected["href"],
            "linkLabel": selected.get("link_label") or "Open",
            "source": (
                f"Principal signal {self._dimension_score(dimensions, 'leadership_network')}/100. "
                f"Decision score {selected['score']}/100."
            ),
            "urgency": selected["urgency"],
            "decision_score": selected["score"],
            "decision_id": selected["id"],
        }
        return {
            "step": step,
            "system": {
                "name": "failure-cost evidence ROI",
                "policy": (
                    "Select the lowest-friction action that creates current, inspectable evidence "
                    "against the weakest Disney-relevant signal while avoiding approval-gated external action."
                ),
                "selected_id": selected["id"],
                "selected_score": selected["score"],
                "current_bottleneck": weakest["key"],
                "inputs": [
                    "verified WDI ride-development design-assurance lead",
                    "principal-scope north star",
                    "role-fit dimension scores",
                    "AO Labs public-source graph",
                    "approval boundary",
                ],
                "candidates": candidates,
            },
        }

    def _step_candidates(
        self,
        state: dict[str, Any],
        dimensions: list[dict[str, Any]],
        weakest: dict[str, Any],
    ) -> list[dict[str, Any]]:
        phd_doc = "https://docs.google.com/document/d/1Ffi51WavVvaFBUQX37AbFQ4ZKGEkRlGl-NRcOVQP03c/edit"
        candidates = [
            {
                "id": "lock-fluxcell-experiment",
                "lane": "leadership_network",
                "title": "Make the FluxCell linkage test.",
                "body": "Actuator-less array, clip-programmed shape, overhang motion check.",
                "why": (
                    "The current source names the prototype path; visible ownership now needs a measured first build."
                ),
                "time": "7 minutes",
                "href": "#proof-capture",
                "link_label": "Start proof",
                "source_doc": phd_doc,
                "urgency": "current ownership is the live failure point",
                "role_alignment": 24,
                "bottleneck_relief": 24,
                "evidence_created": 22,
                "compounding": 16,
                "urgency_score": 13,
                "friction": 6,
                "gate_penalty": 0,
            },
            {
                "id": "update-sarrus-again",
                "lane": "mechanical_depth",
                "title": "Polish Sarrus again.",
                "body": "Make another Sarrus note or explanation.",
                "why": "Low return now. Sarrus is already the completed anchor.",
                "time": "20 minutes",
                "href": "https://sarrus.aolabs.io",
                "urgency": "low",
                "role_alignment": 9,
                "bottleneck_relief": 2,
                "evidence_created": 3,
                "compounding": 3,
                "urgency_score": 0,
                "friction": 9,
                "gate_penalty": 0,
            },
            {
                "id": "revise-profile-copy",
                "lane": "application_packet",
                "title": "Revise the profile copy.",
                "body": "Change the public framing without adding new technical evidence.",
                "why": "Useful later, but copy cannot replace current prototype ownership.",
                "time": "15 minutes",
                "href": "https://imagineer.aolabs.io/profile.html",
                "urgency": "medium",
                "role_alignment": 14,
                "bottleneck_relief": 7,
                "evidence_created": 4,
                "compounding": 8,
                "urgency_score": 5,
                "friction": 6,
                "gate_penalty": 0,
            },
            {
                "id": "ask-for-referral",
                "lane": "leadership_network",
                "title": "Ask for a referral now.",
                "body": "Send a person-facing message before the current technical direction is clearer.",
                "why": "High upside, but approval-gated and premature without a sharper current artifact.",
                "time": "30 minutes",
                "href": "",
                "urgency": "approval-gated",
                "role_alignment": 20,
                "bottleneck_relief": 20,
                "evidence_created": 6,
                "compounding": 12,
                "urgency_score": 8,
                "friction": 12,
                "gate_penalty": 25,
            },
            {
                "id": "run-review-only",
                "lane": "paper_system",
                "title": "Run another AI review.",
                "body": "Re-score the same public record without adding new work.",
                "why": "Good for monitoring, weak as the next move if no new current evidence exists.",
                "time": "3 minutes",
                "href": "https://imagineer.aolabs.io/api/imagineer/ai-review",
                "urgency": "low",
                "role_alignment": 10,
                "bottleneck_relief": 8,
                "evidence_created": 3,
                "compounding": 10,
                "urgency_score": 2,
                "friction": 2,
                "gate_penalty": 0,
            },
        ]
        for candidate in candidates:
            candidate["score"] = max(
                0,
                min(
                    100,
                    candidate["role_alignment"]
                    + candidate["bottleneck_relief"]
                    + candidate["evidence_created"]
                    + candidate["compounding"]
                    + candidate["urgency_score"]
                    - candidate["friction"]
                    - candidate["gate_penalty"],
                ),
            )
        return candidates

    def _dimension_score(self, dimensions: list[dict[str, Any]], key: str) -> int:
        match = next((item for item in dimensions if item.get("key") == key), None)
        return int((match or {}).get("score") or 0)

    def _next_action(self, state: dict[str, Any], weakest: dict[str, Any], allow_openai: bool = False) -> dict[str, Any]:
        if allow_openai:
            generated = self._openai_action(state, weakest)
            if generated:
                return generated

        key = weakest["key"]
        review_count = len(state.get("reviews", []))
        actions = {
            "mechanical_depth": {
                "lane": key,
                "title": "Make one mechanism calculation visible.",
                "body": "Pick one Sarrus or FluxCell mechanism and publish a compact load, travel, stiffness, force, tolerance, or actuation note that reads as mechanically rigorous.",
                "why": "The verified WDI ride-development lead centers mechanical SME judgment, design review, safety, reliability, standards, kinematics, machine design, FEA/CAD, and prototype/development work.",
            },
            "creative_prototyping": {
                "lane": key,
                "title": "Turn one idea into a showable artifact.",
                "body": "Take one prototype detail and make it visible as a photo, sketch, clip, test fixture, bench protocol, or before/after iteration log.",
                "why": "WDI R&D values prototypes that evolve requirements as the team learns.",
            },
            "physical_experience": {
                "lane": key,
                "title": "Translate the technical result into guest value.",
                "body": "Write the one-minute explanation: what someone feels, sees, believes, or can do because this mechanism exists.",
                "why": "The target is not just machinery; it is human-facing physical interaction.",
            },
            "leadership_network": {
                "lane": key,
                "title": "Make the FluxCell linkage test." if review_count else "Run the autonomous AI review.",
                "body": (
                    "Prototype the actuator-less array, clip-program the shape, and check overhang motion."
                    if review_count
                    else "Pull current role, profile, portfolio, and Disney Research context into the AI review, then route the result into one system-owned update."
                ),
                "why": "The principal gap is current ownership. The source now points to a first measurable FluxCell build.",
            },
            "application_packet": {
                "lane": key,
                "title": "Tighten the Glendale profile.",
                "body": "Convert one project into a role-fit artifact: title, thumbnail, 90-second story, technical figure, your contribution, and the next build.",
                "why": "The verified WDI lead asks for advanced mechanical judgment, design sensibility, communication, and prototype/development evidence; principal scope remains unverified.",
            },
            "paper_system": {
                "lane": key,
                "title": "Log the system like a methods section.",
                "body": "Record today's state, chosen action, bottleneck, expected signal, and result so the career machine becomes analyzable instead of motivational.",
                "why": "A publishable system needs state, policy, interventions, outcomes, and guardrails.",
            },
        }
        return actions.get(key, actions["application_packet"])

    def _openai_action(self, state: dict[str, Any], weakest: dict[str, Any]) -> dict[str, Any] | None:
        if not os.getenv("OPENAI_API_KEY"):
            return None
        try:
            from openai import OpenAI

            model = self._openai_model()
            client = OpenAI(timeout=8)
            prompt = {
                "target": state["target"],
                "positioning": state["positioning"],
                "weakest_dimension": weakest,
                "active_experiment": self._active_experiment(state),
                "recent_events": state["events"][:8],
                "guardrails": state["guardrails"],
            }
            response = client.responses.create(
                model=model,
                instructions=(
                    "Return strict JSON for one ethical, concrete career-compounding action. "
                    "Keys: lane, title, body, why. No fabrication, spam, or unapproved applications."
                ),
                input="Return json only.\n" + json.dumps(prompt, ensure_ascii=True),
                text={"format": {"type": "json_object"}},
                max_output_tokens=800,
            )
            raw = self._response_output_text(response) or "{}"
            parsed = json.loads(raw)
            return {
                "lane": str(parsed.get("lane") or weakest["key"])[:80],
                "title": str(parsed.get("title") or "Advance one verified signal.")[:140],
                "body": str(parsed.get("body") or weakest["next_signal"])[:800],
                "why": str(parsed.get("why") or weakest["target_signal"])[:800],
            }
        except Exception as exc:
            return {
                "lane": weakest["key"],
                "title": "Run the deterministic fallback action.",
                "body": self._signal_action_for_dimension(weakest["key"]),
                "why": f"OpenAI planner unavailable, so the guardrailed local policy selected the weakest role-fit signal. Planner error: {type(exc).__name__}.",
            }

    def _openai_model(self) -> str:
        return os.getenv("IMAGINEER_OPENAI_MODEL", "gpt-5-mini").strip() or "gpt-5-mini"

    def _signal_action_for_dimension(self, key: str) -> str:
        signals = {
            "mechanical_depth": "Digitize the Sarrus force, stiffness, and hysteresis curves with uncertainty and test conditions.",
            "creative_prototyping": "Make one prototype iteration visible as a before/after artifact.",
            "physical_experience": "Turn the Sarrus object-manipulation clip into a concise guest-facing motion sequence.",
            "leadership_network": "Make visible ownership and source depth stronger; ask before any external outreach.",
            "application_packet": "Add the final active-rung profile pieces: demo reel, CV bullets, and role-specific narrative.",
            "paper_system": "Add scheduled runs, evaluation history, and outcome tracking so the loop proves persistence.",
        }
        return signals.get(key, "Advance one verified signal.")

    def _dimension_label(self, key: str, fallback: str) -> str:
        labels = {
            "leadership_network": "Principal signal",
            "application_packet": "Glendale profile",
            "paper_system": "Autonomous system",
        }
        return labels.get(key, fallback)

    def _dimension_target_signal(self, key: str, fallback: str) -> str:
        signals = {
            "leadership_network": "Visible ownership, technical direction, source depth, and approval-gated external validation.",
        }
        return signals.get(key, fallback)

    def _confidence_label(self, fit_score: int) -> str:
        if fit_score >= 80:
            return "strong_and_visible"
        if fit_score >= 65:
            return "credible_but_needs_signal"
        if fit_score >= 50:
            return "promising_needs_profile"
        return "early_system_build"

    def _title_for_kind(self, kind: str) -> str:
        titles = {
            "proof": "Work logged",
            "outreach": "Relationship signal logged",
            "portfolio": "Portfolio artifact logged",
            "paper": "Methods signal logged",
            "application": "Application profile signal logged",
        }
        return titles.get(kind, "Imagineer signal logged")
