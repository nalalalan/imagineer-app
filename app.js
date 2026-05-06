const railwayApiBase = "https://imagineer-app-production.up.railway.app";
const sameOriginApiHosts = new Set(["localhost", "127.0.0.1", "imagineer-app-production.up.railway.app"]);
const apiBase = window.IMAGINEER_API_BASE || (sameOriginApiHosts.has(window.location.hostname) ? "" : railwayApiBase);
const paperName = "A proof-governed autonomy system for career conversion in embodied creative research and development";

const fallbackOps = {
  status: "static_fallback",
  generated_at: new Date().toISOString(),
  target: {
    north_star_title: "Principal R&D Imagineer - Mechanical Engineer",
    active_rung_title: "WDI Research & Development Imagineer - Mechanical Design Engineer",
    company: "Walt Disney Imagineering R&D",
    location: "Glendale, California"
  },
  positioning: "Mechanical PhD + soft robotics + creative prototyping + AI-assisted tools for human-facing physical experiences.",
  fit_score: 58,
  confidence: "fallback",
  current_bottleneck: {
    label: "Principal-level network",
    score: 34,
    target_signal: "Real conversations, referrals, project collaborators, and evidence of technical leadership."
  },
  next_action: {
    title: "Run the autonomous AI reviewer.",
    body: "Pull current role, packet, portfolio, and Disney Research context into one critique loop."
  },
  reviewer: {
    mode: "autonomous_ai",
    scope: "whole_public_ao_labs_graph",
    status: "not_run",
    latest: null
  },
  active_experiment: {
    name: "Autonomous AI reviewer v0",
    status: "active",
    hypothesis: "Critique current evidence against WDI R&D fit."
  },
  evidence: {
    proof_events: 0,
    daily_cycles: 0,
    ai_reviews: 0,
    reviewer_ready_artifacts: 0,
    journal_entries: 0
  },
  weekly_paper: {
    week_id: "not loaded",
    status: "fallback",
    updated_at: new Date().toISOString()
  },
  dimensions: [],
  journal: []
};

const $ = (selector) => document.querySelector(selector);

function setText(selector, value) {
  const node = $(selector);
  if (node) node.textContent = value ?? "--";
}

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || 8000);
  try {
    const response = await fetch(`${apiBase}${path}`, {
      method: options.method || "GET",
      cache: "no-store",
      headers: { "Content-Type": "application/json" },
      body: options.body ? JSON.stringify(options.body) : undefined,
      signal: controller.signal
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } finally {
    clearTimeout(timeout);
  }
}

async function loadState() {
  setText("#backend-state", "checking");
  try {
    const ops = await request("/api/imagineer/ops-check");
    render(ops, true);
  } catch {
    render(fallbackOps, false);
  }
}

async function runReview() {
  const button = $("#run-review");
  button.disabled = true;
  button.textContent = "Running";
  setText("#reviewer-status", "running");
  setText("#reviewer-detail", "collecting sources and critiquing packet");
  try {
    const result = await request("/api/imagineer/ai-review/run", { method: "POST", timeout: 30000 });
    render(result.ops || fallbackOps, true);
  } catch {
    setText("#reviewer-status", "failed");
    setText("#reviewer-detail", "review did not complete");
  } finally {
    button.disabled = false;
    button.textContent = "Run review";
  }
}

function render(ops, connected) {
  const evidence = ops.evidence || {};
  const bottleneck = ops.current_bottleneck || {};
  const experiment = ops.active_experiment || {};
  const paper = ops.weekly_paper || {};
  const action = ops.next_action || {};
  const target = ops.target || {};
  const reviewer = ops.reviewer || {};
  const latestReview = reviewer.latest || {};
  const reviewerAction = latestReview.next_action || {};

  setText("#backend-state", connected ? "online" : "fallback");
  $("#backend-state").className = connected ? "is-ok" : "is-warn";
  setText("#backend-detail", connected ? clean(ops.status) : "static fallback");
  setText("#fit-score", Number.isFinite(ops.fit_score) ? ops.fit_score : "--");
  setText("#confidence", clean(ops.confidence));
  setText("#subtitle", ops.positioning || "Mechanical research, creative prototyping, and human-facing physical experiences.");
  setText("#target-role", target.north_star_title || "Principal R&D Imagineer - Mechanical Engineer");
  setText("#target-location", `${target.company || "Walt Disney Imagineering R&D"} / ${target.location || "Glendale, California"}`);
  setText("#bottleneck", bottleneck.label || "--");
  setText("#bottleneck-detail", bottleneck.target_signal || "--");
  setText("#experiment-name", experiment.name || "No active experiment");
  setText("#experiment-status", clean(experiment.status || ops.status));
  setText("#action-title", action.title || "--");
  setText("#action-body", action.body || "--");
  setText("#reviewer-status", latestReview.verdict || clean(reviewer.status || "not run"));
  setText("#reviewer-detail", latestReview.top_issue || reviewerAction.title || clean(reviewer.scope || "Reviews the whole public AO Labs graph."));
  setText("#paper-name", paperName);
  setText("#metric-proof", evidence.proof_events ?? "--");
  setText("#metric-cycles", evidence.daily_cycles ?? "--");
  setText("#metric-ai-reviews", evidence.ai_reviews ?? "--");
  setText("#metric-journal", evidence.journal_entries ?? "--");
  setText("#updated-at", `updated ${formatDateTime(ops.generated_at || paper.updated_at)}`);
  renderDimensions(ops.dimensions || []);
  renderJournal(ops.journal || []);
}

function renderDimensions(dimensions) {
  $("#dimensions").innerHTML = dimensions.length
    ? dimensions.map((dimension) => {
      const score = Math.max(0, Math.min(Number(dimension.score) || 0, 100));
      return `
        <div class="dimension">
          <strong>${escapeHtml(dimension.label || dimension.key)}</strong>
          <div class="bar" aria-hidden="true"><i style="--score:${score}%"></i></div>
          <span class="score">${score}</span>
        </div>
      `;
    }).join("")
    : `<div class="dimension"><strong>No live dimensions</strong><span>Backend not loaded.</span><span class="score">--</span></div>`;
}

function renderJournal(journal) {
  $("#journal").innerHTML = journal.slice(0, 3).map((item) => `
    <div class="journal-item">
      <strong>${escapeHtml(item.title || "Log entry")}</strong>
      <span>${escapeHtml(item.body || "")}</span>
    </div>
  `).join("") || `<div class="journal-item"><strong>No entries loaded</strong><span>Waiting for live state.</span></div>`;
}

function clean(value) {
  return String(value || "--").replaceAll("_", " ");
}

function formatDateTime(value) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "--";
  return parsed.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

$("#refresh").addEventListener("click", loadState);
$("#run-review").addEventListener("click", runReview);
loadState();
