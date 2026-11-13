# Traditional pairwise visual baseline

Uses the explicitly selected **82-screen corrected pilot features** in `../results_corrected_pilot`. No screenshot features were recomputed, and the original dataset, metadata, extraction source and results were preserved. The pairwise method has no graph or navigation context in its scoring.

| Application | Screens | All unique pairs | Within flow | Cross flow |
|---|---:|---:|---:|---:|
| APP01 | 24 | 276 | 148 | 128 |
| APP02 | 20 | 190 | 126 | 64 |
| APP03 | 18 | 153 | 97 | 56 |
| APP04 | 10 | 45 | 20 | 25 |
| APP05 | 10 | 45 | 20 | 25 |
| Total | 82 | 709 | 411 | 298 |

## Output files

- [pairwise_distances.csv](pairwise_distances.csv): 709 pair identifiers, raw CIEDE2000-EMD color costs, absolute foreground/edge differences and mean absolute layout differences.
- [pairwise_similarities.csv](pairwise_similarities.csv): the same 709 identifiers with three separate `1−distance` similarities. Color similarity is absent because no color conversion scale has been approved.
- [pairwise_summary.csv](pairwise_summary.csv): 60 descriptive rows, one for each application × within/cross/all grouping × four distance descriptors. `all` overlaps the other groups and should not be added to them.
- [pair_counts.csv](pair_counts.csv): expected and exported counts.
- [illustrative_pairs.csv](illustrative_pairs.csv): descriptor-specific extrema, not a composite ranking.
- [visualizations](visualizations/): five per-application figures with four raw distance matrices each. Self-diagonal zeros and mirrored values are for display only.
- [configuration.json](configuration.json): exact numerical conventions, dependency versions and source/input fingerprints.
- [validation_checks.json](validation_checks.json): completed export validation and reproducibility checks.
- [validation_report.md](validation_report.md): findings, evidence and limitations.

The smoke export is separate in `../results_pairwise_smoke` and contains 15 diagnostic pairs covering all five applications, both pair types, and foreground extremes.

## How it works

Read [PAIRWISE_METHODS.md](../PAIRWISE_METHODS.md) for formulas, definitions of every mathematical symbol, numerical examples and limitations. Source is [pairwise_baseline.py](../pairwise_baseline.py), tests are [test_pairwise_baseline.py](../test_pairwise_baseline.py), and plotting is [plot_pairwise_distances.py](../plot_pairwise_distances.py).

The main functions are `load_features` (validate and align existing records), `palette_data` (check/canonicalize weighted Lab palettes), `color_distance` (CIEDE2000 cost matrix and balanced transport), `distances` (four independent descriptors), `make_pairs` (within-application combinations), `build_tables` (scores and descriptive summaries), and `run` (fresh exports/provenance). No function reads transitions or uses roles to alter scores.

The linear program uses installed scikit-image and SciPy, with unit total mass and no extra color-cost scaling. Proportions are only corrected for negligible floating-point summation drift after strict validation. Density values are never averaged together, and no composite score or consistency classification is computed.

To reproduce, use the existing `.venv` and a new output directory:

```sh
.venv/bin/python -m unittest -v test_pairwise_baseline
.venv/bin/python pairwise_baseline.py --smoke --output results_pairwise_smoke_reproduction
.venv/bin/python pairwise_baseline.py --output results_pairwise_baseline_reproduction
```

These outputs can be reused as the navigation-independent pair-level measurements for a later contextual method, keeping the same approved feature version and pair population. They are visual descriptor comparisons, not consistency labels.
