# forensic_pipeline.mjs (verbatim)

> Raw audit artifact, wrapped in Markdown for fast-track-eligible tracking. Content below is byte-for-byte the original `forensic_pipeline.mjs`. To extract: delete this header and the surrounding fence lines.

````javascript
#!/usr/bin/env node
/**
 * forensic_pipeline.mjs — CONSOLIDATED orchestrator ("best-of" merge).
 *
 * One Node driver that runs the forensic-audit-pipeline spec as five sequential,
 * falsifiable stages over headless `claude -p` subagents. This file merges the
 * strongest idea from each of the seven independent agent implementations:
 *
 *   [cultivation] enum-coercing validator + error-feedback retry + spawn-error
 *                 handlers + RUN_ID file namespacing + E2BIG prompt-spill
 *   [RNA]         tolerant JSON parse, re-validate-every-handoff, delta-convergence
 *                 gate w/ persisted verdicts + unverified retention + adjudication
 *                 HALT, full env-parameterization, runtime model resolution+fallback,
 *                 --selftest, sub-stage resume (handoff reuse)
 *   [pytest]      opus falsifier + independent Stage-1 falsifier, --fallback-model,
 *                 pre-spawn stale-file delete, halt-on-no-falsification
 *   [DocInsight]  Stage-3 deep dependency pass: production-code coverage +
 *                 DRIFT-vs-DEFECT classification + deterministic back-propagation
 *   [mastery]     orchestrator-runs-the-tests (Stage-3 determinism), per-stage
 *                 cost TRACKING (informational), auto-preflight gate,
 *                 Stage-4 judge-panel consensus on goal grounding
 *   [Mito]        NUL-safe `git ls-files -z` denominator, esc() table rendering
 *
 * Deliberately NOT inherited: pytest's `\n`-split denominator + unescaped table
 * pipes; mastery's hardcoded branch/commands + no-in-process-validation; bare
 * JSON.parse (DocInsight/Mito); and mastery's DOLLAR BUDGET CAP — on a Claude
 * subscription the reported cost is API-equivalent (10–100x the real draw), so a
 * dollar ceiling would truncate legitimate agents and halt good runs for no real
 * reason. Runaway is bounded by --max-turns + per-call timeout; cost is tracked,
 * never gated. Pace a fan-out by your usage window, not the dollar figure.
 *
 * Usage:
 *   node forensic_pipeline.mjs                 # run/resume all incomplete stages
 *   node forensic_pipeline.mjs --from 2        # resume from stage N (reuse prior artifacts)
 *   node forensic_pipeline.mjs --stage 3       # run exactly one stage
 *   node forensic_pipeline.mjs --fresh         # tear down audit/ and start clean
 *   node forensic_pipeline.mjs --selftest      # zero-API: validate schemas+coercion+renderers
 *   node forensic_pipeline.mjs --preflight     # one cheap live call: auth + model resolution
 *   node forensic_pipeline.mjs --no-push       # commit per stage but don't push
 *   node forensic_pipeline.mjs --no-web        # disable web tools in Stage-4 research
 *   node forensic_pipeline.mjs --skip-preflight# skip the automatic auth/tool preflight gate
 *
 * Env knobs [RNA]: AUDIT_CHUNK, AUDIT_CONCURRENCY, AUDIT_S2_CEILING, AUDIT_S2_DELTA,
 *   AUDIT_RESEARCHERS, AUDIT_MODEL_HEAVY, AUDIT_MODEL_FAST.
 */
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync, rmSync, readdirSync } from "node:fs";
import { join, resolve } from "node:path";

// ───────────────────────── config ─────────────────────────
const REPO = resolve(process.cwd());
const AUDIT = join(REPO, "audit");
const WORK = join(AUDIT, ".work");
const RUN_ID = Date.now().toString(36); // [cultivation] namespaces worker files per process
const ARGV = process.argv.slice(2);
const FLAG = (n) => ARGV.includes(n);
const OPT = (n, d) => { const i = ARGV.indexOf(n); return i >= 0 && ARGV[i + 1] ? ARGV[i + 1] : d; };
const num = (v, d) => { const n = Number(v); return Number.isFinite(n) && n > 0 ? n : d; };

const FRESH = FLAG("--fresh");
const NO_PUSH = FLAG("--no-push");
const NO_WEB = FLAG("--no-web");
const DRY = FLAG("--dry-run"); // zero-API flow test: stub runAgent + git + Stage-3 exec with fixtures
const SKIP_PREFLIGHT = FLAG("--skip-preflight");
const ONLY_STAGE = OPT("--stage") ? num(OPT("--stage"), 0) : null;
const FROM_STAGE = OPT("--from") ? num(OPT("--from"), 1) : null;

const CFG = {
  chunk: num(process.env.AUDIT_CHUNK, 55),
  concurrency: num(process.env.AUDIT_CONCURRENCY, 4),
  s2Ceiling: num(process.env.AUDIT_S2_CEILING, 5),
  s2Delta: num(process.env.AUDIT_S2_DELTA, 5),     // [RNA] re-audit adding ≤N survivors/round ⇒ converged
  researchers: num(process.env.AUDIT_RESEARCHERS, 3),
};
// model aliases resolved at preflight [RNA]; opus reserved for gates/synthesis [pytest]
let MODEL_HEAVY = process.env.AUDIT_MODEL_HEAVY || "opus";   // synth / falsify / goal-judge / plan
let MODEL_FAST = process.env.AUDIT_MODEL_FAST || "sonnet";   // enumerate / classify / execute / research
const MODEL_CHEAP = "haiku";                                  // preflight / mechanical

const IGNORE = [/^audit\//, /^\.git\//, /(^|\/)node_modules\//, /(^|\/)\.venv\//, /(^|\/)__pycache__\//,
  /(^|\/)htmlcov\//, /(^|\/)\.pytest_cache\//, /(^|\/)dist\//, /(^|\/)build\//, /(^|\/)\.next\//]; // [mastery] full list
const BINARY_EXT = [".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".so", ".pyc", ".db", ".lance",
  ".zip", ".gz", ".whl", ".bin", ".pt", ".pth", ".onnx", ".parquet", ".woff", ".woff2"]; // [DocInsight]
const isBinary = (p) => BINARY_EXT.some((e) => p.toLowerCase().endsWith(e));

let BRANCH = "HEAD";
let TOTAL_USD = 0;
const COST_BY_STAGE = {}; // [mastery]
let SEQ = 0;

// ───────────────────────── utilities ─────────────────────────
const ts = () => new Date().toISOString().replace("T", " ").slice(0, 19);
function log(...m) { const line = `[${ts()}] ${m.join(" ")}`; console.error(line); try { writeFileSync(join(WORK, "run.log"), line + "\n", { flag: "a" }); } catch {} }

// [cultivation/mastery] spawn wrapper WITH an 'error' handler so a missing binary can't hang the promise.
function sh(cmd, args, opts = {}) {
  return new Promise((r) => {
    const p = spawn(cmd, args, { cwd: REPO, ...opts });
    let O = "", E = "";
    p.stdout?.on("data", (d) => (O += d));
    p.stderr?.on("data", (d) => (E += d));
    p.on("error", (err) => r({ code: 127, out: O, err: String(err) }));
    p.on("close", (code) => r({ code, out: O, err: E }));
  });
}

// [RNA] tolerant JSON: strip BOM, unwrap ```json fences, slice first {..last }.
function tolerantJson(s) {
  if (s == null) return null;
  let t = String(s).replace(/^﻿/, "").trim();
  const fence = t.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fence) t = fence[1].trim();
  const i = t.indexOf("{"), j = t.lastIndexOf("}");
  if (i >= 0 && j > i) t = t.slice(i, j + 1);
  try { return JSON.parse(t); } catch { return null; }
}

// [cultivation] enum synonym tables — the LLM emits drift (HIGH / blocker / confirmed); normalize before validate.
const ENUM_SYNONYMS = {
  severity: { blocker: "critical", crit: "critical", sev1: "critical", major: "high", sev2: "high", med: "medium", moderate: "medium", minor: "low", trivial: "low", info: "low", informational: "low" },
  role: { src: "source", code: "source", tests: "test", docs: "doc", documentation: "doc", configuration: "config", assets: "asset", build: "generated", artifact: "generated", unused: "dead" },
  verdict: { confirmed: "upheld", valid: "upheld", true: "upheld", refuted: "refuted", false: "refuted", invalid: "refuted", amended: "revised", reclassified: "revised" },
  delta: { verified: "confirmed", revised: "refined", amended: "refined" },
};
const SYN_KEYS = new Set(Object.keys(ENUM_SYNONYMS));
function coerceEnums(schema, data, key) {
  if (!schema || data == null) return data;
  if (schema.enum && typeof data === "string" && SYN_KEYS.has(key)) {
    const norm = data.trim().toLowerCase().replace(/[\s_-]+/g, "");
    if (schema.enum.includes(data)) return data;
    if (schema.enum.includes(norm)) return norm;
    const m = ENUM_SYNONYMS[key][norm];
    return m && schema.enum.includes(m) ? m : data;
  }
  if (schema.type === "object" && typeof data === "object") {
    for (const [k, s] of Object.entries(schema.properties || {})) if (k in data) data[k] = coerceEnums(s, data[k], k);
  }
  if (schema.type === "array" && Array.isArray(data) && schema.items) data.forEach((v, i) => (data[i] = coerceEnums(schema.items, v, key)));
  return data;
}

// [cultivation/RNA] dependency-free recursive schema validator → list of human-readable errors.
function validate(schema, data, path = "$") {
  const errs = [];
  const t = schema.type;
  const typeOk = (v) => t === "object" ? v && typeof v === "object" && !Array.isArray(v)
    : t === "array" ? Array.isArray(v) : t === "integer" ? Number.isInteger(v)
    : t === "number" ? typeof v === "number" : t === "string" ? typeof v === "string"
    : t === "boolean" ? typeof v === "boolean" : true;
  if (t && !typeOk(data)) { errs.push(`${path}: expected ${t}, got ${Array.isArray(data) ? "array" : typeof data}`); return errs; }
  if (schema.enum && !schema.enum.includes(data)) errs.push(`${path}: ${JSON.stringify(data)} not in [${schema.enum.join(", ")}]`);
  if (t === "string" && schema.minLength && (data || "").length < schema.minLength) errs.push(`${path}: shorter than minLength ${schema.minLength}`);
  if (t === "object") {
    for (const r of schema.required || []) if (!(r in (data || {}))) errs.push(`${path}.${r}: required`);
    for (const [k, s] of Object.entries(schema.properties || {})) if (data && k in data) errs.push(...validate(s, data[k], `${path}.${k}`));
  }
  if (t === "array") {
    if (schema.minItems && (data || []).length < schema.minItems) errs.push(`${path}: fewer than minItems ${schema.minItems}`);
    if (schema.items && Array.isArray(data)) data.forEach((it, i) => errs.push(...validate(schema.items, it, `${path}[${i}]`)));
  }
  return errs;
}

// [Mito/cultivation] markdown helpers — escape pipes + newlines so a `|` in evidence can't corrupt a table.
const esc = (s) => String(s == null ? "" : s).replace(/\|/g, "\\|").replace(/\n+/g, " ").trim();
const tbl = (head, rows) => [`| ${head.join(" | ")} |`, `| ${head.map(() => "---").join(" | ")} |`, ...rows.map((r) => `| ${r.map(esc).join(" | ")} |`)].join("\n");
const jsonBlock = (o) => "\n\n## Machine-checkable data\n\n```json\n" + JSON.stringify(o, null, 2) + "\n```\n"; // [DocInsight] embedded appendix enables back-prop
const docHead = (t) => `# ${t}\n\n_Generated ${ts()} · branch \`${BRANCH}\` · forensic-audit-pipeline (consolidated)_\n`;

// ───────────────────── invariants (every agent prompt) ─────────────────────
const INVARIANTS = [
  "You are a worker in a FORENSIC AUDIT pipeline. Obey these invariants without exception:",
  "1. Absence of evidence is NOT evidence of absence — never claim a thing is absent/unused/unreachable unless you searched the full Stage-1 surface; otherwise record it as UNVERIFIED.",
  "2. No claim without a concrete `path:line` (or named artifact) a reviewer can open. Drop claims that lack an anchor.",
  "3. Coverage has a denominator and visitation must be EVIDENCED: a self-reported 'visited' list is not proof you opened the file. Visitation counts only when a real Read/Grep actually touched the path (or the falsifier spot-checked it); self-attested coverage is UNVERIFIED.",
  "4. Verification is adversarial, not self-review: a claim is promoted only after a SEPARATE agent, handed the source + the claim, tries to REFUTE it. Refinement improves wording, not truth.",
  "5. You may read/instrument/run/modify code in THIS sandbox to produce evidence; the only shipped deliverable is the audit/*.md documents (mutation is a means, not a deliverable).",
  "6. NEVER exfiltrate sensitive data into an artifact. Repos may hold PII, PHI, secrets, or legal/medical records, and evidence quotes flow into committed, pushed files. Reference sensitive material by location + category ONLY — never paste the content. When in doubt, cite the path and stop.",
  // [openclaw #7 lessons — baked in as hard rules]
  "7. META-REPO RULE: if the repo's primary function is to coordinate/track/reference OTHER repos (a registry, a path list, pervasive cross-repo references), its goal may live in those siblings. Do NOT score a portfolio/mission goal as 'narrative / not-as-built' merely because this repo's own code doesn't optimize for it — label it OUT-OF-SCOPE (delegated) with a pointer, never falsified.",
  "8. STATED-NEGATIVE RULE: an in-repo status note / memory file / README claim that something is 'unbuilt', 'dead', 'stalled', or 'still pending' is NOT ground truth. Verify it against a primary source or live execution before recording it as fact.",
  "9. When given an OUTPUT CONTRACT, use the Write tool to put ONLY raw JSON (no fence, no prose) at the exact path.",
].join("\n");

// ───────────────────────── state / checkpoint ─────────────────────────
const statePath = join(WORK, "state.json");
const loadState = () => existsSync(statePath) ? (tolerantJson(readFileSync(statePath, "utf8")) || { completed: {} }) : { completed: {} };
function saveState(s) { s.totalUsd = TOTAL_USD; s.costByStage = COST_BY_STAGE; writeFileSync(statePath, JSON.stringify(s, null, 2)); }
const readWork = (f) => existsSync(join(WORK, f)) ? tolerantJson(readFileSync(join(WORK, f), "utf8")) : null;
const writeWork = (f, o) => writeFileSync(join(WORK, f), JSON.stringify(o, null, 2));

class Halt extends Error { constructor(stage, why) { super(why); this.stage = stage; } }
async function halt(stage, why, state) {
  const report = `# AUDIT HALTED at ${stage}\n\n${why}\n\n_${ts()} · branch ${BRANCH}_\n`;
  writeFileSync(join(AUDIT, "HALT-REPORT.md"), report);
  state && saveState(state);
  await gitPersist(`audit(${stage}): HALT — ${why.slice(0, 60)}`);
  throw new Halt(stage, why);
}

async function checkpoint(stageKey, mdName, md, jsonName, obj, state) {
  if (jsonName) writeWork(jsonName, obj);
  writeFileSync(join(AUDIT, mdName), md);
  // clear any stale halt now that this stage succeeded [pytest]
  try { rmSync(join(AUDIT, "HALT-REPORT.md")); } catch {}
  delete state.halt;
  state.completed[stageKey] = ts();
  saveState(state);
  await gitPersist(`audit(${stageKey}): checkpoint`);
}

async function gitPersist(message) {
  if (DRY) { log("(dry-run) skip commit/push"); return; }
  await sh("git", ["add", "audit"]);
  const c = await sh("git", ["-c", "commit.gpgsign=false", "commit", "-m", message]);
  if (c.code !== 0) { log("nothing to commit"); return; }
  if (NO_PUSH) { log("committed (push skipped)"); return; }
  for (let i = 0; i < 4; i++) { // [all] push with exponential backoff
    const p = await sh("git", ["push", "-u", "origin", BRANCH]);
    if (p.code === 0) { log("pushed"); return; }
    await new Promise((x) => setTimeout(x, 2000 * 2 ** i));
  }
  log("WARN push failed after retries");
}

// ───────────────────────── cost TRACKING (informational only) ─────────────────────────
// `claude -p` reports an API-equivalent total_cost_usd. On a subscription the real draw is
// ~10–100x lower, so we NEVER gate on it (no ceiling, no per-call --max-budget-usd): a dollar
// cap would truncate legitimate agents. Runaway is bounded by --max-turns + per-call timeout.
function trackCost(stage, usd) { TOTAL_USD += usd; COST_BY_STAGE[stage] = (COST_BY_STAGE[stage] || 0) + usd; }

// ───────────────────────── dry-run fixtures (zero-API end-to-end flow test) ─────────────────────────
// Stubs runAgent with schema-coherent, cross-referenced fixtures so every gate (coverage stop-test,
// adversarial falsify, <60% adjudication HALT, delta-convergence, S3 back-prop, S5 mappability) and
// the checkpoint/resume control flow execute with no API calls and no side effects.
const DRY_FILES = [
  { path: "src/app.py", role: "source" }, { path: "src/util.py", role: "source" },
  { path: "tests/test_app.py", role: "test" }, { path: "README.md", role: "doc" },
  { path: "pyproject.toml", role: "config" },
];
const DRY_GOAL = "DRY-RUN: serve as a self-contained example repo for exercising the audit pipeline end-to-end";
const DRY_FIX = {
  "preflight": { ok: true, model: "dry" },
  "s1:classify": { files: DRY_FILES, entry_points: [{ entry: "src/app.py:main", what: "CLI entry" }] },
  "s1:gapfill": { files: [], entry_points: [] },
  "s1:synth": { architecture_summary: "Dry-run example: a tiny Python package with a CLI entry point and a test.", provisional_intent: "Provide a minimal self-contained target to exercise the forensic pipeline flow." },
  "s1:falsify": { misclassified: [], missed_entry_points: [] },
  "s2:audit": { findings: [
    { id: "x1", location: "src/app.py:10", class: "correctness", severity: "high", evidence: "Dry-run finding A: unchecked return value at the CLI boundary." },
    { id: "x2", location: "src/util.py:5", class: "security", severity: "medium", evidence: "Dry-run finding B: f-string used to assemble a shell command." },
  ], visited: DRY_FILES.map((f) => f.path) },
  // verdicts reference the reId'd ids (F1,F2) so adjudication = 100% (passes the <60% HALT)
  "s2:falsify": { verdicts: [{ id: "F1", verdict: "upheld", reason: "dry" }, { id: "F2", verdict: "upheld", reason: "dry" }] },
  "s3:discover": { commands: [{ cmd: "echo install", purpose: "install" }, { cmd: "echo test", purpose: "test" }, { cmd: "echo coverage", purpose: "coverage" }] },
  "s3:analyze": { coverage_pct: 42, observed: [{ entry: "src/app.py:main", behavior: "exits 0 on --help" }], deltas: [{ id: "F1", delta: "confirmed", evidence: "reproduced at runtime" }], unexecuted: [{ region: "network path", reason: "external-service", command: "python -m app --net", failure: "ConnectionError to api.example.com", stub_tried: "monkeypatched requests.get" }] },
  "s3:verify": { coverage_supported: true, discrepancies: [] },
  "s3:deep": { deps_installed: true, production_coverage_pct: 55, deltas: [{ id: "F2", delta: "refined", classification: "DEFECT", note: "confirmed under real deps" }], version_drift: [], still_unexecuted: [{ region: "GPU path", reason: "hardware-gated" }] },
  "s4:goal": { candidates: [{ goal: DRY_GOAL, status: "grounded", signals: [{ signal: "CLI entry exists", evidence: "src/app.py:main", met: true }] }] },
  "s4:research": { ideas: [{ idea: "Add a coverage gate to CI", advances: "raises the measured-coverage signal", corroboration: "corroborated", sources: ["https://example.org"] }] },
  "s4:judge": { verdicts: [{ goal: DRY_GOAL, grounded: true, status: "grounded", note: "dry" }] },
  "s5:plan": { items: [{ id: "P1", change: "Guard the unchecked return value", links_to: "F1", location: "src/app.py:10", verification: "unit test asserts non-zero exit", depends_on: "none" }] },
  "s5:map": { all_mappable: true, ambiguous: [] },
};
function fakeFromSchema(s) { // fallback for any agent name without an explicit fixture
  if (!s || !s.type) return {};
  if (s.enum) return s.enum[0];
  if (s.type === "string") return "x".repeat(s.minLength || 3);
  if (s.type === "integer" || s.type === "number") return 1;
  if (s.type === "boolean") return true;
  if (s.type === "array") return Array.from({ length: s.minItems || 1 }, () => fakeFromSchema(s.items || { type: "string" }));
  if (s.type === "object") { const o = {}; for (const k of s.required || []) o[k] = fakeFromSchema((s.properties || {})[k] || { type: "string" }); return o; }
  return {};
}
function dryAgent(name, schema) {
  const key = Object.keys(DRY_FIX).filter((k) => name.startsWith(k)).sort((a, b) => b.length - a.length)[0];
  log(`(dry-run) ${name} → ${key || "schema-faked"}`);
  return { ok: true, data: key ? structuredClone(DRY_FIX[key]) : fakeFromSchema(schema) };
}

// ───────────────────────── the agent runner ─────────────────────────
const pMap = async (xs, fn, n = CFG.concurrency) => { // [all] bounded-concurrency barrier
  const out = new Array(xs.length); let i = 0;
  const work = async () => { while (i < xs.length) { const k = i++; out[k] = await fn(xs[k], k); } };
  await Promise.all(Array.from({ length: Math.min(n, xs.length) }, work));
  return out;
};

/**
 * runAgent — drives one `claude -p` subagent, hands off structured JSON via a file,
 * coerces enums + validates, and retries with the *exact validation error fed back*
 * into the next prompt [cultivation]. Tolerant parse [RNA], stale-file delete +
 * fallback-model [pytest], spawn-error safety [mastery/cultivation], usage-limit-aware
 * backoff [RNA]. Bounded by --max-turns + timeout — NO dollar cap (subscription).
 */
async function runAgent({ name, prompt, schema, model = MODEL_FAST, fallback = MODEL_FAST, budgetUsd = 4, maxTurns = 60, web = false, bash = true, timeoutMs = 1_200_000, tries = 3 }) {
  if (DRY) return dryAgent(name, schema);
  const tools = ["Read", "Grep", "Glob", "Write", ...(bash ? ["Bash"] : []), ...(web && !NO_WEB ? ["WebSearch", "WebFetch"] : [])].join(",");
  const out = join(WORK, `a_${name}_${RUN_ID}_${++SEQ}.json`);
  let lastErrs = null;
  for (let attempt = 1; attempt <= tries; attempt++) {
    try { rmSync(out); } catch {} // [pytest] never read a previous attempt's file as success
    const feedback = lastErrs ? `\n\nPREVIOUS ATTEMPT FAILED SCHEMA VALIDATION. Fix exactly these and re-emit the FULL object:\n- ${lastErrs.slice(0, 8).join("\n- ")}` : "";
    let full = `${prompt}\n\nOUTPUT CONTRACT: use the Write tool to put ONLY raw JSON conforming to this schema at ${out}:\n${JSON.stringify(schema)}${feedback}`;
    // [cultivation] E2BIG guard: huge prompts are spilled to a file the worker reads.
    if (Buffer.byteLength(full) > 60_000) { const pf = join(WORK, `prompt_${name}_${RUN_ID}_${SEQ}.txt`); writeFileSync(pf, full); full = `Your full instructions are in the file ${pf} — read it first, then follow it exactly.`; }
    const args = ["-p", full, "--output-format", "json", "--model", model, "--fallback-model", fallback,
      "--max-turns", String(maxTurns), "--allowedTools", tools,  // no --max-budget-usd: subscription cost is API-equiv; a cap truncates legitimate work
      "--add-dir", REPO, "--strict-mcp-config", "--permission-mode", "acceptEdits", "--append-system-prompt", INVARIANTS];
    log(`→ ${name} (attempt ${attempt}/${tries}) model=${model}`);
    const r = await new Promise((res) => {
      const p = spawn("claude", args, { cwd: REPO, stdio: ["ignore", "pipe", "pipe"], env: process.env });
      let O = "", E = "";
      const k = setTimeout(() => { try { p.kill("SIGKILL"); } catch {} }, timeoutMs);
      p.on("error", (err) => { clearTimeout(k); res({ O, E: String(err), spawnFail: true }); });
      p.stdout.on("data", (d) => (O += d));
      p.stderr.on("data", (d) => (E += d));
      p.on("close", () => { clearTimeout(k); res({ O, E }); });
    });
    const env = tolerantJson(r.O);
    if (env && typeof env.total_cost_usd === "number") trackCost(name.split(":")[0], env.total_cost_usd);
    // [RNA] usage/rate-limit detection → longer backoff before retry
    const limited = /usage limit|rate limit|overloaded|429/i.test(r.E + (env?.subtype || ""));
    const data = readWork(out.replace(WORK + "/", "")); // tolerant read of the handoff
    if (!data) { log(`  no/!json handoff (attempt ${attempt})${limited ? " [usage-limited]" : ""}`); await new Promise((x) => setTimeout(x, (limited ? 30000 : 3000) * attempt)); continue; }
    coerceEnums(schema, data);
    const errs = validate(schema, data);
    if (errs.length) { lastErrs = errs; log(`  schema errs: ${errs.slice(0, 3).join("; ")}`); continue; }
    return { ok: true, data };
  }
  return { ok: false, errs: lastErrs };
}

async function gitBranch() { if (DRY) return "dry-run"; const r = await sh("git", ["rev-parse", "--abbrev-ref", "HEAD"]); return (r.out || "").trim() || "HEAD"; }

// ───────────────────────── denominator [Mito/RNA/DocInsight] ─────────────────────────
async function enumerate() {
  if (DRY) return DRY_FILES.map((f) => f.path);
  const tracked = await sh("git", ["ls-files", "-z"]);                                  // [Mito] NUL-safe
  const untracked = await sh("git", ["ls-files", "-z", "--others", "--exclude-standard"]); // ∪ untracked [RNA]
  const all = (tracked.out + "\0" + untracked.out).split("\0").map((s) => s.trim()).filter(Boolean);
  const uniq = [...new Set(all)].filter((p) => !IGNORE.some((re) => re.test(p))).sort();
  return uniq;
}

// ───────────────────────── schemas ─────────────────────────
const ROLE = { type: "string", enum: ["source", "test", "doc", "config", "asset", "generated", "dead", "submodule", "unknown"] };
const SEV = { type: "string", enum: ["critical", "high", "medium", "low", "info"] };
const S1_SLICE = { type: "object", required: ["files"], properties: { files: { type: "array", items: { type: "object", required: ["path", "role"], properties: { path: { type: "string" }, role: ROLE, note: { type: "string" } } } }, entry_points: { type: "array", items: { type: "object", required: ["entry", "what"], properties: { entry: { type: "string" }, what: { type: "string" } } } } } };
const S1_SYNTH = { type: "object", required: ["architecture_summary", "provisional_intent"], properties: { architecture_summary: { type: "string", minLength: 40 }, provisional_intent: { type: "string", minLength: 40 } } };
const S1_FALSIFY = { type: "object", required: ["misclassified", "missed_entry_points"], properties: { misclassified: { type: "array", items: { type: "object", required: ["path", "should_be"], properties: { path: { type: "string" }, should_be: ROLE, why: { type: "string" } } } }, missed_entry_points: { type: "array", items: { type: "string" } } } };
const FINDING = { type: "object", required: ["id", "location", "class", "severity", "evidence"], properties: { id: { type: "string" }, title: { type: "string" }, location: { type: "string" }, class: { type: "string" }, severity: SEV, evidence: { type: "string", minLength: 20 }, intent_mismatch: { type: "boolean" } } };
const S2_AUDIT = { type: "object", required: ["findings", "visited"], properties: { findings: { type: "array", items: FINDING }, visited: { type: "array", items: { type: "string" } } } };
const VERDICT = { type: "object", required: ["id", "verdict"], properties: { id: { type: "string" }, verdict: { type: "string", enum: ["upheld", "refuted", "revised"] }, corrected_severity: SEV, reason: { type: "string" } } };
const S2_FALSIFY = { type: "object", required: ["verdicts"], properties: { verdicts: { type: "array", items: VERDICT } } };
const S3_DISCOVER = { type: "object", required: ["commands"], properties: { commands: { type: "array", items: { type: "object", required: ["cmd", "purpose"], properties: { cmd: { type: "string" }, purpose: { type: "string", enum: ["install", "test", "coverage", "lint", "build", "run"] } } } } } };
const S3_ANALYZE = { type: "object", required: ["coverage_pct", "observed", "deltas", "unexecuted"], properties: { coverage_pct: { type: "number" }, observed: { type: "array", items: { type: "object", required: ["entry", "behavior"], properties: { entry: { type: "string" }, behavior: { type: "string" } } } }, deltas: { type: "array", items: { type: "object", required: ["id", "delta"], properties: { id: { type: "string" }, delta: { type: "string", enum: ["confirmed", "refuted", "refined", "untested"] }, evidence: { type: "string" } } } }, unexecuted: { type: "array", items: { type: "object", required: ["region", "reason", "command", "failure"], properties: { region: { type: "string" }, reason: { type: "string", enum: ["requires-credentials", "external-service", "hardware-gated", "requires-submodule", "dead", "destructive-skip"] }, command: { type: "string" }, failure: { type: "string" }, stub_tried: { type: "string" } } } } } }; // [skill] un-executed needs proof-of-attempt
const S3_VERIFY = { type: "object", required: ["coverage_supported", "discrepancies"], properties: { coverage_supported: { type: "boolean" }, discrepancies: { type: "array", items: { type: "string" } } } };
const S3_ACCOUNT = { type: "object", required: ["flipped", "still_unexecuted"], properties: { flipped: { type: "array", items: { type: "object", required: ["region", "how", "evidence"], properties: { region: { type: "string" }, how: { type: "string" }, evidence: { type: "string" } } } }, still_unexecuted: { type: "array", items: { type: "object", required: ["region", "reason", "command", "failure"], properties: { region: { type: "string" }, reason: { type: "string" }, command: { type: "string" }, failure: { type: "string" } } } } } }; // [skill] adversarial accounting
const S3_DEEP = { type: "object", required: ["deps_installed", "production_coverage_pct", "deltas", "still_unexecuted"], properties: { deps_installed: { type: "boolean" }, production_coverage_pct: { type: "number" }, deltas: { type: "array", items: { type: "object", required: ["id", "delta", "classification"], properties: { id: { type: "string" }, delta: { type: "string", enum: ["confirmed", "refuted", "refined", "untested"] }, classification: { type: "string", enum: ["DEFECT", "DRIFT", "NA"] }, note: { type: "string" } } } }, version_drift: { type: "array", items: { type: "object", required: ["package", "pinned", "installed"], properties: { package: { type: "string" }, pinned: { type: "string" }, installed: { type: "string" } } } }, still_unexecuted: { type: "array", items: { type: "object", required: ["region", "reason"], properties: { region: { type: "string" }, reason: { type: "string" } } } } } };
const GOAL_CANDIDATE = { type: "object", required: ["goal", "status", "signals"], properties: { goal: { type: "string", minLength: 30 }, status: { type: "string", enum: ["grounded", "needs-human-confirm", "speculative", "out-of-scope-delegated"] }, signals: { type: "array", minItems: 1, items: { type: "object", required: ["signal", "evidence", "met"], properties: { signal: { type: "string" }, evidence: { type: "string" }, met: { type: "boolean" } } } } } };
const S4_GOAL = { type: "object", required: ["candidates"], properties: { candidates: { type: "array", minItems: 1, items: GOAL_CANDIDATE } } };
const S4_JUDGE = { type: "object", required: ["verdicts"], properties: { verdicts: { type: "array", items: { type: "object", required: ["goal", "grounded", "status"], properties: { goal: { type: "string" }, grounded: { type: "boolean" }, status: { type: "string", enum: ["grounded", "needs-human-confirm", "speculative", "out-of-scope-delegated"] }, note: { type: "string" } } } } } };
const RESEARCH_IDEA = { type: "object", required: ["idea", "advances", "corroboration"], properties: { idea: { type: "string" }, advances: { type: "string" }, corroboration: { type: "string", enum: ["corroborated", "single-source", "unverified", "blocked"] }, sources: { type: "array", items: { type: "string" } } } };
const S4_RESEARCH = { type: "object", required: ["ideas"], properties: { ideas: { type: "array", items: RESEARCH_IDEA } } };
const S5_PLAN = { type: "object", required: ["items"], properties: { items: { type: "array", items: { type: "object", required: ["id", "change", "links_to", "location", "verification", "depends_on"], properties: { id: { type: "string" }, change: { type: "string" }, links_to: { type: "string" }, location: { type: "string" }, verification: { type: "string" }, depends_on: { type: "string" } } } } } };
const S5_MAP = { type: "object", required: ["all_mappable", "ambiguous"], properties: { all_mappable: { type: "boolean" }, ambiguous: { type: "array", items: { type: "string" } } } };

// ───────────────────────── helpers shared by stages ─────────────────────────
const fp = (f) => `${(f.location || "").split(/[:#]/)[0].toLowerCase()}|${(f.class || "").toLowerCase()}|${(f.title || f.evidence || "").slice(0, 40).toLowerCase()}`;
function dedupe(arr) { const m = new Map(); for (const f of arr) if (!m.has(fp(f))) m.set(fp(f), f); return [...m.values()]; }
const reId = (arr) => arr.map((f, i) => ({ ...f, id: "F" + (i + 1) }));
const sig = (arr) => arr.map(fp).sort().join("\n");
const packChunks = (xs, n) => { const o = []; for (let i = 0; i < xs.length; i += n) o.push(xs.slice(i, i + n)); return o; };

// ───────────────────────── Stage 1 — understanding ─────────────────────────
async function stage1(state) {
  const denom = await enumerate();
  const chunks = packChunks(denom.filter((p) => !isBinary(p)), CFG.chunk);
  const bins = denom.filter(isBinary).map((p) => ({ path: p, role: "asset", note: "binary (classified by extension, not read)" })); // [DocInsight]
  const slices = await pMap(chunks, async (paths, idx) => {
    const r = await runAgent({ name: `s1:classify:${idx}`, model: MODEL_FAST, schema: S1_SLICE,
      prompt: `Classify each of these ${paths.length} files in repo ${REPO} by role (source/test/doc/config/asset/generated/dead/submodule). Trace any entry points (CLI, exported API, route, main). Files:\n${paths.join("\n")}` });
    if (!r.ok) await halt("stage1", `classification slice ${idx} failed: ${(r.errs || []).join("; ")}`, state);
    return r.data;
  });
  let files = dedupeFiles([...bins, ...slices.flatMap((s) => s.files)]);
  const entry_points = slices.flatMap((s) => s.entry_points || []);
  // coverage stop-test: every denominator path classified
  const classified = new Set(files.map((f) => f.path));
  const missing = denom.filter((p) => !classified.has(p));
  if (missing.length) { // one gap-fill round
    const r = await runAgent({ name: "s1:gapfill", model: MODEL_FAST, schema: S1_SLICE, prompt: `Classify these still-unclassified files by role:\n${missing.join("\n")}` });
    if (r.ok) files = dedupeFiles([...files, ...r.data.files]);
  }
  const stillMissing = denom.filter((p) => !new Set(files.map((f) => f.path)).has(p));
  if (stillMissing.length) await halt("stage1", `coverage stop-test failed: ${stillMissing.length} unclassified (e.g. ${stillMissing.slice(0, 5).join(", ")})`, state);
  if (files.some((f) => f.role === "unknown")) log(`WARN ${files.filter((f) => f.role === "unknown").length} files left role=unknown`);

  const synthR = await runAgent({ name: "s1:synth", model: MODEL_HEAVY, schema: S1_SYNTH, prompt: `From this inventory of ${files.length} files + ${entry_points.length} entry points, write an architecture_summary and a provisional_intent (the apparent goal — mark it provisional). Inventory roles: ${JSON.stringify(roleCounts(files))}. Entry points: ${JSON.stringify(entry_points.slice(0, 40))}` });
  if (!synthR.ok) await halt("stage1", "synthesis failed", state);

  // [pytest] independent Stage-1 falsifier: a fresh agent tries to refute the classification + intent
  const falR = await runAgent({ name: "s1:falsify", model: MODEL_HEAVY, schema: S1_FALSIFY, prompt: `Adversarially review this Stage-1 inventory. Find MISCLASSIFIED files and MISSED entry points. Architecture: ${synthR.data.architecture_summary}\nIntent: ${synthR.data.provisional_intent}\nSample roles: ${JSON.stringify(files.slice(0, 60))}` });
  if (falR.ok && (falR.data.misclassified.length || falR.data.missed_entry_points.length)) {
    for (const m of falR.data.misclassified) { const f = files.find((x) => x.path === m.path); if (f) f.role = m.should_be; }
    log(`s1 falsifier corrected ${falR.data.misclassified.length} roles, +${falR.data.missed_entry_points.length} entry points`);
  }
  const inv = { denominator: denom.length, files, entry_points, ...synthR.data };
  await checkpoint("stage1", "01-understanding.md", renderS1(inv), "stage1.json", inv, state);
  return inv;
}
function dedupeFiles(arr) { const m = new Map(); for (const f of arr) if (!m.has(f.path)) m.set(f.path, f); return [...m.values()]; }
function roleCounts(files) { const c = {}; files.forEach((f) => (c[f.role] = (c[f.role] || 0) + 1)); return c; }
function renderS1(inv) {
  return [docHead("01 — Understanding"), `**Coverage denominator:** ${inv.denominator} files (every one classified — see appendix).`, "",
    `## Architecture\n\n${inv.architecture_summary}`, "", `## Provisional intent\n\n${inv.provisional_intent}`, "",
    `## Role distribution\n`, tbl(["Role", "Count"], Object.entries(roleCounts(inv.files))), "",
    `## Entry points (${inv.entry_points.length})\n`, tbl(["Entry", "What"], inv.entry_points.map((e) => [e.entry, e.what])),
    jsonBlock({ denominator: inv.denominator, roleCounts: roleCounts(inv.files), entry_points: inv.entry_points })].join("\n");
}

// ───────────────────────── Stage 2 — static audit (adversarial gate) ─────────────────────────
async function stage2(state, s1) {
  const auditable = s1.files.filter((f) => ["source", "config", "test"].includes(f.role)).map((f) => f.path); // role-scoped denominator [RNA/cultivation]
  const LENSES = ["correctness/logic bugs", "security (injection, authz, SSRF, secrets, path traversal)", "doc/code drift & intent mismatch", "resource/error-handling & dead code"]; // [cultivation] diverse lenses
  let findings = readWork("stage2.json")?.findings || []; // [RNA/mastery] sub-stage resume
  let prevSig = sig(findings), round = 0;

  while (round < CFG.s2Ceiling) {
    round++;
    // audit sweep: lenses × chunks, parallel
    const tasks = LENSES.flatMap((lens) => packChunks(auditable, CFG.chunk).map((paths) => ({ lens, paths })));
    const swept = await pMap(tasks, async (t, i) => {
      const r = await runAgent({ name: `s2:audit:${round}:${i}`, model: MODEL_FAST, schema: S2_AUDIT,
        prompt: `Audit for defects under the lens "${t.lens}" in repo ${REPO}. Judge against the provisional intent: ${s1.provisional_intent}. Each finding needs a precise path:line and concrete evidence. Files:\n${t.paths.join("\n")}` });
      return r.ok ? r.data.findings : [];
    });
    findings = reId(dedupe([...findings, ...swept.flat()]));

    // [skill] Falsify the WHOLE current set every round (not just new ones), on the heavy model
    // [pytest] — so a finding is re-tested against fresh adversarial context and no candidate ships
    // un-falsified. Fixpoint is declared only when a full cycle adds nothing AND refutes nothing.
    const fresh = new Map();
    let anyVerdict = false;
    const verdictBatches = await pMap(packChunks(findings, 25), async (batch, i) => {
      const r = await runAgent({ name: `s2:falsify:${round}:${i}`, model: MODEL_HEAVY, schema: S2_FALSIFY,
        prompt: `You are an INDEPENDENT falsifier. For EACH finding, try to REFUTE it against the actual code, and SPOT-CHECK that the cited path:line really supports it (a wrong/empty location is a refutation). Return a verdict (upheld/refuted/revised) per id with a reason. Findings:\n${JSON.stringify(batch)}` });
      return r.ok ? r.data.verdicts : null;
    });
    for (const vb of verdictBatches) { if (vb) { anyVerdict = true; for (const v of vb) fresh.set(v.id, v); } }
    if (!anyVerdict) await halt("stage2", `falsifier produced no verdicts in round ${round} — treating as outage, not refutation`, state); // [pytest]

    // apply this round's verdicts: drop refuted, apply revised severity, KEEP un-adjudicated as 'unverified' [RNA]
    const refutedThisRound = findings.filter((f) => fresh.get(f.id)?.verdict === "refuted").length;
    findings = findings.filter((f) => fresh.get(f.id)?.verdict !== "refuted").map((f) => {
      const v = fresh.get(f.id);
      if (v?.verdict === "revised" && v.corrected_severity) f.severity = v.corrected_severity;
      f.status = v ? "verified" : "unverified";
      return f;
    });
    findings = reId(findings);

    // [RNA] adjudication-coverage HALT: an outage (most findings unverified) is not convergence
    const adjudicated = findings.filter((f) => f.status === "verified").length;
    if (findings.length && adjudicated / findings.length < 0.6) await halt("stage2", `only ${adjudicated}/${findings.length} adjudicated (<60%) — falsifier coverage too low to trust`, state);

    // [skill] fixpoint ONLY when a full cycle adds nothing AND refutes nothing; delta is the escape valve
    const curSig = sig(findings), added = curSig.split("\n").filter((x) => x && !prevSig.includes(x)).length;
    log(`s2 round ${round}: ${findings.length} findings, ${adjudicated} verified, +${added} new, ${refutedThisRound} refuted`);
    writeWork("stage2.json", { findings }); // persist for sub-stage resume
    if (refutedThisRound === 0 && (curSig === prevSig || added <= CFG.s2Delta)) break;
    prevSig = curSig;
  }
  const obj = { findings, rounds: round, by_severity: bySeverity(findings) };
  await checkpoint("stage2", "02-static-audit.md", renderS2(obj), "stage2.json", obj, state);
  return obj;
}
const bySeverity = (fs) => fs.reduce((a, f) => ((a[f.severity] = (a[f.severity] || 0) + 1), a), {});
function renderS2(o) {
  return [docHead("02 — Static Audit"), `**${o.findings.length} findings** over ${o.rounds} audit→falsify rounds (converged). By severity: ${JSON.stringify(o.by_severity)}.`, "",
    `_Findings marked \`unverified\` survived but were not adjudicated by the falsifier; treat as lower-confidence._`, "",
    tbl(["ID", "Sev", "Status", "Location", "Class", "Evidence"], o.findings.map((f) => [f.id, f.severity, f.status || "verified", f.location, f.class, f.evidence])),
    jsonBlock(o)].join("\n");
}

// ───────────────────────── Stage 3 — execution (deterministic + deep) ─────────────────────────
async function stage3(state, s1, s2) {
  // (a) discovery agent finds the build/test/coverage commands — generic, not hardcoded [cultivation]
  const disc = await runAgent({ name: "s3:discover", model: MODEL_FAST, schema: S3_DISCOVER, bash: true,
    prompt: `Inspect repo ${REPO} (Makefile, pyproject/package.json/Taskfile, CI configs) and list the exact shell commands to install deps, run the test suite, and produce a coverage report. Do NOT run them — just discover them.` });
  if (!disc.ok) await halt("stage3", "command discovery failed", state);

  // (b) THE ORCHESTRATOR runs them deterministically under a timeout [mastery] — the agent never runs the suite itself
  const runLog = [];
  for (const c of disc.data.commands.filter((x) => ["install", "test", "coverage"].includes(x.purpose))) {
    if (DRY) { runLog.push({ cmd: c.cmd, purpose: c.purpose, code: 0, tail: "(dry-run: not executed)" }); continue; }
    log(`s3 run: ${c.cmd}`);
    const r = await sh("bash", ["-lc", `timeout 1200 ${c.cmd}`]);
    const tail = (r.out + "\n" + r.err).slice(-4000);
    runLog.push({ cmd: c.cmd, purpose: c.purpose, code: r.code, tail });
  }
  writeWork("s3_runlog.json", runLog);

  // (c) an agent ANALYZES the captured output (does not re-run) and applies deltas to Stage-2 findings
  const an = await runAgent({ name: "s3:analyze", model: MODEL_FAST, schema: S3_ANALYZE, bash: false,
    prompt: `Here is the captured output of the test/coverage commands the orchestrator ran (you did NOT run them):\n${JSON.stringify(runLog)}\n\nReport measured coverage_pct, observed behaviors, the delta for each Stage-2 finding it touches (confirmed/refuted/refined/untested with evidence), and account for every un-executed region with a reason. Findings:\n${JSON.stringify(s2.findings.map((f) => ({ id: f.id, location: f.location, evidence: f.evidence })))}` });
  if (!an.ok) await halt("stage3", "execution analysis failed", state);

  // (d) independent coverage-honesty verifier re-reads the raw log [cultivation/pytest/RNA]
  const ver = await runAgent({ name: "s3:verify", model: MODEL_HEAVY, schema: S3_VERIFY, bash: true,
    prompt: `Cross-check this coverage claim against the raw run log. Is coverage_pct=${an.data.coverage_pct} supported by the actual output? List discrepancies.\nRun log tails:\n${JSON.stringify(runLog.map((r) => ({ cmd: r.cmd, code: r.code, tail: r.tail.slice(-1500) })))}` });
  const verified = ver.ok ? ver.data.coverage_supported : false;

  // (e) DEEP dependency pass [DocInsight]: install full stack, exercise real production code, classify DRIFT vs DEFECT
  let deep = null;
  const installCmds = disc.data.commands.filter((x) => x.purpose === "install").map((x) => x.cmd);
  if (installCmds.length) {
    const dr = await runAgent({ name: "s3:deep", model: MODEL_FAST, schema: S3_DEEP, bash: true, budgetUsd: 8, maxTurns: 120, timeoutMs: 2_400_000,
      prompt: `DEEP dependency-enabled pass. Install the full stack (${installCmds.join(" ; ")}) into a venv, then exercise the REAL production code that the bounded run could not reach; measure GENUINE production-code coverage (source modules, not test files). CRITICAL: the pinned deps may be uninstallable as-pinned — for every failure, verify installed vs pinned versions (pip show) and classify it [DRIFT] (fails only because installed≠pinned) or [DEFECT] (real bug independent of version). Populate version_drift. Re-examine the dep-requiring Stage-2 findings:\n${JSON.stringify(s2.findings.filter((f) => /import|depend|coverage|runtime/i.test(f.evidence)).map((f) => f.id))}` });
    if (dr.ok) deep = dr.data;
  }

  // (e2) [skill] adversarial accounting: a SEPARATE agent re-attempts every un-executed region
  // (install/stub/harness). Whatever it gets running flips to executed — the original was false.
  let unexec = an.data.unexecuted;
  if (!DRY && unexec.length) {
    const acc = await runAgent({ name: "s3:account", model: MODEL_FAST, schema: S3_ACCOUNT, bash: true, maxTurns: 100, timeoutMs: 1_800_000,
      prompt: `Adversarial accounting. For EACH region the bounded pass marked un-executed, TRY to run it — install missing deps, stub the boundary (fake env/credentials/clients), or write a throwaway harness. Report which you got running ("flipped", with evidence) and which truly cannot run ("still_unexecuted", each with the exact command + actual failure output + the stub you tried). A region with no shown failed attempt is NOT accounted for. Regions:\n${JSON.stringify(unexec)}` });
    if (acc.ok) { unexec = acc.data.still_unexecuted; an.data.observed.push(...acc.data.flipped.map((x) => ({ entry: x.region, behavior: `flipped to executed: ${x.how} (${x.evidence})` }))); log(`s3 accounting flipped ${acc.data.flipped.length} of ${an.data.unexecuted.length} un-executed regions`); }
  }

  // (f) back-propagate deltas into Stage-2 findings DETERMINISTICALLY — no agent re-run [DocInsight]
  const allDeltas = [...an.data.deltas, ...(deep?.deltas || [])];
  let changed = 0;
  for (const d of allDeltas) {
    const f = s2.findings.find((x) => x.id === d.id);
    if (!f) continue;
    if (d.delta === "refuted" && d.classification !== "DRIFT") { f._refuted = true; changed++; }
    else if (d.delta === "confirmed") { f.status = "verified"; f.runtime_confirmed = true; changed++; }
    else if (d.delta === "refined" && d.note && !f.evidence.includes(d.note)) { f.evidence += ` [runtime: ${d.note}]`; changed++; } // idempotent on resume/re-run
  }
  const survivors = reId(s2.findings.filter((f) => !f._refuted));
  if (changed) { const o2 = { findings: survivors, rounds: s2.rounds, by_severity: bySeverity(survivors), backprop: allDeltas.length }; writeFileSync(join(AUDIT, "02-static-audit.md"), renderS2(o2)); writeWork("stage2.json", o2); log(`s3 back-propagated ${changed} deltas into Stage 2 (${survivors.length} survive)`); }

  const exec = { coverage_pct: an.data.coverage_pct, coverage_verified: verified, observed: an.data.observed, deltas: allDeltas, unexecuted: unexec, deep, run_commands: runLog.map((r) => ({ cmd: r.cmd, code: r.code })) };
  await checkpoint("stage3", "03-execution.md", renderS3(exec), "stage3.json", exec, state);
  return { exec, findings: survivors };
}
function renderS3(e) {
  const parts = [docHead("03 — Execution"),
    `**Measured coverage:** ${e.coverage_pct}% ${e.coverage_verified ? "(independently verified against the run log)" : "⚠️ (NOT confirmed by the verifier)"}.`,
    e.deep ? `**Deep production-code coverage:** ${e.deep.production_coverage_pct}% (deps installed=${e.deep.deps_installed}).` : "", "",
    `## Observed behaviors\n`, tbl(["Entry", "Behavior"], e.observed.map((o) => [o.entry, o.behavior])), "",
    `## Finding deltas (runtime)\n`, tbl(["ID", "Delta", "Class", "Note/Evidence"], e.deltas.map((d) => [d.id, d.delta, d.classification || "—", d.note || d.evidence || ""])), "",
    `## Un-executed (100% accounting — each carries proof-of-attempt)\n`, tbl(["Region", "Reason", "Command tried", "Failure"], e.unexecuted.map((u) => [u.region, u.reason, u.command || "—", u.failure || "—"]))];
  if (e.deep?.version_drift?.length) parts.push("", `## Version drift (installed ≠ pinned)\n`, tbl(["Package", "Pinned", "Installed"], e.deep.version_drift.map((v) => [v.package, v.pinned, v.installed])));
  parts.push(jsonBlock(e));
  return parts.join("\n");
}

// ───────────────────────── Stage 4 — goal + research (parallel) ─────────────────────────
async function stage4(state, s1, s2, s3) {
  const ctx = `Architecture: ${s1.architecture_summary}\nProvisional intent: ${s1.provisional_intent}\nTop findings: ${JSON.stringify(s2.findings.slice(0, 20).map((f) => f.evidence))}\nMeasured coverage: ${s3.exec.coverage_pct}%`;
  // GOAL half — candidate goals, then a JUDGE PANEL votes on grounding [mastery]
  const [goalR, ...research] = await Promise.all([
    runAgent({ name: "s4:goal", model: MODEL_HEAVY, schema: S4_GOAL, prompt: `Infer candidate long-term goal(s) for this repo (keep PLURAL). Each candidate: a falsifiable statement + success signals each tied to a Stage 1-3 artifact. Honor invariants 7 & 8 (meta-repo delegation; stated-negatives are not ground truth). ${ctx}` }),
    ...Array.from({ length: CFG.researchers }, (_, i) =>
      runAgent({ name: `s4:research:${i}`, model: MODEL_FAST, web: true, schema: S4_RESEARCH, prompt: `Research external ideas/technologies/projects that materially advance this repo's apparent goal (facet ${i + 1}/${CFG.researchers}). Cross-check sources; label each corroborated/single-source/unverified/blocked. If web is unavailable, return ideas:[] and say so (do not fabricate). ${ctx}` })),
  ]);
  if (!goalR.ok) await halt("stage4", "goal inference failed", state);
  // [mastery] 3-judge majority vote on each candidate's grounding
  const judges = await pMap([0, 1, 2], async (j) => {
    const r = await runAgent({ name: `s4:judge:${j}`, model: MODEL_HEAVY, schema: S4_JUDGE, prompt: `Independently judge whether each candidate goal is GROUNDED in the cited artifacts (true/false) and assign a status (grounded / needs-human-confirm / speculative / out-of-scope-delegated). Apply invariants 7 & 8. Candidates:\n${JSON.stringify(goalR.data.candidates)}` });
    return r.ok ? r.data.verdicts : [];
  });
  const candidates = goalR.data.candidates.map((c) => {
    const votes = judges.map((jv) => jv.find((v) => v.goal === c.goal)).filter(Boolean);
    const grounded = votes.filter((v) => v.grounded).length;
    const statuses = votes.map((v) => v.status);
    const majorityStatus = mode(statuses) || c.status;
    return { ...c, status: majorityStatus, judge_grounded_votes: `${grounded}/${votes.length}` };
  });
  const ideas = research.flatMap((r) => (r.ok ? r.data.ideas : []));
  const obj = { candidates, research: ideas, research_blocked: research.every((r) => r.ok && r.data.ideas.length === 0) };
  await checkpoint("stage4", "04-goal.md", renderS4(obj), "stage4.json", obj, state);
  return obj;
}
const mode = (arr) => { const c = {}; let best, n = -1; for (const x of arr) { c[x] = (c[x] || 0) + 1; if (c[x] > n) { n = c[x]; best = x; } } return best; };
function renderS4(o) {
  return [docHead("04 — Goal + Research"),
    `## Candidate goals (plural by design; judged by a 3-vote panel)\n`,
    tbl(["Goal", "Status", "Judge grounding"], o.candidates.map((c) => [c.goal, c.status, c.judge_grounded_votes || "—"])), "",
    ...o.candidates.map((c) => `### ${c.status.toUpperCase()} — ${c.goal}\n` + c.signals.map((s) => `- ${s.met ? "✅" : "❌"} ${s.signal} — _${s.evidence}_`).join("\n")), "",
    `## External research ${o.research_blocked ? "(web blocked — recorded as such, not fabricated)" : ""}\n`,
    tbl(["Idea", "Advances", "Corroboration"], o.research.map((r) => [r.idea, r.advances, r.corroboration])),
    jsonBlock(o)].join("\n");
}

// ───────────────────────── Stage 5 — plan (convergence-gated) ─────────────────────────
async function stage5(state, s1, s2, s3, s4) {
  let plan = null;
  for (let attempt = 1; attempt <= 2; attempt++) {
    const r = await runAgent({ name: `s5:plan:${attempt}`, model: MODEL_HEAVY, schema: S5_PLAN,
      prompt: `Produce an execution-ready, dependency-ordered change plan. Every item: a concrete change tied to a finding id or goal-gap (links_to), a file/module location, a verification signal (the test/observation that proves it worked), and depends_on. Cover the surviving findings and every ❌ goal signal. Findings:\n${JSON.stringify(s2.findings.map((f) => ({ id: f.id, severity: f.severity, location: f.location })))}\nGoals:\n${JSON.stringify(s4.candidates.map((c) => ({ goal: c.goal, status: c.status })))}` });
    if (!r.ok) await halt("stage5", "plan generation failed", state);
    // independent convergence verifier: can a fresh agent map every item to a diff target with no ambiguity?
    const m = await runAgent({ name: `s5:map:${attempt}`, model: MODEL_FAST, schema: S5_MAP,
      prompt: `For this plan, can each item be mapped to a concrete diff target without asking a clarifying question? Return all_mappable + the ambiguous item ids. Plan:\n${JSON.stringify(r.data.items)}` });
    plan = r.data;
    if (m.ok && m.data.all_mappable) { plan._converged = true; break; }
    plan._ambiguous = m.ok ? m.data.ambiguous : ["map-agent-failed"];
    log(`s5 not converged (attempt ${attempt}): ambiguous ${JSON.stringify(plan._ambiguous)}`);
  }
  await checkpoint("stage5", "05-plan.md", renderS5(plan), "stage5.json", plan, state);
  return plan;
}
function renderS5(p) {
  return [docHead("05 — Execution Plan"),
    `**${p.items.length} change items** — convergence: ${p._converged ? "CONVERGED (all diff-mappable)" : "NOT-CONVERGED: " + JSON.stringify(p._ambiguous || [])}.`, "",
    tbl(["ID", "Change", "Links", "Location", "Verification", "Depends"], p.items.map((i) => [i.id, i.change, i.links_to, i.location, i.verification, i.depends_on])),
    jsonBlock(p)].join("\n");
}

// ───────────────────────── modes: selftest [RNA] + preflight [mastery/RNA] ─────────────────────────
function selftest() {
  let pass = 0, fail = 0;
  const ok = (cond, msg) => { if (cond) { pass++; } else { fail++; console.error("  ✗ " + msg); } };
  // validator
  ok(validate(FINDING, { id: "F1", location: "a.py:1", class: "bug", severity: "high", evidence: "x".repeat(25) }).length === 0, "valid finding passes");
  ok(validate(FINDING, { id: "F1", location: "a.py:1", class: "bug", severity: "huge", evidence: "x".repeat(25) }).length > 0, "bad severity enum fails");
  ok(validate(FINDING, { id: "F1", location: "a.py:1", class: "bug", severity: "high", evidence: "short" }).length > 0, "minLength enforced");
  ok(validate(S4_GOAL, { candidates: [] }).length > 0, "minItems enforced");
  // enum coercion
  const d1 = coerceEnums(FINDING, { id: "F1", location: "a.py:1", class: "bug", severity: "BLOCKER", evidence: "x".repeat(25) });
  ok(d1.severity === "critical", `coerce BLOCKER→critical (got ${d1.severity})`);
  const d2 = coerceEnums(VERDICT, { id: "F1", verdict: "confirmed" });
  ok(d2.verdict === "upheld", `coerce confirmed→upheld (got ${d2.verdict})`);
  const d3 = coerceEnums(S1_SLICE, { files: [{ path: "a.py", role: "CODE" }] });
  ok(d3.files[0].role === "source", `coerce CODE→source (got ${d3.files[0].role})`);
  // tolerant json
  ok(tolerantJson('```json\n{"a":1}\n```')?.a === 1, "fenced json parsed");
  ok(tolerantJson('prefix {"a":2} suffix')?.a === 2, "brace-sliced json parsed");
  ok(tolerantJson("﻿{\"a\":3}")?.a === 3, "BOM-stripped json parsed");
  // renderers: no unescaped pipe leaks
  const md = renderS2({ findings: [{ id: "F1", severity: "high", status: "verified", location: "a.py:1", class: "x | y", evidence: "has | pipe\nand newline" }], rounds: 1, by_severity: { high: 1 } });
  const tableLines = md.split("\n").filter((l) => l.startsWith("| F1"));
  ok(tableLines.length === 1 && tableLines[0].split(" | ").length === 6, "evidence pipe/newline escaped (no column overflow)");
  console.error(`\nselftest: ${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
}

// [skill] ONE cheap call proving auth + tool-use + file-handoff before the long run
async function doPreflight() {
  return runAgent({ name: "preflight", model: MODEL_CHEAP, maxTurns: 4, bash: false, tries: 1, schema: { type: "object", required: ["ok"], properties: { ok: { type: "boolean" }, model: { type: "string" } } }, prompt: "Auth/model check. Per the OUTPUT CONTRACT, use the Write tool to emit {\"ok\":true,\"model\":\"<the model you are>\"}." });
}
async function preflight() { // --preflight standalone mode
  BRANCH = await gitBranch(); mkdirSync(WORK, { recursive: true });
  const r = await doPreflight();
  if (!r.ok) { console.error("preflight FAILED — auth / tool-use / file-handoff problem"); process.exit(2); }
  console.error(`preflight OK — agent path works (model reported: ${r.data.model || "?"})`);
  process.exit(0);
}

// ───────────────────────── main ─────────────────────────
async function main() {
  if (FLAG("--selftest")) return selftest();           // zero-API
  if (FLAG("--preflight")) return preflight();          // one cheap live call
  if (FRESH) { try { rmSync(AUDIT, { recursive: true, force: true }); } catch {} }
  mkdirSync(WORK, { recursive: true });
  BRANCH = await gitBranch();
  const state = loadState();
  const want = (n) => (ONLY_STAGE ? n === ONLY_STAGE : FROM_STAGE ? n >= FROM_STAGE : !state.completed[`stage${n}`]);
  const need = (n, fallback) => readWork(`stage${n}.json`) || fallback; // resume: load prior artifact from disk

  // [skill] automatic preflight gate: prove the agent path works before committing to the long run
  if (!DRY && !SKIP_PREFLIGHT) {
    const pf = await doPreflight();
    if (!pf.ok) await halt("preflight", "auth / tool-use / file-handoff preflight failed — aborting before the long run (use --skip-preflight to override)", state);
    log("preflight OK — agent path verified");
  }
  log(`forensic-audit (consolidated) on ${BRANCH} — cost tracked, never gated (subscription)`);
  let s1, s2, s3, s4;
  s1 = want(1) ? await stage1(state) : need(1);
  s2 = want(2) ? await stage2(state, s1) : need(2);
  s3 = want(3) ? await stage3(state, s1, s2) : { exec: need(3), findings: (need(2) || s2).findings };
  if (want(3)) s2 = { ...s2, findings: s3.findings }; // back-prop may have changed survivors
  s4 = want(4) ? await stage4(state, s1, s2, s3) : need(4);
  if (want(5)) await stage5(state, s1, s2, s3, s4);

  writeWork("SUMMARY.json", { branch: BRANCH, apiEquivUsd: Number(TOTAL_USD.toFixed(2)), note: "API-equivalent cost; real subscription draw is far lower — informational only", costByStage: COST_BY_STAGE, completed: state.completed });
  log(`DONE — API-equiv ~$${TOTAL_USD.toFixed(2)} (informational; ${JSON.stringify(COST_BY_STAGE)})`);
}

main().catch((e) => { if (e instanceof Halt) { console.error(`\nHALTED at ${e.stage}: ${e.message}`); process.exit(3); } console.error("FATAL", e?.stack || e); process.exit(2); });

````
