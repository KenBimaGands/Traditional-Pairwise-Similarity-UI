"""Route six existing pre-graph stages in a fresh isolated project copy."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
STAGES=['feature-extraction','pairwise-similarity','descriptor-investigation','edge-similarity','composite-scoring','tau-sensitivity']
TARGETS={'feature-extraction':'results_corrected_pilot','pairwise-similarity':'results_pairwise_baseline',
         'descriptor-investigation':'pairwise_investigation','edge-similarity':'experiments/edge_similarity_evaluation',
         'composite-scoring':'results/composite_baseline_v1','tau-sensitivity':'results/composite_baseline_v1'}
SCRIPTS={'feature-extraction':'experiments/final_baseline_correction/run_pilot.py','pairwise-similarity':'pairwise_baseline.py',
         'descriptor-investigation':'investigate_pairwise.py','edge-similarity':'experiments/edge_similarity_evaluation/evaluate.py',
         'composite-scoring':'composite_baseline.py','tau-sensitivity':'review_tau_sensitivity.py'}


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path):
    with path.open(encoding='utf-8-sig',newline='') as handle:return list(csv.DictReader(handle))


def validate(work,stage,location=None):
    import numpy as np
    folder=location or work/TARGETS[stage]
    if stage=='feature-extraction':
        sys.path.insert(0,str(work))
        from pairwise_baseline import load_features
        features=load_features(folder,work/'PILOT/screenshots')
        if len(features)!=82:raise ValueError('Approved extraction must contain 82 valid screens')
        summary=json.loads((folder/'run_summary.json').read_text())
        if summary['errors'] or summary['activated']!=['APP02-FLOW01-S01']:raise ValueError('Approved pilot correction differs')
        return dict(screens=82,activation=summary['activated'])
    metadata=table(work/'PILOT/screenshots/screens.csv')
    expected={(a['screen_id'],b['screen_id']) for i,a in enumerate(sorted(metadata,key=lambda r:r['screen_id']))
              for b in sorted(metadata,key=lambda r:r['screen_id'])[i+1:] if a['app_id']==b['app_id']}
    if len(expected)!=709:raise ValueError('Expected the fixed 709-pair pilot universe')
    def pairs(rows,columns):
        if len(rows)!=709 or {(r['screen_a'],r['screen_b']) for r in rows}!=expected:raise ValueError('Missing/duplicate pair records')
        for r in rows:
            for key in columns:
                value=float(r[key])
                if not np.isfinite(value) or value<0 or (key!='color_emd_distance' and value>1):raise ValueError(f'Invalid {key}')
    if stage=='pairwise-similarity':
        pairs(table(folder/'pairwise_distances.csv'),['color_emd_distance','foreground_distance','edge_distance','layout_distance'])
        pairs(table(folder/'pairwise_similarities.csv'),['foreground_similarity','edge_similarity','layout_similarity'])
    elif stage=='composite-scoring':
        pairs(table(folder/'composite_scores.csv'),['color_similarity','density_similarity','layout_similarity','composite_similarity'])
        rows=table(folder/'sensitivity_analysis.csv')
        for name in ['baseline_v1','color_tau5','color_tau20','edge_M0']:
            pairs([r for r in rows if r['configuration']==name],['composite_similarity'])
    elif stage=='edge-similarity':
        pairs(table(folder/'edge_similarity_comparison.csv'),['M0','M1','M2'])
        sample=table(folder/'random_pairs.csv')
        if len(sample)!=24 or len({r['pair_id'] for r in sample})!=24:raise ValueError('Invalid 24-pair random sample')
    elif stage=='descriptor-investigation':
        checks=json.loads((folder/'validation_checks.json').read_text())
        if checks['pairs']!=709 or not checks['records_aligned']:raise ValueError('Invalid descriptor diagnostics')
        if len(table(folder/'selected_examples.csv'))!=120:raise ValueError('Expected 120 purposive descriptor slots')
    else:
        if not (folder/'tau_sensitivity_review.md').exists():raise ValueError('Tau review report missing')
        stats=table(folder/'tau_review_assets/summary.csv')
        if {float(r['tau']) for r in stats}!={5.,10.,20.}:raise ValueError('Missing tau configuration')
        checks=json.loads((folder/'tau_review_assets/checks.json').read_text())
        if checks['pairs_per_tau']!=709 or not checks['all_other_parameters_fixed']:raise ValueError('Invalid tau review')
    return dict(pairs=709,validated_stage=stage)


def rebase(work):
    """Rewrite only location-bearing provenance in the private copy, never saved scores."""
    config=work/'results_pairwise_baseline/configuration.json'
    data=json.loads(config.read_text());previous=data['input_sha256']
    mapped={}
    for old,expected in previous.items():
        original=Path(old); parts=original.parts
        anchor=next((p for p in ['results_corrected_pilot','PILOT'] if p in parts),None)
        if anchor is None:raise ValueError(f'Cannot relocate input path: {old}')
        target=work/Path(*parts[parts.index(anchor):])
        if not target.is_file() or digest(target)!=expected:raise ValueError(f'Input digest mismatch: {target}')
        mapped[str(target.resolve())]=expected
    data['input_sha256']=mapped;data['features_dir']=str(work/'results_corrected_pilot')
    config.write_text(json.dumps(data,indent=2)+'\n')
    return dict(original_input_paths=previous,relocated_input_paths=mapped)


def main(project,output,stage='all',recompute=False):
    project=Path(project).resolve();output=Path(output).resolve()
    if output.exists():raise FileExistsError('Use a fresh --output; existing runs are never overwritten')
    if output.is_relative_to(project):raise ValueError('Output must be outside the input project')
    manifest=json.loads((HERE/'provenance.json').read_text())['files']
    required=[Path(name).relative_to('runtime') for name in manifest]
    missing=[str(p) for p in required if not (project/p).is_file()]
    if missing:raise FileNotFoundError('Missing required pilot fixtures: '+', '.join(missing[:12]))
    before={str(p):digest(project/p) for p in required}
    if project==HERE/'runtime':
        for name,info in manifest.items():
            if digest(HERE/name)!=info['sha256']:raise ValueError(f'Bundled reference changed: {name}')
    work=output/'workspace';work.mkdir(parents=True)
    for relative in required:
        dest=work/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(project/relative,dest)
    relocation=rebase(work)
    (output/'relocation.json').write_text(json.dumps(relocation,indent=2)+'\n')
    chosen=STAGES if stage=='all' else [stage];records=[]
    for current in chosen:
        target=work/TARGETS[current]
        if not recompute:
            check=validate(work,current)
            records.append(dict(stage=current,status='reused_validated_saved_results',location=str(target.relative_to(output)),checks=check))
            print(current+': reused validated saved results',flush=True);continue
        # Fail at prerequisite boundaries before launching a downstream subprocess.
        dependencies={'pairwise-similarity':['feature-extraction'],
                      'descriptor-investigation':['feature-extraction','pairwise-similarity'],
                      'edge-similarity':['feature-extraction','pairwise-similarity'],
                      'composite-scoring':['feature-extraction','pairwise-similarity'],
                      'tau-sensitivity':['composite-scoring']}
        for dependency in dependencies.get(current,[]):validate(work,dependency)
        destination=work/'artifacts'/current;destination.parent.mkdir(exist_ok=True)
        command=[sys.executable,str(work/SCRIPTS[current]),'--output',str(destination)]
        env=dict(os.environ,PYTHONPATH=str(work),PYTHONDONTWRITEBYTECODE='1')
        print(current+': executing in isolated workspace',flush=True)
        with (output/(current+'.log')).open('w') as log:
            result=subprocess.run(command,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode:raise RuntimeError(f'{current} failed; inspect {output/(current+".log")}')
        check=validate(work,current,destination)
        for name in ['README.md','validation_report.md','pairwise_investigation_report.md','edge_similarity_evaluation_report.md','composite_methodology.md']:
            if (target/name).exists() and not (destination/name).exists():shutil.copy2(target/name,destination/name)
        if current in ['descriptor-investigation','edge-similarity','composite-scoring']:
            (destination/'interpretation_provenance.txt').write_text('Markdown interpretations copied from the frozen reference. Generated figures are not new human/expert validation.\n')
        if current=='tau-sensitivity':
            (destination/'inspection_sheets').mkdir(exist_ok=True)
            for name in ['page_11.png','page_12.png']:
                shutil.copy2(work/'results/composite_baseline_v1/inspection_sheets'/name,destination/'inspection_sheets'/name)
        if current in ['feature-extraction','pairwise-similarity','composite-scoring']:
            archive=work/'reference'/current;archive.parent.mkdir(exist_ok=True)
            shutil.move(str(target),archive);shutil.copytree(destination,target)
        records.append(dict(stage=current,status='recomputed_validated',location=str(destination.relative_to(output)),checks=check))
    if before!={str(p):digest(project/p) for p in required}:raise RuntimeError('Input project changed')
    summary=dict(stages=records,source_project=str(project),input_files_unchanged=True,
        graph_methods_included=False,research_parameters_changed=False,
        script_sha256=digest(Path(__file__)),runtime_source_manifest_sha256=digest(HERE/'provenance.json'))
    (output/'run_manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('Completed '+str(len(records))+' stages; source project unchanged.',flush=True)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=HERE/'runtime')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--stage',choices=['all']+STAGES,default='all')
    parser.add_argument('--recompute',action='store_true',help='Execute requested stages; otherwise validate/reuse saved outputs')
    args=parser.parse_args()
    main(args.project,args.output,args.stage,args.recompute)
