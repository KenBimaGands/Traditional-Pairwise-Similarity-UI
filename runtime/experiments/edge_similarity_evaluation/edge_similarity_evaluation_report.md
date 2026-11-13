# Edge similarity metric evaluation

**Decision: INCONCLUSIVE — requires human annotation.** M1 provides an interpretable relative comparison of detected edge amounts and reduces the scale compression of M0. The reviewed examples do not establish that it is a better measure of perceived screen similarity. M2 at the documented epsilon is effectively M1, with little additional benefit on these positive densities. Keep the production baseline unchanged while retaining this experiment as evidence for choosing a metric later.

## Scope and numerical correctness

Used the approved `results_corrected_pilot/visual_features.csv`: 82 screens and the existing 709 unordered within-application pairs, comprising 411 within-flow and 298 cross-flow pairs. All identifiers, application/flow relationships, status fields, finite values, metric bounds and pair uniqueness were checked. Every computed M0 exactly matches its saved baseline similarity. Original and approved edge densities and processed dimensions match for all 82 screens.

No preprocessing, Canny detection or feature extraction was rerun. Color/layout similarities were not changed. Dataset, metadata, baseline features, previous experiments and previous pairwise outputs were fingerprinted before/after and remained unchanged; see [validation checks](validation_checks.json) and [protected hashes](protected_sha256.json). There are no cross-application pairs, composite weights, decision thresholds, graph methods or consistency labels.

The three tests in `test_evaluation.py` passed, including analytic zero/identity cases, reversed inputs, invalid fractions/epsilon, log-ratio equivalence, positive-density convergence, score-independent balanced sampling, shortfall handling and overwrite protection. Two complete temporary runs produced identical files byte-for-byte, including every CSV, JSON and PNG, and matched the saved run. Reproduction is established for the existing environment, not arbitrary future dependency/font versions. See [instructions](README.md).

## Formulas and notation

A and B denote screenshots. Their saved edge fractions are eA and eB, each in [0,1]. In the extraction definition, eA = EA / NA, where EA is the number of Canny edge pixels and NA is the number of processed image pixels for A; B is defined analogously. This experiment reads these fractions without calculating EA or rerunning Canny. All similarities and epsilon are dimensionless.

Let l = min(eA,eB), h = max(eA,eB), and d = |eA−eB| = h−l, where vertical bars mean absolute value.

- **M0:** S0(A,B) = 1−d. It compares absolute edge-fraction differences.
- **M1:** S1(A,B) = l/h when h>0, and S1(A,B)=1 when h=0. Thus exactly one zero gives 0; both zeros give 1. When h>0, S1=1−d/h.
- **M2:** S2(A,B;ε) = exp(−|log((eA+ε)/(eB+ε))|) = (l+ε)/(h+ε) = 1−d/(h+ε). Here ε>0 is epsilon, log is the natural logarithm and exp is its inverse exponential. Both zeros give 1; one zero gives ε/(h+ε), a positive smoothing value. The implementation uses the algebraically equivalent ratio.

To obtain the M2 simplification, consider eA≥eB: the log is nonnegative, so exp of its negative gives (eB+ε)/(eA+ε). Reversing A and B gives the same min/max ratio. Therefore M2 is a smoothed M1, not an independent descriptor. For strictly positive inputs, its limit as ε tends to zero is M1. For h>0, S2−S1 = ε(h−l)/(h(h+ε)) ≥ 0; smoothing pulls scores toward one. At the both-zero point M1 is defined explicitly and is not continuous along every approach to zero.

For the sample statistics, n is a group's pair count, i indexes its pairs, and xi is one method's score. Mean μ = (Σ xi)/n, where Σ sums over i=1,…,n. Sample standard deviation s = sqrt(Σ(xi−μ)²/(n−1)); sqrt denotes square root. Minimum and maximum are observed extrema. Quantiles use NumPy's default linear interpolation: sort scores as x(0),…,x(n−1); for probability p let t=(n−1)p, j=floor(t), and g=t−j. The quantile is (1−g)x(j)+g x(j+1), with the final endpoint returned directly. Floor rounds downward. The median uses p=.5; q10, q25, q75 and q90 use p=.10,.25,.75,.90. Interquartile range (IQR) is q75−q25. All 54 pooled/application/type/method groups are in [metric_statistics.csv](metric_statistics.csv).

The empirical cumulative distribution at score z is F(z) = (1/n)Σ I(xi≤z), where I is 1 when its condition holds and 0 otherwise. Histograms count scores in fixed width .025 bins covering [0,1], with the final bin including 1. The [distribution figure](distributions.png) uses the same score axis for all methods; histogram vertical scales differ and show counts, not accuracy.

For rank comparisons, ri and ti are the two methods' ascending average ranks for pair i, with tied scores receiving their average positions; r̄ and t̄ are the corresponding mean ranks. Spearman correlation is Σ(ri−r̄)(ti−t̄) / sqrt(Σ(ri−r̄)² Σ(ti−t̄)²). Kendall tau-b is (C−D)/sqrt((C+D+T)(C+D+U)), where C and D count concordant and discordant unordered comparisons between pair records, T counts comparisons tied only in the first method and U counts those tied only in the second. Concordance means the two methods order the records in the same direction; discordance means opposite directions. Joint ties contribute to neither numerator nor these denominator counts. No inferential p-values are used.

A numerical tie count at tolerance δ counts unordered record comparisons i<j satisfying |xi−xj|≤δ. Exact uses δ=0; near ties use δ=10⁻¹² and 10⁻⁶ in similarity units. These tolerances describe numerical indistinguishability only, not perceptual equivalence or classification. There are n(n−1)/2 = 250,986 possible comparisons between the 709 score records. Repeated-score records separately means n minus the count of distinct stored float scores.

## Epsilon choice and sensitivity

Chose **ε=10⁻⁵** as a density-scale numerical smoothing quantity, approximately one processed edge pixel: image areas range from 115,712 to 121,344 pixels, so one pixel changes density by approximately 8.24×10⁻⁶ to 8.64×10⁻⁶. This is a numerical scale rationale, not an estimate of Canny uncertainty or a fitted noise model. The value was not selected by maximizing spread or matching applications.

Sensitivity values 10⁻⁸ and 10⁻⁶ probe the near-unsmoothed/subpixel regime, 10⁻⁵ the chosen scale, and 10⁻⁴ and 10⁻³ progressively stronger smoothing, approximately 12 and 116–121 pixels. The larger values are stress checks, not proposed noise corrections. [epsilon_sensitivity.csv](epsilon_sensitivity.csv) provides all summaries.

| ε | Median M2 | Largest M2−M1 | Largest average-rank displacement from M1 |
|---:|---:|---:|---:|
| 10⁻⁸ | .792497 | .000000327 | 0 |
| 10⁻⁶ | .792503 | .000032734 | 0 |
| 10⁻⁵ | .792559 | .000327191 | 1 |
| 10⁻⁴ | .793116 | .003257096 | 3 |
| 10⁻³ | .798504 | .031159825 | 9 |

Average-rank displacement means the absolute difference between the two ranks of the same pair, as defined above. No zero edge densities occur: the observed screen range is .006974212–.108519428. The largest M2−M1 at the chosen epsilon occurs for APP03-FLOW01-S02 / APP03-FLOW02-S00. M2 changes by .031159497 for that pair across the complete epsilon grid, still a density-scale effect rather than validation against perception.

Relative metrics inherently amplify changes at low densities. With l<h, the rate of change of S1 with respect to l is 1/h, and for S2 it is 1/(h+ε), keeping h fixed. M0's corresponding rate is 1. These rates describe local sensitivity, not measured error. At the smallest observed density, one pixel gives a conservative rate-based score-change bound of approximately .00124 for changing one input, versus about .00000864 for M0. Near-zero future screens could be much more sensitive: a hypothetical pair with fractions .00001 and .00002 has M1=.5 and M2=.666667 at the chosen epsilon. This synthetic example is not a dataset result. There is no annotation evidence establishing whether the observed relative sensitivity is excessive, and this pilot does not validate near-zero deployment behavior.

## Distribution and ranking behavior

| All 709 pairs | Minimum | Maximum | Mean | Median | Sample SD | q10 | q25 | q75 | q90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M0 | .907071 | 1 | .987649 | .992188 | .013769 | .973315 | .983208 | .996552 | .998705 |
| M1 | .143665 | 1 | .740875 | .792497 | .206134 | .402839 | .623553 | .907302 | .961629 |
| M2 | .143744 | 1 | .740937 | .792559 | .206089 | .402981 | .623610 | .907324 | .961639 |

M0's IQR is .013343; M1's is .283749. M0 compression follows from small edge fractions, rather than a conversion bug. Even the unrestricted cross-screen density range would bound M0 below by about .898455; the actual within-application universe has minimum .907071. Relative scaling expands contrasts by dividing each absolute difference by its pair's larger density. It changes the interpretation, not just the display axis. Wider spread alone establishes neither higher accuracy nor more meaningful perceptual discrimination.

[Rank correlations](rank_correlations.csv): M0/M1 Spearman .975991 and Kendall .873374; M0/M2 .975993 and .873390; M1/M2 .999999933 and .999984. M1 changes some ordering because the same absolute difference receives a different score at a different density scale. M2 at the chosen epsilon changes rankings only slightly from M1.

[Exact/near ties](score_ties.csv): M0 has 619 distinct stored scores and 97 exact tied record comparisons, increasing to 101 at 10⁻¹² and 110 at 10⁻⁶. M1 and M2 each have 674 distinct scores and 35 exact tied comparisons. At 10⁻⁶, M1 has 36 tied comparisons and M2 has 35. Floating subtraction/rounding partly affects distinctions between exact and near ties. Fewer ties do not recover spatial information or establish useful discrimination.

Within-flow median changes from .991539 (M0) to .772161 (M1); cross-flow from .992762 to .810762. All statistics are descriptive: pairs share the same 82 screens, applications contribute unequal numbers of pairs, and the flow groups differ in screenshot composition. Treating 709 pairs as independent observations would exaggerate evidence. No causal flow interpretation, significance test or independent-sample confidence interval is justified here. Future annotated comparisons should account for screen/application clustering and held-out evaluation.

## Random sample and visual evidence

[24 random pairs](random_pairs.csv) use NumPy's fixed seed **42**. Within each pair-type stratum, applications receive pairs round-robin in seeded application order, then pairs are drawn uniformly without replacement within application/type from ID-sorted pools. Scores are never used. All five applications appear in each stratum. Within-flow allocations APP01–APP05 are 2,2,3,2,3; cross-flow allocations are 3,2,2,3,2. No stratum has a shortfall, repeated unordered pairs or cross-application comparisons. This deliberately balanced design is not an unweighted representative sample of the pooled 709-pair population.

All eight [inspection pages](visual_inspection/) were visually reviewed, covering every random pair. Each row shows originals, saved edge maps, IDs, densities, three scores and signed method differences. Maps are cropped from existing diagnostic figures; no Canny or image-feature calculations were performed. Rendered maps are suitable for visual inspection, not counting edge pixels. Labels round scores while CSVs preserve numerical precision.

| Evidence | Observation and metric implication |
|---|---|
| [Page 1](visual_inspection/page_01.png), APP01-FLOW01-S014 / APP01-FLOW01-S03 | Address confirmation has more detected text/field content than the two-field signup. M0=.986561 and M1=.696645 express different absolute/relative amounts. Many pale field perimeters are absent from the saved maps; M1 cannot restore them. |
| [Page 1](visual_inspection/page_01.png), APP01-FLOW02-S01 / S02 | Similar portfolio scaffolding, with an added horizontal graph line and changed amounts. M1=.876185 versus M0=.995938 responds to additional edge count. Whether this relative penalty is desirable needs annotations. |
| [Page 2](visual_inspection/page_02.png), APP02-FLOW01-S01 / S05 | Gradient marketing screen versus short code-entry form: M0=.974635, M1=.380671. The maps capture headline/button outlines rather than treating the smooth gradient as dense edges. Pale code-box boundaries are largely missing. Foreground-mask correction does not change this independent Canny descriptor. |
| [Page 2](visual_inspection/page_02.png), APP03-FLOW02-S013 / S03 | Image-promotion home versus login modal has M1=.911557 although edge positions/content differ. Both maps contain a comparable amount of detected structure; relative scaling remains spatially blind. |
| [Page 3](visual_inspection/page_03.png), APP04-FLOW02-S01 / S02 | Clinician details versus time-selection overlay: M0=.997569, M1=.940512. Text/buttons/card boundaries contribute similar edge amounts despite substantial arrangement and background changes. Device-frame corner outlines also contribute. |
| [Page 4](visual_inspection/page_04.png), APP05-FLOW01-S02 / S04 | Dark recommendation list versus pale-background completion/cards has M0=.998492, M1=.964293. Relative scaling does not distinguish the theme/arrangement changes. Some subtle dark-card boundaries are missing, while strong filled-card outlines survive. |
| [Page 5](visual_inspection/page_05.png), APP01-FLOW01-S012 / APP01-FLOW02-S05 | Address keyboard versus portfolio page: M0=.996552, M1=.910054. Different edge locations can yield similar counts. Acquisition-footer edges occur in both images and contribute a shared nuisance amount. |
| [Page 6](visual_inspection/page_06.png), APP02-FLOW01-S010 / APP02-FLOW02-S00 | Account-entry form versus home dashboard: M0=.999801 and M1=.995690. This is a strong counterexample to interpreting either near-one edge score as global screen resemblance. |
| [Page 7](visual_inspection/page_07.png), APP04-FLOW01-S00 / APP04-FLOW02-S03 | Intro card versus booking-review overlay: M0=.993877, M1=.790350. Background/theme and content differences extend beyond the edge-amount change. |
| [Page 8](visual_inspection/page_08.png), APP05-FLOW01-S04 / APP05-FLOW02-S03 | Pale completion versus dark source-configuration screen still has M1=.981073. Comparable counts persist across different visible content. M2=.981078 adds no material distinction. |

These are observable descriptor responses and analyst observations, not human ground-truth labels. Footer/device-frame contributions and missed low-contrast boundaries are inherited Canny limitations. Foreground segmentation failures do not directly feed the independently extracted edge density, although preprocessing/ROI artifacts do. Neither relative formula changes edge locations, repairs extraction or models semantic UI structure.

## Separate purposive diagnostics

These five additional unique pairs were selected from the complete universe by density/metric values, separately from the random sample; none overlaps that sample. They explain mechanisms, not failure prevalence. The central pair uses the observed sorted middle pair (index 354 of 709); ties use screen IDs. Largest method disagreement means largest absolute score difference, not disagreement against an annotation. Epsilon sensitivity means maximum M2 minus minimum M2 across the documented epsilon grid.

| Case and figure | Pair | M0 | M1 | Interpretation |
|---|---|---:|---:|---|
| [Smallest density difference](diagnostic_cases/01_minimum_density_difference.png) | APP02-FLOW01-S015 / APP02-FLOW02-S00 | 1 | 1 | Both show the same home view and equal saved edge densities. Identity behavior is appropriate here, but equal density alone cannot guarantee equal content. |
| [Median density difference](diagnostic_cases/02_median_density_difference.png) | APP04-FLOW01-S02 / APP04-FLOW02-S04 | .992188 | .822605 | Goal-choice and booking-completion screens differ by .0078125 in edge density; pale unselected card perimeters are incompletely detected. |
| [Largest density difference](diagnostic_cases/03_maximum_density_difference.png) | APP02-FLOW01-S013 / APP02-FLOW01-S05 | .907071 | .143665 | Dense legal text versus sparse code-entry form. Relative scaling expresses a roughly sevenfold edge-density contrast, but does not measure design consistency. |
| [Largest M0/M1 gap](diagnostic_cases/04_largest_M0_M1_gap.png) | APP03-FLOW02-S00 / APP03-FLOW02-S01 | .960030 | .148564 | Sparse splash versus login welcome. The splash's faint central logo is absent from the edge map; some of its small remaining density comes from chrome/footer. Relative scaling magnifies this inherited contrast. |
| [Most epsilon-sensitive](diagnostic_cases/05_largest_epsilon_sensitivity.png) | APP03-FLOW01-S02 / APP03-FLOW02-S00 | .987201 | .352710 | Sparse chat home versus still sparser splash. M2=.353037 at the chosen epsilon; its range across tested epsilons is .0311595. Smoothing sensitivity concentrates at smaller densities. |

## Implications for choosing a baseline

M0 correctly preserves absolute edge-fraction proximity but compresses these pilot scores near one. M1 correctly expresses relative edge-amount proximity; its larger contrasts can be useful if that is the intended descriptor meaning. It also amplifies low-density extraction effects and still aliases different spatial patterns. M2 adds a near-zero smoothing policy and epsilon dependence, with negligible distinction from M1 in this pilot; there is no observed basis for preferring it as another source of evidence.

No human annotations were collected or invented, and no accuracy percentages are reported. A subsequent blinded annotation study should define the visual property being judged, include low-density/low-contrast examples and structurally different equal-density pairs, and account for shared screens. That evidence is needed to choose between absolute and relative penalties on perceptual grounds. **INCONCLUSIVE — requires human annotation; no production replacement was applied.**
