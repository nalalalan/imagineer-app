const moves = [
  {
    title: "Make one physical proof cleaner.",
    body: "Choose one mechanism, image, plot, or test result and make it easier for a WDI R&D person to understand in sixty seconds."
  },
  {
    title: "Translate research into show value.",
    body: "Write one sentence that connects a technical detail to guest-facing experience: motion, touch, believability, surprise, safety, or repeatability."
  },
  {
    title: "Strengthen the Glendale packet.",
    body: "Improve one artifact that would belong in a Principal R&D Imagineer portfolio: demo video, figure, build note, prototype log, or CV line."
  },
  {
    title: "Find the constraint that matters.",
    body: "Pick one prototype and name the next bottleneck plainly: force, travel, stiffness, latency, fabrication, reliability, control, or storytelling."
  },
  {
    title: "Make the work visible.",
    body: "Record the smallest honest proof from today. A clear trail beats a private grind."
  },
  {
    title: "Practice the room.",
    body: "Explain one project as if an R&D studio lead asked: what is new, what works, what failed, and what should be built next?"
  },
  {
    title: "Keep the line intact.",
    body: "Mechanical PhD, soft robotics, creative prototyping, AI-assisted tools, human-facing physical experiences. Make one action serve that line."
  }
];

const dateKey = new Date().toISOString().slice(0, 10);
const move = moves[Math.floor(Date.now() / 86400000) % moves.length];
const proofKey = `imagineer.proof.${dateKey}`;
const checkKey = `imagineer.checked.${dateKey}`;

const title = document.querySelector("#move-title");
const body = document.querySelector("#move-body");
const proof = document.querySelector("#proof-note");
const save = document.querySelector("#save-proof");
const saveState = document.querySelector("#save-state");
const proofCheck = document.querySelector("#proof-check");

title.textContent = move.title;
body.textContent = move.body;
proof.value = localStorage.getItem(proofKey) || "";
proofCheck.checked = localStorage.getItem(checkKey) === "true";

save.addEventListener("click", () => {
  localStorage.setItem(proofKey, proof.value.trim());
  saveState.textContent = proof.value.trim() ? "Saved for today." : "Cleared today's proof.";
});

proofCheck.addEventListener("change", () => {
  localStorage.setItem(checkKey, proofCheck.checked ? "true" : "false");
});
