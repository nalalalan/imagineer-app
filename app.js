const railwayApiBase = "https://imagineer-app-production.up.railway.app";
const sameOriginApiHosts = new Set(["localhost", "127.0.0.1", "imagineer-app-production.up.railway.app"]);
const apiBase = window.IMAGINEER_API_BASE || (sameOriginApiHosts.has(window.location.hostname) ? "" : railwayApiBase);
const progressApiBase = window.PROGRESS_API_BASE || "https://progress.aolabs.io";

const fallbackStep = {
  title: "Make the FluxCell linkage test.",
  body: "Capture notes and files in PhD; Imagineer reads them into career state.",
  why: "PhD is the intake; Imagineer reads it instead of creating a second typing surface.",
  time: "7 minutes",
  href: "https://phd.aolabs.io/",
  linkLabel: "Open phd",
  source: "Fallback step. Progress state did not load.",
  updatedAt: new Date().toISOString(),
};

const $ = (selector) => document.querySelector(selector);

function setText(selector, value) {
  const node = $(selector);
  if (node) node.textContent = clean(value);
}

function setVisible(selector, visible) {
  const node = $(selector);
  if (node) node.hidden = !visible;
}

async function request(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || 9000);
  const hasBody = Object.prototype.hasOwnProperty.call(options, "body");
  try {
    const response = await fetch(url, {
      method: options.method || "GET",
      cache: "no-store",
      headers: hasBody ? { "Content-Type": "application/json" } : undefined,
      body: hasBody ? JSON.stringify(options.body) : undefined,
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } finally {
    clearTimeout(timeout);
  }
}

async function loadState() {
  setText("#step-title", "Loading current step.");
  setText("#step-body", "Reading Progress and Imagineer state.");
  setVisible("#step-why", false);
  setVisible("#step-meta", false);

  const [opsResult, progressResult] = await Promise.allSettled([
    request(`${apiBase}/api/imagineer/ops-check`),
    request(`${progressApiBase}/api/progress/summary`, { timeout: 12000 }),
  ]);

  const ops = opsResult.status === "fulfilled" ? opsResult.value : null;
  const progress = progressResult.status === "fulfilled" ? progressResult.value : null;
  render(bestStep(ops, progress), ops, progress);
}

function bestStep(ops, progress) {
  const opsStep = ops?.personal_step || ops?.next_action;
  if (opsStep?.title && opsStep?.body) {
    return {
      ...fallbackStep,
      ...opsStep,
      time: opsStep.time || fallbackStep.time,
      href: opsStep.href || fallbackStep.href,
      source: opsStep.source || "Imagineer state.",
      updatedAt: ops?.generated_at || ops?.profile?.updated_at,
    };
  }

  const progressStep = progress?.goals?.imagineer?.nextStep;
  if (progressStep?.title && progressStep?.body) {
    return {
      ...fallbackStep,
      ...progressStep,
      source: progressStep.source || "Progress scan.",
      updatedAt: progressStep.updatedAt || progress?.latest?.createdAt || progress?.updatedAt,
    };
  }

  return fallbackStep;
}

function render(step, ops, progress) {
  const updatedAt = step.updatedAt || progress?.latest?.createdAt || ops?.profile?.updated_at || ops?.generated_at;
  const sourceCount = progress?.latest?.sourceCount || ops?.profile?.source_count || ops?.reviewer?.source_count;
  const source = sourceCount ? `${step.source} ${sourceCount} sources.` : step.source;
  const why = step.why || step.urgency || "";

  setText("#step-title", step.title);
  setText("#step-body", step.body);
  setText("#step-why", why);
  setText("#step-time", step.time || "--");
  setText("#step-updated", formatDateTime(updatedAt));
  setText("#step-source", source || "--");
  setVisible("#step-why", Boolean(why));
  setVisible("#step-meta", true);

  const link = $("#step-link");
  if (link) {
    link.href = step.href || fallbackStep.href;
    link.textContent = step.linkLabel || "Open doc";
  }

  renderLifeLoop(ops?.life_loop || fallbackLifeLoop(step, ops));
  renderSourceIntake(ops);
}

function fallbackLifeLoop(step, ops) {
  if (!ops) return null;
  const bottleneck = ops.current_bottleneck;
  const target = ops.target?.north_star_title || "WDI mechanical R&D";
  const fit = ops.fit_score ? `fit ${ops.fit_score}/100` : "fit reading unavailable";
  return {
    title: "Career source, income path, car",
    summary: "PhD intake first; public career signal next; A3 car path downstream.",
    items: [
      {
        label: "Career",
        value: `${target}; ${fit}`,
        detail: bottleneck ? `${bottleneck.label} ${bottleneck.score}/100 is the current live gap.` : "Current bottleneck unavailable.",
      },
      {
        label: "Source",
        value: String(step.title || "Current PhD source").replace(/\.$/, ""),
        detail: `${step.body || "Capture in PhD; Imagineer reads the source graph."} Then update profile, CV, paper, and Progress.`,
      },
      {
        label: "Money",
        value: "Higher-income R&D path",
        detail: "Stronger inspectable ownership from PhD-sourced work is the controllable lever.",
      },
      {
        label: "Car",
        value: "A3 source pending",
        detail: "A3 queue snapshot did not load through Imagineer yet.",
      },
    ],
  };
}

function renderLifeLoop(loop) {
  const shell = $("#life-loop");
  const grid = $("#life-loop-grid");
  if (!shell || !grid || !loop?.items?.length) {
    setVisible("#life-loop", false);
    return;
  }

  setText("#life-loop-title", loop.title || "Career source, income path, car");
  setText("#life-loop-summary", loop.summary || "");
  grid.replaceChildren(...loop.items.slice(0, 4).map(renderLifeItem));
  setVisible("#life-loop", true);
}

function renderLifeItem(item) {
  const row = document.createElement("div");
  row.className = "life-loop-item";

  const label = document.createElement("span");
  label.textContent = clean(item.label);

  const value = document.createElement("strong");
  value.textContent = clean(item.value);

  const detail = document.createElement("p");
  detail.textContent = clean(item.detail);

  row.append(label, value, detail);
  return row;
}

function renderSourceIntake(ops) {
  const intake = ops?.source_intake;
  const reviewer = ops?.reviewer_state || ops?.reviewer?.review_state;
  const lead = ops?.lead_verification;

  setText("#source-intake-status", intake?.current_step || "Capture in PhD. Imagineer reads PhD, Progress, A3, CV, and lead state.");

  const rows = $("#source-state-rows");
  if (rows) {
    const phd = intake?.primary_source || {};
    const files = intake?.files || {};
    const items = [
      {
        label: "Intake",
        value: phd.status === "current" ? "phd current" : phd.status || "phd unavailable",
        detail: phd.detail || "Write notes and upload files in PhD; Imagineer reads that source.",
      },
      {
        label: "Notes",
        value: phd.note_count != null ? `${phd.note_count} notes` : "notes unavailable",
        detail: phd.latest_note_at ? `Latest PhD note ${formatDateTime(phd.latest_note_at)}.` : "No PhD note timestamp available.",
      },
      {
        label: "Files",
        value: files.file_count != null ? `${files.file_count} files` : "files unavailable",
        detail: files.latest_file_at ? `Latest PhD file ${formatDateTime(files.latest_file_at)}.` : "No PhD file timestamp available.",
      },
      {
        label: "Reviewer",
        value: reviewer?.label || "Review state unavailable",
        detail: reviewer?.action || "Review after PhD source movement changes the career state.",
      },
      {
        label: "Lead",
        value: lead?.status ? `${lead.status}${lead.age_days != null ? `, ${lead.age_days}d` : ""}` : "lead check unavailable",
        detail: lead?.action || "Verify the clicked Disney destination before lead-facing use.",
      },
    ];
    rows.replaceChildren(...items.map(renderSourceRow));
  }
}

function renderSourceRow(item) {
  const row = document.createElement("div");

  const label = document.createElement("dt");
  label.textContent = clean(item.label);

  const value = document.createElement("dd");
  const strong = document.createElement("strong");
  strong.textContent = clean(item.value);
  const detail = document.createElement("span");
  detail.textContent = clean(item.detail);
  value.append(strong, detail);

  row.append(label, value);
  return row;
}

async function handleLeadCheck() {
  const status = $("#source-status");
  const button = $("#lead-check");
  if (button) button.disabled = true;
  if (status) status.textContent = "Checking Disney destination.";
  try {
    const result = await request(`${apiBase}/api/imagineer/lead-check/run`, {
      method: "POST",
      timeout: 20000,
      body: {},
    });
    if (result?.ops) {
      render(bestStep(result.ops, null), result.ops, null);
    }
    if (status) status.textContent = result?.ok ? "Lead destination verified." : "Lead check completed; lead is not current.";
  } catch (error) {
    if (status) status.textContent = "Lead check did not complete.";
  } finally {
    if (button) button.disabled = false;
  }
}

function clean(value) {
  const legacyPacketLabel = ["proof", "packet"].join(" ");
  const legacyPacketTitle = ["Proof", "packet"].join(" ");
  const legacyGapLabel = ["evidence", "gaps"].join(" ");
  const legacyGapTitle = ["Evidence", "gaps"].join(" ");
  const legacyCreateLabel = ["evidence", "to", "create"].join(" ");
  const legacyCreateTitle = ["Evidence", "to", "create"].join(" ");
  return String(value || "--")
    .replaceAll("_", " ")
    .replaceAll(legacyPacketLabel, "profile")
    .replaceAll(legacyPacketTitle, "Profile")
    .replaceAll(legacyGapLabel, "open signals")
    .replaceAll(legacyGapTitle, "Open signals")
    .replaceAll(legacyCreateLabel, "open signal")
    .replaceAll(legacyCreateTitle, "Open signal");
}

function formatDateTime(value) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "--";
  return parsed.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

$("#refresh")?.addEventListener("click", loadState);
$("#lead-check")?.addEventListener("click", handleLeadCheck);
loadState().catch(() => render(fallbackStep, null, null));
