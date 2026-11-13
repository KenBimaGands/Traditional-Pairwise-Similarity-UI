"""Navigation-independent within-application distances from saved visual features."""
import argparse
import csv
import hashlib
from importlib.metadata import version
from itertools import combinations
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from skimage.color import deltaE_ciede2000

ROOT = Path(__file__).resolve().parent
DISTANCES = ['color_emd_distance', 'foreground_distance', 'edge_distance', 'layout_distance']
IDENTIFIERS = ['screen_a', 'screen_b', 'app_id', 'flow_a', 'flow_b', 'pair_type']


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f'Missing or duplicate column names: {path}')
        return list(reader)


def indexed(rows, key, source):
    result = {}
    for row in rows:
        value = row[key]
        if not value or value in result:
            raise ValueError(f'Missing or duplicate {key} in {source}: {value}')
        result[value] = row
    return result


def numeric(values, shape, bounded=False):
    array = np.asarray(values, dtype=float)
    if array.shape != shape or not np.isfinite(array).all():
        raise ValueError(f'Expected finite array of shape {shape}')
    if bounded and np.any((array < 0) | (array > 1)):
        raise ValueError('Feature outside [0,1]')
    return array


def palette_data(colors):
    if not isinstance(colors, list) or not 1 <= len(colors) <= 5:
        raise ValueError('Palette must contain 1 to 5 colors')
    lab = numeric([color['lab'] for color in colors], (len(colors), 3))
    weights = numeric([color['proportion'] for color in colors], (len(colors),), True)
    if not np.isclose(weights.sum(), 1, rtol=0, atol=1e-10):
        raise ValueError('Palette proportions must sum to 1')
    # Remove floating-point summation drift only; invalid palette masses were rejected above.
    weights = weights / weights.sum()
    order = sorted(range(len(colors)), key=lambda i: (*lab[i], weights[i]))
    return lab[order], weights[order]


def load_features(features_dir, metadata_dir):
    features_dir, metadata_dir = Path(features_dir), Path(metadata_dir)
    screens = indexed(read_csv(metadata_dir / 'screens.csv'), 'screen_id', 'screens.csv')
    flows = indexed(read_csv(metadata_dir / 'flows.csv'), 'flow_id', 'flows.csv')
    scalars = indexed(read_csv(features_dir / 'visual_features.csv'), 'screen_id', 'visual_features.csv')
    layouts = indexed(read_csv(features_dir / 'layout_vectors.csv'), 'screen_id', 'layout_vectors.csv')
    palettes = json.loads((features_dir / 'color_palettes.json').read_text())
    if not screens or any(set(source) != set(screens) for source in [scalars, layouts, palettes]):
        raise ValueError('Metadata and feature ID sets must match exactly')
    result = {}
    for sid, screen in screens.items():
        if not screen['app_id'] or screen['flow_id'] not in flows or flows[screen['flow_id']]['app_id'] != screen['app_id']:
            raise ValueError(f'Application/flow mismatch: {sid}')
        if scalars[sid]['status'] != 'ok':
            raise ValueError(f'Unsuccessful extraction: {sid}')
        expected_columns = {'screen_id'} | {f'cell_{i:02d}' for i in range(32)}
        if set(layouts[sid]) != expected_columns:
            raise ValueError(f'Invalid layout schema: {sid}')
        result[sid] = dict(app_id=screen['app_id'], flow_id=screen['flow_id'],
            density=numeric([scalars[sid]['foreground_coverage'], scalars[sid]['edge_density']], (2,), True),
            layout=numeric([layouts[sid][f'cell_{i:02d}'] for i in range(32)], (32,), True),
            palette=palette_data(palettes[sid]['colors']))
    return result


def color_distance(first, second):
    """Balanced unit-mass transport with CIEDE2000 ground costs, no cost rescaling."""
    lab_a, mass_a = first
    lab_b, mass_b = second
    cost = deltaE_ciede2000(lab_a[:, None, :], lab_b[None, :, :], kL=1, kC=1, kH=1)
    n, m = cost.shape
    # Each transport row supplies one source mass; each column receives one destination mass.
    constraints = np.zeros((n + m, n * m))
    for i in range(n):
        constraints[i, i*m:(i+1)*m] = 1
    for j in range(m):
        constraints[n+j, j::m] = 1
    masses = np.r_[mass_a, mass_b]
    # The final marginal equation is redundant because both distributions have unit mass.
    solved = linprog(cost.ravel(), A_eq=constraints[:-1], b_eq=masses[:-1],
                     bounds=(0, None), method='highs-ds',
                     options={'primal_feasibility_tolerance': 1e-9, 'dual_feasibility_tolerance': 1e-9})
    if not solved.success:
        raise RuntimeError(f'Transport solver failed: {solved.message}')
    if np.max(np.abs(constraints @ solved.x - masses)) > 1e-8 or np.min(solved.x) < -1e-9:
        raise RuntimeError('Transport solution violates marginal constraints')
    value = float(solved.fun)
    if not np.isfinite(value) or value < 0:
        raise RuntimeError('Invalid transport cost')
    return value


def distances(first, second):
    return dict(color_emd_distance=color_distance(first['palette'], second['palette']),
                foreground_distance=float(abs(first['density'][0]-second['density'][0])),
                edge_distance=float(abs(first['density'][1]-second['density'][1])),
                layout_distance=float(np.mean(np.abs(first['layout']-second['layout']))))


def make_pairs(features):
    pairs = []
    for app in sorted({screen['app_id'] for screen in features.values()}):
        ids = sorted(sid for sid, screen in features.items() if screen['app_id'] == app)
        for a, b in combinations(ids, 2):
            flow_a, flow_b = features[a]['flow_id'], features[b]['flow_id']
            pairs.append(dict(screen_a=a, screen_b=b, app_id=app, flow_a=flow_a, flow_b=flow_b,
                              pair_type='within_flow' if flow_a == flow_b else 'cross_flow'))
    return pairs


def smoke_selection(pairs, features):
    selected = set()
    for app in sorted({p['app_id'] for p in pairs}):
        app_pairs = [p for p in pairs if p['app_id'] == app]
        for kind in ['within_flow', 'cross_flow']:
            match = next((p for p in app_pairs if p['pair_type'] == kind), None)
            if match:
                selected.add((match['screen_a'], match['screen_b']))
        extreme = max(app_pairs, key=lambda p: abs(features[p['screen_a']]['density'][0]-features[p['screen_b']]['density'][0]))
        selected.add((extreme['screen_a'], extreme['screen_b']))
    return [p for p in pairs if (p['screen_a'], p['screen_b']) in selected]


def build_tables(features, smoke=False):
    pairs = make_pairs(features)
    if smoke:
        pairs = smoke_selection(pairs, features)
    rows, similarities = [], []
    for pair in pairs:
        a, b = features[pair['screen_a']], features[pair['screen_b']]
        metrics = distances(a, b)
        if smoke:
            reverse = distances(b, a)
            if not all(np.isclose(metrics[k], reverse[k], atol=1e-8, rtol=0) for k in DISTANCES):
                raise RuntimeError('Smoke symmetry check failed')
        if not all(np.isfinite(x) for x in metrics.values()) or not all(0 <= metrics[k] <= 1 for k in DISTANCES[1:]):
            raise RuntimeError('Invalid pairwise feature distance')
        rows.append(dict(pair, **metrics))
        similarities.append(dict(pair, **{k.replace('_distance', '_similarity'): 1-metrics[k] for k in DISTANCES[1:]}))
    summary = []
    for app in sorted({p['app_id'] for p in rows}):
        for kind in ['within_flow', 'cross_flow', 'all']:
            selected = [p for p in rows if p['app_id'] == app and (kind == 'all' or p['pair_type'] == kind)]
            if not selected:
                continue
            for metric in DISTANCES:
                values = np.array([p[metric] for p in selected])
                summary.append(dict(app_id=app, pair_type=kind, metric=metric, pair_count=len(values),
                    mean=float(values.mean()), std_sample=float(values.std(ddof=1)) if len(values)>1 else '',
                    minimum=float(values.min()), q25=float(np.quantile(values, .25)), median=float(np.median(values)),
                    q75=float(np.quantile(values, .75)), maximum=float(values.max())))
    return rows, similarities, summary


def write_table(path, rows):
    if not rows:
        raise ValueError('No pairs to export')
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def input_hashes(features_dir, metadata_dir):
    paths = [Path(features_dir)/name for name in ['visual_features.csv','layout_vectors.csv','color_palettes.json','configuration.json','run_summary.json']]
    paths += [Path(metadata_dir)/name for name in ['screens.csv','flows.csv']]
    return {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def run(output, features_dir=ROOT/'results_corrected_pilot', metadata_dir=ROOT/'PILOT/screenshots', smoke=False):
    output = Path(output)
    if output.exists():
        raise ValueError('Use a fresh output directory; previous outputs will not be overwritten')
    before = input_hashes(features_dir, metadata_dir)
    features = load_features(features_dir, metadata_dir)
    tables = build_tables(features, smoke)
    if before != input_hashes(features_dir, metadata_dir):
        raise RuntimeError('Inputs changed during scoring')
    # Calculate and validate all scores before creating any output files.
    output.mkdir(parents=True)
    for name, rows in zip(['pairwise_distances.csv','pairwise_similarities.csv','pairwise_summary.csv'], tables):
        write_table(output/name, rows)
    counts = []
    for app in sorted({f['app_id'] for f in features.values()}):
        n = sum(f['app_id']==app for f in features.values())
        pairs = [p for p in tables[0] if p['app_id']==app]
        counts.append(dict(app_id=app, screens=n, expected_full_pairs=n*(n-1)//2, exported_pairs=len(pairs),
            within_flow=sum(p['pair_type']=='within_flow' for p in pairs), cross_flow=sum(p['pair_type']=='cross_flow' for p in pairs)))
    write_table(output/'pair_counts.csv', counts)
    configuration = dict(feature_version='Approved full-pilot final baseline correction; no feature recomputation',
        features_dir=str(Path(features_dir).resolve()), smoke=smoke, color_ground_cost='CIEDE2000, kL=kC=kH=1',
        transport='Balanced unit mass, scipy.optimize.linprog highs-ds; raw optimal cost; no regularization or cost normalization',
        color_similarity='Not computed; mapping scale not approved', layout_order='cell_00..cell_31 row-major 4x8',
        dependencies={name:version(name) for name in ['numpy','scipy','scikit-image']}, input_sha256=before,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (output/'configuration.json').write_text(json.dumps(configuration, indent=2)+'\n')
    print(json.dumps(dict(screens=len(features), pairs=len(tables[0]), applications=counts), indent=2))
    return tables


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results_pairwise_baseline')
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    run(args.output, smoke=args.smoke)
