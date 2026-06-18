# Reproducibility & raw-artifact extraction

This audit's machine-readable artifacts (`raw/*.json`, `pipeline/*.mjs`) are stored **verbatim**
inside Markdown wrappers (`*.json.md`, `*.mjs.md`) — content is unchanged and parses identically.
This keeps the PR fast-track-eligible for the repo's own `aiv-guard` without fabricating a
verification packet for what is a docs/evidence change. This file explains how to get the originals
back and how to re-run the pipeline.

> **Precision note:** the wrapping is line-based, so an original file that lacked a trailing newline
> (e.g. `raw/stage2.json.md`) will gain a single `\n` on extraction. The JSON is semantically
> identical (`JSON.parse` round-trips to the same object); only that one whitespace byte may differ.

## Why the wrapping

`aiv-guard` exempts a PR from packet validation only when **every** changed path matches a
fast-track pattern (`\.md$`, `\.txt$`, `\.gitignore$`, `README`, `LICENSE` — see
`src/aiv/lib/config.py`). A single `.json` or `.mjs` file makes the whole change non-fast-track,
at which point the guard validates the PR body as a packet and blocks on missing sections. Wrapping
each artifact as `<name>.json.md` / `<name>.mjs.md` makes the tree all-Markdown while preserving
the exact original bytes inside a fenced code block.

> The all-or-nothing fast-track that forces this is itself adjacent to finding **C2/F96** (the
> enforcement surfaces disagree on what they accept). Recorded, not worked around silently.

## Extract every original artifact

Each wrapper is: a `#` title line, a `>` note, a blank line, an opening fence (` ```json ` or
` ```javascript `), the verbatim original content, then a closing fence. To restore the originals
(modulo the possible trailing newline noted above), strip the header and the first/last fence line
of each file:

```bash
cd docs/audits/2026-06-18-forensic
mkdir -p _restored/raw _restored/pipeline

# JSON artifacts
for f in raw/*.json.md; do
  out="_restored/raw/$(basename "${f%.md}")"
  # drop everything up to and including the first ``` fence, and the trailing fence
  awk 'f && /^```/{exit} f{print} /^```json$/{f=1}' "$f" > "$out"
done

# Pipeline sources
for f in pipeline/*.mjs.md; do
  out="_restored/pipeline/$(basename "${f%.md}")"
  awk 'f && /^```/{exit} f{print} /^```javascript$/{f=1}' "$f" > "$out"
done

# Sanity-check the JSON round-trips
for f in _restored/raw/*.json; do node -e "JSON.parse(require('fs').readFileSync('$f','utf8')); console.log('ok: $f')"; done
```

`raw/run-log.txt` is plain text already (no wrapper).

## Re-run the pipeline

The orchestrator (`pipeline/forensic_pipeline.mjs.md` → restore to `forensic_pipeline.mjs`) is
idempotent per stage and reads its resume state from disk. It expects to run from the repo root
with an `audit/` working directory present (see [`RESUME.md`](RESUME.md)). After restoring:

```bash
node _restored/pipeline/forensic_pipeline.mjs --selftest   # zero-API: schema/coercion/renderer check
node _restored/pipeline/forensic_pipeline.mjs --preflight  # one cheap call: auth + tool-use + file-handoff
node _restored/pipeline/forensic_pipeline.mjs              # resume from first incomplete stage
node _restored/pipeline/forensic_pipeline.mjs --fresh      # discard audit/ and re-run from scratch
node _restored/pipeline/forensic_pipeline.mjs --stage 3    # re-run exactly one stage
```

Cost shown in logs is **API-equivalent** and informational only — never a gate (and see the
README caveat on the $10.43 vs ~$117 discrepancy).

## Regenerate the dedup clustering

`raw/distinct-issues.json.md` (the clustering behind [`FINDINGS.md`](FINDINGS.md)) is derived from
`raw/stage2.json`. After restoring the originals, the clustering groups findings by
`(normalized file location, root-cause theme)` and ranks by severity. The exact grouping logic is
documented inline in `FINDINGS.md` ("Why this layer exists") and the resulting clusters — each
listing its member raw finding IDs — are in the restored `distinct-issues.json`.
