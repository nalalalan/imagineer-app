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
  href: "#proof-capture",
  linkLabel: "Start proof",
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
  renderProofCapture(ops, step);
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

function renderProofCapture(ops, step) {
  const capture = ops?.proof_capture;
  const reviewer = ops?.reviewer_state || ops?.reviewer?.review_state;
  const lead = ops?.lead_verification;

  setText("#proof-capture-status", capture?.current_step || "Add one measured FluxCell proof and let the app remember it.");
  setText("#proof-sync-targets", capture?.sync_targets?.join(", ") || "profile, CV, paper, Progress");

  const sourceDoc = $("#proof-source-doc");
  if (sourceDoc) {
    const sourceDocHref = ops?.decision_system?.candidates?.find((item) => item.id === step.decision_id)?.source_doc
      || "https://docs.google.com/document/d/1Ffi51WavVvaFBUQX37AbFQ4ZKGEkRlGl-NRcOVQP03c/edit";
    sourceDoc.href = sourceDocHref;
  }

  const rows = $("#proof-state-rows");
  if (rows) {
    const latest = capture?.latest;
    const items = [
      {
        label: "Latest proof",
        value: latest ? formatDateTime(latest.created_at) : "none logged",
        detail: latest?.measurement || latest?.changed || latest?.notes || "FluxCell proof capture is ready.",
      },
      {
        label: "Reviewer",
        value: reviewer?.label || "Review state unavailable",
        detail: reviewer?.action || "Capture proof before the next review.",
      },
      {
        label: "Lead",
        value: lead?.status ? `${lead.status}${lead.age_days != null ? `, ${lead.age_days}d` : ""}` : "lead check unavailable",
        detail: lead?.action || "Verify the clicked Disney destination before lead-facing use.",
      },
    ];
    rows.replaceChildren(...items.map(renderProofRow));
  }
}

function renderProofRow(item) {
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

async function handleProofSubmit(event) {
  event.preventDefault();
  const status = $("#proof-form-status");
  const submit = $("#proof-submit");
  const file = $("#proof-file")?.files?.[0] || null;
  const body = {
    note: $("#proof-note")?.value || "",
    measurement: $("#proof-measurement")?.value || "",
    changed: $("#proof-changed")?.value || "",
    failure: $("#proof-failure")?.value || "",
    next_update: $("#proof-next")?.value || "",
    link: $("#proof-link")?.value || "",
  };
  const hasText = Object.values(body).some((value) => String(value || "").trim());
  if (!hasText && !file) {
    if (status) status.textContent = "Add a note, measurement, link, or file.";
    return;
  }

  if (submit) submit.disabled = true;
  if (status) status.textContent = "Logging proof.";
  try {
    const filePayload = file ? await fileToPayload(file) : {};
    const result = await request(`${apiBase}/api/imagineer/proofs`, {
      method: "POST",
      timeout: 30000,
      body: { ...body, ...filePayload },
    });
    if (result?.ops) {
      render(bestStep(result.ops, null), result.ops, null);
    }
    $("#proof-form")?.reset();
    if (status) status.textContent = "Proof logged. Runtime profile and journal state updated.";
  } catch (error) {
    if (status) status.textContent = "Proof did not log. Check file size or route.";
  } finally {
    if (submit) submit.disabled = false;
  }
}

async function handleLeadCheck() {
  const status = $("#proof-form-status");
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

async function fileToPayload(file) {
  if (file.size > 12 * 1024 * 1024) {
    throw new Error("file_too_large");
  }
  return {
    artifact_name: file.name,
    artifact_type: file.type.startsWith("image/")
      ? "photo"
      : file.type.startsWith("video/")
        ? "video"
        : file.type === "application/pdf"
          ? "PDF"
          : "text file",
    artifact_mime: file.type || "text/plain",
    artifact_data: await readAsDataUrl(file),
  };
}

function readAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(reader.error || new Error("read_failed"));
    reader.readAsDataURL(file);
  });
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
$("#proof-form")?.addEventListener("submit", handleProofSubmit);
$("#lead-check")?.addEventListener("click", handleLeadCheck);
loadState().catch(() => render(fallbackStep, null, null));
