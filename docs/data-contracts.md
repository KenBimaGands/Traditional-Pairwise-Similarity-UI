# Stage data contracts

All paths are relative to an execution workspace unless stated otherwise. CSV files use headers; metadata has UTF-8 BOM. IDs are strings and join keys; numeric values are parsed as finite floats or integer dimensions/counts. Booleans serialize as JSON booleans or CSV `True`/`False`. Do not use lexicographic ID order as navigation order. No transition or role field affects these visual-only computations.

## Shared metadata and fixed universe

`PILOT/screenshots/screens.csv`: `screen_id,app_id,flow_id,screen_order,screen_name,screen_role,image_path`. Screen IDs are unique/nonempty; image paths resolve beneath the metadata directory. `flows.csv`: `app_id,app_name,flow_id,flow_name,source`. Flow ownership must agree with screen app IDs. All 82 screens are included; app screen counts 24,20,18,10,10 imply 709 unordered within-app pairs. Of these, 411 share a flow and 298 do not. Unknown descriptive metadata is preserved, not inferred.

Shared pair columns are `screen_a,screen_b,app_id,flow_a,flow_b,pair_type`, where pair_type is `within_flow` or `cross_flow`; later stages also use `pair_id=screen_a__screen_b`. The pair ID is bookkeeping, not semantic equivalence. Every complete pair table must match the same unique 709 keys.

## 1. Feature extraction — approved baseline correction

**Entry:** `experiments/final_baseline_correction/run_pilot.py`. Inputs: 82 original screenshots and metadata; root baseline numerical files under `results/`; frozen `experiments/final_baseline_correction/run_01/candidate/` records; original extraction code plus geometry/validation/rendering helpers from `experiments/preprocessing_v2/`. These helper imports do not select earlier segmentation candidates.

**Parameters:** maximum side 512; seed 42; K≤5; original RGB background distance 25; component minimum area 12; Gaussian 5×5, sigma=1; Canny 50/150; full processed image, no cropping. Correction uses frozen side/smoothness parameters from `correct.py`: .035 side-band fraction, 6 step, .25 run-height fraction, 40 RGB span, .5 baseline coverage gate, .35 minimum smooth-region area. It defaults off as a function; the approved runner enables it.

**Processing/output:**

- `visual_features.csv`: screen_id/status/error, original_width/original_height, width/height, foreground_coverage, edge_density, component_count, correction_activated. Counts/dimensions are integers; fractions are in [0,1]. `status=ok` is required for downstream work.
- `color_palettes.json`: screen-ID map of `colors` entries with RGB vector, Lab vector and nonnegative `proportion`, plus `background_rgb`; 1≤K≤5 and masses sum to one. RGB centroids nominally [0,255]; Lab uses standard float coordinates.
- `bounding_boxes.json`: screen-ID map to normalized rectangle lists [x0,y0,x1,y1], coordinates in [0,1] with ordered endpoints.
- `layout_vectors.csv`: screen_id plus `cell_00`…`cell_31`, finite [0,1], row-major four-column/eight-row union occupancy.
- `configuration.json`, `run_summary.json`, `triggers.json`, `differences.csv`, masks, comparisons and source/protection hashes retain evidence/configuration.

**Validation:** ID sets agree, 82 successful records, valid bounds/palettes/geometry. The runner reproduces the original baseline before applying correction, repeats correction, checks no added foreground and matches the frozen sample. In the approved pilot only APP02-FLOW01-S01 activates; the other 81 feature records remain baseline-equivalent. A change requires investigation, not forced output. Numerical repeatability is not segmentation accuracy.

**Status/dependencies:** approved pilot output, using NumPy/Pillow/OpenCV/scikit-learn/threadpoolctl/Matplotlib. Not a new-dataset calibration workflow.

## 2. Pairwise similarity — original descriptor distances

**Entry:** `pairwise_baseline.py`. Inputs: feature scalar/layout/palette files and metadata. The loader validates exact ID sets, feature bounds, palette proportions and app/flow ownership. Boxes/masks are not re-extracted.

**Outputs:** `pairwise_distances.csv`: shared IDs plus `color_emd_distance,foreground_distance,edge_distance,layout_distance`. Raw color EMD is finite nonnegative without an assumed upper bound; the other distances lie in [0,1]. `pairwise_similarities.csv`: shared IDs plus `foreground_similarity,edge_similarity,layout_similarity`, using original M0 edge here. Color similarity is not exported at this stage. `pairwise_summary.csv`, `pair_counts.csv`, configuration and input/source hashes complete provenance.

**Validation:** 709 pairs, unique keys, finite ranges, CIEDE2000/transport analytic identity/symmetry tests and deterministic descriptors; saved input hashes match. Pairwise EMD is recomputed when this stage executes; image features are not.

**Status/dependencies:** established traditional descriptor baseline; NumPy/SciPy/scikit-image. It is not the M1 composite implementation and creates no graph/context score.

## 3. Descriptor investigation — diagnostic branch

**Entry:** `investigate_pairwise.py`. Inputs: pair tables/configuration, feature files, metadata, original screenshots, saved corrected overlays. It validates pair/feature/source provenance and reproduces all pairwise exports twice from saved descriptors, including config alignment in the relocated private project.

**Outputs:** `descriptive_statistics.csv` groups app/type/metric with count/quantiles/extrema/mean/sample SD; `selected_examples.csv` has 120 purposive slots representing 95 unique pairs; `screen_diagnostics.csv`, diagnostic cases, 40 detailed inspection sheets, eight overviews and distribution figures. Validation JSON records the alignment and repetition checks.

**Validation/interpretation:** expect complete 709-pair source universe, fixed slots, valid figures/tables and unchanged features. Historical narrative reports are copied separately with a provenance marker. A generated inspection sheet is not newly verified visual evidence.

**Status/dependencies:** exploratory diagnostics, not baseline alteration or human accuracy; Matplotlib/Pillow/NumPy plus pairwise dependencies. No automatic descriptor selection follows.

## 4. Edge similarity — experimental branch

**Entry:** `experiments/edge_similarity_evaluation/evaluate.py`. Inputs: saved original/approved scalar edge densities, old pairwise similarities, original screenshots and original rendered Canny panels. The approved/original edge densities and dimensions must match. No Canny is rerun.

**Parameters:** M0/M1/M2; epsilon=1e-5, grid 1e-8/1e-6/1e-5/1e-4/1e-3, seed=42. Sample allocation balances apps within 12 within-flow and 12 cross-flow pairs without score-based selection.

**Outputs:** `edge_similarity_comparison.csv` has shared IDs/pair_id, edge_a/edge_b, absolute_difference, M0/M1/M2 and signed method differences; all metric similarities in [0,1]. `random_pairs.csv` has 24 unique pairs; statistics, rank/tie CSVs, epsilon_sensitivity.csv, sampling configuration, five purposive diagnostics and eight random inspection pages preserve evidence.

**Validation:** identity, symmetry, both-zero/one-zero behavior, bounds, saved M0 exact match, M2→M1 for strictly positive inputs, deterministic sampling/results and unchanged source inputs. Epsilon is not fitted for spread.

**Status/dependencies:** experimental comparison; prior perceptual result inconclusive. M1's later provisional adoption is an operational choice, not accuracy validation. NumPy/SciPy/Pillow/Matplotlib and CSV helpers.

## 5. Composite scoring — provisional baseline v1

**Entry:** `composite_baseline.py`. Inputs: saved raw pairwise distances and similarities, approved feature scalars/layout/palettes, metadata and original screenshots for figures. Location-bearing pairwise hashes must match the private workspace. Color transport is not recomputed here.

**Parameters:** M1 edge, color tau=10, group weights 1/3 each, density subweights 1/2 each. Sensitivities: M1/tau=5, M1/tau=20 and M0/tau=10. No optimization.

**Outputs:** `composite_scores.csv` retains shared IDs/pair_id, raw color_emd_distance, foreground_a/b, edge_a/b, layout_mae, configuration/tau/edge_method, six similarity terms, both original M0 and M1, group/sub-contributions and descending average-tie rank. `sensitivity_analysis.csv` has 2,836 rows (four configurations × 709), plus delta_composite and rank_shift against baseline. `composite_summary.csv` has 792 config/app/type/quantity rows; `sensitivity_summary.csv` has 72 grouped change/rank summaries. Selected examples contain 39 slots/32 unique pairs; 13 sheets and plots are diagnostic outputs.

**Validation:** 709 keys per configuration; finite [0,1] similarities; identity/symmetry/extreme cases; group contributions sum to composite, sub-contributions to Density. Changing tau changes only Color; the M0 alternative changes only the edge term. Exact raw EMD and pair IDs are retained.

**Status/dependencies:** approved provisional computational baseline, not calibrated consistency; NumPy/SciPy/Matplotlib/Pillow plus existing pairwise loader dependencies.

## 6. Tau sensitivity — read-only review

**Entry:** `review_tau_sensitivity.py`. Inputs: existing `sensitivity_analysis.csv`, baseline `composite_scores.csv`, original pairwise keys/config. Select only M1 rows with tau 5/10/20. There must be 709 unique identical keys per tau; all non-color columns/contributions remain fixed. It checks formulas but does not create upstream scores or extract features.

**Outputs:** `tau_sensitivity_review.md`; `tau_review_assets/summary.csv` (Color/Composite stats per tau/type), `rank_changes.csv`, `most_affected_pairs.csv` (five largest score changes and a rank-shift example per comparison), two plots and checks with source/input digests. Copied inspection pages 11/12 support the historical links but are not new expert validation.

**Validation:** exact tau=10 match, finite bounds, fixed parameters, formula absolute tolerance 1e-15, report/plot links and unchanged inputs. Tau10 remains provisional absent serious evidence of a problem. Reuse saved configurations; only composite-scoring can regenerate upstream tables if requested.

**Status/dependencies:** diagnostic, parameter-free review beyond existing fixed tau settings; NumPy/SciPy/Matplotlib. The older standalone tau package remains a review-only subpackage; this ecosystem integrates its upstream stages separately.

## Cross-stage reproducibility

`provenance.json` records every packaged source/fixture digest and original hash. `relocation.json` records location-only rebasings in a private workspace. `run_manifest.json` records executed/reused stages, exact outputs and unchanged source inputs. CSV numerical equivalence and parameters are audited separately from platform fonts and absolute provenance paths. Existing generated narrative is labeled as historical. No source stage result is overwritten to hide a failed reproduction. Stop dependent stages when a contract fails.
