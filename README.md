# Security Project MVP (Phase A)

Quick MVP for: **Analyzing Information Flow Violations in Multimodal LLM Pipelines using Access Control Models**.

This phase validates the core idea with a small case suite and policy checks.

## What this MVP does

- Loads curated safety cases (`data/cases/cases.json`)
- Runs an LLM (or mock mode)
- Requests structured output with `used_sources`
- Runs ablations (remove source one at a time)
- Detects policy violations:
  - `missing_required_source`
  - `forbidden_source_used`
- Writes summary outputs to `outputs/`

## Project layout

- `main.py`: entrypoint
- `src/acm.py`: simple access-control matrix helper
- `src/policies.py`: policy checks
- `src/pipeline.py`: LLM runner + prompt + JSON parser
- `src/detector.py`: violation detection wrapper
- `data/cases/cases.json`: quick case suite

## Run

### Option 1: quick local smoke test (no model)

```bash
python main.py --mock
```

### Option 2: run with Hugging Face model

```bash
pip install -r requirements.txt
python main.py --model Qwen/Qwen2.5-3B-Instruct
```

If model loading fails, use `--mock` first to validate the audit pipeline.

## Output

- `outputs/mvp_summary.json`
- `outputs/mvp_summary.md`
