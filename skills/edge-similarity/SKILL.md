---
name: edge-similarity
description: Evaluate the thesis saved edge-density M0/M1/M2 alternatives with deterministic sampling; use for edge metric diagnostics, not feature tuning.
---

# Edge Similarity

Use this module inside the ui-visual-consistency repository. If installed separately, locate the repository containing `pipeline.py` and `provenance.json`; the installed skill folder does not contain the runtime or data. Read the repository's `docs/data-contracts.md` for this stage and `docs/methodology.md` when explaining formulas.

## Inputs and implementation

Saved baseline and approved edge densities, pairwise tables, metadata, screenshots and original saved Canny diagnostic panels.

The implementation is `runtime/experiments/edge_similarity_evaluation/evaluate.py` relative to the repository root. Shared source lives under `runtime/` to preserve imports and avoid six divergent copies; this module owns its responsibility, not a private rewrite of the math.

## Execute

For existing-result validation/reuse:

```sh
python pipeline.py --stage edge-similarity --output runs/edge-similarity-review
```

For an explicitly requested fresh execution, append `--recompute` and use another fresh output name. Use the existing project environment or the repository's pinned direct dependencies. The orchestrator validates prerequisite stages and uses an isolated workspace; it never changes bundled inputs. Missing prerequisites stop execution rather than being silently invented. Do not rerun expensive stages when saved results satisfy the user's task.

## Outputs

709 three-method rows, fixed-seed 24-pair stratified sample, epsilon sensitivity, ranking/tie tables and saved-edge inspection sheets.

Inspect `run_manifest.json` for exact result locations and reuse/recomputation status.

## Validation

Use seed 42, epsilon 1e-5 and the saved grid 1e-8,1e-6,1e-5,1e-4,1e-3. Check sample uniqueness, representation, identity/zeros/symmetry/bounds, saved M0 agreement and convergence. Never regenerate Canny maps for this experiment.

## Boundaries

M2 simplifies to a smoothed M1. Prior perceptual conclusion remains inconclusive; the subsequent operational M1 choice is provisional. Do not choose a metric by spread alone.

Preserve prior outputs and original metadata. No graph scoring is included. Numerical validity, reproducibility and human visual validation are different claims. Read `docs/pipeline-architecture.md` for routing and `docs/audit.md` for legacy dependencies/packaging changes. Do not imply that creating figures constitutes expert review.
