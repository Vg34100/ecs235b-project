# Final Artifact Roles

## Purpose

This document freezes the intended role of the current analysis and export
artifacts so paper writing can proceed from a stable interpretation.

This is not a repository freeze.

It means:

- the benchmark roles are fixed
- the artifact roles are fixed
- major implementation changes should stop unless something is actually broken

## Benchmark Roles

### `InjecAgent`

Role:

- core security anchor
- primary indirect prompt-injection benchmark

What it supports:

- the source-governance framing
- the difference between cleaner `hidden` prompt mode and harsher `explicit`
  prompt mode

Main reported slice:

- `injecagent_final_core24_hidden_qwen3b`

Stress variant:

- `injecagent_final_core24_qwen3b`

### `HybridQA`

Role:

- correctness vs compliance support benchmark
- attribution and required-source stress test

What it supports:

- answer correctness does not imply policy compliance
- multi-source attribution is a real failure mode

Main reported slice:

- `hybridqa_final_eval_20_qwen3b`

### `MMMU`

Role:

- main multimodal forbidden-source benchmark

What it supports:

- image-text reasoning can be overridden by a forbidden textual cue
- the effect generalizes across at least two structured subjects

Main reported runs:

- `mmmu_base_20`
- `mmmu_forbidden_authoritative_20`
- `mmmu_accounting_base_10`
- `mmmu_accounting_forbidden_authoritative_10`

## Artifact Roles

### Dashboard

Artifact:

- `outputs/analysis/analysis_dashboard.html`

Role:

- interactive exploration tool
- supplementary / lab-facing artifact
- case browsing and comparison surface

Not the paper artifact itself.

### Analysis Metrics

Artifacts:

- `outputs/analysis/cross_benchmark_metrics.json`
- `outputs/analysis/case_studies.json`

Role:

- machine-readable source of truth for downstream rendering

These should be regenerated from archived runs rather than edited manually.

### Analysis Summaries

Artifacts:

- `outputs/analysis/cross_benchmark_summary.md`
- `outputs/analysis/cross_benchmark_summary.svg`
- `outputs/analysis/case_studies.md`

Role:

- intermediate report artifacts
- useful for inspection and iteration

These are not necessarily the final paper-ready outputs.

### Paper Exports

Artifacts:

- `outputs/paper/main_results_table.md`
- `outputs/paper/overview_figure.svg`
- `outputs/paper/case_panels/`

Role:

- direct paper-facing export path
- starting point for the final main table, overview figure, and appendix-style
  case panels

These are the files that should now drive the writing process.

## Writing Priorities

The paper should treat the artifacts in this order:

1. `outputs/paper/main_results_table.md`
2. `outputs/paper/overview_figure.svg`
3. `outputs/paper/case_panels/`
4. `outputs/analysis/analysis_dashboard.html`

Reason:

- the first three are curated paper-facing artifacts
- the dashboard is best treated as exploration support or supplementary material

## Freeze Rule

From this point forward:

- do not add new benchmark families
- do not significantly change benchmark roles
- do not redesign the analysis pipeline unless a real bug is found

Allowed work:

- wording cleanup
- visual polish
- paper drafting
- small artifact-export improvements

## Handoff

The intended next phase is:

1. minor polish only if needed
2. draft the paper from the paper exports
3. use the dashboard for exploration and appendix case selection
