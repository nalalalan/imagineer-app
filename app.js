const railwayApiBase = "https://imagineer-app-production.up.railway.app";
const sameOriginApiHosts = new Set(["localhost", "127.0.0.1", "imagineer-app-production.up.railway.app"]);
const apiBase = window.IMAGINEER_API_BASE || (sameOriginApiHosts.has(window.location.hostname) ? "" : railwayApiBase);

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
    title: "Create one real review path.",
    body: "Identify one WDI-adjacent reviewer and prepare a specific review ask around one artifact."
  },
  active_experiment: {
    name: "WDI proof packet v0",
    status: "active",
    hypothesis: "Convert existing soft-robotics work into concise WDI R&D evidence."
  },
  evidence: {
    proof_events: 0,
    daily_cycles: 0,
    reviewer_ready_artifacts: 0,
    journal_entries: 0
  },
  weekly_paper: {
    week_id: "not loaded",
    status: "fallback",
    headline_result: "Waiting for live backend.",
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
  const timeout = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(`${apiBase}${path}`, {
      cache: "no-store",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
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

async function updatePaper() {
  const button = $("#update-paper");
  button.disabled = true;
  button.textContent = "Updating";
  try {
    const result = await request("/api/imagineer/weekly-paper/run", { method: "POST", body: "{}" });
    render(result.ops, true);
  } catch {
    render(fallbackOps, false);
  } finally {
    button.disabled = false;
    button.textContent = "Update paper";
  }
}

function render(ops, connected) {
  const evidence = ops.evidence || {};
  const bottleneck = ops.current_bottleneck || {};
  const experiment = ops.active_experiment || {};
  const paper = ops.weekly_paper || {};
  const action = ops.next_action || {};

  setText("#backend-state", connected ? "online" : "fallback");
  $("#backend-state").className = connected ? "is-ok" : "is-warn";
  setText("#backend-detail", connected ? "live Railway API" : "static fallback");
  setText("#fit-score", Number.isFinite(ops.fit_score) ? ops.fit_score : "--");
  setText("#confidence", clean(ops.confidence));
  setText("#bottleneck", bottleneck.label || "--");
  setText("#bottleneck-detail", bottleneck.target_signal || "--");
  setText("#paper-week", paper.week_id || "--");
  setText("#paper-status", clean(paper.status));
  setText("#subtitle", `${ops.target?.active_rung_title || "WDI R&D mechanical role"} / ${ops.target?.location || "Glendale"}`);
  setText("#loop-title", experiment.name || "No active experiment");
  setText("#loop-state", clean(experiment.status || ops.status));
  setText("#loop-body", experiment.hypothesis || "--");
  setText("#system-job", "Watch the live role-fit state, update the paper, and surface the next constraint without fake progress.");
  setText("#action-title", action.title || "--");
  setText("#action-body", action.body || "--");
  setText("#paper-title", paper.title || "Weekly progress paper");
  setText("#paper-result", paper.headline_result || "--");
  setText("#metric-proof", evidence.proof_events ?? "--");
  setText("#metric-cycles", evidence.daily_cycles ?? "--");
  setText("#metric-reviewer", evidence.reviewer_ready_artifacts ?? "--");
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
  $("#journal").innerHTML = journal.slice(0, 5).map((item) => `
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
$("#update-paper").addEventListener("click", updatePaper);
loadState();
