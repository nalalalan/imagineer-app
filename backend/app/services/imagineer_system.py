from __future__ import annotations

import copy
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


POSITIONING_LINE = (
    "Mechanical PhD + soft robotics + creative prototyping + AI-assisted tools "
    "for human-facing physical experiences."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


DEFAULT_STATE: dict[str, Any] = {
    "target": {
        "north_star_title": "Principal R&D Imagineer - Mechanical Engineer",
        "active_rung_title": "WDI Research & Development Imagineer - Mechanical Design Engineer",
        "company": "Walt Disney Imagineering R&D",
        "location": "Glendale, California",
        "active_listing_job_id": "10146734",
        "active_listing_posted": "2026-04-08",
        "active_listing_url": "https://www.disneycareers.com/en/job/glendale/wdi-research-and-development-imagineer-mechanical-design-engineer/391/93733641696",
        "north_star_note": "Use the principal title as the north-star profile; verify any open principal posting before applying.",
    },
    "positioning": POSITIONING_LINE,
    "guardrails": [
        "No fabricated credentials, projects, relationships, recommendations, or outcomes.",
        "No spam or fake outreach. Human approval is required before applications, direct referrals, or sensitive messages.",
        "Optimize for truthful evidence: working prototypes, clear figures, test logs, concise writing, and real conversations.",
        "Respect Disney and third-party intellectual property; focus on Alan-owned public work and general role-fit evidence.",
    ],
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
            "id": "wdi-proof-packet-v0",
            "name": "WDI proof packet v0",
            "status": "active",
            "hypothesis": (
                "If Alan converts existing soft-robotics work into a concise WDI R&D proof packet, "
                "the gap shifts from unclear fit to visible studio relevance."
            ),
            "variable": "Translation quality from technical result to human-facing physical experience.",
            "success_metric": "Five proof logs, one reviewer-ready portfolio artifact, and one warm review request inside seven days.",
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
            "active_experiment": self._experiment_view(active_experiment, state),
            "dimensions": dimensions,
            "evidence": {
                "proof_events": len(proof_events),
                "outreach_events": len(outreach_events),
                "daily_cycles": len(cycle_events),
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
                "storage": "json_runtime_state",
                "write_surface": "events_only",
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

    def run_weekly_paper_update(self) -> dict[str, Any]:
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
        state = self._load_state()
        event = self._event_from_payload(payload)
        state["events"].insert(0, event)
        state["events"] = state["events"][:300]
        self._append_journal_from_event(state, event)
        self._save_state(state)
        return {"ok": True, "event": event, "ops": self.ops_check()}

    def run_daily_cycle(self) -> dict[str, Any]:
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
            return {"ok": True, "already_ran": True, "event": existing, "next_action": action, "ops": self.ops_check()}

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
        fit_score = round(sum(item["score"] for item in dimensions) / max(len(dimensions), 1))
        return {
            "target": state["target"],
            "fit_score": fit_score,
            "confidence": self._confidence_label(fit_score),
            "current_bottleneck": weakest,
            "next_action": next_action,
            "active_experiment": self._experiment_view(active_experiment, state),
            "dimensions": dimensions,
            "evidence": {
                "proof_events": len(proof_events),
                "outreach_events": len(outreach_events),
                "daily_cycles": len(cycle_events),
                "portfolio_items": len(state["portfolio"]),
                "reviewer_ready_artifacts": len(reviewer_ready_events) + len(reviewer_ready_portfolio),
                "journal_entries": len(state["journal"]),
            },
        }

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
        for list_key in ("dimensions", "experiments", "portfolio", "guardrails", "events", "journal", "weekly_papers"):
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
            score = min(100, int(dimension["score"]) + event_points * 4 + portfolio_points * 2 + daily_points)
            scored.append(
                {
                    "key": key,
                    "label": dimension["label"],
                    "score": score,
                    "gap": max(0, 100 - score),
                    "target_signal": dimension["target_signal"],
                    "next_signal": self._signal_action_for_dimension(key),
                }
            )
        return scored

    def _active_experiment(self, state: dict[str, Any]) -> dict[str, Any]:
        return next((item for item in state["experiments"] if item.get("status") == "active"), state["experiments"][0])

    def _experiment_view(self, experiment: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        start = experiment.get("started_at")
        proof_count = sum(1 for event in state["events"] if event.get("kind") == "proof")
        cycle_count = sum(1 for event in state["events"] if event.get("kind") == "daily_cycle")
        reviewer_ready = sum(1 for event in state["events"] if "reviewer_ready" in event.get("tags", []))
        reviewer_ready += sum(1 for item in state["portfolio"] if "reviewer_ready" in item.get("tags", []))
        warm_review = sum(1 for event in state["events"] if "warm_review" in event.get("tags", []))
        progress = {
            "proof_logs": proof_count,
            "daily_cycles": cycle_count,
            "reviewer_ready_artifacts": reviewer_ready,
            "warm_review_requests": warm_review,
            "target_proof_logs": 5,
            "target_reviewer_ready_artifacts": 1,
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
                "title": "Create one real review path.",
                "body": "Identify one WDI-adjacent engineer, designer, roboticist, professor, or creative technologist and draft a specific review ask around one artifact.",
                "why": "The principal north star requires trust, leadership signal, and relationships, not only private output.",
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

            model = os.getenv("IMAGINEER_OPENAI_MODEL", "gpt-4.1-mini")
            client = OpenAI(timeout=8)
            prompt = {
                "target": state["target"],
                "positioning": state["positioning"],
                "weakest_dimension": weakest,
                "active_experiment": self._active_experiment(state),
                "recent_events": state["events"][:8],
                "guardrails": state["guardrails"],
            }
            response = client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return strict JSON for one ethical, concrete career-compounding action. "
                            "Keys: lane, title, body, why. No fabrication, spam, or unapproved applications."
                        ),
                    },
                    {"role": "user", "content": json.dumps(prompt)},
                ],
            )
            raw = response.choices[0].message.content or "{}"
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

    def _signal_action_for_dimension(self, key: str) -> str:
        signals = {
            "mechanical_depth": "Add one trustworthy mechanical calculation or CAD/manufacturing detail.",
            "creative_prototyping": "Make one prototype iteration visible as a clean artifact.",
            "physical_experience": "Tie one technical result to a felt human experience.",
            "leadership_network": "Create one real review or relationship path.",
            "application_packet": "Make one role-specific portfolio item sharper.",
            "paper_system": "Log state, action, intervention, and result for the methods trail.",
        }
        return signals.get(key, "Advance one verified signal.")

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
