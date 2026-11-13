"""Traditional visual-only composite from approved saved pairwise descriptors."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/thesis-edge-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.stats import rankdata, spearmanr, kendalltau
from PIL import Image, ImageDraw, ImageFont
from matplotlib.font_manager import findfont
from pairwise_baseline import ROOT, IDENTIFIERS, read_csv, indexed, load_features, write_table

OUTPUT = ROOT/'results/composite_baseline_v1'
CONFIGS = [('baseline_v1',10,'M1'),('color_tau5',5,'M1'),
           ('color_tau20',20,'M1'),('edge_M0',10,'M0')]
SIMILARITIES = ['color_similarity','foreground_similarity','edge_similarity',
                'density_similarity','layout_similarity','composite_similarity']
CONTRIBUTIONS = ['color_contribution','density_contribution','layout_contribution',
                 'foreground_contribution','edge_contribution']


def score(color_emd, foreground_a, foreground_b, edge_a, edge_b, layout_mae, tau=10, edge_method='M1'):
    """Compose bounded similarities, rejecting invalid saved inputs rather than clipping."""
    bounded=np.asarray([foreground_a,foreground_b,edge_a,edge_b,layout_mae],float)
    if not np.isfinite(bounded).all() or np.any((bounded<0)|(bounded>1)):
        raise ValueError('Fractions and layout MAE must be finite in [0,1]')
    if not np.isfinite(color_emd) or color_emd<0 or not np.isfinite(tau) or tau<=0:
        raise ValueError('Color distance must be finite/nonnegative; tau finite/positive')
    if edge_method not in ['M0','M1']: raise ValueError('Unknown edge formulation')
    high=max(edge_a,edge_b)
    edge_m0=1-abs(edge_a-edge_b)
    edge_m1=min(edge_a,edge_b)/high if high else 1.
    color=float(np.exp(-color_emd/tau))
    foreground=1-abs(foreground_a-foreground_b)
    edge=edge_m1 if edge_method=='M1' else edge_m0
    density=(foreground+edge)/2
    layout=1-layout_mae
    composite=(color+density+layout)/3
    return dict(color_similarity=color,foreground_similarity=foreground,edge_similarity=edge,
                edge_similarity_M0=edge_m0,edge_similarity_M1=edge_m1,density_similarity=density,
                layout_similarity=layout,composite_similarity=composite,
                color_contribution=color/3,density_contribution=density/3,layout_contribution=layout/3,
                foreground_contribution=foreground/6,edge_contribution=edge/6)


def fingerprint():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ['PILOT','results','results_corrected_pilot','results_pairwise_baseline',
                           'experiments','pairwise_investigation']
            for p in (ROOT/folder).rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and not p.is_relative_to(OUTPUT)}


def load_records():
    base=ROOT/'results_pairwise_baseline'
    provenance=json.loads((base/'configuration.json').read_text())
    for path,digest in provenance['input_sha256'].items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest:
            raise ValueError(f'Approved input fingerprint mismatch: {path}')
    features=load_features(ROOT/'results_corrected_pilot',ROOT/'PILOT/screenshots')
    distances=read_csv(base/'pairwise_distances.csv')
    similarities=indexed([dict(r,pair_id=r['screen_a']+'__'+r['screen_b'])
                          for r in read_csv(base/'pairwise_similarities.csv')],'pair_id','saved similarities')
    expected={(a,b) for a,b in itertools.combinations(sorted(features),2)
              if features[a]['app_id']==features[b]['app_id']}
    if len(features)!=82 or len(expected)!=709 or len(distances)!=709 or len(similarities)!=709:
        raise ValueError('Unexpected approved pilot size')
    seen=set(); records=[]
    for d in distances:
        a,b=d['screen_a'],d['screen_b']; key=(a,b); pair_id=a+'__'+b
        if key not in expected or key in seen: raise ValueError('Missing/duplicate/invalid unordered pair')
        seen.add(key); fa,fb=features[a],features[b]; saved=similarities[pair_id]
        kind='within_flow' if fa['flow_id']==fb['flow_id'] else 'cross_flow'
        identifiers=dict(screen_a=a,screen_b=b,app_id=fa['app_id'],flow_a=fa['flow_id'],flow_b=fb['flow_id'],pair_type=kind)
        if any(d[k]!=v or saved[k]!=v for k,v in identifiers.items()): raise ValueError('Identifier mismatch')
        color,fgd,ed,layout=[float(d[k]) for k in ['color_emd_distance','foreground_distance','edge_distance','layout_distance']]
        fga,ea=fa['density']; fgb,eb=fb['density']
        # Audit saved descriptor distances without rerunning extraction, transport or bounding boxes.
        if fgd!=abs(fga-fgb) or ed!=abs(ea-eb): raise ValueError('Saved density distance mismatch')
        if not np.isclose(layout,np.mean(np.abs(fa['layout']-fb['layout'])),rtol=0,atol=1e-14):
            raise ValueError('Saved layout MAE mismatch')
        s=score(color,fga,fgb,ea,eb,layout)
        for old,new in [('foreground_similarity','foreground_similarity'),('edge_similarity','edge_similarity_M0'),('layout_similarity','layout_similarity')]:
            if float(saved[old])!=s[new]: raise ValueError('Saved similarity mismatch')
        records.append(dict(pair_id=pair_id,**identifiers,color_emd_distance=color,
                            foreground_a=float(fga),foreground_b=float(fgb),edge_a=float(ea),edge_b=float(eb),layout_mae=layout))
    if seen!=expected or set(similarities)!={r['pair_id'] for r in records}: raise ValueError('Incomplete pair universe')
    return records


def summarize(values):
    a=np.asarray(values,float)
    return dict(count=len(a),minimum=float(a.min()),maximum=float(a.max()),mean=float(a.mean()),
                std_sample=float(a.std(ddof=1)),q10=float(np.quantile(a,.1)),q25=float(np.quantile(a,.25)),
                median=float(np.median(a)),q75=float(np.quantile(a,.75)),q90=float(np.quantile(a,.9)))


def calculate(records):
    configurations={}
    for name,tau,method in CONFIGS:
        rows=[]
        for r in records:
            values=score(r['color_emd_distance'],r['foreground_a'],r['foreground_b'],r['edge_a'],r['edge_b'],r['layout_mae'],tau,method)
            rows.append(dict(r,configuration=name,tau=tau,edge_method=method,**values))
        ranks=rankdata([-r['composite_similarity'] for r in rows],method='average')
        for r,rank in zip(rows,ranks): r['rank']=float(rank)
        configurations[name]=rows
    return configurations


def make_sheet(path,slots,metadata):
    sheet=Image.new('RGB',(1200,660*len(slots)),'white'); draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(findfont('DejaVu Sans Mono'),15)
    for i,r in enumerate(slots):
        y=i*660
        lines=[f"{r['selection']} | {r['configuration']} | {r['app_id']} | {r['pair_type']}",
               f"A: {r['screen_a']} | B: {r['screen_b']}",
               f"Color EMD={r['color_emd_distance']:.5f} | C={r['color_similarity']:.4f} F={r['foreground_similarity']:.4f}",
               f"E={r['edge_similarity']:.4f} D={r['density_similarity']:.4f} L={r['layout_similarity']:.4f} Composite={r['composite_similarity']:.4f}"]
        for j,line in enumerate(lines): draw.text((12,y+4+20*j),line,font=font,fill='black')
        for col,sid in enumerate([r['screen_a'],r['screen_b']]):
            path_image=(ROOT/'PILOT/screenshots'/metadata[sid]['image_path']).resolve()
            if not path_image.is_relative_to((ROOT/'PILOT/screenshots').resolve()): raise ValueError('Image outside dataset')
            with Image.open(path_image) as source: image=source.convert('RGB')
            image.thumbnail((570,560),Image.Resampling.LANCZOS)
            sheet.paste(image,(col*600+(600-image.width)//2,y+92))
    sheet.save(path)


def run(output):
    output=Path(output).resolve()
    if output.exists(): raise FileExistsError('Choose a new output directory; historical results are preserved')
    # Temporary reproductions must also stay outside protected historical directories.
    if output!=OUTPUT and any(output.is_relative_to(ROOT/f) for f in ['PILOT','results','results_corrected_pilot','results_pairwise_baseline','experiments','pairwise_investigation']):
        raise ValueError('Reproduce outside protected historical directories')
    before=fingerprint(); records=load_records(); configs=calculate(records); baseline=configs['baseline_v1']
    for rows in configs.values():
        for r in rows:
            if not all(np.isfinite(r[k]) and 0<=r[k]<=1 for k in SIMILARITIES): raise ValueError('Invalid output similarity')
            if not np.isclose(sum(r[k] for k in CONTRIBUTIONS[:3]),r['composite_similarity'],rtol=0,atol=3e-16): raise ValueError('Contribution mismatch')
    output.mkdir(parents=True)
    write_table(output/'composite_scores.csv',baseline)
    sensitivity=[]
    for name,rows in configs.items():
        for r,b in zip(rows,baseline):
            sensitivity.append(dict(r,delta_composite=r['composite_similarity']-b['composite_similarity'],
                                    rank_shift=r['rank']-b['rank']))
    write_table(output/'sensitivity_analysis.csv',sensitivity)
    summaries=[]; rank_summary=[]
    for app in ['ALL']+sorted({r['app_id'] for r in baseline}):
        for kind in ['all','within_flow','cross_flow']:
            mask=[i for i,r in enumerate(baseline) if (app=='ALL' or r['app_id']==app) and (kind=='all' or r['pair_type']==kind)]
            b=np.array([baseline[i]['composite_similarity'] for i in mask])
            for name,rows in configs.items():
                selected=[rows[i] for i in mask]; values=np.array([r['composite_similarity'] for r in selected])
                for metric in SIMILARITIES+CONTRIBUTIONS:
                    summaries.append(dict(configuration=name,app_id=app,pair_type=kind,metric=metric,**summarize([r[metric] for r in selected])))
                shifts=rankdata(-values)-rankdata(-b)
                rank_summary.append(dict(configuration=name,app_id=app,pair_type=kind,count=len(mask),
                    spearman=float(spearmanr(b,values).statistic),kendall_tau_b=float(kendalltau(b,values).statistic),
                    mean_delta=float(np.mean(values-b)),maximum_absolute_delta=float(np.max(np.abs(values-b))),
                    mean_absolute_rank_shift=float(np.mean(np.abs(shifts))),maximum_absolute_rank_shift=float(np.max(np.abs(shifts)))))
    write_table(output/'composite_summary.csv',summaries)
    write_table(output/'sensitivity_summary.csv',rank_summary)
    selections=[]
    for app in sorted({r['app_id'] for r in baseline}):
        for kind in ['within_flow','cross_flow']:
            ordered=sorted([r for r in baseline if r['app_id']==app and r['pair_type']==kind],key=lambda r:(r['composite_similarity'],r['pair_id']))
            for label,index in [('low',0),('median',(len(ordered)-1)//2),('high',len(ordered)-1)]:
                selections.append(dict(ordered[index],selection='baseline '+label))
    for name,_,_ in CONFIGS[1:]:
        rows=configs[name]; ordered=sorted(rows,key=lambda r:(r['composite_similarity'],r['pair_id']))
        for label,r in [('minimum',ordered[0]),('maximum',ordered[-1]),
                        ('largest global rank shift',max(zip(rows,baseline),key=lambda x:abs(x[0]['rank']-x[1]['rank']))[0])]:
            selections.append(dict(r,selection=name+' '+label))
    write_table(output/'selected_pairs.csv',selections)
    metadata=indexed(read_csv(ROOT/'PILOT/screenshots/screens.csv'),'screen_id','metadata')
    (output/'inspection_sheets').mkdir()
    for i in range(0,len(selections),3): make_sheet(output/f'inspection_sheets/page_{i//3+1:02d}.png',selections[i:i+3],metadata)
    fig,axes=plt.subplots(2,2,figsize=(12,9),layout='constrained')
    for name,rows in configs.items():
        v=np.array([r['composite_similarity'] for r in rows]); x=np.sort(v)
        axes[0,0].hist(v,bins=np.linspace(0,1,41),alpha=.4,label=name)
        axes[0,1].step(x,np.arange(1,len(x)+1)/len(x),where='post',label=name)
    for kind in ['within_flow','cross_flow']:
        x=np.sort([r['composite_similarity'] for r in baseline if r['pair_type']==kind])
        axes[1,0].step(x,np.arange(1,len(x)+1)/len(x),where='post',label=kind)
    for metric in SIMILARITIES[:5]:
        if metric=='edge_similarity': continue
        x=np.sort([r[metric] for r in baseline]); axes[1,1].step(x,np.arange(1,len(x)+1)/len(x),where='post',label=metric)
    for ax in axes.flat: ax.set_xlim(0,1); ax.legend(fontsize=8); ax.set_xlabel('Similarity')
    axes[0,0].set(title='Composite distributions',ylabel='Pair count')
    for ax in [axes[0,1],axes[1,0],axes[1,1]]: ax.set_ylabel('Empirical cumulative fraction'); ax.set_ylim(0,1)
    axes[0,1].set_title('Composite sensitivity'); axes[1,0].set_title('Baseline by pair type'); axes[1,1].set_title('Baseline group / foreground similarities')
    fig.savefig(output/'distributions.png',dpi=140); plt.close(fig)
    configuration=dict(feature_source='results_corrected_pilot',pairwise_source='results_pairwise_baseline',
        baseline=dict(tau=10,edge_method='M1',group_weights=[1/3]*3,density_weights=[.5,.5]),
        sensitivity=[dict(name=n,tau=t,edge_method=m) for n,t,m in CONFIGS],
        rank_definition='descending composite, average tied ranks; global in pair tables, within app/type group in summary',
        selection='purposive low/lower-median/high within each app/type; sensitivity extrema and largest rank shifts; not random',
        dependencies=dict(numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        pairwise_helper_sha256=hashlib.sha256((ROOT/'pairwise_baseline.py').read_bytes()).hexdigest())
    (output/'configuration.json').write_text(json.dumps(configuration,indent=2)+'\n')
    if before!=fingerprint(): raise RuntimeError('Protected historical files changed')
    (output/'protected_sha256.json').write_text(json.dumps(before,indent=2,sort_keys=True)+'\n')
    checks=dict(screens=82,pairs=len(baseline),pair_types=dict(Counter(r['pair_type'] for r in baseline)),
        configurations=len(configs),all_identifiers_valid=True,no_duplicates_or_missing=True,
        approved_input_hashes_match=True,saved_M0_foreground_layout_match=True,finite_bounded=True,
        historical_files_unchanged=True,no_extraction_or_transport_rerun=True)
    (output/'validation_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=OUTPUT)
    run(parser.parse_args().output)
