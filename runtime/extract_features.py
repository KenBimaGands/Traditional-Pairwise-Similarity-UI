"""Reproducible visual feature extraction; see README.md for definitions."""
import argparse
import csv
from dataclasses import asdict, dataclass
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits


# One immutable set of settings keeps preprocessing consistent across screenshots.
@dataclass(frozen=True)
class Config:
    # Longest processed side, in pixels; aspect ratio is preserved.
    max_dimension: int = 512
    # Fixed initialization makes clustering repeatable in the same environment.
    seed: int = 42
    # RGB-distance cutoff for foreground; this is a heuristic, not a learned boundary.
    background_distance: float = 25.0
    # Ignore smaller components for boxes/layout, but keep them in coverage.
    min_component_area: int = 12
    # Odd Gaussian window size and its standard deviation, followed by Canny thresholds.
    blur_kernel: int = 5
    blur_sigma: float = 1.0
    canny_low: int = 50
    canny_high: int = 150


# Decode one image and return (RGB array, oriented original width/height).
def load_image(path, config):
    # The context manager closes the file even if decoding fails.
    with Image.open(path) as source:
        if source.format not in {'PNG', 'JPEG', 'WEBP', 'BMP', 'TIFF'}:
            raise ValueError(f'Unsupported image format: {source.format}')
        # Force decoding now so corrupt files raise an error inside this function.
        source.load()
        # Honor camera orientation; RGBA exposes transparency before RGB conversion.
        image = ImageOps.exif_transpose(source).convert('RGBA')
        # Transparent pixels need a defined visible background: composite over white.
        background = Image.new('RGBA', image.size, 'white')
        image = Image.alpha_composite(background, image).convert('RGB')
        original_size = image.size
        # thumbnail changes this image in place, fitting the bounds without stretching/upscaling.
        image.thumbnail((config.max_dimension, config.max_dimension), Image.Resampling.LANCZOS)
        # Array shape is (height, width, 3); pixel values are unsigned integers from 0 to 255.
        return np.asarray(image), original_size


# Compute one screenshot's features; also return masks for visual inspection.
def extract(rgb, config=Config()):
    height, width = rgb.shape[:2]
    # Flatten pixels to RGB rows, then retain each unique color and its frequency.
    colors, counts = np.unique(rgb.reshape(-1, 3), axis=0, return_counts=True)
    # Weighting unique colors preserves the full-pixel clustering objective without duplicates.
    with threadpool_limits(limits=1):
        # Use at most five clusters, and never request more clusters than unique colors.
        model = KMeans(n_clusters=min(5, len(colors)), init='k-means++',
                       random_state=config.seed, n_init=10, algorithm='lloyd')
        model.fit(colors.astype(float), sample_weight=counts)
    # Sum pixel counts assigned to each cluster, then normalize to proportions summing to one.
    weights = np.bincount(model.labels_, weights=counts, minlength=model.n_clusters)
    weights /= weights.sum()
    centers = np.clip(model.cluster_centers_, 0, 255)
    # Float RGB in [0,1] gives standard Lab; [None] temporarily adds an image-row dimension.
    lab = cv2.cvtColor((centers.astype(np.float32) / 255)[None], cv2.COLOR_RGB2LAB)[0]
    # Sort most common colors first; RGB values break equal-proportion ties deterministically.
    order = sorted(range(len(weights)), key=lambda i: (-weights[i], *centers[i]))
    palette = [dict(rgb=centers[i].tolist(), lab=lab[i].tolist(), proportion=float(weights[i])) for i in order]
    # shortcut: one dominant border color assumes a mostly uniform background; review photo/gradient screens.
    # Read the perimeter once per pixel: top/bottom rows plus side columns excluding corners.
    border = np.concatenate([rgb[0], rgb[-1], rgb[1:-1, 0], rgb[1:-1, -1]])
    # Coarse RGB bins group nearly equal perimeter colors; the most frequent bin wins.
    quantized = border // 16
    bins, frequencies = np.unique(quantized, axis=0, return_counts=True)
    dominant = bins[np.argmax(frequencies)]
    # Estimate background from the original colors in that bin, not its quantized values.
    background = np.median(border[np.all(quantized == dominant, axis=1)], axis=0)
    # Float subtraction avoids uint8 wraparound; distance above the cutoff becomes foreground 1.
    mask = (np.linalg.norm(rgb.astype(float) - background, axis=2) > config.background_distance).astype(np.uint8)
    # Edges are an independent feature: grayscale -> blur to reduce noise -> Canny.
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (config.blur_kernel, config.blur_kernel), config.blur_sigma)
    edges = cv2.Canny(blurred, config.canny_low, config.canny_high)
    # Eight-connectivity joins side/corner neighbors; stats contains x, y, width, height, area.
    _, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    boxes = []
    # One binary rectangle-union mask prevents overlapping boxes from being counted twice.
    union = np.zeros_like(mask)
    # Label zero is background; inspect only foreground components.
    for x, y, w, h, area in stats[1:]:
        if area >= config.min_component_area:
            # Store top-left and exclusive bottom-right coordinates normalized to [0,1].
            boxes.append([float(x / width), float(y / height), float((x+w) / width), float((y+h) / height)])
            # Fill the complete bounding rectangle, including empty space inside it.
            union[y:y+h, x:x+w] = 1
    # Five x boundaries and nine y boundaries define four columns and eight rows.
    xs, ys = np.linspace(0, width, 5, dtype=int), np.linspace(0, height, 9, dtype=int)
    # A binary cell mean is its occupied-pixel fraction; output order is left-to-right, top-to-bottom.
    layout = [float(union[ys[r]:ys[r+1], xs[c]:xs[c+1]].mean()) for r in range(8) for c in range(4)]
    # Return JSON-friendly values; coverage counts foreground pixels, edges counts detected edges.
    return dict(palette=palette, background_rgb=background.tolist(),
                foreground_coverage=float(mask.mean()), edge_density=float((edges > 0).mean()),
                boxes=boxes, layout=layout), mask, edges


# Write a six-panel diagnostic image; drawing never modifies the source screenshot.
def visualize(rgb, features, mask, edges, path):
    import matplotlib
    # Use a file-rendering backend so plotting works without a desktop window.
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    # Build a two-row, three-column figure with one panel per visual diagnostic.
    fig, axes = plt.subplots(2, 3, figsize=(10, 11))
    height, width = rgb.shape[:2]
    for ax, title in zip(axes.flat, ['Screenshot', 'Weighted palette', 'Foreground mask', 'Canny edges', 'Bounding boxes', '4 × 8 occupancy']):
        ax.set_title(title)
        ax.axis('off')
    axes[0, 0].imshow(rgb)
    left = 0
    # Each bar segment has width equal to its cluster proportion.
    for index, color in enumerate(features['palette']):
        axes[0, 1].barh(0, color['proportion'], left=left, color=np.array(color['rgb'])/255)
        axes[0, 1].text(0, 1.5 + index * .65, f"{index+1}: {color['proportion']:.2%}  RGB {np.rint(color['rgb']).astype(int).tolist()}", fontsize=8)
        left += color['proportion']
    axes[0, 1].set(xlim=(0, 1), ylim=(5, -1))
    axes[0, 2].imshow(mask, cmap='gray', vmin=0, vmax=1)
    axes[1, 0].imshow(edges, cmap='gray', vmin=0, vmax=255)
    axes[1, 1].imshow(rgb)
    # Convert normalized coordinates back to pixels only for drawing boxes.
    for x0, y0, x1, y1 in features['boxes']:
        axes[1, 1].add_patch(Rectangle((x0*width, y0*height), (x1-x0)*width, (y1-y0)*height, fill=False, edgecolor='red', linewidth=.5))
    axes[1, 2].imshow(rgb)
    # Reshape the flat vector for a spatial heat overlay; fixed color limits allow comparison.
    axes[1, 2].imshow(np.array(features['layout']).reshape(8, 4), extent=(-.5, width-.5, height-.5, -.5), cmap='magma', alpha=.5, vmin=0, vmax=1, interpolation='nearest', aspect='equal')
    for x in np.linspace(0, width, 5):
        axes[1, 2].axvline(x-.5, color='cyan', linewidth=.6)
    for y in np.linspace(0, height, 9):
        axes[1, 2].axhline(y-.5, color='cyan', linewidth=.6)
    # Save the figure and release it so a batch does not accumulate open figures.
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


# Read metadata, process selected screenshots, and export successful features plus error rows.
def run(metadata, output, config=Config(), screen_ids=None, plots=False):
    metadata, output = Path(metadata), Path(output)
    # utf-8-sig removes the metadata BOM; DictReader maps column names to values.
    with metadata.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    ids = [row['screen_id'] for row in rows]
    # Duplicate IDs would overwrite JSON entries, so reject them before processing.
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate screen_id in metadata')
    # An optional selection must contain known IDs; preserve the metadata row order.
    if screen_ids:
        unknown = set(screen_ids) - set(ids)
        if unknown:
            raise ValueError(f'Unknown screen IDs: {sorted(unknown)}')
        rows = [row for row in rows if row['screen_id'] in screen_ids]
    # Create the destination; existing numerical files will be overwritten by this baseline runner.
    output.mkdir(parents=True, exist_ok=True)
    if plots:
        (output / 'visualizations').mkdir(exist_ok=True)
    results, palettes, boxes, layouts = [], {}, {}, []
    for row in rows:
        sid = row['screen_id']
        # Begin with an error row; populate feature fields only after extraction succeeds.
        record = dict(screen_id=sid, status='error', error='', original_width='', original_height='', width='', height='', foreground_coverage='', edge_density='', component_count='')
        try:
            # Resolve relative paths against the CSV directory, then reject paths outside that directory.
            path = (metadata.parent / row['image_path']).resolve()
            if not path.is_relative_to(metadata.parent.resolve()):
                raise ValueError('Image path escapes dataset root')
            rgb, original = load_image(path, config)
            # A tiny image could create empty grid cells and undefined occupancy means.
            if min(rgb.shape[:2]) < 8:
                raise ValueError('Image too small for 4 × 8 grid')
            features, mask, edges = extract(rgb, config)
            if plots:
                # Index-based filenames keep arbitrary metadata IDs out of filesystem paths.
                visualize(rgb, features, mask, edges, output / 'visualizations' / f'{len(results):04d}.png')
            # Keep original IDs as keys; layout cell names make vector ordering explicit in CSV.
            record.update(status='ok', original_width=original[0], original_height=original[1], width=rgb.shape[1], height=rgb.shape[0], foreground_coverage=features['foreground_coverage'], edge_density=features['edge_density'], component_count=len(features['boxes']))
            palettes[sid] = dict(colors=features['palette'], background_rgb=features['background_rgb'])
            boxes[sid] = features['boxes']
            layouts.append(dict(screen_id=sid, **{f'cell_{i:02d}': v for i, v in enumerate(features['layout'])}))
        # Record expected input/decoding errors and continue with other screenshots.
        except (OSError, ValueError, Image.DecompressionBombError) as error:
            record['error'] = str(error)
        results.append(record)
    # Write scalar features/error status and the separate 32-value layout table.
    for name, data, fields in [('visual_features.csv', results, list(results[0]) if results else ['screen_id', 'status', 'error']), ('layout_vectors.csv', layouts, ['screen_id'] + [f'cell_{i:02d}' for i in range(32)])]:
        with (output / name).open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
    # JSON preserves nested palettes/boxes; save settings alongside results for reproduction.
    for name, data in [('color_palettes.json', palettes), ('bounding_boxes.json', boxes), ('config.json', asdict(config))]:
        (output / name).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    print(f"{sum(r['status']=='ok' for r in results)}/{len(results)} extracted → {output}")
    return results


# This block runs only when invoked as a script, not when imported in a notebook/test.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata', default='PILOT/screenshots/screens.csv')
    parser.add_argument('--output', default='results')
    parser.add_argument('--config', help='JSON object overriding Config defaults')
    parser.add_argument('--screen-ids', nargs='+')
    parser.add_argument('--plots', action='store_true')
    # Translate command-line choices into a Config, optionally overriding defaults from JSON.
    args = parser.parse_args()
    config = Config(**json.loads(Path(args.config).read_text())) if args.config else Config()
    # Reject settings that would make preprocessing or edge detection invalid.
    if config.max_dimension < 8 or config.min_component_area < 1 or config.background_distance < 0 or config.blur_kernel < 1 or config.blur_kernel % 2 != 1 or config.blur_sigma <= 0 or not 0 <= config.canny_low < config.canny_high <= 255:
        parser.error('Invalid preprocessing configuration')
    records = run(args.metadata, args.output, config, args.screen_ids, args.plots)
    # Exit code 1 signals at least one failed screenshot, while successful outputs remain saved.
    raise SystemExit(any(row['status'] != 'ok' for row in records))
