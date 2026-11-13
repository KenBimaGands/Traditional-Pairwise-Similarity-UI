# UI Visual Consistency — complete traditional pre-graph ecosystem

One repository containing **six modular Codex skills and one orchestrator**, with the actual extraction, pairwise, diagnostic, edge-experiment, composite and tau-review implementations. It includes the fixed 82-screen pilot and saved outputs so the entire upstream-to-review workflow can run independently of the original thesis folder.

This is the complete **traditional visual-only** pipeline, not just the older tau review subpackage. Graph construction/scoring is deliberately excluded. No mathematical formulations or provisional research choices were changed.

## Seven skills

| Skill | Responsibility |
|---|---|
| `$ui-visual-consistency` | Route full/individual workflows, reuse results, validate contracts and stop on errors |
| `$feature-extraction` | Original feature definitions plus frozen approved mask correction |
| `$pairwise-similarity` | 709 raw EMD/density/layout distances and original M0 similarities |
| `$descriptor-investigation` | Descriptor distributions and purposive visual diagnostics |
| `$edge-similarity` | Experimental M0/M1/M2 comparison with a deterministic random sample |
| `$composite-scoring` | Provisional M1/tau=10/equal-group composite and fixed sensitivities |
| `$tau-sensitivity` | Review saved M1 tau=5/10/20 tables; cannot itself regenerate upstream scores |

[Audit](docs/audit.md) · [Architecture](docs/pipeline-architecture.md) · [Data contracts](docs/data-contracts.md) · [Methodology](docs/methodology.md) · [Validation](docs/validation.md)

## Structure

```text
ui-visual-consistency/
  README.md, SKILL.md, agents/openai.yaml
  pipeline.py, requirements.txt, provenance.json
  skills/
    feature-extraction/SKILL.md
    pairwise-similarity/SKILL.md
    descriptor-investigation/SKILL.md
    edge-similarity/SKILL.md
    composite-scoring/SKILL.md
    tau-sensitivity/SKILL.md
    # Each module also has agents/openai.yaml.
  runtime/
    extract_features.py, pairwise_baseline.py, investigate_pairwise.py
    composite_baseline.py, review_tau_sensitivity.py
    experiments/final_baseline_correction/   # code and frozen sample
    experiments/preprocessing_v2/           # imported existing helpers
    experiments/edge_similarity_evaluation/ # code and experiment evidence
    PILOT/screenshots/                       # 82 images and metadata
    results/, results_corrected_pilot/, results_pairwise_baseline/
    pairwise_investigation/                  # saved diagnostic evidence
    visual_quality_review/                  # fixed review selection/context
  docs/
  tests/
  evidence/                                 # executed integration evidence
```

Shared source under runtime preserves original import relationships instead of making six divergent script copies. Each module can be invoked separately but requires this compatible repository/runtime; skills are not six separate lightweight code distributions. The original standalone tau subpackage remains separate and unchanged.

## Environment and dependencies

Tested with Python **3.13.7** and the existing thesis `.venv`. For a separate checkout, from this repository root:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

On Windows substitute `.venv\Scripts\python.exe`. Do not run Python with `-O`: existing research scripts use assertions for numerical audits. No dependency was installed during packaging.

| Dependency | Purpose |
|---|---|
| NumPy | Arrays, feature arithmetic, statistics and deterministic sampling |
| SciPy | Balanced color transport solver and rank correlations |
| scikit-image | Established CIEDE2000 ground color differences |
| scikit-learn | Original weighted K-Means |
| opencv-python | Color conversion, masks, Canny and connected components |
| Pillow | Image decoding/preprocessing and figure composition |
| threadpoolctl | Single-threaded clustering reproducibility |
| Matplotlib | Plots and a portable bundled font |
| PyYAML | Skill-frontmatter/UI metadata validation tooling |

Direct versions are pinned in `requirements.txt`; the original full environment snapshot is retained under runtime. Transitive dependency resolution, operating-system differences and fonts can affect rendering. No API keys, web service, GPU, NetworkX or graph dependencies are needed. Fresh cross-platform installation has not been tested; exact PNG-byte equivalence is not promised across environments.

## Execute or reuse

Fastest path: validate/reuse the complete saved workflow without image extraction:

```sh
.venv/bin/python pipeline.py --stage all --output runs/review-01
```

Recompute all six stages, including all 82 screenshots and 709 pairs:

```sh
.venv/bin/python pipeline.py --stage all --recompute --output runs/full-01
```

Individual examples:

```sh
.venv/bin/python pipeline.py --stage pairwise-similarity --recompute --output runs/pairs-01
.venv/bin/python pipeline.py --stage composite-scoring --recompute --output runs/composite-01
.venv/bin/python pipeline.py --stage tau-sensitivity --output runs/tau-review-01
.venv/bin/python pipeline.py --stage tau-sensitivity --recompute --output runs/tau-new-report-01
```

Every destination must be new. `--project /path/to/complete-compatible-pilot` can select another donor project; use a destination outside it. The wrapper currently checks/copies the complete declared runtime fixture manifest even for an individual stage, so it is not a minimal-input generic API. Missing fixtures produce an error before execution, not reconstructed historical evidence. See the contracts for what each underlying module actually consumes.

Results live under `<output>/workspace/`; `run_manifest.json` identifies exact artifacts and whether they were reused or recomputed. Logs preserve stage output. Upstream promotion occurs only inside this private workspace; bundled reference results and the source project stay unchanged. A location-only rebase of old absolute provenance paths is recorded in `relocation.json`. If execution fails, inspect its stage log and preserve the run; choose a new destination for a corrected retry.

The approved correction is enabled by the full-pilot runner; root extract_features.py remains the uncorrected baseline. The original pairwise exports retain M0 edge; the composite explicitly uses M1. Tau=10 and equal group weights remain provisional. Experiments do not automatically retune production parameters. Existing diagnostic narratives are copied with `interpretation_provenance.txt`; that does not constitute new human visual review.

## Codex installation

Use the root SKILL.md from this checkout to invoke the orchestrator directly by path, or copy/install this repository as the `ui-visual-consistency` skill folder. Its six module instructions remain nested under `skills/`; the orchestrator can read them without six independent installations.

To expose all seven names separately, install each `skills/<name>/` directory into your Codex user skills directory (usually `~/.codex/skills/`) and keep this repository available. Each installed module must locate this checkout to access code/data/shared docs; it is not a self-contained runtime distribution. No global skills were installed during this task. Reload Codex if newly installed skills are not visible.

Example orchestrator prompt:

```text
Use $ui-visual-consistency in this repository to recompute the full traditional
pre-graph pipeline in a fresh run, validate each stage, and report limitations.
```

Individual prompts:

```text
Use $feature-extraction to reproduce the approved pilot correction in a fresh run.
Use $pairwise-similarity to calculate all 709 pairs from approved saved features.
Use $descriptor-investigation to inspect descriptor limitations without changing formulas.
Use $edge-similarity to reproduce the saved-density M0/M1/M2 comparison.
Use $composite-scoring to reproduce provisional M1/tau=10/equal-weight scoring.
Use $tau-sensitivity to review the existing tau tables without rerunning extraction.
```

Specify this repository's path when an installed skill cannot infer the checkout.

## Tests and remaining limits

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Tests cover reference hashes, no graph inclusion, full reuse, individual tau execution, missing-input/overwrite rejection and existing extraction/pairwise/composite/edge numerical checks. The separate executed six-stage end-to-end run and numerical equivalence audit are archived under `evidence/`; see `docs/validation.md` for actual outcomes.

This package is specific to the approved 82-screen pilot and frozen original/sample fixtures. New datasets need an explicitly designed adapter/calibration experiment rather than removal of count assertions. Graph methods, automatic expert annotation, weight optimization and consistency classification remain excluded. No fresh expert/perceptual validation or cross-platform install was performed. Computation does not prove consistency, semantic equivalence or segmentation quality.

Existing repositories, source research files, installed skills and previous results were not modified. No GitHub commit or upload was performed; this folder is ready for your review and upload as a repository root.
