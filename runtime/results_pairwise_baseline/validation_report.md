# Traditional pairwise baseline validation

Completed **709 unique within-application pairs for all 82 approved corrected-pilot screens**, including 411 within-flow and 298 cross-flow pairs. Counts per application are in [pair_counts.csv](pair_counts.csv). Application/flow metadata only selects and labels pairs; scores do not use transitions, roles or navigation.

## Data and implementation

Used `results_corrected_pilot`, explicitly selected after the final baseline-preserving correction and its full-pilot application. This changes one screen's foreground/layout relative to the original baseline; it is not an A/B/A1/A2 experimental feature selection. All screen, application, flow and feature IDs aligned, all extraction records were successful, and palettes/density/layout values were complete and numerically valid. No screenshot decoding, segmentation, box regeneration or feature recomputation occurred.

Color uses installed scikit-image CIEDE2000 centroid costs and SciPy HiGHS dual-simplex balanced optimal transport. Both palettes have unit mass; the output is the raw minimum transport objective with no extra normalization. Variable palette lengths 1–5 are supported. Foreground and edge distances are separate absolute differences, and layout is corresponding-cell mean absolute difference. Bounded similarities are independently `1−distance`. Color similarity is not computed; an exponential mapping with a future externally justified scale is proposed only in the methodology document. There are no composite weights or consistency labels.

## Validation evidence

Five test cases completed successfully, covering the Sharma CIEDE2000 reference value, analytic black/white transport, 1–5 color palettes, duplicate-color splitting, permutation invariance, zero-distance identity, symmetry, scalar/layout bounds, exact pair counts and labels, missing/nonfinite/invalid input rejection, and complete repeated full exports. Two full runs into temporary directories produced byte-identical CSVs and configuration files.

The exported 15-pair smoke test covers all applications, both pair types and foreground extremes. It completed before the permanent 709-pair export. An additional export audit independently checked every pair's reverse-distance symmetry, all IDs/types, finite numbers, bounded similarities, exact smoke/full agreement, and unchanged input fingerprints. All computed color transport solutions met their full marginal feasibility check. Output provenance and conventions are in [configuration.json](configuration.json), with checks in [validation_checks.json](validation_checks.json).

Five raw-distance matrix figures were generated; the APP04 figure was visually inspected for panel labels, axes and colorbar units. The other four were not manually inspected screen-by-screen. Color display limits are not a score normalization; raw color units are preserved.

## Descriptive observations and illustrative examples

| Descriptor | Lowest observed distance | Highest observed distance | Highest-distance pair |
|---|---:|---:|---|
| Color CIEDE2000-EMD | 0 | 55.602798 | APP04-FLOW01-S00 / APP04-FLOW01-S04 |
| Foreground fraction | 0 | .491528 | APP05-FLOW01-S04 / APP05-FLOW02-S01 |
| Canny edge fraction | 0 | .092929 | APP02-FLOW01-S013 / APP02-FLOW01-S05 |
| Layout occupancy | 0 | .624279 | APP03-FLOW01-S01 / APP03-FLOW02-S08 |

APP02-FLOW01-S015 / APP02-FLOW02-S00 has zero distance in all four descriptors across two flows. This establishes identical measured descriptors, not a semantic consistency label or a general conclusion about the two flows. No claim that the original image files are byte-identical is needed or made.

The different highest-distance pairs show why a single feature cannot summarize every aspect of appearance. These extrema and per-application summaries are descriptive; no statistical group comparison, causal claim or consistency threshold is inferred. See [illustrative_pairs.csv](illustrative_pairs.csv) for the exact values and identities.

## Limits and future reuse

Pairwise observations share screens and are not independent samples. Palette mass can hide small accent-color changes; density fractions ignore content identity; grid envelopes include empty space and do not match semantic UI elements. Source footers, device chrome, missed pale outlines, merged components, and the correction's selective trigger are inherited feature limitations. A zero descriptor distance does not establish that screens serve the same purpose; a large visual distance does not establish a design error.

Reusable artifacts for a future graph method are the fixed screen descriptors, the same 709 pair identities, four raw distances, and three separately defined bounded similarities. Any color similarity scale, composite feature weighting, contextual scoring or classification is future methodology requiring separate justification. No graph-related computation was implemented.

Created only the three new pairwise Python files, `PAIRWISE_METHODS.md`, and the separate smoke/full pairwise output directories. Existing extraction source, original dataset/metadata and extracted features were not changed. Full mathematical definitions and primary library/reference links are in [PAIRWISE_METHODS.md](../PAIRWISE_METHODS.md).
