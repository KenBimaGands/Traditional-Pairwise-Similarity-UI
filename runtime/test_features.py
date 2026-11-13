import csv
from pathlib import Path
import tempfile
import unittest

import numpy as np
from PIL import Image
from extract_features import Config, extract, load_image, run


class FeatureTests(unittest.TestCase):
    def test_dataset_paths_and_formats(self):
        with open('PILOT/screenshots/screens.csv', encoding='utf-8-sig') as handle:
            for row in csv.DictReader(handle):
                with self.subTest(screen_id=row['screen_id']):
                    rgb, _ = load_image(Path('PILOT/screenshots') / row['image_path'], Config())
                    self.assertEqual(rgb.shape[2], 3)
                    self.assertLessEqual(max(rgb.shape[:2]), 512)

    def test_features_and_determinism(self):
        rng = np.random.default_rng(4)
        images = [np.full((80, 40, 3), 255, dtype=np.uint8), rng.integers(0, 256, (80, 40, 3), dtype=np.uint8)]
        for rgb in images:
            features, _, _ = extract(rgb)
            self.assertEqual(features, extract(rgb)[0])
            self.assertLessEqual(len(features['palette']), 5)
            self.assertAlmostEqual(sum(c['proportion'] for c in features['palette']), 1)
            for name in ['foreground_coverage', 'edge_density']:
                self.assertTrue(0 <= features[name] <= 1)
            self.assertEqual(len(features['layout']), 32)
            self.assertTrue(all(0 <= v <= 1 for v in features['layout']))
            for x0, y0, x1, y1 in features['boxes']:
                self.assertTrue(0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1)
        self.assertEqual(len(extract(images[0])[0]['palette']), 1)
        self.assertEqual(extract(images[0])[0]['layout'], [0.] * 32)

    def test_known_palette_and_coverage(self):
        rgb = np.full((80, 40, 3), 255, dtype=np.uint8)
        rgb[20:60, 10:30] = 0
        features, _, _ = extract(rgb)
        self.assertEqual(sorted(c['proportion'] for c in features['palette']), [.25, .75])
        self.assertAlmostEqual(features['palette'][0]['lab'][0], 100, places=3)
        self.assertAlmostEqual(features['foreground_coverage'], .25)
        self.assertEqual(features['boxes'], [[.25, .25, .75, .75]])
        self.assertAlmostEqual(np.mean(features['layout']), .25)

    def test_overlapping_boxes_are_union(self):
        rgb = np.full((80, 40, 3), 255, dtype=np.uint8)
        rgb[10:70, 5] = 0
        rgb[10, 5:35] = 0
        rgb[69, 5:35] = 0
        rgb[30:50, 20:25] = 0
        features, _, _ = extract(rgb, Config(min_component_area=1))
        self.assertEqual(len(features['boxes']), 2)
        self.assertAlmostEqual(np.mean(features['layout']), 30*60/(40*80))

    def test_bad_images_do_not_stop_batch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            Image.new('RGB', (40, 80), 'white').save(root / 'valid.png')
            (root / 'bad.png').write_text('corrupt')
            (root / 'screens.csv').write_text('screen_id,image_path\nmissing,missing.png\ncorrupt,bad.png\nvalid,valid.png\n')
            rows = run(root / 'screens.csv', root / 'results')
            self.assertEqual([r['status'] for r in rows], ['error', 'error', 'ok'])
            self.assertTrue(all(r['error'] for r in rows[:2]))


if __name__ == '__main__':
    unittest.main()
