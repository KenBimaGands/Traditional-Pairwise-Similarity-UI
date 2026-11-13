"""Controlled edge-metric experiment; reads saved features and rendered diagnostics only."""
import argparse
import csv
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/thesis-edge-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.stats import spearmanr, kendalltau, rankdata
from PIL import Image, ImageDraw, ImageFont
from matplotlib.font_manager import findfont
from pairwise_baseline import read_csv, write_table, IDENTIFIERS

HERE = Path(__file__).resolve().parent
EPSILON = 1e-5
EPSILONS = [1e-8, 1e-6, 1e-5, 1e-4, 1e-3]
SEED = 42
METHODS = ['M0', 'M1', 'M2']


def scores(a, b, epsilon=EPSILON):
    """Return absolute, relative and smoothed relative similarities."""
    a, b = np.broadcast_arrays(np.asarray(a, float), np.asarray(b, float))
    if epsilon <= 0 or not np.isfinite(epsilon):
        raise ValueError('epsilon must be finite and positive')
    if not (np.isfinite(a).all() and np.isfinite(b).all() and
            ((a >= 0) & (a <= 1) & (b >= 0) & (b <= 1)).all()):
        raise ValueError('edge fractions must be finite and in [0,1]')
    low, high = np.minimum(a,b), np.maximum(a,b)
    relative = np.divide(low, high, out=np.ones_like(high), where=high > 0)
    return np.stack([1-np.abs(a-b), relative, (low+epsilon)/(high+epsilon)], axis=-1)


def protected_hashes():
    # Include prior experiments but exclude this new experiment and Python bytecode.
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ['PILOT','results','results_corrected_pilot','results_pairwise_baseline',
                           'pairwise_investigation','experiments']
            for p in (ROOT/folder).rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and not p.is_relative_to(HERE)}


def load():
    metadata_rows = read_csv(ROOT/'PILOT/screenshots/screens.csv')
    metadata = {r['screen_id']:dict(r,index=i) for i,r in enumerate(metadata_rows)}
    features_rows = read_csv(ROOT/'results_corrected_pilot/visual_features.csv')
    features = {r['screen_id']:r for r in features_rows}
    assert len(metadata)==len(metadata_rows)==len(features)==len(features_rows)==82
    assert set(features)==set(metadata)
    old = {r['screen_id']:r for r in read_csv(ROOT/'results/visual_features.csv')}
    for sid,f in features.items():
        assert f['status']=='ok' and float(f['edge_density'])==float(old[sid]['edge_density'])
        assert (f['width'],f['height'])==(old[sid]['width'],old[sid]['height'])
    baseline = read_csv(ROOT/'results_pairwise_baseline/pairwise_similarities.csv')
    expected = {tuple(sorted((a,b))) for a,b in itertools.combinations(sorted(metadata),2)
                if metadata[a]['app_id']==metadata[b]['app_id']}
    assert len(expected)==len(baseline)==709
    seen=set(); rows=[]
    for r in baseline:
        a,b=r['screen_a'],r['screen_b']; key=(a,b)
        assert key in expected and key not in seen and a<b
        seen.add(key)
        assert r['app_id']==metadata[a]['app_id']==metadata[b]['app_id']
        assert r['flow_a']==metadata[a]['flow_id'] and r['flow_b']==metadata[b]['flow_id']
        assert r['pair_type']==('within_flow' if r['flow_a']==r['flow_b'] else 'cross_flow')
        ea,eb=[float(features[s]['edge_density']) for s in key]
        values=scores(ea,eb)
        assert values[0]==float(r['edge_similarity'])
        rows.append({**{k:r[k] for k in IDENTIFIERS},'pair_id':f'{a}__{b}',
                     'edge_a':ea,'edge_b':eb,'absolute_difference':abs(ea-eb),
                     **dict(zip(METHODS,values.tolist())),
                     'M1_minus_M0':float(values[1]-values[0]),
                     'M2_minus_M0':float(values[2]-values[0]),
                     'M2_minus_M1':float(values[2]-values[1])})
    assert seen==expected
    return rows,metadata,features


def sample_pairs(rows):
    rng=np.random.default_rng(SEED); selected=[]; allocation=[]
    for kind in ['within_flow','cross_flow']:
        pools={app:sorted([r for r in rows if r['pair_type']==kind and r['app_id']==app],
                          key=lambda r:r['pair_id']) for app in sorted({r['app_id'] for r in rows})}
        order=rng.permutation(list(pools)).tolist(); counts=dict.fromkeys(order,0)
        target=min(12,sum(map(len,pools.values())))
        # Round-robin allocation keeps applications balanced without using any scores.
        while sum(counts.values())<target:
            for app in order:
                if counts[app]<len(pools[app]) and sum(counts.values())<target:
                    counts[app]+=1
        for app in sorted(pools):
            indices=rng.choice(len(pools[app]),size=counts[app],replace=False)
            selected.extend(pools[app][int(i)] for i in sorted(indices))
            allocation.append(dict(pair_type=kind,app_id=app,eligible=len(pools[app]),selected=counts[app]))
    return selected,allocation


def stats(values):
    a=np.asarray(values,float)
    return dict(count=len(a),minimum=a.min(),maximum=a.max(),mean=a.mean(),median=np.median(a),
                std_sample=a.std(ddof=1),q10=np.quantile(a,.1),q25=np.quantile(a,.25),
                q75=np.quantile(a,.75),q90=np.quantile(a,.9),unique_scores=len(np.unique(a)))


def sheet(path, rows, metadata, label):
    canvas=Image.new('RGB',(1400,len(rows)*680),'white'); draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype(findfont('DejaVu Sans Mono'),16)
    for i,r in enumerate(rows):
        y=i*680
        lines=[f"{label} | {r['app_id']} | {r['pair_type']}",
               f"A: {r['screen_a']}    B: {r['screen_b']}",
               f"eA={r['edge_a']:.9f} eB={r['edge_b']:.9f} |diff|={r['absolute_difference']:.9f}",
               f"M0={r['M0']:.6f} M1={r['M1']:.6f} M2={r['M2']:.6f} (epsilon={EPSILON:g})",
               f"M1-M0={r['M1_minus_M0']:+.6f} M2-M0={r['M2_minus_M0']:+.6f} M2-M1={r['M2_minus_M1']:+.6f}"]
        for j,line in enumerate(lines): draw.text((12,y+6+j*22),line,font=font,fill='black')
        for col,(sid,edge) in enumerate([(r['screen_a'],False),(r['screen_a'],True),
                                          (r['screen_b'],False),(r['screen_b'],True)]):
            m=metadata[sid]
            if edge:
                with Image.open(ROOT/'results/visualizations'/f"{m['index']:04d}.png") as im:
                    assert im.size==(1200,1320)
                    # shortcut: crop the existing fixed-layout diagnostic panel; revisit if its renderer changes.
                    im=im.convert('RGB').crop((15,695,395,1305))
            else:
                p=(ROOT/'PILOT/screenshots'/m['image_path']).resolve()
                assert p.is_relative_to((ROOT/'PILOT/screenshots').resolve())
                with Image.open(p) as source: im=source.convert('RGB')
            im.thumbnail((330,520),Image.Resampling.LANCZOS)
            x=col*350+(350-im.width)//2
            canvas.paste(im,(x,y+148))
            draw.text((col*350+15,y+120),('A' if col<2 else 'B')+(' saved edges' if edge else ' original'),font=font,fill='black')
    canvas.save(path)


def run(output):
    if (output/'edge_similarity_comparison.csv').exists():
        raise FileExistsError('Use a fresh --output directory; existing results are preserved')
    before=protected_hashes()
    rows,metadata,features=load(); sample,allocation=sample_pairs(rows)
    assert sample==sample_pairs(rows)[0] and len({r['pair_id'] for r in sample})==len(sample)==24
    output.mkdir(parents=True,exist_ok=True)
    write_table(output/'edge_similarity_comparison.csv',rows)
    write_table(output/'random_pairs.csv',sample)
    write_table(output/'sampling_allocation.csv',allocation)
    configuration=dict(seed=SEED,epsilon=EPSILON,epsilon_values=EPSILONS,
                       feature_source='results_corrected_pilot/visual_features.csv',
                       edge_map_source='results/visualizations; saved rendered Canny panels; no Canny rerun',
                       sampling='12 per pair_type, balanced round-robin seeded application order; random without replacement within app/type; sorted ID pools; no scores used',
                       requested_per_stratum=12,actual_per_stratum={k:sum(r['pair_type']==k for r in sample) for k in ['within_flow','cross_flow']},
                       shortfall_per_stratum={k:max(0,12-sum(r['pair_type']==k for r in sample)) for k in ['within_flow','cross_flow']},
                       near_tolerances=[1e-12,1e-6],numpy=np.__version__,scipy=scipy.__version__,
                       source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (output/'configuration.json').write_text(json.dumps(configuration,indent=2)+'\n')
    statistics=[]
    for app in ['ALL']+sorted({r['app_id'] for r in rows}):
        for kind in ['all','within_flow','cross_flow']:
            group=[r for r in rows if (app=='ALL' or r['app_id']==app) and (kind=='all' or r['pair_type']==kind)]
            for method in METHODS: statistics.append(dict(app_id=app,pair_type=kind,method=method,**stats([r[method] for r in group])))
    write_table(output/'metric_statistics.csv',statistics)
    values=np.array([[r[m] for m in METHODS] for r in rows]); correlations=[]; ties=[]
    for i,j in itertools.combinations(range(3),2):
        correlations.append(dict(method_a=METHODS[i],method_b=METHODS[j],
                                 spearman=float(spearmanr(values[:,i],values[:,j]).statistic),
                                 kendall_tau_b=float(kendalltau(values[:,i],values[:,j]).statistic)))
    write_table(output/'rank_correlations.csv',correlations)
    for i,m in enumerate(METHODS):
        differences=np.abs(values[:,i,None]-values[None,:,i])[np.triu_indices(len(rows),1)]
        for tolerance in [0,1e-12,1e-6]:
            ties.append(dict(method=m,tolerance=tolerance,score_comparisons=len(differences),
                             tied_comparisons=int((differences<=tolerance).sum()),
                             repeated_score_records=len(rows)-len(np.unique(values[:,i]))))
    write_table(output/'score_ties.csv',ties)
    a=np.array([r['edge_a'] for r in rows]); b=np.array([r['edge_b'] for r in rows]); sensitivities=[]
    for eps in EPSILONS:
        s=scores(a,b,eps)[:,2]
        sensitivities.append(dict(epsilon=eps,**stats(s),max_change_from_M1=float(np.max(s-values[:,1])),
                                  mean_change_from_M1=float(np.mean(s-values[:,1])),
                                  spearman_M1=float(spearmanr(s,values[:,1]).statistic),
                                  max_rank_shift_M1=float(np.max(np.abs(rankdata(s)-rankdata(values[:,1]))))))
    write_table(output/'epsilon_sensitivity.csv',sensitivities)
    sensitivity=np.ptp(np.array([scores(a,b,e)[:,2] for e in EPSILONS]),axis=0)
    order=sorted(rows,key=lambda r:(r['absolute_difference'],r['pair_id']))
    choices=[('minimum_density_difference',order[0]),('median_density_difference',order[len(order)//2]),
             ('maximum_density_difference',order[-1]),
             ('largest_M0_M1_gap',max(rows,key=lambda r:abs(r['M1_minus_M0']))),
             ('largest_epsilon_sensitivity',rows[int(np.argmax(sensitivity))])]
    diagnostics=[dict(r,selection=label,epsilon_score_range=float(sensitivity[rows.index(r)]),
                      also_in_random_sample=r['pair_id'] in {s['pair_id'] for s in sample}) for label,r in choices]
    (output/'diagnostic_cases').mkdir(exist_ok=True)
    write_table(output/'diagnostic_cases/selected_pairs.csv',diagnostics)
    for i,r in enumerate(diagnostics): sheet(output/f'diagnostic_cases/{i+1:02d}_{r["selection"]}.png',[r],metadata,'PURPOSIVE: '+r['selection'])
    (output/'visual_inspection').mkdir(exist_ok=True)
    for i in range(0,len(sample),3): sheet(output/f'visual_inspection/page_{i//3+1:02d}.png',sample[i:i+3],metadata,'RANDOM SAMPLE')
    fig,axes=plt.subplots(2,3,figsize=(15,8),layout='constrained')
    for i,m in enumerate(METHODS):
        for kind,color in [('within_flow','tab:blue'),('cross_flow','tab:orange')]:
            v=np.array([r[m] for r in rows if r['pair_type']==kind]); x=np.sort(v)
            axes[0,i].hist(v,bins=np.linspace(0,1,41),alpha=.5,label=kind,color=color)
            axes[1,i].step(x,np.arange(1,len(x)+1)/len(x),where='post',label=kind,color=color)
        axes[0,i].set(title=m,ylabel='Pair count',xlim=(0,1))
        axes[1,i].set(xlabel='Similarity',ylabel='Empirical cumulative fraction',xlim=(0,1),ylim=(0,1)); axes[0,i].legend()
    fig.savefig(output/'distributions.png',dpi=140); plt.close(fig)
    assert np.array_equal(scores(a,b),scores(b,a))
    assert np.isfinite(values).all() and ((values>=0)&(values<=1)).all()
    assert np.allclose(scores(a,b,1e-14)[:,2],values[:,1],atol=2e-12,rtol=0)
    after=protected_hashes(); assert before==after,'Protected inputs changed'
    (output/'protected_sha256.json').write_text(json.dumps(before,indent=2,sort_keys=True)+'\n')
    checks=dict(screens=82,pairs=709,within_flow=411,cross_flow=298,random_pairs=24,
                baseline_M0_exact=True,symmetry=True,bounds=True,positive_epsilon_limit=True,
                random_sample_reproduced=True,original_edge_maps_density_and_dimensions_match=True,
                protected_files_unchanged=True)
    (output/'validation_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=HERE)
    run(parser.parse_args().output.resolve())
