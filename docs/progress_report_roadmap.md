# Progress Report Roadmap

This roadmap describes how to move from the current MVP to a progress-report-ready version of the project. The goal is not to finish the whole project by the progress report. The goal is to be far enough along that the report can honestly show a working system, early results, and a credible path to the final submission.

## Where the project is right now

Current state:

- a standalone project repo exists in `ecs235b/content/project`
- there is a small runnable MVP
- the MVP can load a local LLM or run in mock mode
- the MVP has a case file, policy checks, and summary outputs
- the MVP can already show policy violations on toy examples

What is still weak:

- source attribution is still noisy because it depends too much on model formatting
- the ACM exists in code, but the formal model is not yet central in the workflow
- the evaluation is too small and too fragile for the progress report
- the analysis output is still mostly a raw summary file, not a convincing inspection artifact

## Progress report target

By the progress-report checkpoint, the project should look around 50 to 70 percent complete.

That means the project should have:

- a clearly defined formal model
- a stable data format for cases and traces
- a working detector for at least 3 violation types
- a larger and better-labeled case suite
- some early evaluation results
- at least one clear analysis figure or trace view
- a short written explanation of what works, what does not, and what remains

## Recommended scope for the progress report version

Keep the progress-report version bounded:

- stay text-first, even if the final framing remains multimodal
- represent image evidence symbolically as a named source or short structured field
- use a replay / case-driven pipeline, not a fully autonomous agent system
- focus on policy reasoning and auditing, not model performance

This is the safest way to have a real result in time.

## What to build next

### 1. Make the trace format real

Add a dedicated trace structure instead of treating model output as just a loose response.

Needed fields:

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

Why this matters:

- The progress report needs to show that the project is building a real auditing pipeline, not just printing a summary.

### 2. Strengthen source attribution

Right now the weakest part is deciding what sources actually influenced the output.

For the progress-report version, implement two simple attribution methods:

- reported attribution: what the model says it used
- ablation attribution: rerun with one source removed and compare output

Then define a merge rule:

- always include `prompt`
- include reported sources if valid
- include ablation-changed sources

Why this matters:

- This makes the detector more defensible.
- It also gives the report a meaningful methodological section.

### 3. Expand the policy system

Right now the MVP mainly supports:

- missing required source
- forbidden source used

Add one more policy type:

- consistency violation

Example:

- if `image_evidence` or `retrieved_context` clearly implies danger, the answer should not say "safe" without justification

Why this matters:

- The progress report should show more than one trivial rule type.
- Three policy types is enough to look substantial.

### 4. Build a better case suite

Expand from the current toy cases to about 20 to 30 labeled cases.

Case categories:

- compliant cases
- missing-required-source cases
- forbidden-source cases
- consistency-failure cases
- ambiguous cases
- wrong-answer but policy-compliant cases

Why this matters:

- This is the minimum needed for a believable evaluation section.

### 5. Add an analysis output that looks like a real artifact

For the progress report, you do not need a full dashboard. A good static artifact is enough.

Recommended options:

- per-case markdown trace cards
- a CSV / table export
- one plot of violation counts by type
- one plot or matrix showing source usage frequency by case category

Why this matters:

- The report needs something visual and interpretable.
- This is also where the VISTA / ModalChorus connection can be mentioned carefully.

### 6. Run an initial evaluation

Keep it simple.

Suggested evaluation questions:

- does the detector identify the labeled violation type on hand-built cases?
- can the system distinguish compliant from non-compliant runs?
- what kinds of failures still confuse the detector?

Suggested outputs:

- overall counts
- per-violation accuracy on labeled cases
- 3 short case studies

## Concrete checklist for the progress report checkpoint

- Refactor response output into a stable trace object
- Implement stored trace export in JSON and CSV
- Add consistency-policy logic
- Expand the case suite to 20 to 30 cases
- Clean up source attribution rules
- Re-run cases with at least one local model and one mock baseline
- Generate one summary table and one figure
- Write one-page progress report draft
- Finalize bibliography

## Suggested timeline from now to the progress report

### Phase 1: stabilize the core

- clean up parsing and attribution
- define final trace schema
- finalize 3 policy types

Deliverable:

- stable detector on a small subset of cases

### Phase 2: expand the evidence

- grow the dataset to 20 to 30 cases
- label expected violations by hand
- run detector and collect outputs

Deliverable:

- reproducible case-based evaluation

### Phase 3: make it reportable

- add static analysis views
- write case studies
- summarize results, limitations, and next steps

Deliverable:

- progress report package with report text, references, figures, and early results

## What should remain unfinished after the progress report

Leave these for the final project phase:

- a richer interface
- more realistic multimodal or tool-augmented pipeline cases
- stronger source attribution methods
- more polished evaluation
- deeper discussion of limitations and future work

That is the right balance. The progress report should show real progress, but it should still leave obvious room for the final submission.

## Best framing for the progress report write-up

The strongest honest claim at the progress-report stage is:

"We implemented an initial policy-based audit framework for LLM pipeline traces, defined a formal access-control and information-flow representation, and demonstrated early detection of several violation types on a curated case suite. Current work is focused on improving attribution quality, expanding the evaluation set, and refining the analysis interface."

That reads like genuine progress and still leaves room for the final version.
