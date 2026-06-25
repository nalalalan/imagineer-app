const railwayApiBase = "https://imagineer-app-production.up.railway.app";
const sameOriginApiHosts = new Set(["localhost", "127.0.0.1", "imagineer-app-production.up.railway.app"]);
const apiBase = window.IMAGINEER_API_BASE || (sameOriginApiHosts.has(window.location.hostname) ? "" : railwayApiBase);
const progressApiBase = window.PROGRESS_API_BASE || (
  ["localhost", "127.0.0.1"].includes(window.location.hostname) ? "http://127.0.0.1:8781" : "https://progress.aolabs.io"
);

const fallbackStep = {
  title: "Make the FluxCell linkage test.",
  body: "Actuator-less array, clip-programmed shape, overhang motion check.",
  why: "The current source names the prototype path; visible ownership now needs a measured first build.",
  time: "7 minutes",
  href: "https://docs.google.com/document/d/1Ffi51WavVvaFBUQX37AbFQ4ZKGEkRlGl-NRcOVQP03c/edit",
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
  try {
    const response = await fetch(url, {
      method: options.method || "GET",
      cache: "no-store",
      headers: { "Content-Type": "application/json" },
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
}

function fallbackLifeLoop(step, ops) {
  if (!ops) return null;
  const bottleneck = ops.current_bottleneck;
  const target = ops.target?.north_star_title || "WDI mechanical R&D";
  const fit = ops.fit_score ? `fit ${ops.fit_score}/100` : "fit reading unavailable";
  return {
    title: "Career proof, income path, car",
    summary: "Current proof artifact first; public career signal next; A3 car path downstream.",
    items: [
      {
        label: "Career",
        value: `${target}; ${fit}`,
        detail: bottleneck ? `${bottleneck.label} ${bottleneck.score}/100 is the current live gap.` : "Current bottleneck unavailable.",
      },
      {
        label: "Proof",
        value: String(step.title || "Current proof artifact").replace(/\.$/, ""),
        detail: `${step.body || "Create source-backed public proof."} Then update profile, CV, paper, and Progress.`,
      },
      {
        label: "Money",
        value: "Higher-income R&D path",
        detail: "Stronger inspectable ownership proof is the controllable lever.",
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

  setText("#life-loop-title", loop.title || "Career proof, income path, car");
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
loadState().catch(() => render(fallbackStep, null, null));
