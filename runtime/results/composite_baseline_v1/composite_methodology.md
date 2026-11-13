# Traditional Composite Visual Similarity — Baseline v1

This baseline combines saved Color, Density and Layout descriptors into a visual-only score for the existing 709 within-application screen pairs. It is independent of navigation: flow identifiers are retained for descriptive grouping and never enter the score. Baseline v1 fixes tau=10, M1 edge similarity and equal feature-group weights as provisional modeling assumptions. No weights, thresholds or parameters were fitted to application identity or human labels.

## Inputs and provenance

Approved features come from `results_corrected_pilot/`; distances and previous similarities come from `results_pairwise_baseline/`. All 82 screens, expected unordered within-application pairs, screen/app/flow identifiers, feature presence, status and numerical bounds are validated. Approved feature/metadata hashes must match the existing pairwise configuration. The saved foreground, M0 edge and layout similarities must agree with their definitions. The layout audit compares saved occupancy vectors only; it does not reconstruct boxes or occupancy.

Color EMD is read directly from the existing distance table. No image preprocessing, feature extraction, Canny detection, color transport solving, bounding-box calculation or layout-grid reconstruction is run. Original images are opened solely to create inspection sheets. The prior edge experiment remains unchanged: its inconclusive perceptual finding is compatible with the user's subsequent operational decision to adopt M1 provisionally.

## Mathematical specification

A and B denote screenshots. Every S below is a dimensionless similarity in [0,1], not a probability or a consistency label. Absolute-value bars denote magnitude; min and max select the smaller and larger inputs. exp is the natural exponential function.

### Color

Let dC(A,B) be the saved, nonnegative weighted CIEDE2000 Earth Mover's Distance (EMD). Conceptually, dC = min over T of Σi Σj Tij cij, subject to Tij≥0, Σj Tij=pi and Σi Tij=qj. Here i and j index the up-to-five palette centroids of A and B; pi and qj are their pixel-proportion masses, each palette summing to one; Tij is transported mass; cij is the symmetric CIEDE2000 difference between their CIELAB centroids. Σ denotes summation over the relevant palette indices. These transport values are explanatory notation: the solver is not rerun here.

S_color(A,B;τ) = exp(−dC(A,B)/τ), with τ>0.

τ (tau) has the same color-distance scale as dC so their ratio is dimensionless. The mapping is monotone decreasing, gives 1 at zero distance, remains positive for finite real distances and approaches 0 as distance grows. Extremely large synthetic values can underflow to floating-point zero; zero is a valid bounded output. At dC=τ the score is exp(−1), approximately .367879. This point is a decay scale, not a consistency threshold. Larger tau penalizes a given color distance less. No dataset extrema or min-max normalization are used.

The baseline assumption τ=10 is explicitly provisional; τ=5 and τ=20 test scale sensitivity without choosing a winner. The exponential assumes that additive raw-distance increments produce multiplicative similarity reductions. It is a transparent mapping, not a calibrated human judgment, validated just-noticeable-difference model, or universal perceptual scale for mobile screens. The underlying color descriptor is spatially blind and can be dominated by background pixel mass.

### Density

Let fA and fB be saved foreground pixel fractions for A and B. Let eA and eB be saved Canny edge pixel fractions. All four fractions lie in [0,1].

S_foreground(A,B) = 1−|fA−fB|.

Let l=min(eA,eB) and h=max(eA,eB). Provisional relative edge similarity is S_edge,M1(A,B)=l/h when h>0, and 1 when h=0. Both zero gives 1; exactly one zero gives 0. M1 compares relative amounts of detected edges. It needs no smoothing parameter, but can amplify differences at low densities and cannot distinguish arrangements having the same edge count. The earlier experiment found M2 nearly identical to M1 on this pilot; no further edge experiment is launched.

For the preserved sensitivity alternative, S_edge,M0(A,B)=1−|eA−eB|.

S_density(A,B) = (S_foreground(A,B)+S_edge(A,B))/2.

The baseline uses M1 in this equation; only the designated M0 sensitivity configuration substitutes M0. Equal density subweights are an assumption. Foreground coverage errors and missed pale Canny boundaries are not corrected here, and connected components are not semantic UI elements. Canny density is independently extracted; foreground-mask correction does not itself repair Canny detection.

### Layout

For k=0,…,31, let uA,k and uB,k denote the saved row-major occupancies of the four-column, eight-row grid. Each occupancy is the fraction of a grid cell covered by the union of connected-component bounding boxes. Overlapping boxes are counted through their union, not added repeatedly.

dL(A,B) = (1/32) Σk |uA,k−uB,k|.

S_layout(A,B) = 1−dL(A,B).

Here dL is the saved layout mean absolute error (MAE); the sum runs over all 32 cells. Grid definitions and saved boxes remain unchanged. This coarse representation can saturate around large rectangles/keyboards and alias different text, control states or arrangements inside the same occupied envelopes.

### Composite and contributions

S_composite(A,B) = (S_color(A,B)+S_density(A,B)+S_layout(A,B))/3

= S_color(A,B)/3 + S_foreground(A,B)/6 + S_edge(A,B)/6 + S_layout(A,B)/3.

Color, Density and Layout each receive weight 1/3; Foreground and Edge each receive half the Density weight, hence 1/6 overall. Equal grouping avoids introducing optimized preferences without labels and is easy to reproduce. It is not an assertion of optimal weights, independent descriptors, equal empirical variance, or equal perceptual importance.

The exported group contributions are C_color=S_color/3, C_density=S_density/3 and C_layout=S_layout/3. Their sum equals S_composite. Exported sub-contributions C_foreground=S_foreground/6 and C_edge=S_edge/6 sum to C_density; do not add them again to the three group contributions. C denotes an additive term, not a separate similarity or causal attribution. Scores are compensatory: a strong group can offset a weak group.

Each similarity lies in [0,1], so any positive-weight average with weights summing to one also lies in [0,1]. Identical feature inputs have zero color/layout distances, identical fractions and all similarities equal to 1, giving composite 1. Reversing A and B preserves the symmetric distances, absolute differences and min/max ratio, hence the composite is symmetric. Identical descriptors do not imply identical pixels or semantic content. Invalid inputs are rejected, not silently clipped.

## Sensitivity and descriptive calculations

Four fixed configurations are evaluated on the identical pair universe:

| Configuration | Edge | Tau |
|---|---|---:|
| baseline_v1 | M1 | 10 |
| color_tau5 | M1 | 5 |
| color_tau20 | M1 | 20 |
| edge_M0 | M0 | 10 |

For pair i and configuration c, let xi,c denote composite similarity and xi,0 the baseline value. The exported change is Δi,c=xi,c−xi,0. For color-only changes, Δi,c=(exp(−dC/τc)−exp(−dC/10))/3, where τc is the alternative tau. For the M0 edge alternative, Δi,M0=(S_edge,M0−S_edge,M1)/6. All other group terms remain fixed. This isolates the requested modeling changes without optimizing them.

Rank Ri,c is the descending position of pair i under configuration c, with tied scores assigned their average position. Rank shift is Ri,c−Ri,0; negative means movement toward rank 1. Pair tables use global ranks across 709 pairs. The sensitivity summary recalculates ranks within its stated app/type group, so group shifts need not equal global shifts. Maximum tied extrema are represented by the lexicographically last pair in ascending (score,pair ID) order, not by all tied cases.

For a group of n pairs, the mean is μ=(Σi xi)/n and sample standard deviation is s=sqrt(Σi(xi−μ)²/(n−1)); sqrt means square root, with i running over that group's pairs. Minimum and maximum are observed extrema. Quantiles use linear interpolation: for sorted zero-based values x(0),…,x(n−1) and quantile probability p, set t=(n−1)p, j=floor(t), g=t−j and Q(p)=(1−g)x(j)+g x(j+1), returning the last endpoint directly. Floor rounds down. q10/q25/median/q75/q90 use p=.10/.25/.50/.75/.90.

The empirical cumulative distribution is F(z)=(1/n)Σi I(xi≤z), where z is a plotted score and I is 1 if its condition holds and 0 otherwise. Histogram bins have width .025 on [0,1], with the final bin including 1. Histograms show counts; ECDFs show cumulative fractions.

Spearman correlation compares ascending average ranks ri and ti from two configurations: ρ=Σi(ri−r̄)(ti−t̄)/sqrt(Σi(ri−r̄)² Σi(ti−t̄)²), where bars denote mean ranks. Kendall tau-b is (P−Q)/sqrt((P+Q+U)(P+Q+V)), where P and Q count concordant and discordant unordered record comparisons, U counts ties only in the first ranking and V ties only in the second. Concordant means the same relative order, discordant the opposite order. Joint ties are excluded from these counts. These correlations describe ranking sensitivity, not agreement with experts. Mean/max absolute rank shifts summarize |Ri,c−Ri,0|. Mean delta and maximum absolute delta similarly summarize Δi,c and |Δi,c|.

Groups include each application plus pooled ALL, and within_flow/cross_flow/all. They overlap; pairs share screens and applications have unequal pair counts. No independent-sample inference, causal interpretation of flow differences, confidence interval or perceptual-accuracy estimate is made.

## Files, reproduction and interpretation

[composite_scores.csv](composite_scores.csv) has the baseline's 709 rows. [sensitivity_analysis.csv](sensitivity_analysis.csv) has 2,836 rows, including each of four configurations for every pair. Raw color EMD, foreground/edge inputs, layout MAE, both edge formulations, all similarities, additive contributions, metadata and ranks are retained. [composite_summary.csv](composite_summary.csv) has 792 rows: four configurations × six app groups × three type groups × eleven similarity/contribution quantities. [sensitivity_summary.csv](sensitivity_summary.csv) has the 72 configuration/app/type ranking and change summaries.

[Selected pairs](selected_pairs.csv) contain 39 purposive slots representing 32 unique pairs: low/lower-middle/high baseline cases for every app/type group, plus each alternative's global minimum, maximum and largest global rank-shift example. Lower-middle means sorted zero-based index floor((n−1)/2), an actual observed pair, not an interpolated score. Repeated pairs across selection purposes are intentional. The 13 [inspection sheets](inspection_sheets/) are diagnostic examples, not a random evaluation sample or prevalence estimate. Figure labels C/F/E/D/L mean Color/Foreground/Edge/Density/Layout similarities; numbers are rounded for readability, while CSVs retain float precision.

From the project root, using the existing environment:

```sh
.venv/bin/python composite_baseline.py --output /private/tmp/composite-baseline-reproduction
.venv/bin/python -m unittest test_composite_baseline -v
```

Use a fresh output directory. The default is this saved directory; rerunning against it is refused. Reproduction checks compare generated CSVs, configuration, validation hashes and figures byte-for-byte in this environment. These written methodology/validation documents are explanatory artifacts, not generated by the scoring runner. No extra dependencies are installed.

This baseline is suitable as a fixed computational comparator for later controlled graph-method work. Such a comparison should hold visual inputs, pair universe and evaluation protocol fixed while making contextual changes explicit. No graph method is implemented here. A high composite means agreement under these descriptors and modeling choices; **it does not prove visual consistency**, usability, semantic equivalence or agreement with humans. No consistency classification or expert-ground-truth simulation is performed.
