# Multimodal Information-Flow Auditing for LLM Pipelines

## Description

This repository contains the final project code for auditing information-flow
violations in LLM pipelines that combine multiple sources of evidence. The core
idea is that output accuracy alone is not enough to evaluate a system that
reads prompts, retrieved tool content, tables, images, or attacker-controlled
text. A model can return a plausible answer while still relying on the wrong
source, omitting a required source, or following a forbidden one.

The project implements a shared policy-audit framework across three benchmark
families: `InjecAgent` for indirect prompt injection in text-agent settings,
`HybridQA` for table-text reasoning, and curated `MMMU` subsets for image-text
reasoning. Each case is converted into a common schema with explicit source
channels, required-source and forbidden-source policies, and detector logic for
three main violation types: `missing_required_source`,
`forbidden_source_used`, and `consistency_violation`.

The repository also includes the analysis layer built on top of these runs.
Archived evaluations can be regenerated into cross-benchmark metrics, case
studies, a local interactive dashboard, and paper-facing artifacts such as the
main results table and overview figure. In other words, the repo is not only a
set of benchmark scripts; it is the full evaluation and reporting pipeline used
for the final writeup.

## Installation

This project was developed with Python 3.10 on Linux.

1. Clone the repository and enter the project directory.

```bash
git clone git@github.com:Vg34100/ecs235b-project.git
cd ecs235b-project
```

2. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the required dependencies.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Notes:

- If you only want to validate the pipeline logic, you can use `--mock` mode
  and avoid loading a local model.
- If you want to run the full reported experiments, you will need a local
  Hugging Face model setup capable of loading
  `Qwen/Qwen2.5-3B-Instruct` (or another compatible model) and, for the final
  reported runs, 4-bit quantization support.

## Execution

### 1. Quick smoke test

This validates the audit pipeline without loading a real model:

```bash
python main.py --mock
```

This writes summary files under `outputs/`, including:

- `outputs/policy_traces.json`
- `outputs/policy_traces.csv`
- `outputs/evaluation_summary.md`
- `outputs/mvp_summary.json`

### 2. Run a real benchmark slice

Example: run the final curated `HybridQA` evaluation slice with the model used
in the final project reporting.

```bash
python main.py \
  --model Qwen/Qwen2.5-3B-Instruct \
  --quantization 4bit \
  --cases data/processed/hybridqa/hybridqa_final_eval_subset.json \
  --limit 20 \
  --max-new-tokens 192
```

Example: run the final `InjecAgent` core slice in the cleaner `hidden`
attacker-source mode.

```bash
python main.py \
  --model Qwen/Qwen2.5-3B-Instruct \
  --quantization 4bit \
  --cases data/processed/injecagent/injecagent_final_core24_subset.json \
  --limit 24 \
  --max-new-tokens 192 \
  --injecagent-attacker-source-mode hidden
```

### 3. Run a paired comparison experiment

The top-level experiment runner automates base-vs-attack workflows such as the
reported `MMMU` comparisons.

```bash
python run_experiment.py compare \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --quantization 4bit \
  --run-a-name mmmu_base_20 \
  --run-a-cases data/processed/mmmu/mmmu_computer_science_stage2_subset_20.json \
  --run-b-name mmmu_forbidden_authoritative_20 \
  --run-b-cases data/processed/mmmu/mmmu_computer_science_forbidden_authoritative_20case.json \
  --limit 20 \
  --max-new-tokens 96 \
  --skip-ablations \
  --comparison-name mmmu_base_vs_forbidden_20 \
  --title "MMMU Base vs Forbidden Comparison (20 cases)" \
  --notes-a "Base MMMU Computer_Science 20-case slice" \
  --notes-b "Authoritative forbidden-hint MMMU Computer_Science 20-case slice"
```

### 4. Build the analysis dashboard and paper artifacts

After runs are archived, regenerate the cross-benchmark analysis outputs:

```bash
python src/analysis/collect_cross_benchmark_metrics.py
python src/analysis/render_cross_benchmark_summary.py
python src/analysis/render_cross_benchmark_figure.py
python src/analysis/export_case_studies.py
python src/analysis/build_analysis_dashboard.py
python src/analysis/build_paper_artifacts.py
```

The main outputs to inspect are:

- `outputs/analysis/analysis_dashboard.html`
- `outputs/paper/main_results_table.md`
- `outputs/paper/overview_figure.svg`

### 5. Demo to show in class

If the goal is a short demo, the most useful path is:

1. run one benchmark slice with `main.py`
2. archive it with `src/analysis/archive_run_outputs.py`
3. regenerate the dashboard and paper artifacts
4. open `outputs/analysis/analysis_dashboard.html`

That shows the full pipeline from benchmark input to policy traces to
cross-benchmark visual analysis.
