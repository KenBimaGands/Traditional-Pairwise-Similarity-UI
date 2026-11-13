---
name: pairwise-similarity
description: Calculate the thesis traditional visual-only pairwise distances from saved features; use for 709-pair EMD/density/layout computation, not composite scoring.
---

# Pairwise Similarity

Use this module inside the ui-visual-consistency repository. If installed separately, locate the repository containing `pipeline.py` and `provenance.json`; the installed skill folder does not contain the runtime or data. Read the repository's `docs/data-contracts.md` for this stage and `docs/methodology.md` when explaining formulas.

## Inputs and implementation

Approved feature CSV/JSON files and screenshot/flow metadata.

The implementation is `runtime/pairwise_baseline.py` relative to the repository root. Shared source lives under `runtime/` to preserve imports and avoid six divergent copies; this module owns its responsibility, not a private rewrite of the math.

## Execute

For existing-result validation/reuse:

```sh
python pipeline.py --stage pairwise-similarity --output runs/pairwise-similarity-review
```

For an explicitly requested fresh execution, append `--recompute` and use another fresh output name. Use the existing project environment or the repository's pinned direct dependencies. The orchestrator validates prerequisite stages and uses an isolated workspace; it never changes bundled inputs. Missing prerequisites stop execution rather than being silently invented. Do not rerun expensive stages when saved results satisfy the user's task.

## Outputs

709 raw distance rows, bounded foreground/M0-edge/layout similarity rows, pair counts, descriptive summaries and provenance.

Inspect `run_manifest.json` for exact result locations and reuse/recomputation status.

## Validation

Validate exact 709 unique within-app unordered pairs, 411 within-flow/298 cross-flow, finite EMD and bounded other descriptors, palette masses and exact ID alignment. Do not invent a color similarity at this stage.

## Boundaries

M0 is retained in the original pairwise exports; M1 is adopted later by composite scoring. No navigation, roles or graph methods affect scores.

Preserve prior outputs and original metadata. No graph scoring is included. Numerical validity, reproducibility and human visual validation are different claims. Read `docs/pipeline-architecture.md` for routing and `docs/audit.md` for legacy dependencies/packaging changes. Do not imply that creating figures constitutes expert review.
