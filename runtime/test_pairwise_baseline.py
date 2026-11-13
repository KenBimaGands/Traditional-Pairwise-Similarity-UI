import contextlib
import io
from itertools import combinations
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from skimage.color import deltaE_ciede2000
from pairwise_baseline import (ROOT, DISTANCES, load_features, palette_data, color_distance,
                               distances, make_pairs, run, numeric)


def palette(colors, weights):
    return palette_data([dict(lab=c, proportion=w) for c,w in zip(colors,weights)])


class PairwiseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.features = load_features(ROOT/'results_corrected_pilot', ROOT/'PILOT/screenshots')

    def test_ciede_reference_and_checkable_transport(self):
        # Published Sharma CIEDE2000 reference pair, expected value rounded to four decimals.
        self.assertAlmostEqual(float(deltaE_ciede2000([50,2.6772,-79.7751],[50,0,-82.7485])),2.0425,places=4)
        black, white = [0,0,0], [100,0,0]
        a = palette([black,white],[.75,.25]); b = palette([black,white],[.25,.75])
        self.assertAlmostEqual(color_distance(a,b),50,places=8)
        self.assertAlmostEqual(color_distance(palette([black],[1]),palette([white],[1])),100,places=8)
        split = palette([black,black,white],[.25,.5,.25])
        self.assertAlmostEqual(color_distance(a,split),0,places=8)
        self.assertAlmostEqual(color_distance(a,palette([white,black],[.25,.75])),0,places=8)
        for k in range(1,6):
            p = palette([[i*15,0,0] for i in range(k)],[1/k]*k)
            self.assertAlmostEqual(color_distance(p,p),0,places=8)

    def test_identity_symmetry_and_known_scalar_differences(self):
        values = list(self.features.values())
        for feature in values:
            self.assertTrue(all(v==0 for v in distances(feature,feature).values()))
        for a,b in zip(values,values[1:]):
            np.testing.assert_allclose(list(distances(a,b).values()),list(distances(b,a).values()),atol=1e-8,rtol=0)
        a = dict(values[0],density=np.array([0.,.25]),layout=np.zeros(32))
        b = dict(values[0],density=np.array([1.,.75]),layout=np.ones(32))
        d = distances(a,b)
        self.assertEqual([d[k] for k in DISTANCES[1:]],[1.,.5,1.])

    def test_pair_enumeration(self):
        pairs=make_pairs(self.features); seen=set()
        for pair in pairs:
            a,b=pair['screen_a'],pair['screen_b']
            self.assertLess(a,b); self.assertNotIn((a,b),seen); seen.add((a,b))
            self.assertEqual(self.features[a]['app_id'],self.features[b]['app_id'])
            self.assertEqual(pair['app_id'],self.features[a]['app_id'])
            self.assertEqual(pair['flow_a'],self.features[a]['flow_id'])
            self.assertEqual(pair['flow_b'],self.features[b]['flow_id'])
            self.assertEqual(pair['pair_type'],'within_flow' if pair['flow_a']==pair['flow_b'] else 'cross_flow')
        for app in sorted({f['app_id'] for f in self.features.values()}):
            ids=[sid for sid,f in self.features.items() if f['app_id']==app]
            actual=[p for p in pairs if p['app_id']==app]
            self.assertEqual(len(actual),len(ids)*(len(ids)-1)//2)
            within=sum(self.features[a]['flow_id']==self.features[b]['flow_id'] for a,b in combinations(ids,2))
            self.assertEqual(sum(p['pair_type']=='within_flow' for p in actual),within)

    def test_invalid_features_rejected(self):
        for masses in [[.5,.6],[-.1,1.1],[float('nan'),1]]:
            with self.assertRaises(ValueError): palette([[0,0,0],[100,0,0]],masses)
        with self.assertRaises(ValueError): numeric([0]*31,(32,),True)
        with self.assertRaises(ValueError): numeric([float('inf')]*32,(32,),True)
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)
            for name in ['visual_features.csv','layout_vectors.csv','color_palettes.json']:
                (target/name).write_bytes((ROOT/'results_corrected_pilot'/name).read_bytes())
            palettes=json.loads((target/'color_palettes.json').read_text()); palettes.pop(next(iter(palettes)))
            (target/'color_palettes.json').write_text(json.dumps(palettes))
            with self.assertRaises(ValueError): load_features(target,ROOT/'PILOT/screenshots')

    def test_repeated_full_exports_and_alignment(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            a,b=Path(directory)/'one',Path(directory)/'two'
            rows,sims,summary=run(a); run(b)
            for file in a.iterdir(): self.assertEqual(file.read_bytes(),(b/file.name).read_bytes())
            self.assertEqual(len(rows),len(make_pairs(self.features)))
            self.assertEqual(len(rows),len(sims))
            for row,sim in zip(rows,sims):
                self.assertEqual(row['screen_a'],sim['screen_a']); self.assertEqual(row['screen_b'],sim['screen_b'])
                self.assertTrue(all(np.isfinite(row[k]) for k in DISTANCES))
                for key in DISTANCES[1:]:
                    self.assertTrue(0<=row[key]<=1)
                    self.assertEqual(sim[key.replace('_distance','_similarity')],1-row[key])
                self.assertNotIn('color_similarity',sim)
            for group in summary:
                for key in ['mean','minimum','q25','median','q75','maximum']:
                    self.assertTrue(np.isfinite(group[key]))
            with self.assertRaises(ValueError): run(a)


if __name__=='__main__': unittest.main()
