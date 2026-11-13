---
name: composite-scoring
description: Compute the thesis traditional visual-only composite baseline with M1 edge and tau=10 plus fixed sensitivities; use after pairwise distances are available.
---

# Composite Scoring

Use this module inside the ui-visual-consistency repository. If installed separately, locate the repository containing `pipeline.py` and `provenance.json`; the installed skill folder does not contain the runtime or data. Read the repository's `docs/data-contracts.md` for this stage and `docs/methodology.md` when explaining formulas.

## Inputs and implementation

Approved foreground/edge fractions, layout records, metadata, saved raw EMD and prior pairwise provenance.

The implementation is `runtime/composite_baseline.py` relative to the repository root. Shared source lives under `runtime/` to preserve imports and avoid six divergent copies; this module owns its responsibility, not a private rewrite of the math.

## Execute

For existing-result validation/reuse:

```sh
python pipeline.py --stage composite-scoring --output runs/composite-scoring-review
```

For an explicitly requested fresh execution, append `--recompute` and use another fresh output name. Use the existing project environment or the repository's pinned direct dependencies. The orchestrator validates prerequisite stages and uses an isolated workspace; it never changes bundled inputs. Missing prerequisites stop execution rather than being silently invented. Do not rerun expensive stages when saved results satisfy the user's task.

## Outputs

709 composite records; 2836 four-configuration sensitivity rows; grouped statistics, additive contributions, ranks, plots and 39 purposive example slots.

Inspect `run_manifest.json` for exact result locations and reuse/recomputation status.

## Validation

Fix tau=10, M1 edge, equal Density subweights and equal Color/Density/Layout group weights. Sensitivities are M1 tau=5/20 and M0 tau=10. Check bounded finite results, identity/symmetry, contribution arithmetic and unchanged raw EMD/pair IDs.

## Boundaries

Weights and tau are baseline assumptions, not calibrated optima. High aggregate similarity is not consistency. Do not optimize weights, classify pairs or simulate expert labels.

Preserve prior outputs and original metadata. No graph scoring is included. Numerical validity, reproducibility and human visual validation are different claims. Read `docs/pipeline-architecture.md` for routing and `docs/audit.md` for legacy dependencies/packaging changes. Do not imply that creating figures constitutes expert review.
