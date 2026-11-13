"""Focused, versioned experiment; never writes baseline inputs or results."""
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from PIL import Image, ImageDraw
from extract_features import Config, extract, load_image

HERE = Path(__file__).resolve().parent
SETTINGS = dict(side_fraction=.035, row_smoothing=9, row_distance=12.,
                median_kernel=31, local_distance=6., pale_distance=3.,
                footer_search_fraction=.06, footer_min_jump=20., footer_max_gray=90.)


def footer_candidate(rgb, settings=SETTINGS):
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    medians = np.median(gray, axis=1)
    height = len(medians)
    candidates = [y for y in range(int(height*(1-settings['footer_search_fraction'])), height-2)
                  if medians[y-1]-medians[y] > settings['footer_min_jump']
                  and np.median(gray[y:]) < settings['footer_max_gray']]
    return min(candidates) if candidates else None


def region(rgb, approved_footer, settings=SETTINGS):
    cut = footer_candidate(rgb, settings)
    flags = []
    if cut is not None and not approved_footer:
        flags.append('unconfirmed_footer_candidate_retained')
    if approved_footer and cut is None:
        flags.append('approved_footer_not_detected_retained')
    cropped = rgb[:cut] if approved_footer and cut is not None else rgb
    # Frame identity is ambiguous without provenance; preserve pixels and explicitly block rollout.
    corners = cropped[[0, 0, -1, -1], [0, -1, 0, -1]].astype(float)
    inset = max(2, round(cropped.shape[1]*.04))
    nearby = cropped[[inset, inset, -inset-1, -inset-1], [inset, -inset-1, inset, -inset-1]].astype(float)
    if np.any(np.linalg.norm(corners-nearby, axis=1) > 25):
        flags.append('possible_synthetic_frame_retained_manual_review')
    return cropped, dict(footer_candidate_y=cut, footer_removed=bool(approved_footer and cut is not None),
                         bounds_xyxy=[0, 0, cropped.shape[1], cropped.shape[0]], flags=flags)


def segment(rgb, method, settings=SETTINGS):
    height, width = rgb.shape[:2]
    local_background = cv2.medianBlur(rgb, settings['median_kernel'])
    residual = np.linalg.norm(rgb.astype(float)-local_background.astype(float), axis=2)
    if method == 'local_median':
        return (residual > settings['local_distance']).astype(np.uint8)
    if method != 'row_background':
        raise ValueError(f'Unknown method: {method}')
    band = max(1, round(width*settings['side_fraction']))
    left = np.median(rgb[:, :band], axis=1).astype(np.uint8)
    right = np.median(rgb[:, -band:], axis=1).astype(np.uint8)
    left = cv2.medianBlur(left[:, None, :], settings['row_smoothing'])[:, 0]
    right = cv2.medianBlur(right[:, None, :], settings['row_smoothing'])[:, 0]
    fraction = np.linspace(0, 1, width)[None, :, None]
    background = left[:, None, :]*(1-fraction)+right[:, None, :]*fraction
    distance = np.linalg.norm(rgb.astype(float)-background, axis=2)
    # shortcut: low local residuals retain pale strokes but can also retain shadows; inspect before rollout.
    return ((distance > settings['row_distance']) | (residual > settings['pale_distance'])).astype(np.uint8)


def geometry(mask, min_area):
    height, width = mask.shape
    _, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    boxes, union = [], np.zeros_like(mask)
    for x, y, w, h, area in stats[1:]:
        if area >= min_area:
            boxes.append([float(x/width), float(y/height), float((x+w)/width), float((y+h)/height)])
            union[y:y+h, x:x+w] = 1
    xs, ys = np.linspace(0, width, 5, dtype=int), np.linspace(0, height, 9, dtype=int)
    layout = [float(union[ys[r]:ys[r+1], xs[c]:xs[c+1]].mean()) for r in range(8) for c in range(4)]
    return boxes, layout


def validate(features):
    assert 1 <= len(features['palette']) <= 5
    assert abs(sum(c['proportion'] for c in features['palette'])-1) < 1e-12
    assert all(np.isfinite(c['lab']).all() for c in features['palette'])
    assert all(0 <= features[k] <= 1 for k in ['foreground_coverage', 'edge_density'])
    assert len(features['layout']) == 32 and all(0 <= x <= 1 for x in features['layout'])
    assert all(0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1 for x0,y0,x1,y1 in features['boxes'])


def read_csv(path, encoding="utf-8"):
    return list(csv.DictReader(path.read_text(encoding=encoding).splitlines()))


def write_csv(path, rows):
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def hashes():
    paths = list((ROOT/'PILOT').rglob('*')) + list((ROOT/'results').rglob('*'))
    paths += [ROOT/'extract_features.py', ROOT/'test_features.py']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


def draw_boxes(rgb, boxes):
    image = Image.fromarray(rgb).copy()
    draw = ImageDraw.Draw(image)
    height, width = rgb.shape[:2]
    for x0,y0,x1,y1 in boxes:
        draw.rectangle((x0*width,y0*height,min(width-1,x1*width),min(height-1,y1*height)),outline='red')
    return image


def comparison(path, sid, original, roi, baseline, base_mask, candidates):
    width, height = 240, 590
    canvas = Image.new('RGB', (width*8, height), 'white')
    draw = ImageDraw.Draw(canvas)
    draw.text((8,5),sid,fill='black')
    panels = [('Baseline image',Image.fromarray(original)), ('ROI image',Image.fromarray(roi)),
              ('Baseline mask',Image.fromarray(base_mask*255).convert('RGB')),
              ('Baseline boxes',draw_boxes(original,baseline['boxes']))]
    for name in ['row_background', 'local_median']:
        features, mask = candidates[name]
        panels += [(f'{name} mask',Image.fromarray(mask*255).convert('RGB')),
                   (f'{name} boxes',draw_boxes(roi,features['boxes']))]
    for i,(title,panel) in enumerate(panels):
        draw.text((i*width+5,30),title,fill='black')
        panel.thumbnail((width-8,510),Image.Resampling.LANCZOS)
        canvas.paste(panel,(i*width+(width-panel.width)//2,60))
    canvas.save(path)


def run(output):
    if output.exists():
        raise ValueError('Output already exists; choose a fresh version directory')
    before = hashes()
    output.mkdir(parents=True)
    config = Config()
    selected = read_csv(ROOT/'visual_quality_review/selected_screens.csv')
    metadata = {r['screen_id']:r for r in read_csv(ROOT/'PILOT/screenshots/screens.csv', 'utf-8-sig')}
    approvals = json.loads((HERE/'roi_review.json').read_text())
    saved = {name: {} for name in ['roi_baseline','row_background','local_median']}
    rois, differences = {}, []
    (output/'comparisons').mkdir()
    for row in selected:
        sid = row['screen_id']
        original, _ = load_image(ROOT/'PILOT/screenshots'/metadata[sid]['image_path'],config)
        baseline, baseline_mask, _ = extract(original,config)
        roi, info = region(original, approvals[sid]['source_footer_confirmed'])
        rois[sid] = dict(**info, review=approvals[sid])
        roi_base, _, edges = extract(roi,config)
        saved['roi_baseline'][sid] = roi_base
        candidates = {}
        for method in ['row_background','local_median']:
            mask = segment(roi,method)
            assert np.array_equal(mask, segment(roi,method))
            boxes, layout = geometry(mask,config.min_component_area)
            features = dict(roi_base,foreground_coverage=float(mask.mean()),boxes=boxes,layout=layout)
            validate(features)
            saved[method][sid] = features
            candidates[method] = (features,mask)
            directory=output/method/'masks'; directory.mkdir(parents=True,exist_ok=True)
            Image.fromarray(mask*255).save(directory/f'{sid}.png')
            differences.append(dict(screen_id=sid,method=method,
                baseline_foreground=baseline['foreground_coverage'], roi_only_foreground=roi_base['foreground_coverage'],
                revised_foreground=features['foreground_coverage'], foreground_delta=features['foreground_coverage']-baseline['foreground_coverage'],
                baseline_edges=baseline['edge_density'], revised_edges=features['edge_density'],edge_delta=features['edge_density']-baseline['edge_density'],
                baseline_components=len(baseline['boxes']),revised_components=len(boxes),component_delta=len(boxes)-len(baseline['boxes']),
                baseline_layout_mean=float(np.mean(baseline['layout'])),revised_layout_mean=float(np.mean(layout)),
                full_grid_cells=sum(x==1 for x in layout)))
        comparison(output/'comparisons'/f'{sid}.png',sid,original,roi,baseline,baseline_mask,candidates)
        print(sid,flush=True)
    for method, screens in saved.items():
        directory=output/method; directory.mkdir(exist_ok=True)
        write_csv(directory/'visual_features.csv',[dict(screen_id=sid,status='ok',foreground_coverage=f['foreground_coverage'],edge_density=f['edge_density'],component_count=len(f['boxes'])) for sid,f in screens.items()])
        write_csv(directory/'layout_vectors.csv',[dict(screen_id=sid,**{f'cell_{i:02d}':x for i,x in enumerate(f['layout'])}) for sid,f in screens.items()])
        write_json(directory/'color_palettes.json',{sid:f['palette'] for sid,f in screens.items()})
        write_json(directory/'bounding_boxes.json',{sid:f['boxes'] for sid,f in screens.items()})
    write_csv(output/'feature_differences.csv',differences)
    write_json(output/'roi_manifest.json',rois)
    write_json(output/'config.json',dict(baseline=asdict(config),segmentation=SETTINGS,sample_ids=[r['screen_id'] for r in selected]))
    assert before == hashes(), 'Baseline or input files changed'
    write_json(output/'baseline_sha256.json',before)
    write_json(output/'checks.json',dict(baseline_unchanged=True,screen_count=12,candidate_numerical_checks=True,segmentation_repeatability=True,rollout='pending_visual_review'))


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'sample_run_02')
    args=parser.parse_args()
    output=args.output.resolve()
    if not output.is_relative_to(HERE):
        parser.error('Output must stay inside this versioned experiment directory')
    run(output)
