# Reproducible Comparison Workflow

## Purpose

This workflow is for report-ready comparison artifacts that should be generated
from real run outputs rather than hand-edited tables.

The first target comparison is:

- `MMMU` base `10`-case pilot
- `MMMU` authoritative forbidden-hint `10`-case pilot

## Step 1: Run the base experiment

```bash
source ~/dev/s26/.venv/bin/activate
cd ~/dev/s26/ecs235b/content/project
python main.py \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --quantization 4bit \
  --cases data/processed/mmmu/mmmu_computer_science_pilot_subset.json \
  --limit 10 \
  --skip-ablations \
  --max-new-tokens 96
```

## Step 2: Archive the base run

```bash
python src/analysis/archive_run_outputs.py \
  --run-name mmmu_base_10 \
  --case-file data/processed/mmmu/mmmu_computer_science_pilot_subset.json \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --quantization 4bit \
  --notes "Base MMMU Computer_Science 10-case pilot"
```

## Step 3: Run the authoritative forbidden-hint experiment

```bash
python main.py \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --quantization 4bit \
  --cases data/processed/mmmu/mmmu_computer_science_forbidden_authoritative_10case.json \
  --limit 10 \
  --skip-ablations \
  --max-new-tokens 96
```

## Step 4: Archive the forbidden-hint run

```bash
python src/analysis/archive_run_outputs.py \
  --run-name mmmu_forbidden_authoritative_10 \
  --case-file data/processed/mmmu/mmmu_computer_science_forbidden_authoritative_10case.json \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --quantization 4bit \
  --notes "Authoritative forbidden-hint MMMU Computer_Science 10-case pilot"
```

## Step 5: Collect metrics from both archived runs

```bash
python src/analysis/collect_comparison_metrics.py \
  --run-dir outputs/archive/mmmu_base_10 \
  --run-dir outputs/archive/mmmu_forbidden_authoritative_10 \
  --write-output outputs/analysis/mmmu_base_vs_forbidden_metrics.json
```

## Step 6: Render the markdown comparison table

```bash
python src/analysis/render_mmmu_comparison_table.py \
  --metrics-json outputs/analysis/mmmu_base_vs_forbidden_metrics.json \
  --write-output outputs/analysis/mmmu_base_vs_forbidden_table.md
```

## Output artifacts

After the workflow runs cleanly, the main comparison artifacts should be:

- `outputs/archive/mmmu_base_10/`
- `outputs/archive/mmmu_forbidden_authoritative_10/`
- `outputs/analysis/mmmu_base_vs_forbidden_metrics.json`
- `outputs/analysis/mmmu_base_vs_forbidden_table.md`

## Why this workflow matters

This prevents the final report from relying on:

- one mutable `outputs/` folder
- manually copied numbers
- non-reproducible comparison tables

Instead, the comparison becomes:

- rerunnable
- inspectable
- easy to update after future experiments
