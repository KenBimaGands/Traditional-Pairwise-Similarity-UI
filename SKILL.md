---
name: ui-visual-consistency
description: Coordinate the six-stage thesis pre-graph UI visual analysis pipeline from approved screenshot features through pairwise distances, descriptor/edge experiments, composite scoring and tau review. Use for full workflow execution or routing one stage; graph methods are excluded.
---

# UI visual consistency — pre-graph orchestrator

Locate this repository by `pipeline.py`, `provenance.json` and `runtime/`. An installed skill copy is a router, not a data bundle. Read README and `docs/pipeline-architecture.md` before execution; read the selected stage's data contract before running it.

Map the user's intent to these modules and read only the required module instructions:

- [feature-extraction](skills/feature-extraction/SKILL.md): approved image features and frozen correction.
- [pairwise-similarity](skills/pairwise-similarity/SKILL.md): raw EMD, density and layout comparisons.
- [descriptor-investigation](skills/descriptor-investigation/SKILL.md): feature-level diagnostics.
- [edge-similarity](skills/edge-similarity/SKILL.md): experimental M0/M1/M2 comparison from saved densities.
- [composite-scoring](skills/composite-scoring/SKILL.md): provisional M1/tau=10 fixed-weight baseline.
- [tau-sensitivity](skills/tau-sensitivity/SKILL.md): reuse existing tau score tables and report effects.

The order for a full execution is feature extraction → pairwise distances → descriptor diagnostics → edge experiment → composite scoring → tau review. The two diagnostic branches do not select production parameters automatically. M1/tau=10/equal weights are already provisional research choices, not optimization targets.

Use `python pipeline.py --stage all --output <fresh-directory>` to validate/reuse saved outputs. Use a named stage for individual execution. Add `--recompute` only when the user's task calls for fresh computation; a full recomputation is expensive. The included pipeline makes a private copy, checks input fingerprints, rebases location-only provenance there, validates stage prerequisites, logs execution, validates outputs and promotes upstream results only inside that private workspace. It refuses an existing destination. Optional `--project` points to another complete compatible pilot project; missing required fixtures are reported, not fabricated.

If installed outside the repository, the links above resolve in the repository copy of SKILL.md; locate that copy before opening module files. Skill invocation does not require subagents or external publication. Check `run_manifest.json` and relevant validation reports before declaring a stage complete. If a stage fails, stop dependent execution, identify the log and preserve the failed run for investigation.

Do not modify baseline mathematics, original inputs or prior runs, substitute rejected segmentation candidates, introduce graph algorithms, optimize weights, classify consistency or invent expert labels. Existing interpretations copied into a new run are explicitly historical, not fresh human evaluation. Report actual execution/reuse, tests, missing integration and remaining methodological limitations.
