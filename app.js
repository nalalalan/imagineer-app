const railwayApiBase = "https://imagineer-app-production.up.railway.app";
const sameOriginApiHosts = new Set(["localhost", "127.0.0.1", "imagineer-app-production.up.railway.app"]);
const apiBase = window.IMAGINEER_API_BASE || (sameOriginApiHosts.has(window.location.hostname) ? "" : railwayApiBase);
const paperName = "A proof-governed autonomy system for career conversion in embodied creative research and development";

const fallbackOps = {
  status: "static_fallback",
  generated_at: new Date().toISOString(),
  target: {
    north_star_title: "Principal R&D Imagineer - Mechanical Engineer",
    company: "Walt Disney Imagineering R&D",
    location: "Glendale, California"
  },
  positioning: "Mechanical PhD + soft robotics + creative prototyping + AI-assisted tools for human-facing physical experiences.",
  fit_score: 58,
  confidence: "fallback",
  current_bottleneck: {
    label: "Review intelligence",
    score: 34,
    target_signal: "Repeatable critique, role calibration, source coverage, and optional approved human escalation.",
    next_signal: "Run autonomous critique first; use human review only as an approved escalation.",
    score_basis: "Fallback score because the live backend did not load."
  },
  next_action: {
    title: "Run the autonomous AI reviewer.",
    body: "Pull current role, packet, portfolio, and Disney Research context into one critique loop."
  },
  reviewer: {
    mode: "autonomous_ai",
    model: "gpt-5.5",
    scope: "whole_public_ao_labs_graph",
    status: "not_run",
    review_count: 0,
    source_count: 0,
    approval_boundary: "Human approval is required before external outreach or application actions.",
    latest: null
  },
  evidence: {
    proof_events: 0,
    daily_cycles: 0,
    ai_reviews: 0,
    journal_entries: 0
  },
  weekly_paper: {
    status: "fallback",
    updated_at: new Date().toISOString()
  },
  dimensions: [
    {
      key: "review_intelligence",
      label: "Review intelligence",
      score: 34,
      target_signal: "Whether the system can critique the public portfolio against WDI-style mechanical R&D expectations.",
      next_signal: "Generate a live AI reviewer report from current sources.",
      score_basis: "Static fallback; the live reviewer state was unavailable."
    }
  ],
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
  setText("#reviewer-detail", "collecting public sources and generating critique");
  setText("#report-generated", "Running the reviewer. This can take about a minute.");
  try {
    const result = await request("/api/imagineer/ai-review/run", { method: "POST", timeout: 210000 });
    render(result.ops || fallbackOps, true);
  } catch {
    setText("#reviewer-status", "not completed");
    setText("#reviewer-detail", "the reviewer run timed out or returned an error");
    setText("#report-generated", "The last reviewer run did not complete in the browser.");
  } finally {
    button.disabled = false;
    button.textContent = "Run review";
  }
}

function render(ops, connected) {
  const evidence = ops.evidence || {};
  const bottleneck = ops.current_bottleneck || {};
  const paper = ops.weekly_paper || {};
  const target = ops.target || {};
  const reviewer = ops.reviewer || {};
  const latestReview = reviewer.latest || {};
  const reviewerAction = latestReview.next_action || ops.next_action || {};
  const generatedAt = latestReview.created_at || ops.generated_at || paper.updated_at;

  setText("#backend-state", connected ? "online" : "fallback");
  $("#backend-state").className = connected ? "is-ok" : "is-warn";
  setText("#backend-detail", connected ? clean(ops.status) : "static fallback");
  setText("#fit-score", Number.isFinite(ops.fit_score) ? ops.fit_score : "--");
  setText("#confidence", clean(ops.confidence));
  setText("#target-role", target.north_star_title || "Principal R&D Imagineer - Mechanical Engineer");
  setText("#target-location", `${target.company || "Walt Disney Imagineering R&D"} / ${target.location || "Glendale, California"}`);
  setText("#bottleneck", bottleneck.label || "--");
  setText("#bottleneck-detail", bottleneck.target_signal || "--");
  setText("#reviewer-status", clean(reviewer.status || "not run"));
  setText("#reviewer-detail", reviewer.approval_boundary || "Autonomous critique only; external action needs approval.");
  setText("#reviewer-model", latestReview.model || reviewer.model || "--");
  setText("#reviewer-sources", `${latestReview.source_count || reviewer.source_count || 0} sources; ${reviewer.review_count || 0} saved reviews`);
  setText("#reviewer-scope", clean(reviewer.scope || "whole_public_ao_labs_graph"));
  setText("#metric-proof", evidence.proof_events ?? "--");
  setText("#metric-cycles", evidence.daily_cycles ?? "--");
  setText("#metric-ai-reviews", evidence.ai_reviews ?? "--");
  setText("#metric-journal", evidence.journal_entries ?? "--");
  setText("#updated-at", `updated ${formatDateTime(ops.generated_at || paper.updated_at)}`);
  setText("#paper-status", "Current PDF.");

  renderReviewerReport(latestReview, reviewerAction, generatedAt);
  renderDimensions(ops.dimensions || []);
}

function renderReviewerReport(latestReview, action, generatedAt) {
  if (!latestReview || !latestReview.id) {
    setText("#report-score", "--");
    setText("#report-generated", "No AI reviewer report has been generated yet.");
    setText("#report-verdict", "Run the reviewer to generate the first report.");
    setText("#report-summary", "The report will read the public AO Labs evidence graph, compare it against WDI R&D mechanical Imagineering signals, and return the most useful critique.");
    setText("#report-top-issue", "Waiting for reviewer output.");
    setText("#report-action-title", action.title || "--");
    setText("#report-action-body", action.body || "--");
    setText("#report-action-signal", action.expected_signal || action.why || "--");
    setText("#report-action-source", action.source || "--");
    setList("#best-evidence", []);
    setList("#evidence-gaps", []);
    setList("#packet-edits", []);
    return;
  }

  setText("#report-score", Number.isFinite(latestReview.score) ? latestReview.score : "--");
  setText("#report-generated", `generated ${formatDateTime(generatedAt)} by ${latestReview.model || "AI reviewer"}`);
  setText("#report-verdict", latestReview.verdict || "Reviewer generated a report.");
  setText("#report-summary", reviewerSummary(latestReview, action));
  setText("#report-top-issue", latestReview.top_issue || "No top issue returned.");
  setText("#report-action-title", action.title || "No action returned");
  setText("#report-action-body", action.body || "--");
  setText("#report-action-signal", action.expected_signal ? `Expected signal: ${action.expected_signal}` : "--");
  setText("#report-action-source", action.source ? `Source: ${action.source}` : "--");
  setList("#best-evidence", latestReview.best_existing_evidence || []);
  setList("#evidence-gaps", latestReview.evidence_gaps || []);
  setList("#packet-edits", latestReview.packet_edits || []);
}

function renderDimensions(dimensions) {
  $("#dimensions").innerHTML = dimensions.length
    ? dimensions.map((dimension) => {
      const score = Math.max(0, Math.min(Number(dimension.score) || 0, 100));
      return `
        <article class="dimension-card">
          <div class="dimension-top">
            <strong>${escapeHtml(dimension.label || dimension.key)}</strong>
            <span>${score}</span>
          </div>
          <div class="bar" aria-hidden="true"><i style="--score:${score}%"></i></div>
          <p><b>Measures</b> ${escapeHtml(dimension.target_signal || "No measurement target supplied.")}</p>
          <p><b>Score basis</b> ${escapeHtml(dimension.score_basis || "Score basis will appear after the backend update deploys.")}</p>
          <p><b>Next evidence</b> ${escapeHtml(dimension.next_signal || "No next evidence target supplied.")}</p>
        </article>
      `;
    }).join("")
    : `<article class="dimension-card"><div class="dimension-top"><strong>No live dimensions</strong><span>--</span></div><p>Backend not loaded.</p></article>`;
}

function setList(selector, items) {
  const node = $(selector);
  if (!node) return;
  const cleanItems = Array.isArray(items) ? items.filter(Boolean) : [];
  node.innerHTML = cleanItems.length
    ? cleanItems.map((item) => `<li>${escapeHtml(item)}</li>`).join("")
    : `<li>Not returned in the latest review.</li>`;
}

function reviewerSummary(latestReview, action) {
  const raw = latestReview.reviewer_summary || latestReview.why_it_matters || "The reviewer generated a critique from the public source graph.";
  const cleaned = removeDanglingNextMove(raw);
  if (cleaned) return cleaned;
  if (action && action.title && action.body) return `${action.title} ${action.body}`;
  return "The reviewer generated a critique from the public source graph.";
}

function removeDanglingNextMove(value) {
  let text = clean(value);
  text = text.replace(/\s+The best next move is to\s*$/i, "");
  text = text.replace(/\s+The selected next move is to\s*$/i, "");
  if (/[.!?]$/.test(text)) return text;
  const lastStop = Math.max(text.lastIndexOf("."), text.lastIndexOf("!"), text.lastIndexOf("?"));
  if (lastStop > 80) return text.slice(0, lastStop + 1);
  return text;
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
