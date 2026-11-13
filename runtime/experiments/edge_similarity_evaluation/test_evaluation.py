"""Analytic edge cases and complete byte-for-byte experiment reproduction."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
import numpy as np
from evaluate import scores, load, sample_pairs, run, HERE


class EvaluationTests(unittest.TestCase):
    def test_metric_definitions(self):
        np.testing.assert_array_equal(scores([0,.2,1],[0,.2,1]),np.ones((3,3)))
        np.testing.assert_allclose(scores(0,.2),[.8,0,1e-5/(.2+1e-5)])
        np.testing.assert_allclose(scores(.2,.8),[.4,.25,(.2+1e-5)/(.8+1e-5)])
        np.testing.assert_array_equal(scores(.2,0),scores(0,.2))
        a=np.array([0,.001,.2,1]); b=np.array([1,.3,0,.1])
        np.testing.assert_allclose(scores(a,b)[:,2],np.exp(-np.abs(np.log((a+1e-5)/(b+1e-5)))))
        np.testing.assert_allclose(scores(.002,.08,1e-14)[1:], [.025,.025],atol=1e-11)
        for value in [-.1,1.1,np.nan,np.inf]:
            with self.assertRaises(ValueError): scores(value,.1)
        for epsilon in [0,-1,np.nan,np.inf]:
            with self.assertRaises(ValueError): scores(.1,.2,epsilon)

    def test_sampling_and_baseline(self):
        rows,_,_=load(); selected,allocation=sample_pairs(rows)
        self.assertEqual(sample_pairs(rows)[0],selected)
        self.assertEqual(len({r['pair_id'] for r in selected}),24)
        for kind in ['within_flow','cross_flow']:
            group=[r for r in selected if r['pair_type']==kind]
            self.assertEqual(len(group),12)
            self.assertEqual(len({r['app_id'] for r in group}),5)
            self.assertEqual(sorted(a['selected'] for a in allocation if a['pair_type']==kind),[2,2,2,3,3])
        # Changing every metric leaves the random IDs unchanged.
        changed=[dict(r,M0=0,M1=0,M2=0) for r in rows]
        self.assertEqual([r['pair_id'] for r in selected],[r['pair_id'] for r in sample_pairs(changed)[0]])
        short=[r for r in rows if r['app_id']=='APP05'][:3]
        self.assertEqual(len(sample_pairs(short)[0]),3)

    def test_complete_reproduction(self):
        with tempfile.TemporaryDirectory() as temporary,contextlib.redirect_stdout(io.StringIO()):
            directories=[Path(temporary)/name for name in ['first','second']]
            for directory in directories: run(directory)
            first,second=directories
            files={p.relative_to(first) for p in first.rglob('*') if p.is_file()}
            self.assertEqual(files,{p.relative_to(second) for p in second.rglob('*') if p.is_file()})
            for relative in files:
                self.assertEqual((first/relative).read_bytes(),(second/relative).read_bytes(),str(relative))
                self.assertEqual((first/relative).read_bytes(),(HERE/relative).read_bytes(),str(relative))
            with self.assertRaises(FileExistsError): run(first)


if __name__=='__main__': unittest.main()
