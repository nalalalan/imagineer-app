from __future__ import annotations

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
    "for human-facing physical experiences."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


DEFAULT_STATE: dict[str, Any] = {
    "active_experiment_id": "autonomous-ai-reviewer-v0",
    "target": {
        "north_star_title": "Principal R&D Imagineer - Mechanical Engineer",
        "active_rung_title": "WDI Research & Development Imagineer - Mechanical Design Engineer",
        "company": "Walt Disney Imagineering R&D",
        "location": "Glendale, California",
        "active_listing_job_id": "10146734",
        "active_listing_posted": "2026-04-08",
        "active_listing_url": "https://jobs.disneycareers.com/job/glendale/wdi-research-and-development-imagineer-mechanical-design-engineer/391/93733641696",
        "north_star_note": "Use the principal title as the north-star profile; verify any open principal posting before applying.",
    },
    "positioning": POSITIONING_LINE,
    "guardrails": [
        "No fabricated credentials, projects, relationships, recommendations, or outcomes.",
        "No spam or fake outreach. Human approval is required before applications, direct referrals, sensitive messages, or external requests.",
        "Optimize for truthful evidence: working prototypes, clear figures, test logs, concise writing, and real conversations.",
        "Respect Disney and third-party intellectual property; focus on Alan-owned public work and general role-fit evidence.",
    ],
    "reviewer": {
        "mode": "autonomous_ai",
        "model": "gpt-5.5",
        "scope": "whole_public_ao_labs_graph",
        "approval_boundary": "AI critique can run autonomously. Human approval is required before any external outreach or application action.",
        "source_urls": [
            "https://aolabs.io/",
            "https://jobs.disneycareers.com/job/glendale/wdi-research-and-development-imagineer-mechanical-design-engineer/391/93733641696",
            "https://imagineer.aolabs.io/proof-packet.html",
            "https://imagineer.aolabs.io/imagineer-autonomous-position-system.pdf",
            "https://cv.aolabs.io",
            "https://cv.aolabs.io/alan-nguyen-pham-cv.pdf",
            "https://sarrus.aolabs.io",
            "https://fluxcell.aolabs.io",
            "https://relay.aolabs.io",
            "https://relaylive.aolabs.io",
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
            "reconfigurable mechanisms, morphing interfaces, research papers, public project surfaces, "
            "and autonomous systems across AO Labs."
        ),
        "current_role": "Mechanical engineering PhD candidate at Worcester Polytechnic Institute; expected 2027.",
        "technical_pattern": [
            "Soft robotics, compliant mechanisms, continuum robots, modular soft robots, morphing surfaces, haptics, and human-robot interaction.",
            "First-author Sarrus work on monolithically printed pneumatic cells that reconfigure into surfaces and robot bodies.",
            "FluxCell work exploring printed electropermanent actuation for Sarrus cells.",
            "Mechanical design experience spanning CAD, prototype fabrication, testing, dynamics, sensors, and physical systems.",
        ],
        "builder_pattern": [
            "AO Labs turns projects into public surfaces, papers, dashboards, media walls, and autonomous loops.",
            "Relay shows the user's preference for operational systems with metrics, state, experiments, logs, and money/result tracking.",
            "Imagineer should use the same operational style for career conversion: evidence intake, source review, critique, action selection, and logged progress.",
        ],
        "wdi_relevance": [
            "Strongest fit is embodied creative R&D: mechanisms that produce readable physical motion, shape change, responsiveness, surprise, or believable object behavior.",
            "The gap is not motivation; the gap is reviewer-proof evidence that makes mechanical credibility and show value obvious from public artifacts.",
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
            "summary": "Printed electropermanent actuation concept for Sarrus cells.",
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
            "label": "Human-facing physical experience",
            "score": 68,
            "target_signal": "Guest-facing language: believability, surprise, touch, motion, repeatability, safety, and show value.",
        },
        {
            "key": "leadership_network",
            "label": "Principal-level network",
            "score": 34,
            "target_signal": "Real conversations, referrals, project collaborators, and evidence of technical leadership.",
        },
        {
            "key": "application_packet",
            "label": "Glendale packet",
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
            "name": "Autonomous AI reviewer v0",
            "status": "active",
            "hypothesis": (
                "If the system repeatedly critiques Alan-owned evidence against live WDI R&D signals, "
                "the next useful artifact becomes obvious without waiting for a human reviewer."
            ),
            "variable": "Source coverage and critique specificity.",
            "success_metric": "One autonomous review run, a ranked gap list, and one concrete packet or portfolio improvement selected from the review.",
            "started_at": "2026-05-06",
        },
        {
            "id": "wdi-proof-packet-v0",
            "name": "WDI proof packet v0",
            "status": "supporting",
            "hypothesis": (
                "If Alan converts existing soft-robotics work into a concise WDI R&D proof packet, "
                "the gap shifts from unclear fit to visible studio relevance."
            ),
            "variable": "Translation quality from technical result to human-facing physical experience.",
            "success_metric": "Five proof logs, one reviewer-ready portfolio artifact, and one AI critique cycle inside seven days.",
            "started_at": "2026-05-06",
        },
        {
            "id": "principal-signal-map-v0",
            "name": "Principal signal map",
            "status": "queued",
            "hypothesis": "A principal-track map exposes which missing signals matter most: leadership, autonomy, vendor work, or shop-floor depth.",
            "variable": "Gap priority order.",
            "success_metric": "A ranked 12-signal checklist with evidence links and a concrete owner/action for each signal.",
            "started_at": None,
        },
        {
            "id": "nature-methods-v0",
            "name": "Adaptive career methods paper",
            "status": "queued",
            "hypothesis": "The same machinery used for autonomous revenue can become a publishable career-conversion system if evidence and ethics are first-class.",
            "variable": "Outcome metric design.",
            "success_metric": "A methods outline with state schema, decision policy, intervention log, and evaluation metrics.",
            "started_at": None,
        },
    ],
    "events": [],
    "reviews": [],
    "journal": [
        {
            "id": "seed-001",
            "created_at": "2026-05-06T12:00:00+00:00",
            "title": "Target locked",
            "body": "Aim the system at WDI R&D in Glendale, with the active WDI R&D mechanical design role as the immediate live rung and Principal R&D Imagineer as the north star.",
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
        self._state_lock = threading.RLock()

    def ops_check(self) -> dict[str, Any]:
        state = self._load_state()
        dimensions = self._score_dimensions(state)
        weakest = min(dimensions, key=lambda item: item["score"])
        next_action = self._next_action(state, weakest)
        active_experiment = self._active_experiment(state)
        proof_events = [event for event in state["events"] if event.get("kind") == "proof"]
        outreach_events = [event for event in state["events"] if event.get("kind") == "outreach"]
        cycle_events = [event for event in state["events"] if event.get("kind") == "daily_cycle"]
        reviewer_ready_events = [event for event in state["events"] if "reviewer_ready" in event.get("tags", [])]
        reviewer_ready_portfolio = [item for item in state["portfolio"] if "reviewer_ready" in item.get("tags", [])]
        ai_reviews = state.get("reviews", [])
        fit_score = round(sum(item["score"] for item in dimensions) / max(len(dimensions), 1))

        return {
            "status": "building_position_machine_v1",
            "generated_at": _utc_now(),
            "target": state["target"],
            "positioning": state["positioning"],
            "fit_score": fit_score,
            "confidence": self._confidence_label(fit_score),
            "current_bottleneck": weakest,
            "next_action": next_action,
            "reviewer": self._reviewer_report_from_state(state, compact=True),
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
            "paper": self.paper_outline(compact=True),
            "weekly_paper": self.weekly_paper(compact=True),
            "artifacts": {
                "paper_pdf": "https://aolabs.io/imagineer/imagineer-autonomous-position-system.pdf",
                "paper_pdf_custom_domain": "https://imagineer.aolabs.io/imagineer-autonomous-position-system.pdf",
                "live_backend": "https://imagineer-app-production.up.railway.app/api/imagineer/ops-check",
            },
            "system_health": {
                "state_path": str(self.state_path),
                "openai_planner": bool(os.getenv("OPENAI_API_KEY")),
                "openai_model": self._openai_model() if os.getenv("OPENAI_API_KEY") else None,
                "storage": "json_runtime_state",
                "write_surface": "events_and_ai_reviews",
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
                "claim": "An adaptive, guardrailed agent system can convert an ambiguous career target into daily evidence-building interventions.",
            },
            {
                "title": "System Architecture",
                "claim": "The loop maintains target-role state, role-signal dimensions, event logs, experiments, and a policy for choosing the next action.",
            },
            {
                "title": "Decision Policy",
                "claim": "Actions are chosen by the weakest verified role-fit signal, with optional language-model planning constrained by evidence and ethics.",
            },
            {
                "title": "Evaluation",
                "claim": "The system tracks proof velocity, reviewer-ready artifacts, review paths, application readiness, and conversion milestones.",
            },
            {
                "title": "Guardrails",
                "claim": "The system forbids fabrication, spam, credential inflation, and unapproved applications or sensitive outreach.",
            },
            {
                "title": "Case Study",
                "claim": "The first deployment targets WDI R&D mechanical roles using Alan-owned soft robotics, actuation, and creative prototyping evidence.",
            },
        ]
        if compact:
            return {
                "working_title": "Adaptive Evidence Systems for Career Conversion in Embodied Creative R&D",
                "thesis": "Career progress becomes optimizable when evidence, decisions, experiments, and ethics are logged as a closed-loop system.",
                "section_count": len(sections),
            }
        return {
            "working_title": "Adaptive Evidence Systems for Career Conversion in Embodied Creative R&D",
            "thesis": "Career progress becomes optimizable when evidence, decisions, experiments, and ethics are logged as a closed-loop system.",
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
                "link": "https://imagineer.aolabs.io/proof-packet.html",
                "tags": ["ai_reviewer", "paper_system", "application_packet", "mechanical_depth"],
                "impact": 2,
            }
            state["events"].insert(0, event)
            state["events"] = state["events"][:300]
            self._append_journal_from_event(state, event)
            self._save_state(state)
            return {"ok": True, "review": review, "ops": self.ops_check()}

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
                    "title": "Weekly progress paper updated",
                    "body": paper["headline_result"],
                    "tags": ["weekly_paper", "paper_system", "application_packet"],
                },
            )
            state["journal"] = state["journal"][:120]
            self._save_state(state)
            return {"ok": True, "paper": paper, "ops": self.ops_check()}

    def record_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._state_lock:
            state = self._load_state()
            event = self._event_from_payload(payload)
            state["events"].insert(0, event)
            state["events"] = state["events"][:300]
            self._append_journal_from_event(state, event)
            self._save_state(state)
            return {"ok": True, "event": event, "ops": self.ops_check()}

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
                    "This weekly paper reports the progress of an autonomous, guardrailed career-conversion system "
                    "targeting WDI R&D mechanical Imagineering roles. The system converts Alan-owned evidence, "
                    "daily actions, experiments, and guardrails into an adaptive decision loop."
                ),
            },
            {
                "heading": "Methods Update",
                "body": (
                    "The system scores six role-fit dimensions, selects the weakest verified signal, records proof events, "
                    "runs daily cycles, and maintains a research journal. OpenAI planning is used only when configured; "
                    "otherwise the local deterministic policy chooses the next ethical action."
                ),
            },
            {
                "heading": "Weekly Results",
                "body": (
                    f"This week has {len(recent_events)} logged events, {ops['evidence']['proof_events']} total proof logs, "
                    f"{ops['evidence']['daily_cycles']} daily cycles, {ops['evidence']['reviewer_ready_artifacts']} reviewer-ready artifacts, "
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
                    "Progress must come from truthful evidence, real artifacts, useful relationships, and visible technical work."
                ),
            },
        ]
        return {
            "id": str(uuid.uuid4()),
            "week_id": week_id,
            "title": "Weekly Progress Paper: Autonomous Imagineer Position System",
            "status": "published_weekly_snapshot" if persisted else "live_preview_until_weekly_snapshot",
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
        next_action = self._next_action(state, weakest)
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
            "reviewer": self._reviewer_report_from_state(state, compact=True),
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
        }

    def _reviewer_report_from_state(self, state: dict[str, Any], compact: bool = False) -> dict[str, Any]:
        latest = next(iter(state.get("reviews", [])), None)
        report = {
            "mode": state.get("reviewer", {}).get("mode", "autonomous_ai"),
            "scope": state.get("reviewer", {}).get("scope", "whole_public_ao_labs_graph"),
            "status": "review_ready" if latest else "not_run",
            "approval_boundary": state.get("reviewer", {}).get("approval_boundary", ""),
            "latest": self._compact_review(latest) if latest else None,
            "review_count": len(state.get("reviews", [])),
            "source_count": len(state.get("reviewer", {}).get("source_urls", [])),
        }
        if compact:
            return report
        return {
            **report,
            "reviews": state.get("reviews", [])[:10],
            "source_urls": state.get("reviewer", {}).get("source_urls", []),
        }

    def _compact_review(self, review: dict[str, Any] | None) -> dict[str, Any] | None:
        if not review:
            return None
        next_actions = review.get("next_actions") or []
        return {
            "id": review.get("id"),
            "created_at": review.get("created_at"),
            "score": review.get("score"),
            "verdict": self._review_display_text(
                review.get("verdict"),
                review.get("reviewer_summary"),
                "Credible WDI R&D direction; the public packet still needs denser mechanical proof.",
            ),
            "top_issue": self._review_display_text(
                review.get("top_issue"),
                None,
                (
                    "The current public packet still needs one mechanism-centered Sarrus or FluxCell artifact with "
                    "geometry, travel, load path, constraints, actuation margin, prototype build, test result, and iteration."
                ),
            ),
            "why_it_matters": review.get("why_it_matters"),
            "best_existing_evidence": self._string_list(review.get("best_existing_evidence"), 5, 260),
            "evidence_gaps": self._string_list(review.get("evidence_gaps"), 6, 260),
            "packet_edits": self._string_list(review.get("packet_edits"), 5, 260),
            "reviewer_summary": review.get("reviewer_summary"),
            "next_action": next_actions[0] if next_actions else None,
            "source_count": review.get("source_count"),
            "model": review.get("model"),
            "fallback_reason": review.get("fallback_reason"),
        }

    def _collect_review_sources(self, state: dict[str, Any], ops: dict[str, Any]) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []

        system_snapshot = {
            "target": state["target"],
            "positioning": state["positioning"],
            "fit_score": ops["fit_score"],
            "current_bottleneck": ops["current_bottleneck"],
            "next_action": ops["next_action"],
            "active_experiment": ops["active_experiment"],
            "dimensions": ops["dimensions"],
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
        return sources[:28]

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
        if "imagineer.aolabs.io/proof-packet" in lowered:
            return "WDI proof packet"
        if "imagineer.aolabs.io/imagineer-autonomous-position-system" in lowered:
            return "Imagineer paper PDF"
        if "sarrus.aolabs.io" in lowered:
            return "Sarrus portfolio"
        if "fluxcell.aolabs.io" in lowered:
            return "FluxCell portfolio"
        if "relaylive.aolabs.io" in lowered:
            return "Relay live dashboard"
        if "relay.aolabs.io" in lowered:
            return "Relay product"
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
                "review_goal": "Autonomously critique Alan Pham's WDI R&D Imagineering proof packet and portfolio fit.",
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
                    "You are an evidence-only autonomous reviewer for a WDI R&D mechanical Imagineering target. "
                    "Use only the supplied sources. Do not invent credentials, contacts, referrals, or outcomes. "
                    "Return strict JSON with keys: verdict, score, top_issue, why_it_matters, "
                    "best_existing_evidence, evidence_gaps, next_actions, packet_edits, reviewer_summary. "
                    "next_actions must be an array of objects with title, body, expected_signal, and source."
                ),
                input="Return json only.\n" + json.dumps(prompt, ensure_ascii=True),
                text={"format": {"type": "json_object"}},
                max_output_tokens=3000,
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
                    "title": str(item.get("title") or "Improve one proof artifact.")[:140],
                    "body": str(item.get("body") or "")[:700],
                    "expected_signal": str(item.get("expected_signal") or "")[:260],
                    "source": str(item.get("source") or "")[:220],
                }
            )
            if len(next_actions) >= 5:
                break

        return {
            "verdict": str(parsed.get("verdict") or "Review completed; packet needs sharper evidence.")[:220],
            "score": max(0, min(int(parsed.get("score") or 0), 100)),
            "top_issue": str(parsed.get("top_issue") or "The packet needs one concrete proof point.")[:260],
            "why_it_matters": str(parsed.get("why_it_matters") or "")[:800],
            "best_existing_evidence": self._string_list(parsed.get("best_existing_evidence"), 5, 220),
            "evidence_gaps": self._string_list(parsed.get("evidence_gaps"), 6, 260),
            "next_actions": next_actions,
            "packet_edits": self._string_list(parsed.get("packet_edits"), 6, 260),
            "reviewer_summary": str(parsed.get("reviewer_summary") or "")[:900],
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
            "top_issue": "The packet still needs one hard mechanical validation artifact that connects directly to a believable human-facing physical experience.",
            "why_it_matters": (
                "The WDI R&D role asks for hands-on mechanical design, prototype testing, loads, moments, forces, CAD, "
                "iteration, and collaboration across creative and technical disciplines. The current packet is aligned, "
                "but the reviewer-grade proof should make one mechanism impossible to dismiss."
            ),
            "best_existing_evidence": [
                "Sarrus gives the core soft robotics mechanism and physical morphing surface proof.",
                "FluxCell gives a concrete actuation route for moving beyond tethered pneumatic demos.",
                "The proof packet already targets WDI R&D language instead of a generic academic robotics framing.",
            ],
            "evidence_gaps": [
                "One compact force/load/travel/stiffness calculation tied to the mechanism.",
                "One visual before/after prototype iteration that shows testing changed the design.",
                "One 60-90 second demo or storyboard showing what a guest would see, feel, or believe.",
                "One explicit SolidWorks/GD&T/manufacturing detail for mechanical design credibility.",
            ],
            "next_actions": [
                {
                    "title": "Add one reviewer-proof mechanical figure.",
                    "body": "Create a single figure or packet block with Sarrus cell travel, load path, estimated force or stiffness, prototype material/process, and what changed after testing.",
                    "expected_signal": "Mechanical reviewer can see loads, motion, fabrication, and iteration without asking for missing basics.",
                    "source": source_names or "Live Imagineer state",
                },
                {
                    "title": "Add one guest-facing demo frame.",
                    "body": "Pair the mechanical figure with one storyboard frame: what the mechanism makes an object do, and why that motion would feel alive, responsive, or surprising.",
                    "expected_signal": "The work reads as WDI physical experience R&D, not only soft robotics research.",
                    "source": "Proof packet and portfolio sources",
                },
            ],
            "packet_edits": [
                "Replace the human review ask with an autonomous AI review contract.",
                "Add a compact validation block: mechanism, measurement, failure, design change, next proof.",
                "Add one role-fit line that names CAD, loads/forces, prototype fabrication, and test iteration.",
            ],
            "reviewer_summary": (
                "Autonomous fallback review used available live state and public sources. The next compounding move is a "
                "single mechanical validation artifact, not more positioning text."
            ),
        }

    def _string_list(self, value: Any, limit: int, max_chars: int) -> list[str]:
        if not isinstance(value, list):
            return []
        items: list[str] = []
        for item in value:
            text = self._review_list_item_text(item)
            if text:
                items.append(text[:max_chars].rstrip())
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
                return self._clean_inline_text(f"{source}: {evidence}")
            if gap and detail:
                return self._clean_inline_text(f"{gap}: {detail}")
            if gap:
                return self._clean_inline_text(gap)
            if section and edit:
                return self._clean_inline_text(f"{section}: {edit}")
            if title and body:
                return self._clean_inline_text(f"{title}: {body}")
            if edit:
                return self._clean_inline_text(edit)
            if evidence:
                return self._clean_inline_text(evidence)
            return self._clean_inline_text(json.dumps(item, ensure_ascii=True, sort_keys=True))
        return self._clean_inline_text(str(item or ""))

    def _review_display_text(self, primary: Any, fallback: Any, default: str) -> str:
        text = self._clean_inline_text(str(primary or ""))
        if text and text[-1] in ".!?":
            return text
        fallback_text = self._clean_inline_text(str(fallback or ""))
        if fallback_text:
            return self._first_sentence(fallback_text)
        return default

    def _first_sentence(self, text: str) -> str:
        for marker in (". ", "! ", "? "):
            index = text.find(marker)
            if index > 0:
                return text[: index + 1]
        return text

    def _clean_inline_text(self, text: str) -> str:
        return " ".join(text.strip().split())

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
        for list_key in ("dimensions", "experiments", "portfolio", "guardrails", "events", "reviews", "journal", "weekly_papers"):
            merged.setdefault(list_key, copy.deepcopy(DEFAULT_STATE[list_key]))
        self._merge_list_by_key(merged, "portfolio", "name")
        self._merge_list_by_key(merged, "experiments", "id")
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
        body = event["notes"] or event["link"] or "Evidence logged."
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
        scored: list[dict[str, Any]] = []
        for dimension in state["dimensions"]:
            key = dimension["key"]
            event_points = sum(
                int(event.get("impact") or 1)
                for event in events
                if key in event.get("tags", [])
            )
            portfolio_points = portfolio_tags.count(key)
            daily_points = sum(1 for event in events if event.get("kind") == "daily_cycle" and key in event.get("tags", []))
            base_score = int(dimension["score"])
            event_score = event_points * 4
            portfolio_score = portfolio_points * 2
            score = min(100, base_score + event_score + portfolio_score + daily_points)
            scored.append(
                {
                    "key": key,
                    "label": self._dimension_label(key, dimension["label"]),
                    "score": score,
                    "gap": max(0, 100 - score),
                    "target_signal": self._dimension_target_signal(key, dimension["target_signal"]),
                    "next_signal": self._signal_action_for_dimension(key),
                    "score_basis": (
                        f"Base {base_score}; +{event_score} from logged event impact; "
                        f"+{portfolio_score} from portfolio evidence tags; +{daily_points} from daily-cycle evidence; capped at 100."
                    ),
                }
            )
        return scored

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

    def _next_action(self, state: dict[str, Any], weakest: dict[str, Any], allow_openai: bool = False) -> dict[str, Any]:
        if allow_openai:
            generated = self._openai_action(state, weakest)
            if generated:
                return generated

        key = weakest["key"]
        actions = {
            "mechanical_depth": {
                "lane": key,
                "title": "Make one mechanism calculation visible.",
                "body": "Pick one Sarrus or FluxCell mechanism and publish a compact load, travel, stiffness, force, tolerance, or actuation note that a mechanical reviewer can trust.",
                "why": "The active listing asks for mechanical design, prototyping, loads, moments, forces, CAD, FEA/GD&T, and hands-on engineering.",
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
                "why": "The target is not just machinery; it is human-facing physical experience.",
            },
            "leadership_network": {
                "lane": key,
                "title": "Run the autonomous AI reviewer.",
                "body": "Pull current role, packet, portfolio, and Disney Research context into the AI reviewer, then route the top critique into one proof-packet or portfolio improvement.",
                "why": "The principal north star needs rigorous external-style critique, but the first review loop can be autonomous and repeatable before any human outreach.",
            },
            "application_packet": {
                "lane": key,
                "title": "Sharpen the Glendale packet.",
                "body": "Convert one project into a role-fit artifact: title, thumbnail, 90-second story, technical figure, your contribution, and the next build.",
                "why": "The active role asks for a portfolio that demonstrates a foundation in mechanical design.",
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
        return os.getenv("IMAGINEER_OPENAI_MODEL", "gpt-5.5").strip() or "gpt-5.5"

    def _signal_action_for_dimension(self, key: str) -> str:
        signals = {
            "mechanical_depth": "Add one trustworthy mechanical calculation or CAD/manufacturing detail.",
            "creative_prototyping": "Make one prototype iteration visible as a clean artifact.",
            "physical_experience": "Tie one technical result to a felt human experience.",
            "leadership_network": "Run autonomous critique first; use human review only as an approved escalation.",
            "application_packet": "Make one role-specific portfolio item sharper.",
            "paper_system": "Log state, action, intervention, and result for the methods trail.",
        }
        return signals.get(key, "Advance one verified signal.")

    def _dimension_label(self, key: str, fallback: str) -> str:
        labels = {
            "leadership_network": "Review intelligence",
        }
        return labels.get(key, fallback)

    def _dimension_target_signal(self, key: str, fallback: str) -> str:
        signals = {
            "leadership_network": "Repeatable critique, role calibration, source coverage, and optional approved human escalation.",
        }
        return signals.get(key, fallback)

    def _confidence_label(self, fit_score: int) -> str:
        if fit_score >= 80:
            return "strong_and_visible"
        if fit_score >= 65:
            return "credible_but_needs_signal"
        if fit_score >= 50:
            return "promising_needs_packet"
        return "early_system_build"

    def _title_for_kind(self, kind: str) -> str:
        titles = {
            "proof": "Proof logged",
            "outreach": "Relationship signal logged",
            "portfolio": "Portfolio artifact logged",
            "paper": "Methods signal logged",
            "application": "Application packet signal logged",
        }
        return titles.get(kind, "Imagineer signal logged")
