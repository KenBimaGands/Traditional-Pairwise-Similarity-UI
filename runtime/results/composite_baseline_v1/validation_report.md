# Composite Baseline v1 — Validation report

**Implemented and numerically reproducible for all 709 approved pairs.** Baseline v1 fixes M1 edge similarity, tau=10 and equal Color/Density/Layout weights. It can serve as a frozen visual-only comparator for later contextual-method work. This conclusion concerns computation and provenance, not validated perceptual accuracy or consistency classification.

## Numerical validation

- 82 approved screens; 709 unique unordered within-application pairs: 411 within-flow and 298 cross-flow. No self-pairs, cross-application pairs, missing features or identifier mismatches.
- Approved feature/metadata hashes match the saved pairwise configuration. Existing foreground, M0 edge and layout scores agree with the saved descriptors and definitions.
- Every similarity is finite and in [0,1] for all four configurations; additive group contributions reproduce the composite.
- Analytic tests check identical inputs giving 1, symmetry, both-zero and one-zero edge handling, extreme inputs giving 0, equal weighting, density subweights and rejection of invalid inputs. A corrupted duplicate pair is rejected.
- All three tests passed. Two complete temporary runs matched one another and the saved generated outputs byte-for-byte, including figures. Reusing an existing output directory is refused. See [test log](test_results.log), [machine-readable checks](validation_checks.json) and [configuration](configuration.json).
- Historical dataset, metadata, extraction records, previous experiments and previous pairwise results remain unchanged, verified through [protected SHA-256 hashes](protected_sha256.json). No extraction, transport solver, Canny detection or grid reconstruction was rerun.

The implementation is [composite_baseline.py](../../composite_baseline.py); tests are [test_composite_baseline.py](../../test_composite_baseline.py). The [methodology](composite_methodology.md) defines every formula, notation, assumption, output and reproduction command.

## Distribution and sensitivity

All summaries below use the same 709 pairs, not independently sampled populations.

| Configuration | Minimum | Mean | Median | Maximum | Sample SD |
|---|---:|---:|---:|---:|---:|
| Baseline v1: M1, tau=10 | .406668 | .748485 | .772447 | 1 | .127723 |
| M1, tau=5 | .330782 | .699146 | .704679 | 1 | .130046 |
| M1, tau=20 | .487177 | .786893 | .812025 | 1 | .116702 |
| M0, tau=10 | .463292 | .789614 | .818742 | 1 | .120718 |

Baseline q10=.547695, q25=.673350, q75=.842687 and q90=.899862. [Distribution plots](distributions.png) show histograms and empirical cumulative curves, including pair-type and feature-group views.

| Alternative vs baseline | Mean score change | Largest absolute change | Spearman rank correlation | Kendall tau-b | Mean absolute global rank shift | Maximum |
|---|---:|---:|---:|---:|---:|---:|
| tau=5 | −.049339 | .083333 | .992927 | .932096 | 18.80 | 75 |
| tau=20 | +.038408 | .083328 | .993936 | .935109 | 16.99 | 68 |
| M0 edge | +.041129 | .135244 | .956926 | .829909 | 44.11 | 231 |

Reducing tau lowers color scores; increasing tau raises them. Substituting M0 raises scores because its absolute edge-fraction formulation is compressed near one on this pilot. The edge change has a larger observed ranking effect than either color sensitivity choice. This does not make M0 or M1 more accurate. No configuration was selected by score spread, no weights were optimized and no consistency threshold was introduced. Pairwise changes, full contributions and global ranks are in [sensitivity_analysis.csv](sensitivity_analysis.csv); grouped changes/rankings are in [sensitivity_summary.csv](sensitivity_summary.csv).

### Per-feature contributions

| Configuration | Mean Color contribution | Mean Density contribution | Mean Layout contribution |
|---|---:|---:|---:|
| Baseline v1 | .215245 | .275942 | .257298 |
| tau=5 | .165906 | .275942 | .257298 |
| tau=20 | .253653 | .275942 | .257298 |
| M0 edge | .215245 | .317071 | .257298 |

Each row sums to the composite mean before rounding. The tau variants change only Color; the M0 variant changes only Density. Equal group weights do not imply equal empirical variability: baseline contribution standard deviations are .094786 for Color, .038948 for Density and .039373 for Layout. Color has greater observed contribution variation, but those values do not establish feature importance, accuracy or causal influence. Raw color EMD is retained for audit, and no dataset min-max scaling is used.

### Within-flow and cross-flow descriptions

| Configuration | Within-flow mean / median (411 pairs) | Cross-flow mean / median (298 pairs) |
|---|---:|---:|
| Baseline v1 | .755821 / .779346 | .738367 / .764210 |
| tau=5 | .710219 / .722799 | .683874 / .695781 |
| tau=20 | .791793 / .817027 | .780134 / .806979 |
| M0 edge | .800228 / .842090 | .774974 / .795865 |

[composite_summary.csv](composite_summary.csv) also provides each application's statistics. These overlapping groups share screenshots; applications have unequal pair counts. No independent-pair inference, causal flow claim or classification is supported. Application/flow identifiers do not affect scoring.

## Inspection evidence and extremes

The [selection manifest](selected_pairs.csv) contains 39 purposive selection slots, 32 unique pairs, across [13 sheets](inspection_sheets/). Baseline low/lower-middle/high examples cover all five applications and both pair types. The remaining slots show each sensitivity configuration's minimum, maximum and largest global rank shift. Repeated pairs across purposes are intentional; examples do not estimate error prevalence.

Pages 01, 03, 06, 07, 10, 11, 12 and 13 and the distribution plot were visually inspected. Other sheets were generated for further review and were not individually inspected. Observations below are analyst diagnostics, not expert labels.

- **Broad appearance differences:** APP01-FLOW01-S00 / APP01-FLOW01-S015 scores .491902: sparse splash versus illustrated account-type cards ([page 01](inspection_sheets/page_01.png)). The same page's portfolio pair APP01-FLOW02-S03 / S04 scores .977633 despite changed chart shapes. The aggregate describes coarse properties and is insensitive to some chart/content differences.
- **Color and edge contrasts remain traceable:** APP02-FLOW01-S02 / S05 scores .450397: blue choice screen versus white verification form. APP02-FLOW01-S013 / S04 scores .745983 despite dense legal text versus a sparse phone form; its relative edge similarity is only .3679 but Color/Foreground/Layout offset that term. APP02-FLOW01-S07 / S08 scores .980917 for empty versus filled name fields ([page 03](inspection_sheets/page_03.png)). Compensation and control-state insensitivity remain limitations.
- **Baseline global minimum:** APP03-FLOW01-S01 / APP03-FLOW02-S00 is a modal/dimmed home screen versus a sparse splash, scoring .406668. It remains the minimum for tau=5 (.330782) and tau=20 (.487177). These are descriptor responses to changes in color mass, detected content and layout, not proof of inconsistency ([pages 06](inspection_sheets/page_06.png), [11](inspection_sheets/page_11.png), [12](inspection_sheets/page_12.png)).
- **Tied maxima:** APP02-FLOW01-S015 / APP02-FLOW02-S00 and APP03-FLOW01-S00 / APP03-FLOW02-S013 have identical saved descriptors and score 1 under every configuration. The inspected APP03 pair shows the same image-promotion view. Descriptor identity does not imply all future score-1 pairs have identical images.
- **Palette changes can dominate:** APP04-FLOW01-S00 / S03 scores .514054 with Color=.0043 although Foreground=.9675 and Layout=.8157. The dark-green introductory screen and white/pink preference screen have strongly different palette masses. APP04-FLOW02-S00 / S01 scores .932909 for visibly shared screen scaffolding ([page 07](inspection_sheets/page_07.png)). This illustrates descriptor contributions, not human calibration.
- **APP05 global low under M0:** APP05-FLOW01-S00 / APP05-FLOW02-S04 is .449063 in baseline v1 and .463292 under M0, the M0 configuration's minimum. Dark document-entry versus pale completion differs in palette and occupancy while edge counts remain similar. APP05-FLOW01-S03 / APP05-FLOW02-S02 scores .971512 despite different form choices/text ([pages 10](inspection_sheets/page_10.png), [13](inspection_sheets/page_13.png)).
- **Largest color rank changes:** APP03-FLOW02-S01 / S06 moves from baseline score .797390, rank 288, to .770207/rank 213 with tau=5 and .811969/rank 356 with tau=20. This welcome/login versus account-password pair shifts by −75 and +68 places although only Color changes. Direction depends on how other pairs' scores move, not solely on this pair's score change ([pages 11–12](inspection_sheets/page_11.png)).
- **Largest edge rank change:** APP03-FLOW01-S00 / APP03-FLOW02-S00, image-promotion home versus sparse splash, rises from .754217/rank 392.5 under M1 to .881679/rank 161.5 under M0, a −231-place shift ([page 13](inspection_sheets/page_13.png)). Fractional ranks reflect tied scores. M0 attenuates the relative edge-density contrast, materially affecting the composite ordering.

## Limitations and research interpretation

Foreground segmentation may misread background regions, omit pale controls or fragment components. Palette proportions emphasize large background surfaces and omit spatial arrangement. Canny density counts edges rather than their locations, can miss pale boundaries and includes inherited acquisition footer/device-frame edges. Layout occupancy is a coarse bounding-box-union representation subject to saturation and missed control-state differences. Connected components are not semantic UI elements. These limitations are inherited, documented and unchanged.

The M1 choice is provisional and operational; the prior edge experiment did not validate perceptual superiority. Tau=10 and equal grouping are transparent assumptions, not expert-calibrated scales or optimal weights. Correlated descriptors and compensatory averaging can hide a large change in one property. High scores indicate agreement under this formula, not visual consistency, usability or semantic equivalence.

This deliverable completes the traditional visual-only baseline and its controlled sensitivity analysis. Later graph-based evaluation can use it as a fixed comparator while keeping data and visual inputs controlled. No graph scoring, navigation adjustment, optimization, consistency classification or simulated expert ground truth has been implemented. Independent human annotations remain necessary for perceptual or consistency-validity claims.
