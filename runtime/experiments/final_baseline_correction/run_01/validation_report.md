# Final segmentation experiment: baseline-preserving gradient correction

**Decision: PASS on the controlled 12-screen sample. Recommend the optional correction for a reviewed full-pilot rerun only. Do not promote automatically. The original pipeline remains the default. Segmentation optimization stops here.**

One fixed correction was tested, with no parameter sweep or second candidate. It subtracts one large smooth boundary-connected region only when both side profiles show sustained gradual color change and baseline foreground coverage is high. It does not replace background estimation, add foreground, change the ROI, or alter feature definitions.

## Visual and numerical evidence

Both conditions use the **identical complete processed original screenshot**. No attribution footer, frame, device chrome or genuine navigation was cropped. Original outputs reproduced the saved baseline's palette, boxes and all grid values. Lower foreground coverage is not the acceptance basis: the [gradient comparison](comparisons/APP02-FLOW01-S01.png) shows the broad background removed while filled buttons, heading/copy, icons and footer remain. White mask pixels indicate foreground, black background.

Inspected every selected screen in contact sheets [1](contact_sheet_1.png), [2](contact_sheet_2.png), [3](contact_sheet_3.png), with detailed original/corrected boxes and grids for the [gradient](comparisons/APP02-FLOW01-S01.png) and [mixed-background](comparisons/APP05-FLOW01-S04.png) cases. All 12 individual comparisons are in [comparisons](comparisons/).

| Screens | Finding |
|---|---|
| APP02-FLOW01-S01 | Only activation. Foreground .961439 → .202650; components 6 → 18; mean box-union occupancy .964007 → .246538. Broad smooth gradient no longer forms an almost-full-screen foreground rectangle. Both filled Log in/Sign up buttons remain solid rather than hollow. Heading, descriptive text, status/progress icons and attribution elements remain visible. Some enclosed background pockets/counters and touching text regions still count as foreground; semantic separation is not claimed. |
| APP05-FLOW01-S04 | No activation; foreground .610067, 41 boxes and all 32 grid entries identical. Filled dark cards and header/bottom regions remain. No mixed-background regression, but merging and fine-detail limitations remain unresolved. |
| APP01-FLOW01-S00, APP03-FLOW02-S00 | Splash logos unchanged, with the same source-footer/device-indicator interference. |
| APP01-FLOW01-S02, APP02-FLOW01-S014 | Form/table masks unchanged. Filled buttons remain; existing missed pale outlines are not repaired. |
| APP01-FLOW02-S04 | Chart, floating navigation and their masks/boxes remain identical; no false patch introduced as in A1. Chart-envelope empty-area occupancy remains. |
| APP02-FLOW01-S013 | Legal text and filled circular control unchanged; fragmentation remains. |
| APP03-FLOW01-S00 | Artwork, composer, pale-control misses and footer unchanged. |
| APP04-FLOW01-S00, APP04-FLOW02-S03 | Filled welcome/booking cards and buttons unchanged; adjacent cards still merge and corner artifacts remain. |
| APP05-FLOW01-S00 | Dark-card borders, text, boxes and baseline fills unchanged; baseline component limitations remain. |

The eleven nonactivated masks are pixel-identical, and their boxes/grid/features are exactly unchanged. Palette and Canny differences are zero for all twelve. Per-screen coverage/count differences and all 32 layout changes are in [differences.csv](differences.csv); full numerical files are in [baseline](baseline/) and [candidate](candidate/).

## Corrected diagnosis of the mixed-background case

The original baseline actually estimates **[215,227,223]**, the light panel, on APP05-FLOW01-S04. It marks the dark headers/cards as foreground and leaves the large empty light area background. Earlier wording that the baseline chose a dark background and classified the whole light panel as foreground was incorrect; the historical reports are preserved. High coverage alone did not establish an error. This screen illustrates merging, mixed-background interpretation and fine-detail limitations; the gradient correction correctly abstains rather than attempting a general fix.

By contrast, APP02-FLOW01-S01 selects **[47,47,47]**, the source-footer gray. Uniform footer samples beat the gradient's dispersed RGB bins; thresholding distance from that single gray then marks nearly the whole gradient foreground. Prior footer-free baseline coverage was still about .511, so ROI sensitivity is only part of the problem. A single background vector cannot capture the whole gradient. These findings and complete formulas are documented in the [README](../README.md).

## Trigger behavior and sparse validation

The known gradient activates; none of the other eleven screens activate. This is a descriptive audit of this purposive sample, not a measured specificity/sensitivity estimate. The mixed case intentionally abstains. An analytic horizontal-only gradient demonstrates a **missed gradient** because vertical side-profile variation is absent. A genuine smooth gradient control spanning both borders could also cause false activation; unseen data are not validated.

Reused the five prior assistant-visually annotated patches as evaluation-only regions, without new labels or tuning. [Patch counts](patch_counts.csv) show:

- Two empty gradient patches: 7,700 baseline foreground pixels → 0 corrected foreground pixels among the same 7,700 background-labeled pixels.
- Filled Log in interior: 223/225 foreground pixels before and after.
- Filled WellNest card interior: 1,550/1,550 foreground pixels before and after.
- Empty mixed-screen light-panel patch: 0/6,200 foreground pixels before and after.

These sparse, non-independent patches support the visible effect but are not whole-object, full-screen or dataset accuracy. Text/icon retention on the activated screen is visually assessed, not quantified against expert annotation.

## Acceptance and tests

| Criterion | Result on this sample |
|---|---|
| Material reduction of gradient false foreground | PASS: visible gradient cleared, no giant background box, supporting patch evidence. |
| Mixed background not worse | PASS: bitwise identical, with prior interpretation corrected. |
| Filled controls substantially intact | PASS: both gradient-screen buttons visibly filled; sampled interior unchanged; other eleven screens identical. |
| No major regressions in acceptable screens/details | PASS on the reviewed sample; existing pale-detail misses remain. |
| No new large false foreground region | PASS: correction only removes original foreground; comparisons show no new bands. |
| Numerical correctness and reproducibility | PASS: five original tests and four new tests, exact sample regeneration and protected-file hashes. |

See [original test log](../existing_tests.log) and [correction test log](../correction_tests.log). The new tests cover disabled/default preservation, constant and abrupt-background abstention, a synthetic gradient with filled objects, the documented horizontal-gradient miss, full sample mask/box/grid/palette/edge reproduction, and preservation of earlier files. Bounded feature values, normalized palettes with at most five clusters, finite Lab and 32 grid entries passed.

This is a narrow improvement over the baseline on the known gradient while preserving the baseline elsewhere in this sample. It is **not** a claim of universally safe segmentation, solved mixed backgrounds, or semantic UI components. Source artifacts, faint boundaries, merges, counters and box-envelope overcounting remain. The original baseline stays unchanged; no full 82-screen rerun, further optimization, similarity, graph/scoring or classification work was performed. Review of the archived evidence is the next step before any controlled full-pilot rerun.
