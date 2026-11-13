# Executed validation and known limits

## End-to-end execution

A full `--stage all --recompute` run completed successfully in `/private/tmp/ui-ecosystem-e2e-01`, using a fresh isolated runtime copy and the existing Python 3.13.7 environment. All six stages executed in order; the newly produced extraction, pairwise and composite records were promoted only inside that workspace for downstream consumption.

1. Approved extraction: all 82 screenshots successful, one expected correction activation (APP02-FLOW01-S01), baseline/sample checks and correction repeatability passed.
2. Traditional pairwise: all 709 pairs generated from the newly reproduced extraction.
3. Descriptor investigation: all 709 records aligned; saved-descriptor exports reproduced twice; diagnostic figures/tables generated.
4. Edge experiment: all 709 M0/M1/M2 records, deterministic 24-pair sample and epsilon sensitivity generated without Canny recomputation.
5. Composite: all 709 baseline records and 2,836 fixed-sensitivity records generated; parameters unchanged.
6. Tau review: reused the newly generated M1 tau tables, produced the report/statistics/plots, and kept all non-color terms fixed.

The [full run manifest](../evidence/full_run_manifest.json) and six stage logs preserve execution evidence. Temp workspace paths in evidence describe the actual validation run and are not required to execute a new checkout. Full recomputed artifacts remain in that temporary workspace; bundled canonical outputs remain the original frozen references, avoiding another large duplicate archive. Use the documented command to reproduce.

## Numerical equivalence

Twenty-five key numerical artifacts across the six stages match frozen reference data: exact bytes for CSVs and parsed equality for JSON palettes/boxes/triggers. The [equivalence audit](../evidence/numerical_equivalence.json) lists every comparison. These include approved feature records, all pair distances/similarities, descriptor statistics/selections, edge comparisons/sample/epsilon tables, composite/sensitivity tables and tau summary/rank/extreme-case tables.

Location-bearing configurations, script hashes, protection inventories and font-rendered image bytes can legitimately differ after relocation/packaging. Their provenance is recorded separately. No raw numerical records were normalized or rewritten to conceal mismatches. All 586 copied source/fixture originals were checked against their original recorded hashes and remained unchanged.

## Automated tests and skills

The package suite passed **5 tests in 58.223 seconds**; see [tests.log](../evidence/tests.log). It covers:

- Integrity of all packaged runtime hashes and graph-code exclusion.
- Full saved-result validation/reuse and refusal to overwrite a run.
- Individual tau recomputation with prerequisite checks.
- Missing fixtures failing before output creation.
- Existing source numerical checks: five extraction tests, five pairwise tests, one composite analytic test and two edge analytic/sampling tests, all passing in subprocesses.

All **seven SKILL.md definitions** passed the skill-creator validator. UI metadata lengths/default prompts and local authored documentation links were checked. No skill was globally installed or independently invoked through a fresh Codex session; validation establishes format/routing structure, not a user-study result.

## Scope of claims

The current environment successfully executed the complete fixed-pilot computational chain and independently selected stages. Saved-result reuse also completed all six stages without image extraction. Neither test asserts that segmentation is accurate, that M1/tau/weights are optimal, or that composites agree with experts.

Copied narrative reports retain prior interpretation and are explicitly marked when added to recomputed stage outputs. Generated figures were not all manually re-reviewed during ecosystem packaging. No new human/expert annotations were collected. Rendering portability was improved by substituting Matplotlib's bundled font in two copied rendering functions; a fresh Windows/Linux dependency install has not been tested.

## Remaining unintegrated or intentionally unsupported work

- A generic new-dataset adapter and creation of original baseline/frozen correction fixtures are not implemented. The approved full runner remains tied to the 82-screen pilot.
- Individual stage invocation still expects a complete compatible runtime fixture manifest. The older standalone tau package remains the lightweight table-only option.
- Global Codex skill installation and GitHub publication are not performed.
- Graph construction/contextual scoring, role-aware analysis, consistency classification and weight optimization are outside this pre-graph package.
- Expert calibration and perceptual/consistency validity remain future research work, not missing automatic software outputs.

No prior source/output was moved or deleted. The only implementation edits relative to copied research source are the two recorded font substitutions; orchestration and documentation are new files in this separate package. `provenance.json` records both original and packaged digests so those differences are reviewable.
