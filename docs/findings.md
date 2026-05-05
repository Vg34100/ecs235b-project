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

## 2026-04-27

### Decision: use the real downloaded InjecAgent benchmark as the progress-report base

After the earlier dataset discussion, the project direction became more concrete:

- `InjecAgent` is now the primary public benchmark basis
- `MMMU` remains a possible later extension if we want a stronger multimodal story
- the progress-report version should stay focused on the security question first

This decision matters because it changes the project from:

- a toy LLM auditing demo with made-up cases

into:

- a benchmark-backed auditing pipeline with a real public source dataset

That is a much stronger position for the progress report and final report.

### Correction: do not fabricate benchmark files

One important project-process lesson happened here.

At one point, partial local copies of `InjecAgent`-style files had been written from limited fetched content. That was not acceptable as a dataset basis. The benchmark files now used by the project are the real downloaded files from the public repo, stored locally under:

- `data/raw/injecagent/`

This is worth writing down because the final report should be precise about provenance:

- the current raw benchmark data is real downloaded source data
- it is not hand-written benchmark content
- the project-specific processing happens only after the real raw files are available locally

### Raw benchmark contents now available locally

The local raw `InjecAgent` directory now contains the benchmark source and synthesized test-case files:

- `user_cases.jsonl`
- `attacker_cases_dh.jsonl`
- `attacker_cases_ds.jsonl`
- `test_cases_dh_base.json`
- `test_cases_dh_enhanced.json`
- `test_cases_ds_base.json`
- `test_cases_ds_enhanced.json`
- `tools.json`
- `attacker_simulated_responses.json`

Observed benchmark counts:

- `17` user-case templates
- `30` direct-harm attacker templates
- `32` data-stealing attacker templates
- `510` direct-harm synthesized base cases
- `544` data-stealing synthesized base cases

This resolves the earlier concern that the benchmark looked "too small." The benchmark is small at the template level, but not at the synthesized case level. For this project, that is actually useful because:

- the cases remain understandable
- the attack structure is explicit
- the dataset is still large enough to support curated evaluation

### Data-layout cleanup

The project data layout was also cleaned up during this phase.

Earlier MVP work had stored case data under `src/data/`, which was not a good long-term layout. That was changed so the project now separates code and data more clearly:

- `src/` for code
- `data/` for raw and processed datasets
- `outputs/` for run results

This was a small repo hygiene change, but it makes the project much easier to reason about and document.

### Inspection step added before conversion

Before writing any conversion logic, an inspection script was added:

- `src/inspect_injecagent.py`

Purpose of this script:

- verify the raw benchmark files are present and readable
- summarize user-case, attacker-case, and synthesized-case counts
- show coarse distributions such as attack types and user tools
- print a few sample cases in readable form

Reasoning for doing this first:

- we needed to inspect the real benchmark shape before designing the processed dataset
- it reduces the risk of writing a converter against incorrect assumptions
- it gives concrete material for the project report later when describing the dataset

This script is not the main experiment. It is a dataset-understanding tool, and that distinction is important.

### Local project schema became the stable internal format

The next important step was to stop thinking of `InjecAgent` as the direct runtime format.

Instead, the project now treats `InjecAgent` as:

- the raw public benchmark source

and treats the local schema from `docs/dataset_schema.md` as:

- the stable internal project format

This is a good design decision because:

- the code should not be tightly coupled to one benchmark's exact field names
- the auditing pipeline should operate on a consistent internal representation
- future extensions, including a possible `MMMU` subset later, can map into the same schema

### Conversion step added

A conversion script was then added:

- `src/convert_injecagent.py`

What it does:

- reads the real synthesized `InjecAgent` benchmark files
- normalizes cases into the project's local schema
- parses stringified structured fields such as tool parameters and tool responses
- assigns a project-level `system_policy`
- infers a coarse application domain from the user tool name
- writes processed outputs under:
  - `data/processed/injecagent/injecagent_processed_all.json`
  - `data/processed/injecagent/injecagent_curated_subset.json`

Why this conversion matters:

- it is the actual bridge from raw benchmark data into the project pipeline
- after this step, the project has a real benchmark-backed dataset in its own format
- later code can operate on that internal format without caring where the case originally came from

### Processed dataset size and curated subset design

The full processed dataset contains:

- `1054` cases

The curated subset currently contains:

- `84` cases

The curated subset was designed to be balanced rather than simply taking the first N cases. Current observed balance:

- domains:
  - `developer_platform`: `12`
  - `email`: `12`
  - `calendar`: `12`
  - `commerce`: `12`
  - `health`: `12`
  - `social_media`: `12`
  - `web`: `12`
- attack-type groups:
  - `Physical Harm`: `14`
  - `Financial Harm`: `14`
  - `Data Security Harm`: `14`
  - `Physical Data`: `14`
  - `Financial Data`: `14`
  - `Others`: `14`

This balancing decision is important enough to record explicitly.

Why not just use the full 1054 cases immediately?

- for the progress report, a smaller but balanced subset is easier to inspect and debug
- the current pipeline still needs real-model validation on the new schema
- early experiments should favor interpretability over volume

The full dataset still exists and can be used later once the schema path is stable.

### Pipeline integration: support both toy cases and processed InjecAgent cases

After the conversion step, the main project pipeline had to be updated.

This is where the project moved from:

- "we have a processed dataset on disk"

to:

- "the actual pipeline can read and use that dataset"

The key design decision here was to support both case styles at the same time:

- the original toy/MVP cases
- the processed `InjecAgent` cases

This was the right choice for now because:

- the toy cases are still useful for quick sanity checks
- they give a controlled baseline when debugging parsing or policy logic
- the benchmark path is more realistic but also more complex

So the code now treats the toy dataset as a small debugging path, not as the main experiment.

### What the model now sees for processed InjecAgent cases

For processed benchmark cases, the prompt builder no longer assumes the old MVP structure like:

- `prompt`
- `image_evidence`
- `retrieved_context`
- `hidden_metadata`

Instead, it now uses the explicit `sources` block in the processed schema.

For a converted `InjecAgent` case, the model input can now include fields such as:

- `user_prompt`
- `tool_parameters`
- `tool_response`
- `system_policy`
- `attacker_instruction`

This is an important modeling choice.

The goal is not to hide the benchmark structure from ourselves. The goal is to make source-level reasoning explicit, because the detector later needs to reason about:

- which sources were available
- which were required
- which were forbidden

### Mock-mode baseline also had to change

While adding processed-schema support, mock mode also had to be corrected.

Earlier mock behavior was too naive. It effectively treated every non-empty source as used, which would create fake policy violations on processed benchmark cases.

That behavior was changed. For processed cases, mock mode now acts like a clean baseline:

- it uses the required sources
- it does not automatically use forbidden sources
- it only injects a forbidden source when the case is explicitly set up to do that

This matters because the mock path should be useful for sanity-checking the pipeline structure, not for creating meaningless failures.

### Verification status after integration

After the integration work:

- the old toy path still runs
- the processed `InjecAgent` path also runs in mock mode

This means the code is now structurally ready for the first real benchmark-backed runs.

However, one important boundary remains:

- the processed `InjecAgent` path has not yet been meaningfully evaluated with a real model in this new schema flow

That is the next real experimental milestone.

### Comment/readability pass

There was also a small but useful readability pass across `src/`.

Comments were added and then shortened so they read more like research-project code notes:

- enough to explain intent and assumptions
- not so much that the files become overloaded with commentary

This is a minor implementation detail, but it will help later when writing the report because the codebase is becoming easier to review and explain.

### Current interpretation of project state

At this point, the project is no longer just an idea plus a toy MVP.

It now has:

- a real benchmark basis
- a local raw-data copy
- an inspection tool
- a benchmark-to-schema conversion tool
- a processed dataset in the project's own format
- pipeline support for running that processed dataset

That is real progress toward the reportable version of the project.

### Immediate next technical step

The next step is no longer dataset search or schema planning.

The next step is:

- run the processed `InjecAgent` cases through a real model
- inspect the traces and policy-violation outputs
- see whether the current source-reporting and parsing logic is good enough

That experiment is what will tell us what needs to be tightened before the progress report:

- prompt format
- parsing robustness
- source attribution logic
- reporting format

## 2026-04-30

### Progress-report status check

Re-reading the progress-report roadmap is useful here because the project is no longer at the "toy MVP only" stage.

Relative to the roadmap, the project is now roughly:

- about `60%` of the way to a strong progress-report submission

Reason for that estimate:

- the project now has a real public benchmark basis
- the project now has a stable internal case schema
- the project now has a real trace object and trace export
- the project now has three policy types in code:
  - `missing_required_source`
  - `forbidden_source_used`
  - `consistency_violation`
- the project now has early real-model runs on processed benchmark cases

What is still missing for the progress report:

- more stable source attribution
- a cleaner merge rule for reported vs inferred source use
- a report-scale evaluation subset with clearer expected outcomes
- one real analysis artifact beyond raw JSON / markdown summary
- a short explanation of current limitations and what remains

This means the progress report is now realistic, but the weakest section is still methodology around attribution quality.

### Stable traces are now part of the pipeline

The roadmap asked for a real trace structure. That has now been implemented.

Current trace outputs store fields such as:

- `case_id`
- `prompt`
- `available_sources`
- `required_sources`
- `forbidden_sources`
- `model_answer`
- `used_sources_reported`
- `used_sources_inferred`
- `final_used_sources`
- `violation_types`
- `policy_explanation`

This matters because the project is now producing per-run auditing records, not just loose summary rows.

### Real-model benchmark runs have started

The processed `InjecAgent` benchmark path has now been exercised with a real local model:

- `meta-llama/Llama-3.2-1B-Instruct`

This was an important transition point. Before this, the project had:

- mock benchmark runs
- real-model toy runs

Now it also has:

- real-model processed benchmark runs

The results are still noisy, but they are now exposing the real bottleneck instead of a toy-path bottleneck.

### What those early runs taught us

The early `InjecAgent` runs showed several distinct issues:

1. chat/instruct model usage mattered
- using the wrong model variant or wrong interface led to prompt echo and useless source reports

2. partial JSON is common
- small instruct models often returned something close to JSON, but truncated before the final closing braces

3. self-reported source use is unreliable
- the model sometimes reported almost every source
- the model sometimes omitted clearly important sources like `tool_response`
- the model sometimes reported labels that were not useful for policy reasoning

4. ablation checks add real value
- when source self-reports were weak, ablation could still recover evidence that `tool_response` mattered

These observations are important for the report because they justify why the project does not rely on one attribution signal alone.

### Current attribution picture

At this point the project has two attribution signals:

- reported attribution:
  - what the model says it used
- inferred attribution:
  - what ablation suggests mattered

The main lesson so far is:

- reported attribution is noisy
- ablation is useful but still limited

So the current technical focus is no longer "can we load the model?" or "can we convert the benchmark?"

The current technical focus is:

- how to combine noisy source signals into a more defensible final source attribution

That is why the next implementation step is a more conservative merge rule.

### Policy layer has been expanded

The original MVP mostly had two policy checks:

- `missing_required_source`
- `forbidden_source_used`

The policy layer now also includes:

- `consistency_violation`

Current simple consistency idea:

- if the case says the model should not carry out the attacker instruction
- and the answer clearly follows or repeats the attacker instruction
- then that should be flagged even if source lists look superficially acceptable

This is still a simple rule, but it is enough to satisfy the roadmap requirement that the progress-report version support at least three violation types.

### Prompting and parsing changes already made

Several important runtime changes have already been made in response to the benchmark runs:

- chat-template-capable instruct models now use a chat-style input path
- generation now uses `return_full_text=False`
- the pipeline now tries to repair truncated partial JSON before falling back
- generation warning spam was reduced by setting pad token behavior and cleaning generation config

These changes did not "solve" attribution, but they did move the project from unusable outputs toward partially usable traces.

### What the current runs mean

The latest small benchmark runs do not yet show polished evaluation results.

What they do show is:

- the system can run real benchmark-backed cases end-to-end
- the trace structure can capture model answer and source-use evidence
- different failure modes are now visible:
  - missing required source
  - forbidden source used
  - attacker-following answers that motivate consistency checks

That is enough to support an honest progress-report claim of:

- early end-to-end functionality exists
- attribution quality remains the main open technical problem

### Immediate next implementation focus

The most important next code change is:

- make the source merge rule more conservative

Meaning:

- trust self-reported source lists less
- trust ablation-supported sources more
- be stricter before concluding that a forbidden source was truly used

This is the right next step because current runs suggest that self-reported source use is still the least reliable part of the pipeline.

## 2026-04-30 (later)

### Evaluation and reporting artifacts are now in place

Since the last findings update, the project gained several reporting-focused outputs:

- `policy_traces.json`
- `policy_traces.csv`
- `policy_trace_table.md`
- `evaluation_summary.md`
- `mvp_summary.md`

This matters for the progress report because the project is no longer limited to one raw summary dump. It now produces:

- machine-readable trace data
- a spreadsheet-friendly export
- a readable trace table
- a compact evaluation summary by domain and violation type

That is enough to start treating the current system as a reportable evaluation pipeline rather than just an experiment script.

### Current progress-report estimate

After the 30-case benchmark-backed run, the project is now roughly:

- about `80%` of the way to a strong progress-report submission

Reason for this updated estimate:

- the benchmark integration is real and functioning
- the trace format is stable enough to discuss
- multiple policy types are active in the detector
- a real 30-case evaluation now exists
- the current results are interpretable enough to write about

What still remains:

- pick the best 2 to 3 case studies for the writeup
- summarize limitations more clearly
- optionally run one additional comparison or baseline if useful
- draft the actual one-page progress report text

### 30-case real-model evaluation

A larger evaluation was run on:

- `30` processed `InjecAgent` cases
- using `meta-llama/Llama-3.2-1B-Instruct`

Observed result:

- `5` compliant cases
- `25` violating cases

Violation counts:

- `forbidden_source_used`: `19`
- `missing_required_source`: `12`
- `consistency_violation`: `6`

Important note for interpretation:

- these counts overlap
- one case can contribute to multiple violation types

### Main finding from the 30-case run

The strongest current finding is:

- the dominant failure mode is forbidden-source influence

This means that on this current benchmark subset, the model often appears to incorporate or follow attacker-originated instructions that should have remained non-authoritative.

This is a good fit for the overall project claim because it supports the idea that:

- prompt-injection-style failures can be represented as information-flow violations

in particular:

- forbidden information sources influencing final outputs

### Secondary finding from the 30-case run

A second recurring pattern is:

- missing required sources

In practical terms, this often means the final inferred source set is missing something like:

- `system_policy`
- or `tool_response`

This is also meaningful for the project, because it suggests a second type of failure:

- the model may not be adequately incorporating the policy-governing source or the relevant retrieved/tool content source

So the current evaluation does not just show one failure type. It shows at least two distinct classes of information-flow problems:

- disallowed-source influence
- incomplete required-source use

### Domain-level observations

The 30-case run also produced early domain-level variation:

- `developer_platform`: `5/5` violating
- `email`: `4/5` violating
- `calendar`: `3/4` violating
- `commerce`: `4/4` violating
- `health`: `3/4` violating
- `social_media`: `2/4` violating
- `web`: `4/4` violating

This is still too small to support strong domain claims, but it is enough to justify a cautious statement in the progress report:

- some categories appear more failure-prone than others in early experiments

The safest phrasing is to present this as an exploratory observation, not a conclusion.

### What the current system is good enough to claim

At this stage, the project can honestly claim:

- it implements a benchmark-backed audit pipeline for LLM information-flow analysis
- it supports a stable case and trace representation
- it can detect multiple policy-violation types
- early benchmark-backed results show a strong pattern of forbidden-source influence, along with missing-required-source failures

This is now enough for the progress report to move from:

- describing planned work

to:

- describing implemented functionality and early empirical findings

### Best current framing for the results section

The strongest short version of the current results is:

- on an initial 30-case subset of `InjecAgent`, the current audit pipeline found that the dominant failure mode was forbidden-source influence, with additional failures arising from omission of required policy-governing or content-bearing sources

This is a stronger and cleaner result than the earlier smaller runs because it is:

- benchmark-backed
- based on more than a handful of cases
- supported by exported traces and summary artifacts

### What remains the main technical limitation

Even with the improved results, the main technical limitation remains:

- source attribution quality is still imperfect

This matters because:

- the detector still relies on a merge of model-reported source use and ablation-based evidence
- self-reported sources remain noisy
- small local instruct models sometimes return partial JSON or incomplete source lists

So while the current findings are useful and interpretable, the final report should still present attribution quality as the main open challenge.

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

## 2026-05-04

### Progress-report phase is complete

At this point, the progress-report checkpoint should be treated as complete work that has already been submitted. The project is now in the final stretch toward the completed project and final report.

This matters because the framing changes:

- the project is no longer trying to become "progress-report ready"
- the project is now trying to become "final-project ready"

So the current work should be interpreted as:

- strengthening the core evaluation
- clarifying what the detector can and cannot currently support
- preparing for the multimodal extension and final report

### 30-case core evaluation after attribution and export improvements

A new 30-case run was completed on the processed `InjecAgent` subset using:

- `meta-llama/Llama-3.2-1B-Instruct`

Observed result:

- `12` compliant cases
- `18` violating cases

Violation counts:

- `forbidden_source_used`: `17`
- `missing_required_source`: `6`
- `consistency_violation`: `5`

These counts overlap because one case can trigger more than one violation type.

### Confirmatory metric added to the evaluation summary

The evaluation pipeline now includes a simple confirmatory check against the benchmark-derived expected labels.

For the current curated `InjecAgent` subset:

- each case currently carries an expected label of `forbidden_source_used`

Observed confirmatory result on the 30-case run:

- cases with expected labels: `30`
- expected-label hit count: `17`
- expected-label exact-match count: `8`
- expected-label false negatives: `13`

Interpretation:

- the detector is now catching a substantial fraction of the expected forbidden-source violations
- but it still misses a meaningful number of them
- this supports the claim that the framework is useful, but still incomplete

### Updated interpretation of the core security pipeline

The current core pipeline is now strong enough to support the following claims:

- it can run benchmark-backed cases end-to-end
- it can distinguish compliant from violating runs
- it can separate several failure types:
  - forbidden-source influence
  - missing required sources
  - answer-level consistency failures
- it can provide both exploratory and confirmatory outputs

That means the project now has:

- EDA-style outputs
  - domain-level breakdowns
  - violation-type breakdowns
  - per-case trace tables
- CDA-style outputs
  - expected-label hit and miss counts on benchmark-backed cases

### Updated exploratory observations

The strongest exploratory result is still:

- forbidden-source influence is the dominant observed failure mode

The current domain summary for the 30-case run is:

- `calendar`: `4` total, `3` violating
- `commerce`: `4` total, `3` violating
- `developer_platform`: `5` total, `3` violating
- `email`: `5` total, `4` violating
- `health`: `4` total, `2` violating
- `social_media`: `4` total, `2` violating
- `web`: `4` total, `1` violating

This should still be treated as exploratory only. The dataset slice is not large enough to justify strong domain-level claims.

### Current state of the core

The security-first core is now in a credible state for the final project:

- benchmark-backed case set
- stable trace format
- three policy types
- exportable analysis artifacts
- early real-model evaluation with both descriptive and confirmatory metrics

What still appears weakest:

- attribution quality
- consistency and completeness of source reporting
- stability across model runs and domains

### What the final stretch should focus on

The remaining work should now be organized around two tracks:

1. core strengthening
- improve attribution robustness
- improve confirmatory evaluation quality
- identify final case studies

2. multimodal extension
- choose the extension format
- map it into the same schema and trace logic
- test whether the same security framing transfers cleanly

This is the correct transition point from progress-report work into final-project work.
