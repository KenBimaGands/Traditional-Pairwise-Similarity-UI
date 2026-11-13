"""Review existing M1 tau configurations; never rerun extraction or scoring."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, rankdata
from composite_baseline import ROOT, OUTPUT, read_csv, write_table, summarize, plt

TAUS=[5,10,20]


def run(output):
    output=Path(output); assets=output/'tau_review_assets'; report=output/'tau_sensitivity_review.md'
    if assets.exists() or report.exists(): raise FileExistsError('Review exists; choose fresh --output')
    protected={p:hashlib.sha256(p.read_bytes()).hexdigest() for folder in
               ['PILOT','results','results_corrected_pilot','results_pairwise_baseline','experiments']
               for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    source=OUTPUT/'sensitivity_analysis.csv'; rows=read_csv(source)
    approved={r['pair_id']:r for r in read_csv(OUTPUT/'composite_scores.csv')}
    original=read_csv(ROOT/'results_pairwise_baseline/pairwise_distances.csv')
    expected={r['screen_a']+'__'+r['screen_b'] for r in original}
    assert len(expected)==len(original)==len(approved)==709 and set(approved)==expected
    data={}
    for tau in TAUS:
        selected=[r for r in rows if float(r['tau'])==tau and r['edge_method']=='M1']
        data[tau]={r['pair_id']:r for r in selected}
        assert len(selected)==len(data[tau])==709 and set(data[tau])==expected
    ids=sorted(expected); fixed=['screen_a','screen_b','app_id','flow_a','flow_b','pair_type','color_emd_distance',
        'foreground_a','foreground_b','edge_a','edge_b','layout_mae','foreground_similarity','edge_similarity',
        'density_similarity','layout_similarity','density_contribution','layout_contribution']
    for pid in ids:
        b=data[10][pid]
        for tau in TAUS:
            r=data[tau][pid]
            assert all(r[k]==b[k] for k in fixed)
            assert r['pair_id']==r['screen_a']+'__'+r['screen_b']
            assert np.isclose(float(r['edge_similarity']),float(r['edge_similarity_M1']),rtol=0,atol=1e-15)
            for k in ['color_similarity','foreground_similarity','edge_similarity','density_similarity','layout_similarity','composite_similarity']:
                assert np.isfinite(float(r[k])) and 0<=float(r[k])<=1
            c=float(r['color_similarity']); d=float(r['color_emd_distance'])
            assert np.isclose(c,np.exp(-d/tau),rtol=0,atol=1e-15)
            assert np.isclose(float(r['density_similarity']),(float(r['foreground_similarity'])+float(r['edge_similarity']))/2,rtol=0,atol=1e-15)
            assert np.isclose(float(r['composite_similarity']),(c+float(r['density_similarity'])+float(r['layout_similarity']))/3,rtol=0,atol=1e-15)
        assert all(approved[pid][k]==b[k] for k in approved[pid])
    groups=['all','within_flow','cross_flow']; metrics=['color_similarity','composite_similarity']
    def values(tau,metric,group='all'):
        return np.array([float(data[tau][pid][metric]) for pid in ids if group=='all' or data[tau][pid]['pair_type']==group])
    summaries=[]
    for tau in TAUS:
        for group in groups:
            for metric in metrics:
                summaries.append(dict(tau=tau,pair_type=group,metric=metric,**summarize(values(tau,metric,group))))
    comparisons=[]; extremes=[]
    for a,b in [(5,10),(20,10),(20,5)]:
        for group in groups:
            for metric in metrics:
                va,vb=values(a,metric,group),values(b,metric,group)
                shift=rankdata(-va)-rankdata(-vb)
                comparisons.append(dict(tau=a,reference_tau=b,pair_type=group,metric=metric,
                    spearman=float(spearmanr(va,vb).statistic),mean_delta=float(np.mean(va-vb)),
                    maximum_absolute_delta=float(np.max(np.abs(va-vb))),
                    mean_absolute_rank_shift=float(np.mean(np.abs(shift))),maximum_absolute_rank_shift=float(np.max(np.abs(shift)))))
        differences={pid:float(data[a][pid]['composite_similarity'])-float(data[b][pid]['composite_similarity']) for pid in ids}
        ranks={t:dict(zip(ids,rankdata(-values(t,'composite_similarity')))) for t in [a,b]}
        ordered=sorted(ids,key=lambda pid:(-abs(differences[pid]),pid))[:5]
        largest_rank=max(ids,key=lambda pid:abs(ranks[a][pid]-ranks[b][pid]))
        for reason,pool in [('largest score difference',ordered),('largest global rank shift',[largest_rank])]:
            for pid in pool:
                r=data[a][pid]
                extremes.append(dict(tau=a,reference_tau=b,selection=reason,pair_id=pid,screen_a=r['screen_a'],screen_b=r['screen_b'],
                    app_id=r['app_id'],pair_type=r['pair_type'],color_emd_distance=float(r['color_emd_distance']),
                    composite_tau=float(r['composite_similarity']),composite_reference=float(data[b][pid]['composite_similarity']),
                    delta=differences[pid],rank_tau=float(ranks[a][pid]),rank_reference=float(ranks[b][pid]),
                    rank_shift=float(ranks[a][pid]-ranks[b][pid])))
    output.mkdir(parents=True,exist_ok=True); assets.mkdir()
    write_table(assets/'summary.csv',summaries); write_table(assets/'rank_changes.csv',comparisons); write_table(assets/'most_affected_pairs.csv',extremes)
    fig,axes=plt.subplots(2,2,figsize=(12,9),layout='constrained')
    for tau in TAUS:
        for i,metric in enumerate(metrics):
            v=values(tau,metric); x=np.sort(v)
            axes[0,i].hist(v,bins=np.linspace(0,1,41),alpha=.4,label=f'tau={tau}')
            axes[1,i].step(x,np.arange(1,len(x)+1)/len(x),where='post',label=f'tau={tau}')
            axes[0,i].set_title(metric.replace('_',' ').title()); axes[0,i].set_ylabel('Pair count')
            axes[1,i].set_ylabel('Empirical cumulative fraction')
    for ax in axes.flat: ax.set_xlim(0,1); ax.set_xlabel('Similarity'); ax.legend()
    fig.savefig(assets/'distributions.png',dpi=140); plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    for tau in TAUS:
        for group,style in [('within_flow','-'),('cross_flow','--')]:
            x=np.sort(values(tau,'composite_similarity',group))
            axes[0].step(x,np.arange(1,len(x)+1)/len(x),where='post',linestyle=style,label=f'{tau}: {group}')
    axes[0].set(xlim=(0,1),xlabel='Composite similarity',ylabel='Empirical cumulative fraction'); axes[0].legend(fontsize=8)
    for tau in [5,20]:
        axes[1].scatter([float(data[tau][pid]['color_emd_distance']) for pid in ids],
                         values(tau,'composite_similarity')-values(10,'composite_similarity'),s=10,alpha=.5,label=f'{tau} minus 10')
    axes[1].set(xlabel='Saved color EMD distance',ylabel='Composite change'); axes[1].legend()
    fig.savefig(assets/'flow_and_distance_effects.png',dpi=140); plt.close(fig)
    def table(items,columns):
        return '\n'.join(['| '+' | '.join(label for key,label in columns)+' |',
                         '| '+' | '.join('---' for _ in columns)+' |']+
                         ['| '+' | '.join(f'{r[k]:.6f}' if isinstance(r[k],float) else str(r[k]) for k,_ in columns)+' |' for r in items])
    composite=[r for r in summaries if r['metric']=='composite_similarity' and r['pair_type']=='all']
    color=[r for r in summaries if r['metric']=='color_similarity' and r['pair_type']=='all']
    ranks=[r for r in comparisons if r['metric']=='composite_similarity' and r['pair_type']=='all']
    flow=[r for r in summaries if r['metric']=='composite_similarity' and r['pair_type']!='all']
    most=[r for r in extremes if r['selection']=='largest score difference'][::5]
    text=f'''# Color normalization tau sensitivity review

**Decision: retain τ=10 as a provisional baseline.** All three requested M1 configurations were already present and numerically coherent. No missing configurations were calculated, and no extraction, edge experiment, color transport or baseline scoring run was launched. The review summarizes existing saved results; formula evaluation is used only to check them.

## Scope and validation

Read `sensitivity_analysis.csv`, `composite_scores.csv`, `configuration.json` and the existing `validation_report.md`. Reviewed the same 709 unique within-application pairs: 411 within-flow and 298 cross-flow. Pair IDs match the original pairwise universe and approved composite table. Each tau configuration has exactly one record per pair; tau=10 matches every baseline column exactly. M0 rows are excluded.

Across τ=5,10,20, raw color EMD, foreground/edge fractions, M1 edge similarity, Density, Layout, identifiers and non-color contributions are fixed. Saved density aggregation and composite arithmetic agree with the equal-weight formulas within absolute tolerance 10⁻¹⁵. All similarity outputs are finite in [0,1]. These numerical checks do not establish perceptual validity. Source hashes and historical-file preservation checks are in [checks.json](tau_review_assets/checks.json).

## Composite distributions

{table(composite,[('tau','τ'),('count','Pairs'),('mean','Mean'),('median','Median'),('minimum','Min'),('maximum','Max'),('std_sample','Sample SD')])}

Reducing τ from 10 to 5 lowers the mean by .049339 and the median from .772447 to .704679. Increasing it to 20 raises the mean by .038408 and median to .812025. Across τ=5 to 20, the mean changes by .087746. These are material score-scale effects, not grounds to prefer the highest-scoring configuration.

## Color similarity distributions

{table(color,[('tau','τ'),('mean','Mean'),('median','Median'),('minimum','Min'),('maximum','Max'),('std_sample','Sample SD'),('q10','q10'),('q25','q25'),('q75','q75'),('q90','q90')])}

Larger tau compresses a given distance penalty toward one. Background-dominated palettes and spatially different screenshots with similar color distributions remain descriptor limitations under every tau. Full statistics for Color and Composite by pair type are in [summary.csv](tau_review_assets/summary.csv).

![Color and composite histograms and ECDFs](tau_review_assets/distributions.png)

The plots use fixed [0,1] similarity axes and .025-wide histogram bins. Histogram vertical scales differ between Color and Composite; they count pairs, not accuracy.

## Rankings

{table(ranks,[('tau','τ'),('reference_tau','Reference τ'),('spearman','Composite Spearman'),('mean_absolute_rank_shift','Mean absolute rank shift'),('maximum_absolute_rank_shift','Max rank shift'),('maximum_absolute_delta','Max absolute score change')])}

Global rankings are strongly correlated but not identical. Relative to tau=10, average absolute shifts are about 19 places for tau=5 and 17 for tau=20, with maxima of 75 and 68 among 709 positions. Across tau=5 and 20, the larger ranking changes are reported above. Thus overall order is fairly stable while individual positions remain sensitive; no statistical/perceptual cutoff is assigned to “substantial.” In exact arithmetic, the strictly monotone color mapping preserves raw-distance ordering. Stored floating-point Color Spearman correlations are approximately 0.99999998–0.99999999 pooled, and 1 within each pair type; tiny differences in rounded ties cause maximum average-rank changes of .5. This is numerical tie behavior, not meaningful color-order discrimination. Composite ranks can change because the unchanged Density and Layout terms trade off against the altered Color term. [rank_changes.csv](tau_review_assets/rank_changes.csv) also reports each pair type.

## Most affected pairs

Largest absolute score change for each comparison (the first tau minus the reference tau):

{table(most,[('tau','τ'),('reference_tau','Reference τ'),('screen_a','Screen A'),('screen_b','Screen B'),('color_emd_distance','Raw color EMD'),('composite_tau','Composite'),('composite_reference','Reference composite'),('delta','Change')])}

[most_affected_pairs.csv](tau_review_assets/most_affected_pairs.csv) includes the five largest score changes and a largest-rank-shift example for each comparison. These are purposive numerical diagnostics, not a random sample or human judgments. Score-shift extremes need not coincide with rank-shift extremes.

APP03-FLOW02-S01 / APP03-FLOW02-S06 has the largest tau=5 versus 10 rank movement (−75) and tau=20 versus 10 movement (+68): scores .770207, .797390 and .811969 for tau=5,10,20, respectively. Existing original-image inspection sheets [page 11](inspection_sheets/page_11.png) and [page 12](inspection_sheets/page_12.png) show this welcome/login versus password-form pair; those sheets are reused, not regenerated. This numerical review does not collect new expert labels or independently re-review every screenshot.

## Within-flow versus cross-flow

{table(flow,[('tau','τ'),('pair_type','Pair type'),('count','Pairs'),('mean','Mean'),('median','Median'),('minimum','Min'),('maximum','Max'),('std_sample','Sample SD')])}

![Flow distributions and raw-distance sensitivity](tau_review_assets/flow_and_distance_effects.png)

Both groups move in the same direction as tau increases. Cross-flow mean changes are −.054492 at tau=5 and +.041768 at tau=20 relative to 10; within-flow changes are −.045602 and +.035972. Different raw-color-distance compositions explain different aggregate shifts; flow membership is not a score input and is not a causal explanation. These overlapping pairs share screens, and applications contribute unequal pair counts. Descriptions do not constitute independent-sample inference, consistency comparisons or accuracy estimates.

## Formulas and notation

A and B denote screenshots. d=dC(A,B)≥0 is their saved weighted CIEDE2000-EMD color distance. τ>0 is the decay scale in the same distance units as d; exp denotes the natural exponential and log its inverse. Color similarity is Cτ=exp(−d/τ). At d=τ it equals exp(−1), approximately .367879, which defines a scale, not a consistency threshold. No dataset min-max normalization is used.

Let fA,fB be saved foreground fractions and eA,eB the saved Canny edge fractions. F=1−|fA−fB|, where vertical bars denote absolute value. E=min(eA,eB)/max(eA,eB) if the maximum is positive; otherwise E=1. Exactly one zero gives E=0. Density similarity is D=(F+E)/2. Let uA,k,uB,k be saved layout union occupancies for cell k=0,…,31 of the four-column/eight-row grid. Layout similarity is L=1−(Σk|uA,k−uB,k|)/32, where Σk sums over those cells. The composite is Xτ=(Cτ+D+L)/3=Cτ/3+F/6+E/6+L/3. Thus only the color contribution changes in this review.

For positive tau values a and b, the score difference is Δ(a,b)=Xa−Xb=(exp(−d/a)−exp(−d/b))/3. Keeping d fixed, the rate of change with tau is ∂Xτ/∂τ=d exp(−d/τ)/(3τ²)≥0; ∂ denotes differentiation. Scores must increase or remain unchanged when tau rises, but higher scores are not evidence of improved modeling. For a<b, the largest possible absolute difference over nonnegative d occurs at d*=ab log(b/a)/(b−a); the asterisk denotes the maximizing distance, not an observed annotation. This follows by setting the derivative of the difference with respect to d to zero. It approaches zero at d=0 and as d grows without bound.

For 5 versus 10, d*≈6.931472; for 10 versus 20, d*≈13.862944. Each has theoretical maximum composite change 1/12≈.083333. For 5 versus 20, d*≈9.241962. The observed extreme pairs lie near these distances. Consequently, intermediate raw color distances can be more tau-sensitive than the largest EMD values. Sensitivity does not identify an optimal tau.

For n pairs with score xi, mean μ=(Σi xi)/n and sample standard deviation s=sqrt(Σi(xi−μ)²/(n−1)), where i indexes the group, Σi sums over it and sqrt denotes square root. Minimum and maximum are observed extrema. Quantiles use NumPy linear interpolation: for ascending zero-based values x(0),…,x(n−1), let t=(n−1)p, j=floor(t), g=t−j and Q(p)=(1−g)x(j)+g x(j+1), returning the final endpoint directly. Floor rounds down. Median uses p=.5; q10,q25,q75,q90 use p=.10,.25,.75,.90.

The empirical cumulative distribution at z is H(z)=(1/n)Σi I(xi≤z), with I equal to 1 if its condition holds and 0 otherwise. Histograms use the fixed bins described above, with the final bin including 1. Descending rank Ri,τ gives the position of pair i for tau τ, assigning average positions to ties; a negative rank change means movement toward rank 1. Within-type rank summaries recalculate ranks inside their own group. Spearman correlation is the Pearson correlation of average ascending ranks ri and ti: ρ=Σi(ri−r̄)(ti−t̄)/sqrt(Σi(ri−r̄)²Σi(ti−t̄)²), where bars denote mean ranks. Rank direction reversal in both inputs leaves this correlation unchanged. No p-values or independence claims are used.

## Findings and decision

1. **Score sensitivity:** tau materially shifts absolute color/composite values, with a bounded per-pair effect under these fixed weights. It does not change extracted features.
2. **Ranking sensitivity:** high Spearman correlations show broadly stable ordering; changes of up to 75/68 positions relative to 10 remain meaningful to disclose. No claim of perceptual ranking improvement follows.
3. **Affected pairs:** intermediate raw color EMD values produce the largest score shifts; largest rank shifts additionally depend on Density, Layout and neighboring pairs' scores. The linked pair table identifies the actual screens.
4. **Retain τ=10 provisionally:** no serious numerical or methodological inconsistency was detected in the existing three configurations. Tau=10 remains a transparent middle sensitivity setting, not an empirically optimal or perceptually validated calibration. Do not choose tau=20 because it yields higher scores. Final calibration should use independent expert annotations and a stated evaluation protocol.

Equal weights remain fixed and unoptimized. Descriptor errors, palette background dominance, scalar-density aliasing, layout saturation and compensatory averaging remain. High visual similarity does not prove consistency, usability or semantic equivalence. No dataset, prior result, graph method, threshold, classification or expert-ground-truth simulation was changed or introduced.

## Reproduce this review

From the project root: `.venv/bin/python review_tau_sensitivity.py --output /private/tmp/tau-review-reproduction`, choosing a fresh destination. The script reads the saved configurations, validates formulas and writes descriptive tables/figures/report; it does not recompute missing feature records. Outputs in the saved review are protected from overwriting.
'''
    report.write_text(text)
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in protected.items())
    checks=dict(saved_tau_values=TAUS,pairs_per_tau=709,within_flow=411,cross_flow=298,
                all_other_parameters_fixed=True,formula_absolute_tolerance=1e-15,
                baseline_matches_exactly=True,original_files_unchanged=True,
                source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                reviewer_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (assets/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=OUTPUT)
    run(parser.parse_args().output)
