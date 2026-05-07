const railwayApiBase = "https://imagineer-app-production.up.railway.app";
const sameOriginApiHosts = new Set(["localhost", "127.0.0.1", "imagineer-app-production.up.railway.app"]);
const apiBase = window.IMAGINEER_API_BASE || (sameOriginApiHosts.has(window.location.hostname) ? "" : railwayApiBase);
const paperName = "An autonomous career system for embodied creative research and development";

const fallbackOps = {
  status: "static_fallback",
  generated_at: new Date().toISOString(),
  target: {
    north_star_title: "Principal R&D Imagineer - Mechanical Engineer",
    active_rung_title: "WDI Research & Development Imagineer - Mechanical Design Engineer",
    company: "Walt Disney Imagineering R&D",
    location: "Glendale, California"
  },
  fit_score: 58,
  confidence: "fallback",
  current_bottleneck: {
    key: "principal_signal",
    label: "Principal signal",
    score: 34,
    target_signal: "Visible ownership, technical direction, and source-backed role calibration.",
    next_signal: "Reconnect the live system and regenerate the readout."
  },
  next_action: {
    title: "Reconnect the live system.",
    body: "The page is showing fallback state because the backend did not load."
  },
  reviewer: {
    mode: "autonomous_ai",
    model: "gpt-5.5",
    scope: "whole_public_ao_labs_graph",
    status: "offline",
    review_count: 0,
    source_count: 0,
    latest: null
  },
  evidence: {
    daily_cycles: 0,
    ai_reviews: 0,
    journal_entries: 0,
    portfolio_items: 0
  },
  active_experiment: {
    name: "Autonomous career loop",
    status: "waiting",
    progress: {}
  },
  weekly_paper: {
    status: "fallback",
    updated_at: new Date().toISOString()
  },
  dimensions: [
    {
      key: "mechanical_depth",
      label: "Mechanical case",
      score: 58,
      target_signal: "Real mechanism work, loads, fabrication, measurement, and iteration.",
      next_signal: "Reconnect the live source graph."
    }
  ]
};

const $ = (selector) => document.querySelector(selector);

function setText(selector, value) {
  const node = $(selector);
  if (node) node.textContent = clean(value);
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
  setText("#system-state", "checking");
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
  button.textContent = "Updating";
  setText("#system-state", "running");
  setText("#system-detail", "reading public sources and refreshing the state");
  try {
    const result = await request("/api/imagineer/ai-review/run", { method: "POST", timeout: 210000 });
    render(result.ops || fallbackOps, true);
  } catch {
    setText("#system-state", "not completed");
    setText("#system-detail", "the review timed out or returned an error");
  } finally {
    button.disabled = false;
    button.textContent = "Update readout";
  }
}

function render(ops, connected) {
  const evidence = ops.evidence || {};
  const target = ops.target || {};
  const reviewer = ops.reviewer || {};
  const latestReview = reviewer.latest || {};
  const activeExperiment = ops.active_experiment || {};
  const progress = activeExperiment.progress || {};
  const generatedAt = latestReview.created_at || ops.generated_at || ops.weekly_paper?.updated_at;
  const dimensions = ops.dimensions || [];
  const readiness = Number.isFinite(ops.fit_score) ? ops.fit_score : "--";
  const mainState = buildReadout(ops, latestReview);

  setText("#current-read", mainState.headline);
  setText("#why-care", mainState.why);
  setText("#readiness-score", readiness);
  setText("#readiness-caption", mainState.caption);
  setText("#generated-at", `updated ${formatDateTime(generatedAt)}`);

  setText("#where-now-title", mainState.whereNowTitle);
  setText("#where-now-body", mainState.whereNowBody);
  setText("#where-needed-title", mainState.whereNeededTitle);
  setText("#where-needed-body", mainState.whereNeededBody);
  setText("#system-owned-title", mainState.systemOwnedTitle);
  setText("#system-owned-body", mainState.systemOwnedBody);
  setText("#alan-gate-title", mainState.alanGateTitle);
  setText("#alan-gate-body", mainState.alanGateBody);

  setText("#system-state", connected ? "online" : "fallback");
  $("#system-state").className = connected ? "is-ok" : "is-warn";
  setText("#system-detail", connected ? systemDetail(ops, reviewer) : "static fallback");
  setText("#system-loop", activeExperiment.name || "Autonomous career loop");
  setText("#system-loop-detail", activeExperiment.status || ops.status || "--");
  setText("#system-model", latestReview.model || reviewer.model || "gpt-5.5");
  setText("#system-model-detail", `${latestReview.source_count || reviewer.source_count || 0} sources; ${reviewer.review_count || 0} saved reviews`);
  setText("#system-progress", `${evidence.ai_reviews ?? 0} reviews / ${evidence.daily_cycles ?? 0} cycles`);
  setText("#system-progress-detail", `${evidence.journal_entries ?? 0} journal entries; ${progress.reviewer_ready_artifacts ?? evidence.portfolio_items ?? 0} public artifacts tracked`);
  setText("#system-boundary", "external steps gated");
  setText("#system-boundary-detail", "applications, referral asks, and direct outreach still require approval");

  setText("#target-role", target.north_star_title || "Principal R&D Imagineer - Mechanical Engineer");
  setText("#target-detail", `${target.company || "Walt Disney Imagineering R&D"} / ${target.location || "Glendale, California"}`);
  setText("#paper-title", paperName);
  setText("#paper-status", `PDF is live; weekly system paper updates separately from this dashboard.`);

  renderLanes(dimensions);
}

function buildReadout(ops, latestReview) {
  const fit = Number(ops.fit_score) || 0;
  const mechanical = findDimension(ops, "mechanical_depth");
  const physical = findDimension(ops, "physical_experience");
  const principal = findDimension(ops, "leadership_network") || ops.current_bottleneck || {};
  const packet = findDimension(ops, "application_packet");
  const paper = findDimension(ops, "paper_system");
  const latestText = latestReview?.reviewer_summary || latestReview?.why_it_matters || "";
  const credible = fit >= 70;

  return {
    headline: credible
      ? "Credible for WDI R&D mechanical design. Principal signal is the active gap."
      : "Promising technical base. Principal signal is still thin.",
    why: (
      "Sarrus is the technical anchor. The active gap is principal-scope ownership: technical direction, integrated systems, design-review leadership, collaborators, or comparable responsibility."
    ),
    caption: "Controllable readiness. Not a hiring probability.",
    whereNowTitle: "Technical base is credible.",
    whereNowBody: `Mechanical depth is ${scoreText(mechanical)}. The public record now shows mechanism geometry, pneumatic actuation, modular assembly, measured behavior, and motion examples.`,
    whereNeededTitle: "Ownership signal is thin.",
    whereNeededBody: `Principal signal is ${scoreText(principal)}. Disney still needs to see ownership: technical direction, integrated systems, design-review leadership, collaborators, or comparable responsibility.`,
    systemOwnedTitle: "System-owned work.",
    systemOwnedBody: `Re-read AO Labs, score the lanes, update this dashboard, update the profile/paper, and log source-backed changes.`,
    alanGateTitle: "Approval boundary.",
    alanGateBody: "Applications, referral asks, direct outreach, or person-facing claims require approval.",
    latestText,
    mechanical,
    physical,
    principal,
    packet,
    paper
  };
}

function renderLanes(dimensions) {
  const laneSpecs = [
    {
      key: "mechanical_depth",
      title: "Mechanical case",
      why: "Mechanism credibility: geometry, actuation, measured behavior.",
      now: "Sarrus is the anchor: mechanism geometry, actuation path, build state, and measured behavior.",
      system: "Keep Sarrus primary, keep figures current, and make measurements easier to inspect."
    },
    {
      key: "physical_experience",
      title: "Disney motion",
      why: "Readable motion and embodied interaction.",
      now: "The motion exists: surface waves, object manipulation, crawling, and rolling.",
      system: "Translate one motion sequence into a short, human-facing story: what someone sees, feels, or believes."
    },
    {
      key: "leadership_network",
      title: "Principal signal",
      why: "Visible ownership and technical direction.",
      now: "The weak part is visible ownership, technical direction, and external validation.",
      system: "Mine the public record for leadership signals, prepare clean source-backed framing, and wait for approval before any person-facing step."
    }
  ];

  $("#lanes").innerHTML = laneSpecs.map((lane) => {
    const dimension = findDimension({ dimensions }, lane.key) || {};
    const score = Math.max(0, Math.min(Number(dimension.score) || 0, 100));
    const state = score >= 82 ? "strong" : score >= 68 ? "building" : "thin";
    return `
      <article class="lane-card ${state}">
        <div class="lane-top">
          <span>${escapeHtml(lane.title)}</span>
          <strong>${score || "--"}</strong>
        </div>
        <div class="bar" aria-hidden="true"><i style="--score:${score}%"></i></div>
        <p>${escapeHtml(lane.why)}</p>
        <dl>
          <div><dt>Current</dt><dd>${escapeHtml(lane.now)}</dd></div>
          <div><dt>System</dt><dd>${escapeHtml(lane.system)}</dd></div>
        </dl>
      </article>
    `;
  }).join("");
}

function findDimension(ops, key) {
  return (ops.dimensions || []).find((dimension) => dimension.key === key);
}

function scoreText(dimension) {
  if (!dimension || !Number.isFinite(Number(dimension.score))) return "not loaded";
  return `${dimension.score}/100`;
}

function systemDetail(ops, reviewer) {
  const status = clean(ops.status || "running");
  const count = reviewer.review_count || 0;
  if (count > 0) return `${status}; ${count} system readouts saved`;
  return status;
}

function clean(value) {
  let text = String(value || "--").replaceAll("_", " ");
  const replacements = [
    ["proof packet", "profile"],
    ["Proof packet", "Profile"],
    ["evidence packet", "profile"],
    ["Evidence packet", "Profile"],
    ["reviewer-facing", "public"],
    ["Reviewer-facing", "Public"],
    ["reviewer-visible", "public"],
    ["Reviewer-visible", "Public"],
    ["Autonomous AI reviewer", "Autonomous career loop"],
    ["autonomous AI reviewer", "autonomous career loop"],
    ["AI reviewer", "career signal loop"],
    ["ai reviewer", "career signal loop"],
    ["best evidence", "current signal"],
    ["Best evidence", "Current signal"],
    ["evidence gaps", "open signals"],
    ["Evidence gaps", "Open signals"],
    ["evidence to create", "open signal"],
    ["Evidence to create", "Open signal"],
    ["next evidence", "open signal"],
    ["Next evidence", "Open signal"],
    ["best next move", "current state"],
    ["Best next move", "Current state"],
    ["show-value", "motion"],
    ["Show-value", "Motion"],
    ["source coverage", "source depth"],
    ["Source coverage", "Source depth"],
    ["packet", "profile"],
    ["Packet", "Profile"]
  ];
  for (const [from, to] of replacements) text = text.replaceAll(from, to);
  return text;
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
