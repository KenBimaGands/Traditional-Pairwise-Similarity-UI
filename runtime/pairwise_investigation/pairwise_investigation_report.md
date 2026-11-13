# Exploratory investigation of traditional pairwise visual descriptors

The computed distances are numerically reproducible and describe specific visual properties, but **none is a complete measure of screen appearance or design consistency**. Color separates broad color/theme changes while deemphasizing spatial structure; foreground fraction aliases different content arrangements; edge similarity is strongly compressed near one; layout captures broad occupied envelopes but misses some control-state changes and can saturate around keyboards/merged regions. These are feature-level diagnostic findings, not classifications or claims of agreement with human perception.

## Evidence and coverage

Read the existing 709 pairs from the approved 82-screen `results_corrected_pilot` extraction: 411 within-flow and 298 cross-flow. No screenshot features, masks, palettes, boxes or occupancy vectors were recomputed or changed. Scores were re-evaluated from the saved descriptors only in temporary directories to audit reproducibility; reported values come from the existing CSVs. No formulas or feature settings changed.

[Descriptive statistics](descriptive_statistics.csv) contain 72 application/type/descriptor groups: five applications plus the pooled `ALL` population, each with within-flow, cross-flow and combined `all` rows, across four displayed measures. These are overlapping descriptive groups, not independent observations.

[Selected examples](selected_examples.csv) contain **120 selection slots representing 95 unique pairs**: lowest, lower-central and highest values for every application × pair type × descriptor group. Every application is represented in every eligible group. Low color distance means closer palettes; low similarity means more descriptor difference. The central example is an actual observed pair at zero-based index floor((n−1)/2), not an artificial screenshot pair assigned the interpolated group median. Ties use screen IDs deterministically. Repeated pairs across features are intentional. These purposive examples do not estimate error prevalence.

The [40 detailed sheets](inspection_sheets/) show original screenshot A/B, pair IDs, all four numerical results, reused corrected bounding-box overlays and saved palette strips. The [eight overview sheets](overviews/) cover all 120 slots. Six additional, explicitly chosen diagnostic cases appear in [page 1](diagnostic_cases_1.png), [page 2](diagnostic_cases_2.png) and [diagnostic_cases.csv](diagnostic_cases.csv).

All eight overview sheets were inspected, plus detailed APP04 within-flow color and APP01 within-flow layout sheets, both diagnostic pages and the edge-distribution chart. The other detailed sheets were generated for review but not individually inspected at full resolution. Figure labels round values to four decimals; a displayed `1.0000` need not be exactly one. CSVs retain full float precision.

## 1. Numerical correctness

The investigation checked all 709 distance/similarity rows against the expected unordered within-application pairs, including screen/app/flow IDs, pair types, absence of self/reversed/cross-app pairs, finite nonnegative distances, [0,1] bounds for the three bounded measures and exact similarity conversion. Existing within-flow/cross-flow split tables match their corresponding combined-table partitions.

Both complete temporary reproductions matched saved distance, similarity, summary, pair-count and configuration files **byte-for-byte**. The approved feature/metadata fingerprints and pairwise source fingerprint match the original run. All original dataset, extraction/experiment outputs and prior pairwise tables were fingerprinted before and after the investigation and remained unchanged. See [validation_checks.json](validation_checks.json) and [protected_sha256.json](protected_sha256.json).

The investigation found no numerical mismatch. This establishes implementation/data alignment and repeatability, not perceptual validity. The original tests already cover analytic transport, palette permutations, identity and symmetry; the present reproduction audits their actual exported population without changing any scores.

## 2. Descriptor behavior

### Distribution overview

| Displayed measure, all 709 pairs | Minimum | Median | Maximum | Interquartile range |
|---|---:|---:|---:|---:|
| Raw color EMD distance | 0 | 3.123557 | 55.602798 | 3.122569 |
| Foreground similarity | .508472 | .942547 | 1 | .102392 |
| Edge similarity | .907071 | .992188 | 1 | .013343 |
| Layout similarity | .375721 | .791464 | 1 | .171037 |

Color cost has different units from the three similarities. These ranges cannot justify equal feature weights, a feature ranking by importance, or a composite formula.

Distribution figures show empirical cumulative distributions per application/type on the left and a pooled observed-range view on the right:

- [Color EMD distance](distributions/color_emd_distance.png).
- [Foreground similarity](distributions/foreground_similarity.png).
- [Edge similarity](distributions/edge_similarity.png).
- [Layout similarity](distributions/layout_similarity.png).

The bounded left axes cover 0–1 so compression is visible. Right axes zoom to the observed values without rescaling stored scores. Pair pooling weights applications according to their number of pairs, not equally.

### Color: useful theme signal, background-dominated and spatially blind

APP04-FLOW01-S00 versus APP04-FLOW01-S04 has color distance **55.602798**. The detailed sheet shows a dark green welcome screen against a predominantly white completion screen. This is an interpretable palette-level response to a large color-distribution change. APP04-FLOW01-S01 versus S04, with mostly white surfaces and green accents, instead has color distance **.305275** (approximately), although one screen is a multi-field form and the other a completion/card screen. See [APP04 color examples](inspection_sheets/APP04_within_flow_color_emd_distance.png).

APP01-FLOW01-S010 versus APP01-FLOW02-S07 provides a clearer spatial limitation: a personal-details form versus a portfolio list. Both are mostly white, with dominant near-white palette masses **.885345** and **.863869**. Color EMD is only **.845562**, foreground similarity .987305, but layout similarity .837914. Visible differences in fields versus holdings do not require a large palette change. See [diagnostic page 1](diagnostic_cases_1.png), row 1.

This is not an incorrect transport solution. Pixel-proportion weighting necessarily favors large color areas and ignores where they occur. Small accent/control changes can contribute little to mass-weighted cost. A dominant centroid is not automatically background, but the screenshot and near-white centroid values support that interpretation in this specific pair. No palette reweighting or masking was applied.

### Foreground fraction: amount without arrangement

APP02-FLOW01-S012 (fee/disclosure list) and APP02-FLOW01-S08 (two-name form) have foreground fractions **.137427406** and **.137436048**. Their foreground similarity is **.999991358**, yet layout similarity is **.804426074**. The screenshots show text distributed down the left screen versus two fields concentrated near the top of the right screen. See [diagnostic page 1](diagnostic_cases_1.png), row 2.

The fractions correctly describe nearly equal foreground amounts. They cannot encode spatial placement, widget identity or content. Labeling their near-one similarity as global visual sameness would overinterpret a scalar descriptor. Likewise, a large fraction difference can reflect a keyboard or modal rather than a defect.

### Edge density: real numerical variation, compressed similarity scale

Saved per-screen edge fractions span approximately **.006974–.108519**. Consequently, `1−absolute_difference` has little room to move away from one. Observed pairwise edge similarities span **.907071–1**, with median **.992188**, interquartile range **.013343**, and standard deviation **.013769**. Narrow spread is not evidence of a solver or conversion bug; it follows from the absolute scale of edge-pixel fractions.

| Application, both pair types | Pairs | Minimum edge similarity | Median | IQR |
|---|---:|---:|---:|---:|
| APP01 | 276 | .954015 | .993467 | .009327 |
| APP02 | 190 | .907071 | .983852 | .021651 |
| APP03 | 153 | .960030 | .992689 | .011105 |
| APP04 | 45 | .974684 | .991990 | .009535 |
| APP05 | 45 | .985578 | .996555 | .005785 |

APP01-FLOW01-S07 versus APP01-FLOW02-S06 compares a phone-number keyboard screen with a portfolio screen. Edge similarity is **.999930863**, while layout similarity is **.588857703**. Their amount of detected edge pixels is nearly the same, despite different visible structures. See [diagnostic page 1](diagnostic_cases_1.png), row 3.

At the other end, APP02-FLOW01-S013 (dense legal text) versus APP02-FLOW01-S05 (short verification form) yields edge similarity **.907071004**, the lowest in this experiment. The screenshots visibly differ in text quantity, supporting an edge-amount interpretation; nevertheless, even this extreme remains numerically near one. See [within-flow edge overview](overviews/within_flow_edge_similarity.png), APP02 low-value row.

The descriptor retains numerical ordering of edge amounts but has limited visual separation on a 0–1 similarity axis. High displayed edge similarity should not be treated as a strong semantic/perceptual match. No transformation was modified or normalized by dataset extrema.

### Layout: broad spatial discrimination with envelope collisions and saturation

APP03-FLOW01-S01 versus APP03-FLOW02-S08 has layout distance **.624279** and similarity **.375721**: the first includes an overlay/prompt and the second a verification form/modal. The selected screenshots differ in broad occupied regions. This is the strongest layout separation in these within-application pairs. See [cross-flow layout overview](overviews/cross_flow_layout_similarity.png), APP03 low-value row. The magnitude also depends on how masks and component rectangles represent modal/dimmed backgrounds, not only on intended widget positions.

APP03-FLOW02-S010 versus APP03-FLOW02-S09 has **exactly identical layout vectors** (similarity 1). Both show the same name/age form geometry, but one contains entered values and a dark button, while the other is empty with a disabled gray button. The union envelopes stay the same. See [diagnostic page 2](diagnostic_cases_2.png), row 1. Layout behaves as coarse geometry, not control-state/color/content matching.

APP01-FLOW01-S07 and S08 each have **12 of 32 cells exactly equal to 1**, and layout similarity **.997315677**. The shared keyboard-containing lower region and filled rectangle envelopes occupy many of the same cells; entered text and button-state changes affect relatively little grid area. See [diagnostic page 2](diagnostic_cases_2.png), row 2, and [detailed layout sheet](inspection_sheets/APP01_within_flow_layout_similarity.png). These occupied cells are not automatically segmentation errors, but saturation limits sensitivity within them. Across the approved dataset, the maximum exact saturated-cell count is 12; no screen has an all-32-cells-saturated vector. Do not confuse earlier rejected A1 outputs with the approved feature set.

### Within-flow versus cross-flow: descriptive only

| Pooled measure | Within-flow median | Cross-flow median |
|---|---:|---:|
| Color distance | 3.000481 | 3.361495 |
| Foreground similarity | .951163 | .936994 |
| Edge similarity | .991539 | .992762 |
| Layout similarity | .809835 | .750504 |

These are composition-dependent descriptions of the selected screens. Flow groups share screenshots, differ in content, and are not randomized. They do not show that flow membership causes a distance change, nor establish that either group is more consistent. Edge medians even move in a different direction from some other descriptors, reinforcing the need to keep descriptors separate.

## 3. Extraction-related limitations

The saved overlays show missed pale field outlines, fragmented text, large chart rectangles and merged neighboring cards. For example, in the APP01 form/portfolio diagnostic, some boxes follow text instead of pale input boundaries, while chart/floating-navigation envelopes include empty space in other selected APP01 sheets. These are inherited mask/geometry limitations; this investigation does not regenerate or repair them.

Source attribution footers and device chrome are retained in the approved full-image ROI. They are visible in many APP01–APP03 examples and can contribute common color mass, edge pixels and bottom-grid occupancy. Shared artifact pixels can contribute to resemblance, but their exact contribution was not isolated experimentally here.

APP05-FLOW01-S04 still contains merged card/header/bottom-region envelopes, with mean occupancy **.627851** and six fully occupied cells. Its high foreground fraction **.610067** is not itself proof of a failure: the final diagnosis established that the light panel is estimated as background and dark regions are foreground. Do not repeat the earlier erroneous interpretation that the entire light panel is foreground. The mask is a single-color contrast heuristic, not a semantic content segmentation.

The approved correction affects only APP02-FLOW01-S01's foreground/layout. Its color palette and Canny density are intentionally unchanged. Its comparison with APP02-FLOW01-S05 still has color distance **47.505325**, because a colored gradient and a white verification screen have different color distributions. This is not evidence that the foreground correction failed. See [diagnostic page 2](diagnostic_cases_2.png), row 3. Residual smooth-content/counter issues and trigger misses remain inherited limitations. No claim of segmentation accuracy is made without ground truth.

## 4. Metric limitations and implications before future aggregation/context work

- Color EMD measures weighted color distributions, not position, purpose or semantic equivalence. Its units are not those of bounded density/layout similarities; no color similarity scale is approved.
- Density fractions collapse spatial arrangements to a single amount each. Foreground and edge should remain distinct; neither is a complete density/content model.
- Edge similarity's small empirical spread makes a near-one value weak evidence of broad resemblance. Its theoretical bound of one does not make its practical scale comparable to layout similarity.
- Layout occupancy deliberately loses component identity, inside-box detail, typography and some control-state differences. Component extraction artifacts propagate to the distance.
- Pair observations share screens; repeated descriptors across flows can also occur. Zero distance need not establish duplicate source images, and there is no human-label benchmark here.

The metrics perform their specified calculations, but a future composite would require an explicit rationale for scale, contribution and interpretation. Do not equate a collection of large similarities with consistency. A future graph/context evaluation must reuse the same approved features and comparable pair population if it is intended to isolate the value of contextual modeling. This report does not implement or claim any graph benefit, weights, calibration or consistency threshold.

## Formulas and notation used in this investigation

Let A,B denote screenshots. A's palette has m Lab colors c_i and masses p_i; B's has n colors d_j and masses q_j. Indices i=1,…,m and j=1,…,n identify colors; masses are nonnegative and each palette sums to one. The ground cost is C_ij=ΔE_00(c_i,d_j), the established CIEDE2000 color difference with k_L=k_C=k_H=1. Here L*,a*,b* are the conventional Lab coordinates and Δ denotes a difference. The ground formula is

    ΔE_00 = sqrt[(ΔL′/(k_L S_L))² + (ΔC′/(k_C S_C))²
                + (ΔH′/(k_H S_H))²
                + R_T(ΔC′/(k_C S_C))(ΔH′/(k_H S_H))].

Primes denote CIEDE2000-corrected terms: ΔL′ is lightness difference, ΔC′ corrected chroma difference and ΔH′ the hue-related chromatic difference; S_L,S_C,S_H are standard sensitivity functions, R_T the chroma–hue interaction, and k_L,k_C,k_H the fixed viewing-condition factors. `sqrt` is nonnegative square root and superscript ² means square. Full standard subformula definitions and implementation references remain in [PAIRWISE_METHODS.md](../PAIRWISE_METHODS.md); none was changed or reimplemented here.

For transport masses T_ij, raw color distance is D_C(A,B)=min_T Σ_iΣ_j T_ij C_ij with T_ij≥0, Σ_j T_ij=p_i and Σ_i T_ij=q_j. `min` selects the feasible transport matrix of minimum total cost; Σ is summation and ≥ denotes greater than or equal. Both total masses equal one. No color similarity is used in this investigation.

Let F_s and E_s be screen s's saved foreground and edge fractions. Distances are D_F(A,B)=|F_A−F_B| and D_E(A,B)=|E_A−E_B|, where |·| is scalar absolute value. Let v_(s,l) be screen s's saved grid occupancy at row-major cell l=0,…,31. Layout distance is D_L(A,B)=Σ_l|v_(A,l)−v_(B,l)|/32. Corresponding similarities are S_k(A,B)=1−D_k(A,B), k∈{F,E,L}. Each lies in [0,1]. These are separate quantities, never combined.

For screen edge extrema e_min=min_s E_s and e_max=max_s E_s, D_E≤e_max−e_min and S_E≥1−(e_max−e_min). Here min/max select the smallest/largest screen value, ≤ means less than or equal and s indexes all saved screens. This global bound also applies to the within-app subset, but the subset's observed extrema can be narrower. It explains compression without introducing a threshold or new normalization.

For a group G of r observed pair values x_1,…,x_r, mean μ=Σ_t x_t/r and sample standard deviation σ_sample=sqrt[Σ_t(x_t−μ)²/(r−1)], with t indexing pairs. The deviation is undefined for r=1; exported singleton groups would have a blank value. Range is max_t x_t−min_t x_t. Interquartile range IQR=Q(.75)−Q(.25). To define quantile Q(p), sort values z_0,…,z_(r−1), set h=(r−1)p, j=floor(h), α=h−j, and Q(p)=(1−α)z_j+αz_min(j+1,r−1). Probability p lies in [0,1], floor rounds down and α is interpolation weight. Q(.05),Q(.25),Q(.5),Q(.75),Q(.95) give exported quantiles. The symbol j is local to this quantile definition, unrelated to a palette index. Unique-value count counts distinct stored float values, not perceptually distinguishable levels.

The empirical cumulative distribution is H_G(x)=Σ_(t=1)^r 1[x_t≤x]/r, where x is a horizontal-axis value and indicator 1[condition] equals one if true, zero otherwise. Curves show the fraction of observed pair values at or below x; they are not model probabilities or confidence bounds.

For saved screen palette masses, dominant mass P_s=max_i p_(s,i). Exact layout saturation count is U_s=Σ_(l=0)^31 1[v_(s,l)=1], and empty-cell count V_s=Σ_l1[v_(s,l)=0]. These are endpoint counts, not consistency cutoffs. Mean layout occupancy is Σ_l v_(s,l)/32. They are computed from existing features, not regenerated masks. Notation is local to these diagnostic definitions.

## Reproduce and scope

From the project root: `.venv/bin/python investigate_pairwise.py --output pairwise_investigation_reproduction`. Use a fresh destination; existing directories are refused. The procedure uses the existing environment and source metrics, audits scoring in temporary directories, then reads saved values for summaries and images. It writes only the new investigation directory. No new dependencies, original-feature edits, composite scores, consistency labels, thresholds or graph methods were introduced.

There are no human perceptual annotations in this investigation. Observations describe visible content and descriptor behavior; they do not establish correlation with human judgments, causal flow effects or the effectiveness of a future contextual method.
