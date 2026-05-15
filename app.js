const railwayApiBase = "https://imagineer-app-production.up.railway.app";
const sameOriginApiHosts = new Set(["localhost", "127.0.0.1", "imagineer-app-production.up.railway.app"]);
const apiBase = window.IMAGINEER_API_BASE || (sameOriginApiHosts.has(window.location.hostname) ? "" : railwayApiBase);
const progressApiBase = window.PROGRESS_API_BASE || (
  ["localhost", "127.0.0.1"].includes(window.location.hostname) ? "http://127.0.0.1:8781" : "https://progress.aolabs.io"
);

const fallbackStep = {
  title: "Write one Sarrus design decision.",
  body: "In the PhD doc: constraint, choice, result, next test.",
  time: "5 minutes",
  href: "https://docs.google.com/document/d/1Ffi51WavVvaFBUQX37AbFQ4ZKGEkRlGl-NRcOVQP03c/edit",
  source: "Fallback step. Progress state did not load.",
  updatedAt: new Date().toISOString(),
};

const $ = (selector) => document.querySelector(selector);

function setText(selector, value) {
  const node = $(selector);
  if (node) node.textContent = clean(value);
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

  const [opsResult, progressResult] = await Promise.allSettled([
    request(`${apiBase}/api/imagineer/ops-check`),
    request(`${progressApiBase}/api/progress/summary`, { timeout: 12000 }),
  ]);

  const ops = opsResult.status === "fulfilled" ? opsResult.value : null;
  const progress = progressResult.status === "fulfilled" ? progressResult.value : null;
  render(bestStep(ops, progress), ops, progress);
}

function bestStep(ops, progress) {
  const progressStep = progress?.goals?.imagineer?.nextStep;
  if (progressStep?.title && progressStep?.body) {
    return {
      ...fallbackStep,
      ...progressStep,
      source: progressStep.source || "Progress scan.",
      updatedAt: progressStep.updatedAt || progress?.latest?.createdAt || progress?.updatedAt,
    };
  }

  const opsStep = ops?.personal_step || ops?.next_action;
  if (opsStep?.title && opsStep?.body) {
    return {
      ...fallbackStep,
      title: opsStep.title,
      body: opsStep.body,
      time: opsStep.time || "5 minutes",
      href: opsStep.href || fallbackStep.href,
      source: opsStep.source || "Imagineer state.",
      updatedAt: ops?.profile?.updated_at || ops?.generated_at,
    };
  }

  return fallbackStep;
}

function render(step, ops, progress) {
  const updatedAt = step.updatedAt || progress?.latest?.createdAt || ops?.profile?.updated_at || ops?.generated_at;
  const sourceCount = progress?.latest?.sourceCount || ops?.profile?.source_count || ops?.reviewer?.source_count;
  const source = sourceCount ? `${step.source} ${sourceCount} sources.` : step.source;

  setText("#step-title", step.title);
  setText("#step-body", step.body);
  setText("#step-time", step.time || "--");
  setText("#step-updated", formatDateTime(updatedAt));
  setText("#step-source", source || "--");

  const link = $("#step-link");
  if (link) {
    link.href = step.href || fallbackStep.href;
    link.textContent = step.linkLabel || "Open doc";
  }
}

function clean(value) {
  return String(value || "--")
    .replaceAll("_", " ")
    .replaceAll("proof packet", "profile")
    .replaceAll("Proof packet", "Profile")
    .replaceAll("evidence gaps", "open signals")
    .replaceAll("Evidence gaps", "Open signals")
    .replaceAll("evidence to create", "open signal")
    .replaceAll("Evidence to create", "Open signal");
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
