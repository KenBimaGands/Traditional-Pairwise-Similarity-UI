"""Analytic, data-boundary and complete reproduction checks for composite v1."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import composite_baseline as cb


class CompositeTests(unittest.TestCase):
    def test_identity_symmetry_weights_and_extremes(self):
        for name,tau,method in cb.CONFIGS:
            identity=cb.score(0,.3,.3,.2,.2,0,tau,method)
            self.assertEqual(identity['composite_similarity'],1)
            self.assertEqual(cb.score(0,0,0,0,0,0,tau,method)['edge_similarity'],1)
            self.assertEqual(cb.score(0,0,0,0,1,0,tau,method)['edge_similarity'],0)
            a=cb.score(7,.1,.6,.02,.05,.3,tau,method)
            b=cb.score(7,.6,.1,.05,.02,.3,tau,method)
            self.assertEqual(a,b)
            for k in cb.SIMILARITIES: self.assertTrue(np.isfinite(a[k]) and 0<=a[k]<=1)
            expected=(np.exp(-7/tau)+(.5+(.4 if method=='M1' else .97))/2+.7)/3
            self.assertAlmostEqual(a['composite_similarity'],expected)
            self.assertAlmostEqual(sum(a[k] for k in cb.CONTRIBUTIONS[:3]),expected)
            self.assertAlmostEqual(a['foreground_contribution']+a['edge_contribution'],a['density_contribution'])
            self.assertEqual(cb.score(1e308,0,1,0,1,1,tau,method)['composite_similarity'],0)
        for inputs in [(np.nan,0,0,0,0,0),(-1,0,0,0,0,0),(0,-.1,0,0,0,0),
                       (0,0,0,0,1.1,0),(0,0,0,0,0,np.inf)]:
            with self.assertRaises(ValueError): cb.score(*inputs)
        for tau in [0,-1,np.nan,np.inf]:
            with self.assertRaises(ValueError): cb.score(0,0,0,0,0,0,tau)
        with self.assertRaises(ValueError): cb.score(0,0,0,0,0,0,edge_method='M2')

    def test_pair_universe_and_reject_duplicate(self):
        rows=cb.load_records()
        self.assertEqual(len(rows),709)
        self.assertEqual(len({r['pair_id'] for r in rows}),709)
        read=cb.read_csv
        def duplicate(path):
            records=read(path)
            if Path(path).name=='pairwise_distances.csv': records[-1]=records[0]
            return records
        with patch.object(cb,'read_csv',side_effect=duplicate):
            with self.assertRaises(ValueError): cb.load_records()

    def test_complete_reproduction(self):
        with tempfile.TemporaryDirectory() as temporary,contextlib.redirect_stdout(io.StringIO()):
            first,second=[Path(temporary)/name for name in ['first','second']]
            cb.run(first); cb.run(second)
            generated={p.relative_to(first) for p in first.rglob('*') if p.is_file()}
            self.assertEqual(generated,{p.relative_to(second) for p in second.rglob('*') if p.is_file()})
            for name in generated:
                self.assertEqual((first/name).read_bytes(),(second/name).read_bytes(),str(name))
                self.assertEqual((first/name).read_bytes(),(cb.OUTPUT/name).read_bytes(),str(name))
            with self.assertRaises(FileExistsError): cb.run(first)


if __name__=='__main__': unittest.main()
