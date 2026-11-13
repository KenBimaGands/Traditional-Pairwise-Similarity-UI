"""Apply the frozen final correction to all pilot metadata rows, in a fresh directory."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from correct import (ROOT, HERE, PARAMS, Config, extract, load_image, correct_mask,
                     geometry, validate, comparison, protected_hashes,
                     read_csv, write_csv, write_json, np, Image)


def run(output):
    # Refuse overwrites: baseline and sample evidence remain separate from this full run.
    if output.exists():
        raise ValueError('Use a fresh output directory')
    protected = protected_hashes()
    protected.update({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (HERE / 'run_01').rglob('*') if p.is_file()})
    metadata_path = ROOT / 'PILOT/screenshots/screens.csv'
    rows = read_csv(metadata_path, 'utf-8-sig')
    ids = [row['screen_id'] for row in rows]
    if len(rows) != 82 or len(set(ids)) != len(ids):
        raise ValueError('Expected exactly 82 distinct pilot screen IDs')
    palettes_before = json.loads((ROOT / 'results/color_palettes.json').read_text())
    boxes_before = json.loads((ROOT / 'results/bounding_boxes.json').read_text())
    layout_before = {r['screen_id']: r for r in read_csv(ROOT / 'results/layout_vectors.csv')}
    scalar_before = {r['screen_id']: r for r in read_csv(ROOT / 'results/visual_features.csv')}
    sample_palettes = json.loads((HERE / 'run_01/candidate/color_palettes.json').read_text())
    sample_boxes = json.loads((HERE / 'run_01/candidate/bounding_boxes.json').read_text())
    sample_layout = {r['screen_id']: r for r in read_csv(HERE / 'run_01/candidate/layout_vectors.csv')}
    sample_scalar = {r['screen_id']: r for r in read_csv(HERE / 'run_01/candidate/visual_features.csv')}
    output.mkdir(parents=True)
    for name in ['visualizations', 'masks']:
        (output / name).mkdir()
    results, palettes, boxes, layouts, differences, triggers = [], {}, {}, [], [], {}
    for index, row in enumerate(rows):
        sid = row['screen_id']
        record = dict(screen_id=sid, status='error', error='', original_width='', original_height='', width='', height='', foreground_coverage='', edge_density='', component_count='', correction_activated='')
        try:
            path = (metadata_path.parent / row['image_path']).resolve()
            if not path.is_relative_to(metadata_path.parent.resolve()):
                raise ValueError('Image path escapes dataset root')
            rgb, original_size = load_image(path, Config())
            if min(rgb.shape[:2]) < 8:
                raise ValueError('Image too small for 4 × 8 grid')
            baseline, mask, edges = extract(rgb)
            # Reproduce all saved baseline features before applying the unchanged correction.
            assert baseline['palette'] == palettes_before[sid]['colors']
            assert baseline['background_rgb'] == palettes_before[sid]['background_rgb']
            assert baseline['boxes'] == boxes_before[sid]
            assert baseline['layout'] == [float(layout_before[sid][f'cell_{i:02d}']) for i in range(32)]
            assert all(baseline[key] == float(scalar_before[sid][key]) for key in ['foreground_coverage', 'edge_density'])
            revised, info = correct_mask(rgb, mask, enabled=True)
            repeated, repeated_info = correct_mask(rgb, mask, enabled=True)
            np.testing.assert_array_equal(revised, repeated)
            assert info == repeated_info and np.all(revised <= mask)
            retained_boxes, layout = geometry(revised, Config().min_component_area)
            features = dict(baseline, foreground_coverage=float(revised.mean()), boxes=retained_boxes, layout=layout)
            validate(features)
            if not info['trigger']:
                np.testing.assert_array_equal(revised, mask)
                assert features == baseline
            # Ensure the 12-screen selected method is reproduced exactly within this full run.
            if sid in sample_palettes:
                assert features['palette'] == sample_palettes[sid] and retained_boxes == sample_boxes[sid]
                assert layout == [float(sample_layout[sid][f'cell_{i:02d}']) for i in range(32)]
                assert all(features[key] == float(sample_scalar[sid][key]) for key in ['foreground_coverage', 'edge_density'])
            comparison(output / 'visualizations' / f'{index:04d}.png', sid, rgb, baseline, features, mask, revised)
            Image.fromarray(revised * 255).save(output / 'masks' / f'{index:04d}.png')
            record.update(status='ok', original_width=original_size[0], original_height=original_size[1], width=rgb.shape[1], height=rgb.shape[0], foreground_coverage=features['foreground_coverage'], edge_density=features['edge_density'], component_count=len(retained_boxes), correction_activated=info['trigger'])
            palettes[sid] = dict(colors=features['palette'], background_rgb=features['background_rgb'])
            boxes[sid] = retained_boxes
            layouts.append(dict(screen_id=sid, **{f'cell_{i:02d}': value for i, value in enumerate(layout)}))
            triggers[sid] = info
            differences.append(dict(screen_id=sid, activated=info['trigger'], baseline_foreground=baseline['foreground_coverage'], corrected_foreground=features['foreground_coverage'], foreground_delta=features['foreground_coverage']-baseline['foreground_coverage'], baseline_components=len(baseline['boxes']), corrected_components=len(retained_boxes), baseline_layout_mean=float(np.mean(baseline['layout'])), corrected_layout_mean=float(np.mean(layout)), removed_pixels=int(np.count_nonzero(mask != revised)), **{f'cell_{i:02d}_delta':layout[i]-baseline['layout'][i] for i in range(32)}))
        except (OSError, ValueError, Image.DecompressionBombError) as error:
            record['error'] = str(error)
        results.append(record)
        print(f"{index+1}/82 {sid}: {record['status']} activated={record['correction_activated']}", flush=True)
    write_csv(output / 'visual_features.csv', results)
    if layouts:
        write_csv(output / 'layout_vectors.csv', layouts)
        write_csv(output / 'differences.csv', differences)
    write_json(output / 'color_palettes.json', palettes)
    write_json(output / 'bounding_boxes.json', boxes)
    write_json(output / 'triggers.json', triggers)
    write_json(output / 'configuration.json', dict(baseline=asdict(Config()), correction=PARAMS, correction_enabled=True, analyzed_region='Complete original processed image, no cropping', screenshot_count=len(rows)))
    after = protected_hashes()
    after.update({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (HERE / 'run_01').rglob('*') if p.is_file()})
    assert protected == after
    write_json(output / 'protected_sha256.json', protected)
    write_json(output / 'source_sha256.json', {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT / 'extract_features.py', HERE / 'correct.py', Path(__file__).resolve(), HERE.parent / 'preprocessing_v2/revised_pipeline.py', HERE.parent / 'preprocessing_v2/review_assets.py', ROOT / 'requirements-lock.txt']})
    summary = dict(requested=82, extracted=sum(r['status']=='ok' for r in results), errors=[r for r in results if r['status']!='ok'], activated=[sid for sid, info in triggers.items() if info['trigger']], protected_files_unchanged=True, baseline_reproduced=True, correction_repeatability=True, selected_sample_reproduced=True)
    write_json(output / 'run_summary.json', summary)
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'results_corrected_pilot')
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT):
        parser.error('Output must remain inside the project directory')
    summary = run(output)
    raise SystemExit(bool(summary['errors']))
