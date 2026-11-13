import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pipeline


class EcosystemTests(unittest.TestCase):
    def test_packaged_integrity_and_no_graph_code(self):
        manifest=json.loads((ROOT/'provenance.json').read_text())['files']
        for name,info in manifest.items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),info['sha256'],name)
        self.assertFalse((ROOT/'runtime/graph_foundation.py').exists())
        self.assertFalse((ROOT/'runtime/results/graph_foundation').exists())

    def test_reuse_full_workflow_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            output=Path(tmp)/'reuse'
            result=pipeline.main(ROOT/'runtime',output)
            self.assertEqual(len(result['stages']),6)
            self.assertTrue(result['input_files_unchanged'])
            self.assertTrue(all(r['status']=='reused_validated_saved_results' for r in result['stages']))
            with self.assertRaises(FileExistsError):pipeline.main(ROOT/'runtime',output)

    def test_individual_tau_execution(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            result=pipeline.main(ROOT/'runtime',Path(tmp)/'tau','tau-sensitivity',True)
            self.assertEqual(len(result['stages']),1)
            self.assertEqual(result['stages'][0]['status'],'recomputed_validated')
            report=Path(tmp)/'tau'/result['stages'][0]['location']/'tau_sensitivity_review.md'
            self.assertTrue(report.is_file())

    def test_missing_fixture_fails_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            donor=Path(tmp)/'incomplete';donor.mkdir();output=Path(tmp)/'output'
            with self.assertRaisesRegex(FileNotFoundError,'Missing required pilot fixtures'):
                pipeline.main(donor,output)
            self.assertFalse(output.exists())

    def test_original_numerical_checks(self):
        cases=['test_features','test_pairwise_baseline',
               'test_composite_baseline.CompositeTests.test_identity_symmetry_weights_and_extremes']
        result=subprocess.run([sys.executable,'-m','unittest','-v',*cases],cwd=ROOT/'runtime',capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        edge=ROOT/'runtime/experiments/edge_similarity_evaluation'
        result=subprocess.run([sys.executable,'-m','unittest','-v',
            'test_evaluation.EvaluationTests.test_metric_definitions',
            'test_evaluation.EvaluationTests.test_sampling_and_baseline'],cwd=edge,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


if __name__=='__main__':unittest.main()
