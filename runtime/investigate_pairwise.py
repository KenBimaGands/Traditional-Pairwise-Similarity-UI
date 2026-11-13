"""Read-only diagnostic investigation of saved pairwise scores and screenshots."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile
import contextlib
import io

os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/thesis-pairwise-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
from pairwise_baseline import (ROOT, IDENTIFIERS, DISTANCES, read_csv, load_features,
                               make_pairs, run, write_table, input_hashes)

BASE = ROOT/'results_pairwise_baseline'
METRICS = ['color_emd_distance','foreground_similarity','edge_similarity','layout_similarity']


def fingerprint():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ['PILOT','results','results_corrected_pilot','results_pairwise_baseline','experiments']
            for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def statistics(values):
    a=np.asarray(values,float)
    return dict(count=len(a),minimum=float(a.min()),q05=float(np.quantile(a,.05)),q25=float(np.quantile(a,.25)),
                median=float(np.median(a)),q75=float(np.quantile(a,.75)),q95=float(np.quantile(a,.95)),maximum=float(a.max()),
                mean=float(a.mean()),std_sample=float(a.std(ddof=1)) if len(a)>1 else '',
                iqr=float(np.quantile(a,.75)-np.quantile(a,.25)),range=float(np.ptp(a)),unique_values=len(np.unique(a)))


def read_image(sid,metadata):
    path=(ROOT/'PILOT/screenshots'/metadata[sid]['image_path']).resolve()
    if not path.is_relative_to((ROOT/'PILOT/screenshots').resolve()):
        raise ValueError('Image path escapes dataset')
    with Image.open(path) as image:
        return image.convert('RGB')


def image_panel(canvas,image,x,y,width,height):
    image=image.copy(); image.thumbnail((width,height),Image.Resampling.LANCZOS)
    canvas.paste(image,(x+(width-image.width)//2,y))


def make_sheet(path,slots,metadata,palettes):
    sheet=Image.new('RGB',(1000,1590),'white'); draw=ImageDraw.Draw(sheet)
    for row,slot in enumerate(slots):
        y=row*530; a,b=slot['screen_a'],slot['screen_b']
        draw.text((8,y+5),f"{slot['app_id']} | {slot['pair_type']} | {slot['metric']} | {slot['selection']}",fill='black')
        draw.text((8,y+24),f"A: {a} | B: {b}",fill='black')
        draw.text((8,y+43),f"Color distance={float(slot['color_emd_distance']):.4f} | Foreground S={float(slot['foreground_similarity']):.4f} | Edge S={float(slot['edge_similarity']):.4f} | Layout S={float(slot['layout_similarity']):.4f}",fill='black')
        for col,sid in enumerate([a,b]):
            image_panel(sheet,read_image(sid,metadata),col*250+4,y+72,240,430)
            # Saved overlays are reused, not regenerated from source pixels.
            overlay=ROOT/'results_corrected_pilot/visualizations'/f"{metadata[sid]['index']:04d}.png"
            with Image.open(overlay) as image:
                w,h=image.size
                bbox=image.crop((4*w//7,45,5*w//7,h-10))
                image_panel(sheet,bbox,500+col*250+4,y+72,240,400)
            left=500+col*250+4
            for color in palettes[sid]['colors']:
                width=240*color['proportion']; rgb=tuple(round(v) for v in color['rgb'])
                draw.rectangle((left,y+480,left+width,y+495),fill=rgb); left+=width
            draw.text((500+col*250+4,y+502),'Saved corrected boxes + palette',fill='black')
    sheet.save(path)


def diagnostic_cases(output):
    distances=read_csv(BASE/'pairwise_distances.csv'); similarities=read_csv(BASE/'pairwise_similarities.csv')
    lookup={(d['screen_a'],d['screen_b']):dict(d,**{k:s[k] for k in METRICS[1:]}) for d,s in zip(distances,similarities)}
    metadata={r['screen_id']:dict(r,index=i) for i,r in enumerate(read_csv(ROOT/'PILOT/screenshots/screens.csv'))}
    palettes=json.loads((ROOT/'results_corrected_pilot/color_palettes.json').read_text())
    cases=[('color_emd_distance','background-dominated colors','APP01-FLOW01-S010','APP01-FLOW02-S07'),
           ('foreground_similarity','same fraction, different placement','APP02-FLOW01-S012','APP02-FLOW01-S08'),
           ('edge_similarity','edge fraction hides screen content','APP01-FLOW01-S07','APP01-FLOW02-S06'),
           ('layout_similarity','identical occupancy, changed controls','APP03-FLOW02-S010','APP03-FLOW02-S09'),
           ('layout_similarity','keyboard box saturation','APP01-FLOW01-S07','APP01-FLOW01-S08'),
           ('color_emd_distance','corrected gradient still differs in color','APP02-FLOW01-S01','APP02-FLOW01-S05')]
    slots=[]
    for metric,label,a,b in cases:
        a,b=sorted([a,b]); slots.append(dict(lookup[a,b],metric=metric,selection=label))
    write_table(output/'diagnostic_cases.csv',slots)
    for i in range(2): make_sheet(output/f'diagnostic_cases_{i+1}.png',slots[i*3:i*3+3],metadata,palettes)


def main(output):
    if output.exists(): raise ValueError('Use a fresh investigation directory')
    before=fingerprint()
    features=load_features(ROOT/'results_corrected_pilot',ROOT/'PILOT/screenshots')
    distances=read_csv(BASE/'pairwise_distances.csv'); similarities=read_csv(BASE/'pairwise_similarities.csv')
    expected=make_pairs(features)
    assert len(distances)==len(similarities)==len(expected)==709
    for d,s,p in zip(distances,similarities,expected):
        assert all(d[k]==s[k]==p[k] for k in IDENTIFIERS)
        assert all(np.isfinite(float(d[k])) and float(d[k])>=0 for k in DISTANCES)
        assert all(0<=float(d[k])<=1 for k in DISTANCES[1:])
        for k in DISTANCES[1:]:
            assert float(s[k.replace('_distance','_similarity')])==1-float(d[k])
    config=json.loads((BASE/'configuration.json').read_text())
    assert config['input_sha256']==input_hashes(ROOT/'results_corrected_pilot',ROOT/'PILOT/screenshots')
    assert config['source_sha256']==hashlib.sha256((ROOT/'pairwise_baseline.py').read_bytes()).hexdigest()
    # Re-evaluate saved descriptors only to audit reproducibility; never recompute image features.
    with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
        runs=[Path(temp)/'first',Path(temp)/'second']
        for directory in runs: run(directory)
        for name in ['pairwise_distances.csv','pairwise_similarities.csv','pairwise_summary.csv','pair_counts.csv','configuration.json']:
            assert (BASE/name).read_bytes()==(runs[0]/name).read_bytes()==(runs[1]/name).read_bytes()
    merged=[dict(d,**{k:s[k] for k in METRICS[1:]}) for d,s in zip(distances,similarities)]
    output.mkdir(parents=True); (output/'distributions').mkdir(); (output/'inspection_sheets').mkdir(); (output/'overviews').mkdir()
    metadata={r['screen_id']:dict(r,index=i) for i,r in enumerate(read_csv(ROOT/'PILOT/screenshots/screens.csv'))}
    palettes=json.loads((ROOT/'results_corrected_pilot/color_palettes.json').read_text())
    groups=[]; selection=[]; slots_by_sheet={}
    apps=sorted({r['app_id'] for r in merged})
    for app in apps+['ALL']:
        for kind in ['within_flow','cross_flow','all']:
            subset=[r for r in merged if (app=='ALL' or r['app_id']==app) and (kind=='all' or r['pair_type']==kind)]
            for metric in METRICS:
                groups.append(dict(app_id=app,pair_type=kind,feature=metric,**statistics([r[metric] for r in subset])))
            if app=='ALL' or kind=='all': continue
            for metric in METRICS:
                ranked=sorted(subset,key=lambda r:(float(r[metric]),r['screen_a'],r['screen_b']))
                slots=[]
                for label,index in [('low_value',0),('median_value',(len(ranked)-1)//2),('high_value',len(ranked)-1)]:
                    row=dict(ranked[index],metric=metric,selection=label,rank_index=index,group_size=len(ranked))
                    slots.append(row); selection.append(row)
                filename=f'{app}_{kind}_{metric}.png'; slots_by_sheet[filename]=slots
                make_sheet(output/'inspection_sheets'/filename,slots,metadata,palettes)
    write_table(output/'descriptive_statistics.csv',groups)
    write_table(output/'selected_examples.csv',selection)
    assert len(selection)==120 and len(slots_by_sheet)==40
    for metric in METRICS:
        fig,axes=plt.subplots(1,2,figsize=(12,4))
        for app in apps:
            for kind,style in [('within_flow','-'),('cross_flow','--')]:
                vals=np.sort([float(r[metric]) for r in merged if r['app_id']==app and r['pair_type']==kind])
                axes[0].plot(vals,np.arange(1,len(vals)+1)/len(vals),linestyle=style,label=f'{app} {kind}',linewidth=1)
        color='distance' if metric=='color_emd_distance' else 'similarity'
        axes[0].set(xlabel=f'{metric} ({color})',ylabel='Empirical cumulative fraction',title='Per application and pair type')
        if metric!='color_emd_distance': axes[0].set_xlim(0,1)
        for kind in ['within_flow','cross_flow']:
            vals=np.sort([float(r[metric]) for r in merged if r['pair_type']==kind])
            axes[1].plot(vals,np.arange(1,len(vals)+1)/len(vals),label=kind)
        axes[1].set(xlabel=f'{metric} (observed range)',ylabel='Empirical cumulative fraction',title='Pooled pairs: observed-range view')
        axes[0].legend(fontsize=6); axes[1].legend(); fig.tight_layout(); fig.savefig(output/'distributions'/f'{metric}.png',dpi=150); plt.close(fig)
        for kind in ['within_flow','cross_flow']:
            sheet=Image.new('RGB',(1500,1210),'white'); draw=ImageDraw.Draw(sheet)
            for col,app in enumerate(apps):
                slots=slots_by_sheet[f'{app}_{kind}_{metric}.png']
                for row,slot in enumerate(slots):
                    x=col*300;y=row*400
                    draw.text((x+3,y+4),f"{app} {slot['selection']} {float(slot[metric]):.4f}",fill='black')
                    draw.text((x+3,y+20),slot['screen_a'],fill='black'); draw.text((x+3,y+34),slot['screen_b'],fill='black')
                    image_panel(sheet,read_image(slot['screen_a'],metadata),x+3,y+52,145,340)
                    image_panel(sheet,read_image(slot['screen_b'],metadata),x+153,y+52,145,340)
            sheet.save(output/'overviews'/f'{kind}_{metric}.png')
    diagnostic=[]
    for sid,f in features.items():
        colors=palettes[sid]['colors']
        diagnostic.append(dict(screen_id=sid,app_id=f['app_id'],flow_id=f['flow_id'],foreground=float(f['density'][0]),edge=float(f['density'][1]),
            dominant_palette_mass=max(c['proportion'] for c in colors),layout_mean=float(f['layout'].mean()),
            saturated_grid_cells=int(np.sum(f['layout']==1)),empty_grid_cells=int(np.sum(f['layout']==0))))
    write_table(output/'screen_diagnostics.csv',diagnostic)
    diagnostic_cases(output)
    assert before==fingerprint()
    write_json=lambda name,data:(output/name).write_text(json.dumps(data,indent=2)+'\n')
    write_json('validation_checks.json',dict(screens=82,pairs=709,within_flow=411,cross_flow=298,records_aligned=True,numerical_ranges_valid=True,
        exact_reproduction_against_saved_exports=True,two_repeated_exports_identical=True,protected_files_unchanged=True,
        selections=120,inspection_sheets=40,unique_selected_pairs=len({(s['screen_a'],s['screen_b']) for s in selection}),
        features_recomputed=False,formulas_changed=False))
    write_json('protected_sha256.json',before)
    print(json.dumps(json.loads((output/'validation_checks.json').read_text()),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path,default=ROOT/'pairwise_investigation'); args=parser.parse_args()
    main(args.output.resolve())
