---
name: tau-sensitivity
description: Review the thesis existing tau=5,10,20 composite results and rankings with all non-color parameters fixed; use for tau diagnostics, not upstream feature generation.
---

# Tau Sensitivity

Use this module inside the ui-visual-consistency repository. If installed separately, locate the repository containing `pipeline.py` and `provenance.json`; the installed skill folder does not contain the runtime or data. Read the repository's `docs/data-contracts.md` for this stage and `docs/methodology.md` when explaining formulas.

## Inputs and implementation

Saved sensitivity_analysis.csv, composite_scores.csv and original pairwise pair IDs; exclude M0 rows.

The implementation is `runtime/review_tau_sensitivity.py` relative to the repository root. Shared source lives under `runtime/` to preserve imports and avoid six divergent copies; this module owns its responsibility, not a private rewrite of the math.

## Execute

For existing-result validation/reuse:

```sh
python pipeline.py --stage tau-sensitivity --output runs/tau-sensitivity-review
```

For an explicitly requested fresh execution, append `--recompute` and use another fresh output name. Use the existing project environment or the repository's pinned direct dependencies. The orchestrator validates prerequisite stages and uses an isolated workspace; it never changes bundled inputs. Missing prerequisites stop execution rather than being silently invented. Do not rerun expensive stages when saved results satisfy the user's task.

## Outputs

Tau review Markdown, Color/Composite summary CSVs, rank changes, affected pair IDs, distributions and validation checks.

Inspect `run_manifest.json` for exact result locations and reuse/recomputation status.

## Validation

Reuse existing scores. Check 709 pairs per M1 tau and identical non-color terms. Explain mean/median/extrema/SD, Spearman, largest score/rank effects and dependent within/cross-flow descriptions.

## Boundaries

This stage cannot regenerate upstream scores. The orchestrator can separately invoke composite-scoring if missing scores are needed. Retain tau=10 provisionally unless evidence shows a serious issue; final calibration requires expert annotations.

Preserve prior outputs and original metadata. No graph scoring is included. Numerical validity, reproducibility and human visual validation are different claims. Read `docs/pipeline-architecture.md` for routing and `docs/audit.md` for legacy dependencies/packaging changes. Do not imply that creating figures constitutes expert review.
