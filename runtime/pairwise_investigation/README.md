# Pairwise descriptor investigation

Start with [pairwise_investigation_report.md](pairwise_investigation_report.md). This is an exploratory feature-level investigation, not consistency classification or a human-perception evaluation.

## Evidence files

| File/folder | Contents |
|---|---|
| [descriptive_statistics.csv](descriptive_statistics.csv) | 72 application/type/feature groups, including pooled/all margins, with counts, quantiles, mean, sample deviation, IQR, range and unique-value counts |
| [distributions](distributions/) | Four ECDF figures: color distance and foreground/edge/layout similarities; each shows app/type curves and a pooled observed-range panel |
| [selected_examples.csv](selected_examples.csv) | 120 low/central/high selection slots covering all five apps, both pair types and all four descriptors; 95 unique pairs |
| [overviews](overviews/) | Eight compact pages covering all ranked selection slots |
| [inspection_sheets](inspection_sheets/) | 40 readable three-row sheets with original screenshots, pair IDs, four numerical results, saved corrected-box overlays and palettes |
| [diagnostic_cases.csv](diagnostic_cases.csv) | Six deliberately chosen descriptor limitations, using existing scores |
| [Diagnostic page 1](diagnostic_cases_1.png) | Background-weighted color, foreground fraction aliasing, edge-density compression |
| [Diagnostic page 2](diagnostic_cases_2.png) | Layout collisions, saturation around keyboards, corrected-gradient example |
| [screen_diagnostics.csv](screen_diagnostics.csv) | Existing per-screen density, dominant palette mass, mean occupancy and exact saturated/empty-cell counts |
| [validation_checks.json](validation_checks.json) | Alignment, numerical/reproduction checks, selection coverage and actual visual-inspection scope |
| [protected_sha256.json](protected_sha256.json) | Original dataset and prior output fingerprints, verified unchanged |
| `source_manifest.json` | Investigation source and dependency-version provenance |

Low/high refers to the plotted measure itself: low color distance means closer palettes, while low foreground/edge/layout similarity means more descriptor difference. The central selection is the lower central observed pair by rank. Tied values use screen-ID ordering. Four-decimal figure labels can round a value below one to `1.0000`; use CSV precision when investigating compression.

These are descriptive groups and purposive examples, not independent samples, calibrated resemblance classes or accuracy estimates. Do not sum `all` margins with the groups they already contain. Formula/notation definitions are in the report and the unchanged [PAIRWISE_METHODS.md](../PAIRWISE_METHODS.md).

Reproduce from the project root into a fresh directory:

```sh
.venv/bin/python investigate_pairwise.py --output pairwise_investigation_reproduction
```

Saved descriptors are read, not regenerated. Pairwise scores are audited in temporary directories using the unchanged scoring source; the existing pairwise and feature tables are never overwritten. The selected screenshot thumbnails and overlays are for visual inspection only, not new extracted features. No new dependencies were installed.
