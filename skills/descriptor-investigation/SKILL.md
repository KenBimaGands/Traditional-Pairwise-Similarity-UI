---
name: descriptor-investigation
description: Investigate the thesis saved visual descriptor behavior using statistics and diagnostic figures; use for feature diagnostics, not consistency classification.
---

# Descriptor Investigation

Use this module inside the ui-visual-consistency repository. If installed separately, locate the repository containing `pipeline.py` and `provenance.json`; the installed skill folder does not contain the runtime or data. Read the repository's `docs/data-contracts.md` for this stage and `docs/methodology.md` when explaining formulas.

## Inputs and implementation

Saved pairwise exports, approved features, metadata, original screenshots and saved correction overlays.

The implementation is `runtime/investigate_pairwise.py` relative to the repository root. Shared source lives under `runtime/` to preserve imports and avoid six divergent copies; this module owns its responsibility, not a private rewrite of the math.

## Execute

For existing-result validation/reuse:

```sh
python pipeline.py --stage descriptor-investigation --output runs/descriptor-investigation-review
```

For an explicitly requested fresh execution, append `--recompute` and use another fresh output name. Use the existing project environment or the repository's pinned direct dependencies. The orchestrator validates prerequisite stages and uses an isolated workspace; it never changes bundled inputs. Missing prerequisites stop execution rather than being silently invented. Do not rerun expensive stages when saved results satisfy the user's task.

## Outputs

Grouped descriptive CSVs, 120 purposive example slots, 40 inspection sheets, overviews, distributions and numerical audit.

Inspect `run_manifest.json` for exact result locations and reuse/recomputation status.

## Validation

The existing script reproduces pairwise scoring twice from saved descriptors; it does not recompute image features. Verify IDs and reproducibility first. Distinguish numerical alignment from visual quality and state exactly which figures were inspected.

## Boundaries

Diagnostic examples are purposive, not random accuracy evidence. Historical narrative reports are copied with explicit provenance, not presented as new expert evaluation.

Preserve prior outputs and original metadata. No graph scoring is included. Numerical validity, reproducibility and human visual validation are different claims. Read `docs/pipeline-architecture.md` for routing and `docs/audit.md` for legacy dependencies/packaging changes. Do not imply that creating figures constitutes expert review.
