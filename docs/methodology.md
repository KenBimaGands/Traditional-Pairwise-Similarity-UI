# Methodology: traditional visual-only analysis

This package preserves the implemented formulas and decisions. Graphs, navigation context, consistency thresholds, role matching and expert-label simulation are excluded. Numerical validity and reproducibility do not establish perceptual validity.

## Image features and preprocessing

Let I be the processed RGB image, W its width, H its height, N=WH its pixel count, and p=(x,y) a pixel location. Inputs are decoded, EXIF-oriented, alpha-composited onto white and aspect-preserving Lanczos-resized within 512×512, without upscaling or padding. The full processed image is used; footer/device chrome is not silently cropped.

For unique RGB vector u_j with count n_j, weighted K-Means minimizes J=Σ_j n_j||u_j−μ_(a_j)||². J is the squared RGB objective; μ_k is centroid k, a_j the cluster assigned to vector j, ||·|| Euclidean norm, and Σ summation. K=min(5,U), where U is the number of unique vectors. Seed 42, ten K-Means++ initializations and Lloyd iterations are fixed. Cluster mass q_k=(Σ_(j:a_j=k) n_j)/N sums to one. Float RGB centroids are converted to standard D65 CIELAB coordinates (L* lightness and signed a*,b* chromatic axes), not encoded 8-bit Lab. The original algorithm remains weighted RGB clustering, not Lab clustering.

The baseline background vector B is the median RGB of the dominant quantized perimeter-color bin (bin width 16). Mask M(p)=1 when ||I(p)−B||>25, otherwise 0. Foreground coverage f=(Σ_p M(p))/N. The frozen correction can suppress one large four-connected smooth region touching both side borders, subject to side-gradient/coverage/area gates defined in `correct.py`. If R(p) indicates the selected region, M′(p)=M(p)(1−R(p)); otherwise M′=M. Corrected coverage uses M′. No new foreground pixels are added. Palette and Canny outputs are unchanged. The function defaults disabled; the approved pilot runner enables it.

Let E(p) be the binary edge map from independent grayscale conversion, 5×5 Gaussian blur with sigma=1 pixel and Canny thresholds 50/150. Edge fraction e=(Σ_p E(p))/N. Foreground components use eight-connectivity and minimum area 12 for retained boxes; small mask components still count toward coverage. For grid cell G_k and union R_box of retained component rectangles, occupancy u_k=area(G_k∩R_box)/area(G_k), where area counts pixels and ∩ denotes intersection. k=0,…,31 follows row-major order across four columns and eight rows. Union avoids double-counting overlapping boxes. Components are not semantic UI elements.

## Traditional pairwise descriptors

A and B denote screenshots. Comparisons include every unordered pair within the same application, with no self-pairs or reversed duplicates. For n_a screens in application a, pair count is n_a(n_a−1)/2. Summing across the five applications gives 709. Flow labels group descriptions only.

For palettes with CIELAB centroids c_i,d_j and normalized nonnegative masses p_i,q_j, let C_ij=ΔE_00(c_i,d_j), the standard CIEDE2000 color difference with viewing-condition factors k_L=k_C=k_H=1. i and j index source/target centroids. ΔE_00 denotes the established library formula, not a new normalization. Its lightness/chroma/hue corrections and analytic reference cases are documented in `runtime/PAIRWISE_METHODS.md` and tested in `test_pairwise_baseline.py`.

Raw color distance is dC(A,B)=min_T Σ_iΣ_j T_ij C_ij, subject to T_ij≥0, Σ_j T_ij=p_i, Σ_i T_ij=q_j. T_ij is transported pixel mass; min chooses the feasible transport matrix with smallest cost; ≥ means at least. Both palette masses sum to one. The existing SciPy linear program uses highs-ds with no regularization, dataset min-max scaling or color-cost division. Scalar raw EMD is retained.

Foreground distance dF=|fA−fB| and original edge distance dE=|eA−eB|, where vertical bars mean absolute value and fA/fB/eA/eB are saved fractions. Layout MAE dL=(Σ_(k=0)^31 |uA,k−uB,k|)/32 compares saved occupancies. MAE means mean absolute error. Original pairwise similarities are 1−dF, 1−dE and 1−dL. This stage has no color similarity column and retains original M0 edge for reproducibility.

## Edge experiment and provisional selection

Let l=min(eA,eB) and h=max(eA,eB). Experimental formulations are:

- M0: S0=1−|eA−eB|.
- M1: S1=l/h when h>0, otherwise 1. Both zero gives 1; exactly one zero gives 0.
- M2: S2=exp(−|log((eA+ε)/(eB+ε))|)=(l+ε)/(h+ε), with positive smoothing ε. exp is the natural exponential; log its inverse.

M2 is a smoothed M1, not an independent descriptor. For strictly positive inputs S2 approaches S1 as ε approaches zero. The chosen ε=10⁻⁵ approximates one processed-pixel fraction; the documented sensitivity grid is not optimized for spread. Seed 42 samples 24 random pairs balanced by pair type/application, separately from purposive extremes. Saved diagnostic edge panels are reused, not redetected. Prior perceptual evidence was inconclusive. M1 was subsequently chosen provisionally for simplicity and relative interpretation, not as an accuracy claim.

## Composite baseline and tau

Color similarity C_τ=exp(−dC/τ), with τ>0 a decay scale in the same units as dC. At dC=τ it equals exp(−1), approximately .367879; this is not a consistency threshold. The mapping assumes additive color-distance increments yield multiplicative similarity reductions. It is not calibrated to humans or normalized by dataset extremes.

Foreground F=1−dF, provisional Edge E=S1, Density D=(F+E)/2 and Layout L=1−dL. Composite X_τ=(C_τ+D+L)/3=C_τ/3+F/6+E/6+L/3. Thus Color/Density/Layout each have weight 1/3, with equal Density subweights. Equal grouping is transparent, not empirically optimal or proof of independent/equally informative features. Group additive contributions sum to the composite; foreground/edge sub-contributions already belong to Density and must not be counted twice.

Baseline v1 uses τ=10 and M1. Fixed sensitivities use M1 with τ=5/20 and M0 with τ=10. All similarities are finite in [0,1]; the mean of bounded terms stays bounded. Identical descriptors yield 1; symmetric distances and min/max ratios preserve screenshot reversal symmetry. High composite can conceal a weak feature because averaging is compensatory.

Tau review reads the three existing M1 configurations. For positive scales a,b, pair score change is Δ(a,b)=X_a−X_b=(exp(−dC/a)−exp(−dC/b))/3. The subscript here identifies a tau setting, not screenshot A. Keeping dC fixed, ∂X_τ/∂τ=dC exp(−dC/τ)/(3τ²)≥0; ∂ denotes a derivative. Larger scores under larger tau are mechanically expected, not evidence of improvement. For a<b the largest absolute effect over nonnegative distance occurs at d*=ab log(b/a)/(b−a), where * marks the maximizing distance, not an expert label. Intermediate distances can therefore be more affected than the largest distances.

The saved mean composite is .699146/.748485/.786893 at τ=5/10/20. Their medians are .704679/.772447/.812025. Spearman against τ=10 is .992927 for 5 and .993936 for 20, with maximum global rank shifts 75 and 68. These are descriptive sensitivities, not evidence to select the highest score. Retain τ=10 provisionally; final calibration requires independent expert annotations.

## Diagnostic statistics and notation

For n records with values x_i, mean μ=Σ_i x_i/n and sample standard deviation s=sqrt(Σ_i(x_i−μ)²/(n−1)); sqrt denotes square root. Extrema are observed min/max. Quantiles use NumPy linear interpolation over sorted values: t=(n−1)p, j=floor(t), g=t−j, Q(p)=(1−g)x_(j)+g x_(j+1), with the last endpoint returned directly. Here p is quantile probability, floor rounds down, and sorted indices are zero-based. Median uses p=.5; q10/q25/q75/q90 use .10/.25/.75/.90.

Empirical cumulative fraction H(z)=Σ_i I(x_i≤z)/n, where I is 1 when its condition holds and 0 otherwise, and z a plotted value. Spearman is Pearson correlation of average tied ranks: ρ=Σ_i(r_i−r̄)(t_i−t̄)/sqrt(Σ_i(r_i−r̄)²Σ_i(t_i−t̄)²), where r_i,t_i rank the two configurations and bars denote their mean ranks. Descending rank changes are alternative minus reference; negative moves toward rank 1. Kendall tau-b, tie tolerances and full case-specific notation remain in the frozen edge/composite reports shipped under runtime. There are no new hypothesis tests or independent-pair confidence intervals.

## Interpretation boundaries

Background mass dominates some palettes; scalar foreground/edge amounts alias different layouts; Canny misses some pale boundaries and includes inherited footer/frame edges; rectangle occupancy can saturate. None of these limitations is removed by composite scaling. Pair records share screenshots and have unequal application representation, so within/cross-flow distributions are descriptive rather than causal or independent samples. No percentage accuracy, expert agreement, consistency threshold or semantic classification is inferred. Historical reports copied into recomputations are marked as prior interpretation. Every newly generated visual requires actual inspection before claiming a new visual-quality finding.
