# AIV Forensic Audit — Pause / Resume Guide

This pipeline is a detached `node` process driving `claude -p` subagents through five
stages. **All resume state lives on local disk under `audit/`** (the orchestrator reads
it from the filesystem, not from git), so resume does **not** depend on `git push`
(which is 403-blocked in this environment).

## State that matters
| Path | Purpose |
|------|---------|
| `audit/forensic_pipeline.mjs` | the orchestrator — re-runnable, idempotent per stage |
| `audit/.work/state.json` | which stages are marked complete (drives auto-resume) |
| `audit/.work/stageN.json` | per-stage structured results (resume handoffs) |
| `audit/0N-*.md` | the deliverables produced so far |

## Case A — Pause with disk intact (session suspend/resume; the common case)
The background process is detached and may still be running. Check first:
```bash
pgrep -f forensic_pipeline.mjs        # still running?
tail -n 20 /tmp/forensic_run.log      # latest progress
```
- **Still running** → nothing to do; it continues on its own.
- **Stopped** → resume (skips completed stages automatically):
```bash
cd /home/user/aiv-protocol
node audit/forensic_pipeline.mjs            # auto-resume from first incomplete stage
#   node audit/forensic_pipeline.mjs --from 2     # force resume from Stage 2
#   node audit/forensic_pipeline.mjs --stage 3    # run exactly one stage
```
Stage 2 reloads `audit/.work/stage2.json` and keeps refining from the last persisted
findings, so a mid-Stage-2 restart does not start from zero.

## Case B — Full container teardown (disk lost)
Local commits are **not** on the remote (push blocked), so restore from the resume kit:
```bash
# 1. fresh container re-clones the repo source from the remote
# 2. drop the kit back in:
tar xzf aiv-audit-resume-kit.tar.gz -C /home/user/aiv-protocol
# 3. resume:
cd /home/user/aiv-protocol && node audit/forensic_pipeline.mjs
```

## Other modes
```bash
node audit/forensic_pipeline.mjs --fresh      # discard audit/ and start over
node audit/forensic_pipeline.mjs --selftest   # zero-API: validate schemas/coercion/renderers
node audit/forensic_pipeline.mjs --preflight  # one cheap call: prove auth + tool-use + file-handoff
```

## Notes
- The cost figure in logs is **API-equivalent** (subscription draw is far lower) — informational, never a gate.
- The git pre-commit signing/push warnings are expected here and harmless: subagents commit
  unsigned (no interactive signing) and push is blocked, so the audit history stays local-only.
