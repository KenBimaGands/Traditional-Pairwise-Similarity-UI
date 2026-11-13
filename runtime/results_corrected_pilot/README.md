# Final corrected pilot features — 82 screenshots

This directory contains the full-pilot application of the selected optional correction from `experiments/final_baseline_correction/run_01`. All 82 metadata screenshots were processed successfully, with no image errors and no parameter changes.

Use these numerical files for the selected corrected pilot feature set. The original baseline remains in `../results/`, and the original twelve-screen comparison remains in `../experiments/final_baseline_correction/run_01/`.

## What changed

The gradient correction activated only for **APP02-FLOW01-S01**. The other 81 screens have exactly the same masks and numerical features as the original baseline. Color palettes and Canny edge density remain unchanged for all 82 screens.

For the activated screen:

| Descriptor | Original | Corrected |
|---|---:|---:|
| Foreground coverage | 0.961439 | 0.202650 |
| Retained component count | 6 | 18 |
| Mean bounding-box union grid occupancy | 0.964007 | 0.246538 |

The before/after image was visually inspected: the large smooth gradient is suppressed, with the filled buttons, main text and icons retained. Higher component count reflects separation of foreground regions after background suppression, not semantic UI-element detection.

## Files

- `visual_features.csv`: original screen IDs, status/errors, original/processed dimensions, foreground coverage, Canny density, component count and correction activation.
- `color_palettes.json`: original weighted RGB/CIELAB palettes and baseline background estimates. `background_rgb` describes the unchanged baseline estimate, not a newly fitted background.
- `bounding_boxes.json`: corrected normalized boxes, with exclusive bottom-right coordinates.
- `layout_vectors.csv`: corrected 32-value, row-major 4×8 rectangle-union occupancy vectors.
- `differences.csv`: per-screen original/corrected coverage, component counts, mean grid occupancy, removed pixels and all 32 signed grid changes.
- `triggers.json`: diagnostic evidence and activation/abstention reasons for every screenshot.
- `configuration.json`: exact unchanged baseline and correction settings, with correction explicitly enabled for this run.
- `visualizations/`: 82 seven-panel before/after figures, indexed by zero-based metadata row position.
- `masks/`: 82 corrected masks using the same indices, with white foreground and black background.
- `run_summary.json`: machine-readable processing and verification summary.
- `protected_sha256.json`, `source_sha256.json`: protected input/history fingerprints and the source/dependency snapshot fingerprints used for this run.

For example, the activated screenshot is row index 25: [before/after figure](visualizations/0025.png), [corrected mask](masks/0025.png). Resolve other indices using row order in `visual_features.csv` (excluding the CSV header).

## Checks performed

All 82 original extractions reproduced the saved baseline palette, estimated background, coverage, edge density, boxes and layout before correction. Each correction was repeated and produced identical masks and trigger diagnostics. All twelve earlier corrected sample results were reproduced exactly. All saved numerical exports were checked for aligned IDs, normalized palettes with at most five colors, finite Lab values, density bounds, valid boxes and exactly 32 bounded grid entries. All 82 comparison images and 82 masks were verified present.

The five existing baseline numerical tests completed successfully. Current before/after SHA-256 checks confirmed that original PILOT files, baseline results/source/tests, previous experiments and the twelve-screen final-correction results were unchanged by this application. Historical fingerprints from before the earlier comment-only source edit were preserved, not rewritten.

## Reproduce

From the project root, use a new output directory:

```sh
LOKY_MAX_CPU_COUNT=1 .venv/bin/python experiments/final_baseline_correction/run_pilot.py --output results_corrected_pilot_reproduction
```

The runner refuses an existing destination. It reuses the existing environment, baseline extraction functions and frozen correction; it does not modify the production default. No new dependencies were installed. The analyzed ROI is the complete processed original screenshot for both baseline and correction, with no new cropping.

For annotated source, mathematical formulas and parameter definitions, see the [final correction README](../experiments/final_baseline_correction/README.md) and [root README](../README.md).

## Remaining limitations

The correction is selective, not a general foreground-segmentation solution. Horizontal-only gradients can be missed; genuinely smooth foreground connected across both borders could be removed if the trigger activates. Source footers, device chrome, frame pixels, missed pale boundaries, merged components and empty areas inside bounding boxes remain inherited limitations. Mixed-background APP05-FLOW01-S04 remains identical to the original baseline.

Every record was numerically checked, but only the activated comparison was newly visually inspected in this full run; the earlier twelve-screen visual review remains available. There is no full-dataset pixel ground truth, segmentation accuracy percentage, similarity metric, graph score or consistency classification. No additional segmentation optimization was performed.
