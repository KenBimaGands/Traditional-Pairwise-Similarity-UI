---
name: feature-extraction
description: Extract and reproduce the thesis approved UI visual features and frozen gradient correction; use for screenshot extraction, not pairwise scoring.
---

# Feature Extraction

Use this module inside the ui-visual-consistency repository. If installed separately, locate the repository containing `pipeline.py` and `provenance.json`; the installed skill folder does not contain the runtime or data. Read the repository's `docs/data-contracts.md` for this stage and `docs/methodology.md` when explaining formulas.

## Inputs and implementation

Screenshots, screens.csv, original baseline results and the frozen 12-screen correction fixtures.

The implementation is `runtime/experiments/final_baseline_correction/run_pilot.py` relative to the repository root. Shared source lives under `runtime/` to preserve imports and avoid six divergent copies; this module owns its responsibility, not a private rewrite of the math.

## Execute

For existing-result validation/reuse:

```sh
python pipeline.py --stage feature-extraction --output runs/feature-extraction-review
```

For an explicitly requested fresh execution, append `--recompute` and use another fresh output name. Use the existing project environment or the repository's pinned direct dependencies. The orchestrator validates prerequisite stages and uses an isolated workspace; it never changes bundled inputs. Missing prerequisites stop execution rather than being silently invented. Do not rerun expensive stages when saved results satisfy the user's task.

## Outputs

82 scalar records, weighted RGB/CIELAB palettes, normalized boxes, 32-cell layout, masks, comparisons and correction/provenance files.

Inspect `run_manifest.json` for exact result locations and reuse/recomputation status.

## Validation

Check all 82 IDs, successful extraction, unchanged palette/Canny definitions, baseline reproduction and the frozen activation APP02-FLOW01-S01. Read the source if activation changes; do not force the expected count. The function defaults to correction disabled; the full runner enables it.

## Boundaries

The approved runner is specific to this pilot and its saved reference/sample fixtures. It is not a generic new-dataset extractor. No cropping or role inference is introduced.

Preserve prior outputs and original metadata. No graph scoring is included. Numerical validity, reproducibility and human visual validation are different claims. Read `docs/pipeline-architecture.md` for routing and `docs/audit.md` for legacy dependencies/packaging changes. Do not imply that creating figures constitutes expert review.
