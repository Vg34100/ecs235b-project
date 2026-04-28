# Findings Log

This file is a running project log for decisions, observations, tradeoffs, and next-step planning.

## 2026-04-26

### Current status reminder

- The project proposal was submitted and the professor responded positively.
- Main feedback from professor:
  - the idea is good
  - the pipeline may be very complex
  - simplification will probably be necessary
- Current codebase already has a small MVP:
  - local project repo
  - simple policy checks
  - toy case suite
  - real or mock LLM runner
  - summary outputs

### Professor feedback interpretation

The professor's reply is effectively approval of the project direction. The risk is not whether the topic fits the class. The risk is scope control.

That means the best next move is:

- keep the formal security model central
- choose a dataset base that naturally supports source-level policy reasoning
- avoid getting stuck in multimodal plumbing before the progress report

### Decision we are now evaluating

We want a public dataset or public benchmark as the basis for the project, but we do not want to use it completely as-is.

Instead, the plan is:

- start from a public benchmark or dataset
- curate a smaller subset
- add project-specific policy annotations on top
- use that curated subset as the evaluation set for the auditing framework

This avoids two bad extremes:

- fully synthetic random mock data with no real grounding
- blindly reusing a public benchmark that does not actually match the security question

## Dataset evaluation: INJECAGENT vs MMMU

### Candidate 1: INJECAGENT

Source:

- Paper: https://aclanthology.org/2024.findings-acl.624/
- Paper page with code link: https://huggingface.co/papers/2403.02691
- Reported benchmark repo: https://github.com/uiuc-kang-lab/InjecAgent

What it is:

- a benchmark for indirect prompt injection attacks on tool-integrated LLM agents
- 1,054 total test cases
- built from 17 user cases and 62 attacker cases
- two major attack families:
  - direct harm
  - data stealing

What the paper says the internal test-case structure looks like:

- `user tool`
- `user instruction`
- `tool parameters`
- `tool response template`
- placeholder where attacker instruction is inserted
- `attacker instruction`
- combined final tool response after injection

Important construction detail from the paper:

- they create 17 user cases
- they create 62 attacker cases
- they synthesize the final benchmark by combining them
- total = `17 x 62 = 1054`

Why this is very good for our project:

- the source structure already matches the project idea
- there is a natural notion of trusted vs untrusted information
- the core security question is already source-sensitive
- it naturally maps to ACM objects like:
  - `user_prompt`
  - `system_policy`
  - `tool_response`
  - `attacker_instruction`
  - `private_data`
  - `final_action`
- policy labels are much easier to define

Confirmed repo structure:

- repo: `uiuc-kang-lab/InjecAgent`
- top-level folders include:
  - `data/`
  - `src/`
- README explicitly states the benchmark data is stored as:
  - `data/user_cases.jsonl`
  - `data/attacker_cases_dh.jsonl`
  - `data/attacker_cases_ds.jsonl`
  - `data/test_cases_dh_{setting}.json`
  - `data/test_cases_ds_{setting}.json`

Confirmed example fields in `user_cases.jsonl`:

- `User Tool`
- `User Instruction`
- `Tool Parameters`
- `Tool Response Template`
- `Thought`
- `Level`

Confirmed example fields in `attacker_cases_dh.jsonl`:

- `Attacker Tools`
- `Modifed`
- `Attacker Instruction`
- `Expected Achievements`
- `Attack Type`

Confirmed example fields in synthesized `test_cases_dh_base.json`:

- all attacker-case fields
- all user-case fields
- `Tool Response`

What this means:

- the benchmark is already in a structured case format
- we do not need to reverse-engineer the benchmark from a paper alone
- there is a very direct path from their released JSON to our local project schema

Ease of use:

- moderate, but better than expected
- we still need a conversion script or adapter
- however, the repo structure is already compatible with a case-based audit workflow
- this is much easier than wrapping a generic benchmark from scratch

Main strengths:

- strongest security fit
- easiest to justify as an information-flow project
- easiest to define forbidden-source and required-source policies
- naturally aligned with the references we already added:
  - Instruction Hierarchy
  - BIPIA
  - INJECAGENT

Main weaknesses:

- not multimodal in the image sense
- weaker VIS story unless we build a strong trace / flow visualization
- may require extra work to make the benchmark runnable outside the original agent framework

Bottom line:

- best candidate for the progress-report version
- possibly the best overall candidate if the class grade is the main priority

### Candidate 2: MMMU

Source:

- Hugging Face dataset: https://huggingface.co/datasets/MMMU/MMMU
- GitHub: https://github.com/MMMU-Benchmark/MMMU

What it is:

- a public multimodal benchmark
- 11.5K multimodal reasoning questions
- college-level problems from 30 subjects and 183 subfields
- image-text reasoning benchmark
- released in Parquet format on Hugging Face
- license: Apache-2.0

Availability details:

- easy to access from Hugging Face
- standard dataset tooling works
- public and straightforward to use
- total dataset size reported around 3.65 GB
- format reported by Hugging Face: Parquet

Observed dataset fields from the Hugging Face dataset card / viewer:

- `id`
- `question`
- `options`
- `explanation`
- `image_1` through `image_7`
- `img_type`
- `answer`
- `topic_difficulty`
- `question_type`
- `subfield`

What this means practically:

- MMMU is basically a multimodal QA / reasoning benchmark
- each example is centered on answering a question correctly from image + text
- it is good for evaluating whether a model can solve a multimodal task
- it is not directly built for evaluating whether the model used the wrong information source
- examples already contain answer and explanation fields, so it is usable for curated case selection
- but the security-policy structure would still need to be layered on manually

Why it is attractive:

- real multimodal data
- strong paper / VIS / ML appeal
- includes charts, diagrams, tables, medical images, maps, and other heterogeneous visual inputs
- easy to explain as a serious benchmark

Why it is awkward for our project:

- the native task is QA accuracy, not policy violation detection
- there is no built-in trusted/untrusted source distinction
- there is no native forbidden-source field
- there is no attacker channel or privileged instruction hierarchy in the base dataset
- we would need to add our own extra sources and policies around each example

What adaptation would likely look like:

- choose a subset of MMMU examples
- define extra sources ourselves, for example:
  - `prompt`
  - `image_evidence`
  - `retrieved_context`
  - `hidden_metadata`
  - `answer_policy`
- create policy cases around them
- possibly inject conflicting or misleading context

Ease of use:

- easy to load
- harder to convert into a strong security experiment

Main strengths:

- strongest multimodal story
- best paper upside if we want a true image-based final project
- easy public access

Main weaknesses:

- weaker native security fit
- requires more custom policy wrapping
- more likely to drift into ordinary benchmark evaluation instead of security modeling

Bottom line:

- good candidate for a final-project multimodal extension
- not the best first base for the progress report if the goal is a strong security argument

## Current recommendation

### If the goal is the best progress report

Use INJECAGENT-style data as the base.

Reason:

- clearer source structure
- clearer policy story
- stronger fit to course expectations
- easier to explain as "run-time detection of policy-violating flows"

### If the goal is the best final-project paper direction

Use a hybrid plan:

- progress report base: INJECAGENT-style or BIPIA-style source/policy dataset
- final extension: a curated MMMU subset to show the framework can transfer to real multimodal examples

That gives:

- security-first core
- public-dataset grounding
- later multimodal extension
- lower risk than starting with MMMU directly

## Next concrete task candidates

1. Inspect whether the INJECAGENT benchmark repo is easy to pull into a simple local case format.
2. If repo access is awkward, use a BIPIA-style public text dataset as the progress-report basis and keep MMMU as the final multimodal extension.
3. Draft the exact project case schema that maps public benchmark examples into our ACM / policy format.

## 2026-04-26: updated decision after repo inspection

After looking directly at the released `InjecAgent` files, the recommendation is stronger than before.

### Updated recommendation

Use `InjecAgent` as the primary public-dataset basis for the progress-report version.

Reason:

- its released files already match the project's source-structured logic
- it gives real public benchmark cases, not purely invented mock data
- it minimizes unnecessary annotation work
- it preserves the security-first identity of the project

Then use `MMMU` only as a later extension if we want a true multimodal image-based section in the final project.
