# Controlled edge similarity experiment

Read [the evaluation report](edge_similarity_evaluation_report.md) for findings and limitations. This directory is an isolated experiment. The production extraction and traditional pairwise baseline remain unchanged.

From the project root, using the existing environment:

```sh
.venv/bin/python experiments/edge_similarity_evaluation/evaluate.py --output /private/tmp/edge-evaluation-reproduction
.venv/bin/python -m unittest discover -s experiments/edge_similarity_evaluation -p 'test_evaluation.py' -v
```

Choose a fresh output directory. The runner refuses to overwrite an existing comparison CSV. Tests reproduce the whole experiment twice in temporary directories and compare every generated file, including PNGs, against the saved run. Determinism is checked in this environment; library/font changes can change rendered bytes. No installation or feature extraction is needed.

`evaluate.py` reads approved saved densities, validates all 709 pair identifiers, computes three edge metrics, samples pairs without using scores, writes tables, and reuses saved rendered edge panels. `test_evaluation.py` checks analytic definitions, invalid inputs, zeros, sampling, reproduction and overwrite protection.

- `edge_similarity_comparison.csv`: full pair universe, densities, metrics and signed method differences.
- `random_pairs.csv`, `sampling_allocation.csv`, `configuration.json`: fixed-seed sample and its design.
- `metric_statistics.csv`: pooled/application/type descriptions; overlapping groups.
- `rank_correlations.csv`, `score_ties.csv`: rankings and numerical ties.
- `epsilon_sensitivity.csv`: smoothing sensitivity; epsilon was not chosen to maximize spread.
- `distributions.png`: fixed 0–1 histograms and empirical cumulative distributions.
- `visual_inspection/`: eight pages, three random pairs per page, covering all 24 pairs.
- `diagnostic_cases/`: separately selected purposive cases, not random prevalence evidence.
- `validation_checks.json`, `protected_sha256.json`: checks and unchanged historical-file hashes.

Edge maps are crops of existing 1200×1320 diagnostic figures, not newly generated raw Canny arrays. The panel crop is a fixed figure-layout operation, not screenshot ROI cropping. Original and approved saved edge densities and processed dimensions are verified equal for all 82 screens. All numerical comparisons use saved CSV densities, never rendered pixels.
