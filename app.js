const fallbackOps = {
  status: "static_fallback",
  target: {
    north_star_title: "Principal R&D Imagineer - Mechanical Engineer",
    active_rung_title: "WDI Research & Development Imagineer - Mechanical Design Engineer",
    company: "Walt Disney Imagineering R&D",
    location: "Glendale, California"
  },
  positioning: "Mechanical PhD + soft robotics + creative prototyping + AI-assisted tools for human-facing physical experiences.",
  fit_score: 58,
  confidence: "promising_needs_packet",
  current_bottleneck: {
    key: "leadership_network",
    label: "Principal-level network",
    score: 34,
    target_signal: "Real conversations, referrals, project collaborators, and evidence of technical leadership.",
    next_signal: "Create one real review or relationship path."
  },
  next_action: {
    lane: "application_packet",
    title: "Sharpen the Glendale packet.",
    body: "Convert one project into a role-fit artifact: title, thumbnail, 90-second story, technical figure, your contribution, and the next build.",
    why: "The public backend is not connected here yet, so this page is showing the local fallback action."
  },
  active_experiment: {
    name: "WDI proof packet v0",
    hypothesis: "Convert existing soft-robotics work into concise WDI R&D evidence.",
    progress: {
      proof_logs: 0,
      daily_cycles: 0,
      reviewer_ready_artifacts: 0,
      target_proof_logs: 5,
      target_reviewer_ready_artifacts: 1,
      target_warm_review_requests: 1
    }
  },
  evidence: {
    proof_events: 0,
    daily_cycles: 0,
    portfolio_items: 4,
    journal_entries: 2
  },
  dimensions: [
    { key: "mechanical_depth", label: "Mechanical depth", score: 74, next_signal: "Add one trustworthy mechanical calculation or CAD/manufacturing detail." },
    { key: "creative_prototyping", label: "Creative prototyping", score: 78, next_signal: "Make one prototype iteration visible as a clean artifact." },
    { key: "physical_experience", label: "Human-facing physical experience", score: 68, next_signal: "Tie one technical result to a felt human experience." },
    { key: "leadership_network", label: "Principal-level network", score: 34, next_signal: "Create one real review or relationship path." },
    { key: "application_packet", label: "Glendale packet", score: 46, next_signal: "Make one role-specific portfolio item sharper." },
    { key: "paper_system", label: "Autonomous career system", score: 42, next_signal: "Log state, action, intervention, and result for the methods trail." }
  ],
  journal: [
    { title: "Target locked", body: "Aim at WDI R&D Glendale, with Principal R&D Imagineer as the north star." },
    { title: "Positioning line", body: "Mechanical PhD + soft robotics + creative prototyping + AI-assisted tools for human-facing physical experiences." }
  ],
  paper: {
    working_title: "Adaptive Evidence Systems for Career Conversion in Embodied Creative R&D",
    thesis: "Career progress becomes optimizable when evidence, decisions, experiments, and ethics are logged as a closed-loop system."
  },
  weekly_paper: {
    week_id: "2026-W19",
    title: "Weekly Progress Paper: Autonomous Imagineer Position System",
    status: "static_preview_until_api_connects",
    updated_at: new Date().toISOString(),
    next_update_due: "weekly",
    abstract: "This weekly paper reports the progress of an autonomous, guardrailed career-conversion system targeting WDI R&D mechanical Imagineering roles.",
    headline_result: "The current bottleneck is principal-level network signal; the next intervention is to create one real review path."
  }
};

const railwayApiBase = "https://imagineer-app-production.up.railway.app";
const sameOriginApiHosts = new Set([
  "localhost",
  "127.0.0.1",
  "imagineer-app-production.up.railway.app"
]);
const apiBase = window.IMAGINEER_API_BASE || (sameOriginApiHosts.has(window.location.hostname) ? "" : railwayApiBase);
const dateKey = new Date().toISOString().slice(0, 10);
const localProofKey = `imagineer.localProof.${dateKey}`;

const $ = (selector) => document.querySelector(selector);

function setText(selector, value) {
  const node = $(selector);
  if (node) node.textContent = value ?? "";
}

function tagsFromForm() {
  return [...document.querySelectorAll(".tag-row input:checked")].map((input) => input.value);
}

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 6000);
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

async function loadOps() {
  try {
    const ops = await request("/api/imagineer/ops-check");
    renderOps(ops, true);
    loadWeeklyPaper(true);
  } catch {
    renderOps(fallbackOps, false);
    renderWeeklyPaper(fallbackWeeklyPaper(), false);
  }
}

function renderOps(ops, apiConnected) {
  setText("#positioning", ops.positioning);
  setText("#target-company", ops.target?.company || "Walt Disney Imagineering R&D");
  setText("#target-location", ops.target?.location || "Glendale, California");
  setText("#target-rung", ops.target?.active_rung_title || ops.target?.north_star_title || "WDI R&D mechanical role");
  setText("#fit-score", Number.isFinite(ops.fit_score) ? ops.fit_score : "--");
  setText("#confidence", (ops.confidence || "checking").replaceAll("_", " "));

  const bottleneck = ops.current_bottleneck || {};
  setText("#bottleneck-title", bottleneck.label || "Current bottleneck");
  setText("#bottleneck-body", bottleneck.target_signal || bottleneck.next_signal || "");

  const evidence = ops.evidence || {};
  setText("#metric-proof", evidence.proof_events ?? "--");
  setText("#metric-cycles", evidence.daily_cycles ?? "--");
  setText("#metric-portfolio", evidence.portfolio_items ?? "--");
  setText("#metric-journal", evidence.journal_entries ?? "--");

  const action = ops.next_action || {};
  setText("#action-title", action.title || "Choose one compounding action.");
  setText("#action-body", action.body || "");
  setText("#action-why", action.why || "");

  const experiment = ops.active_experiment || {};
  setText("#experiment-title", experiment.name || "Active experiment");
  setText("#experiment-body", experiment.hypothesis || experiment.success_metric || "");
  renderProgress(experiment.progress || {});
  renderDimensions(ops.dimensions || []);
  renderJournal(ops.journal || []);

  if (ops.paper) {
    setText("#paper-title", ops.weekly_paper?.title || ops.paper.working_title);
    setText("#paper-thesis", ops.weekly_paper?.abstract || ops.paper.thesis);
  }

  const logger = apiConnected
    ? "API connected. New signals write to the position-system event log."
    : "API not connected on this surface yet. New signals are saved locally for today.";
  setText("#logger-state", logger);
}

async function loadWeeklyPaper(apiConnected) {
  if (!apiConnected) {
    renderWeeklyPaper(fallbackWeeklyPaper(), false);
    return;
  }
  try {
    const paper = await request("/api/imagineer/weekly-paper");
    renderWeeklyPaper(paper, true);
  } catch {
    renderWeeklyPaper(fallbackWeeklyPaper(), false);
  }
}

function fallbackWeeklyPaper() {
  return {
    week_id: fallbackOps.weekly_paper.week_id,
    title: fallbackOps.weekly_paper.title,
    status: fallbackOps.weekly_paper.status,
    updated_at: fallbackOps.weekly_paper.updated_at,
    next_update_due: fallbackOps.weekly_paper.next_update_due,
    headline_result: fallbackOps.weekly_paper.headline_result,
    sections: [
      {
        heading: "Abstract",
        body: fallbackOps.weekly_paper.abstract
      },
      {
        heading: "Weekly Results",
        body: fallbackOps.weekly_paper.headline_result
      },
      {
        heading: "Next Intervention",
        body: fallbackOps.next_action.body
      }
    ]
  };
}

function renderWeeklyPaper(paper, apiConnected) {
  setText("#paper-title", paper.title || "Weekly Progress Paper");
  setText("#paper-thesis", paper.headline_result || paper.sections?.[0]?.body || "");
  setText("#paper-week", paper.week_id ? `week ${paper.week_id}` : "week pending");
  setText("#paper-status", (paper.status || (apiConnected ? "live" : "fallback")).replaceAll("_", " "));
  setText("#paper-next", paper.next_update_due ? `next update ${formatDate(paper.next_update_due)}` : "next update pending");
  const sections = paper.sections || [];
  $("#paper-sections").innerHTML = sections.slice(0, 6).map((section) => `
    <div class="paper-section">
      <strong>${escapeHtml(section.heading || "Section")}</strong>
      <p>${escapeHtml(section.body || "")}</p>
    </div>
  `).join("");
}

function formatDate(value) {
  if (!value || value === "weekly") return value || "";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return parsed.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function renderProgress(progress) {
  const items = [
    ["proof logs", progress.proof_logs, progress.target_proof_logs],
    ["reviewer artifacts", progress.reviewer_ready_artifacts, progress.target_reviewer_ready_artifacts],
    ["warm reviews", progress.warm_review_requests || 0, progress.target_warm_review_requests]
  ];
  $("#experiment-progress").innerHTML = items.map(([label, value, target]) => (
    `<span><strong>${value ?? 0}/${target ?? 1}</strong>${label}</span>`
  )).join("");
}

function renderDimensions(dimensions) {
  $("#dimensions").innerHTML = dimensions.map((dimension) => {
    const score = Math.max(0, Math.min(Number(dimension.score) || 0, 100));
    return `
      <article class="dimension">
        <header>
          <h3>${escapeHtml(dimension.label || dimension.key)}</h3>
          <strong>${score}</strong>
        </header>
        <div class="bar" aria-hidden="true"><i style="--score: ${score}%"></i></div>
        <p>${escapeHtml(dimension.next_signal || dimension.target_signal || "")}</p>
      </article>
    `;
  }).join("");
}

function renderJournal(journal) {
  $("#journal").innerHTML = journal.slice(0, 4).map((item) => `
    <div class="journal-item">
      <strong>${escapeHtml(item.title || "Journal entry")}</strong>
      <span>${escapeHtml(item.body || "")}</span>
    </div>
  `).join("");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

$("#proof-note").value = localStorage.getItem(localProofKey) || "";

$("#proof-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const note = $("#proof-note").value.trim();
  const link = $("#proof-link").value.trim();
  const kind = $("#proof-kind").value;
  const tags = tagsFromForm();
  const title = note ? note.split(/[.!?]/)[0].slice(0, 120) : "Imagineer signal logged";

  localStorage.setItem(localProofKey, note);
  setText("#save-state", "Saving signal...");

  try {
    const result = await request("/api/imagineer/events", {
      method: "POST",
      body: JSON.stringify({ kind, title, notes: note, link, tags, impact: 1 })
    });
    renderOps(result.ops, true);
    setText("#save-state", "Signal saved to the system.");
    $("#proof-note").value = "";
    $("#proof-link").value = "";
  } catch {
    setText("#save-state", "Saved locally for today. API write is not connected on this surface.");
  }
});

$("#run-cycle").addEventListener("click", async () => {
  const button = $("#run-cycle");
  button.disabled = true;
  button.textContent = "Running...";
  try {
    const result = await request("/api/imagineer/daily-cycle", { method: "POST", body: "{}" });
    renderOps(result.ops, true);
    setText("#save-state", result.already_ran ? "Daily cycle was already selected today." : "Daily cycle selected and logged.");
  } catch {
    renderOps(fallbackOps, false);
    setText("#save-state", "Daily cycle needs the backend API. Showing fallback action.");
  } finally {
    button.disabled = false;
    button.textContent = "Run daily cycle";
  }
});

$("#update-paper").addEventListener("click", async () => {
  const button = $("#update-paper");
  button.disabled = true;
  button.textContent = "Updating...";
  try {
    const result = await request("/api/imagineer/weekly-paper/run", { method: "POST", body: "{}" });
    renderWeeklyPaper(result.paper, true);
    renderOps(result.ops, true);
    setText("#save-state", "Weekly paper updated.");
  } catch {
    renderWeeklyPaper(fallbackWeeklyPaper(), false);
    setText("#save-state", "Weekly paper update needs the backend API.");
  } finally {
    button.disabled = false;
    button.textContent = "Update paper";
  }
});

loadOps();
