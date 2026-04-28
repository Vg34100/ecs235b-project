# InjecAgent Raw Data Notes

This directory is the intended landing spot for locally cached raw `InjecAgent` benchmark files.

Recommended files to place here first:

- `user_cases.jsonl`
- `attacker_cases_dh.jsonl`
- `attacker_cases_ds.jsonl`

Optional later:

- one or more synthesized test-case files such as:
  - `test_cases_dh_base.json`
  - `test_cases_ds_base.json`

Why these files matter:

- `user_cases.jsonl` gives the normal user tasks
- `attacker_cases_*.jsonl` gives the malicious injected instructions
- `test_cases_*.json` gives benchmark-ready combinations

For the project, we will likely convert a curated subset of these files into the local schema described in:

- `docs/dataset_schema.md`

The raw benchmark files are reference inputs.
The curated converted cases will be the actual project dataset.
