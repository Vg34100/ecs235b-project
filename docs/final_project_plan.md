# Final Project Plan

## Project Direction

Final project goal:

- build a security-focused audit framework for detecting information-flow violations in LLM pipelines
- extend that framework to a multimodal setting in a way that is real, visible, and defensible

The project should be planned in two layers:

1. a strong security-first core that is enough for a complete and successful class project on its own
2. a multimodal extension that demonstrates the framework can generalize beyond the initial tool-agent setting

This is the right structure because it protects the class-project outcome while still preserving the more ambitious final vision.

## Current State

What already exists:

- standalone repo for the project
- policy-based MVP
- real `InjecAgent` benchmark downloaded locally
- converter from raw benchmark data into local project schema
- processed dataset and curated subset
- trace-based audit pipeline
- JSON, CSV, markdown trace, and evaluation-summary exports
- three policy types in code:
  - `missing_required_source`
  - `forbidden_source_used`
  - `consistency_violation`
- early real-model evaluation results on benchmark-backed cases
- progress-report draft and bibliography

What this means:

- the project is already past the “idea only” stage
- the security core is real and usable
- the remaining work is mostly about strengthening evaluation, improving attribution, and building the final extension and final report

## Final Deliverable

The completed project should ideally include:

1. a formal security framing for LLM pipeline auditing
2. a benchmark-backed implementation for policy-based source auditing
3. a larger and more stable evaluation on the core dataset
4. representative case studies and analysis artifacts
5. a multimodal extension using the same audit framework
6. a complete final report with methodology, results, limitations, and future work

## Core Security Project

This is the required foundation.

Core claim:

- LLM pipeline failures can be analyzed as information-flow violations over explicitly modeled sources

Core implementation pieces:

1. case schema
- unified representation for prompts, tool outputs, policy instructions, attacker content, and expected behavior

2. trace schema
- stable runtime records for model answer, reported source use, inferred source use, merged source use, and final policy result

3. policy detector
- checks for required-source omission
- checks for forbidden-source influence
- checks for consistency violations

4. source attribution logic
- model-reported source use
- ablation-based source inference
- conservative merge rule

5. evaluation pipeline
- reproducible runs
- exported traces
- summary artifacts

## Multimodal Extension Goal

This is a major part of the final plan, but it should only be built after the core is stable enough.

Extension goal:

- show that the same policy-based audit framework can be applied when the model has access to multiple modalities, not only prompt and tool text

Ideal version:

- a real multimodal setting with image-text or another clearly distinct second modality

Practical requirement:

- the multimodal extension should reuse as much of the existing framework as possible
- it should not become a completely separate project

That means the extension should keep:

- the same case schema structure
- the same trace format
- the same policy detector
- the same reporting outputs

The main change should be:

- adding one or more multimodal source types and evaluating whether the same framework still identifies policy-violating information flow

## Multimodal Options

### Option A: Real image-text extension

What it is:

- prompt plus real visual input
- additional sources may include retrieved context, hidden metadata, or policy instructions

Why it is attractive:

- strongest final-project upside
- best connection to multimodal safety literature
- best fit for a security plus ML plus VIS story

Main risks:

- harder tooling
- harder attribution
- noisier evaluation

### Option B: Structured or tabular multimodal extension

What it is:

- prompt plus table, record, or structured state

Why it is useful:

- cleaner semantics
- easier to define required and forbidden fields
- easier attribution story

Main tradeoff:

- less visually compelling than image-based multimodality

### Option C: Symbolic visual-state extension

What it is:

- prompt plus structured visual-state descriptions such as `image_evidence`

Why it is useful:

- easier than real images
- still supports a visual-style extension path

Main tradeoff:

- weaker as a “true multimodal” claim than real image input

## Recommended Final Strategy

The recommended final strategy is:

1. finish the security-first core well
2. attempt a real multimodal extension
3. if the real multimodal version becomes too costly or unstable, fall back to a structured or symbolic multimodal extension rather than forcing a weak image pipeline

This keeps the multimodal goal central without letting it destroy the core project.

## EDA and CDA

The project should include both exploratory and confirmatory analysis.

### Exploratory Data Analysis (EDA)

EDA in this project means:

- inspecting how cases are distributed across domains
- inspecting which violation types appear most often
- inspecting which sources are most often missing or implicated
- comparing compliant and violating traces
- looking for domain-specific or task-specific failure patterns

Useful EDA questions:

- which violation type is most common?
- which domains appear most failure-prone?
- when runs fail, do they fail by forbidden-source influence, missing required sources, or both?
- which sources are most often missing from final attribution?
- how often does the model produce attacker-following answers versus partial or incomplete answers?

Useful EDA artifacts:

- violation counts by type
- violation counts by domain
- trace tables for compliant and violating cases
- small case-study comparisons

### Confirmatory Data Analysis (CDA)

CDA in this project means:

- testing specific expectations against the curated benchmark cases

Current confirmatory question for the `InjecAgent` core:

- does the detector identify expected forbidden-source influence on benchmark cases designed around indirect prompt injection?

Future confirmatory questions:

- does attribution improve when ablations are enabled?
- does the conservative merge rule reduce false positives from noisy self-reports?
- does the same audit framework still detect policy-violating flows in the multimodal extension?

Useful CDA metrics:

- expected-label detection rate
- false negative rate on benchmark cases with expected violations
- compliant versus violating counts on curated subsets
- violation-type overlap counts

This split is useful because:

- EDA helps discover failure patterns and refine the detector
- CDA helps support stronger claims in the final report

## Must Have

These are the things that need to be finished for the final project to feel complete.

1. stable benchmark-backed security pipeline
2. larger evaluation on the core dataset
3. clean trace and summary artifacts
4. at least three violation types working and demonstrated
5. representative case studies
6. final report with clear methodology and findings

## Should Have

These are important quality improvements that would make the final project much stronger.

1. improved attribution robustness
2. evaluation on more than one model if feasible
3. better domain-level and violation-level summaries
4. cleaner final report figures or tables
5. stronger explanation of the formal ACM / protection-system framing

## Stretch Goals

These are ambitious additions that are good if time allows.

1. real multimodal extension with image-text cases
2. second benchmark basis beyond `InjecAgent`
3. richer visualization or inspection interface
4. more formal threat-model discussion
5. paper-style framing and polishing beyond class-project needs

## Remaining Technical Work

### 1. Strengthen source attribution

Why:

- attribution is still the main weak point

Needed work:

- continue reducing noisy self-reported source use
- improve ablation handling
- possibly add answer-overlap heuristics for `tool_response` and multimodal sources

### 2. Expand core evaluation

Why:

- the current 30-case result is useful but still small

Needed work:

- run a larger curated subset
- inspect which failure modes stay stable
- identify representative compliant and violating cases

### 3. Prepare final analysis artifacts

Why:

- the final report should not rely only on raw trace files

Needed work:

- one compact evaluation table
- one domain or violation summary
- short written case analyses

### 4. Build the multimodal extension

Why:

- this is the major planned extension for the final project

Needed work:

- choose the multimodal input format
- build a small but real case set
- map it into the same schema
- run the same detector and reporting pipeline

### 5. Write the final report

Needed sections:

- problem statement
- security framing
- related work
- dataset and case construction
- implementation
- evaluation
- case studies
- limitations
- multimodal extension
- conclusion

## Risks

### Risk 1: attribution remains noisy

Effect:

- weakens the detector’s credibility

Response:

- emphasize conservative merging
- rely more on ablations and case studies

### Risk 2: multimodal extension takes too long

Effect:

- could endanger the quality of the core project

Response:

- treat the extension as phase two
- fall back to structured or symbolic multimodal cases if needed

### Risk 3: small models behave inconsistently

Effect:

- unstable results

Response:

- keep evaluation artifact-focused
- compare with at least one stronger local model if feasible

## Timeline for the Remaining Month

### Phase 1: stabilize the core

Target:

- improve attribution
- expand core evaluation
- finalize case studies

Deliverable:

- stronger benchmark-backed results for the security core

### Phase 2: build the extension

Target:

- implement multimodal case path
- run a small extension experiment

Deliverable:

- second experimental section showing framework generalization

### Phase 3: package the final project

Target:

- finalize artifacts
- complete final report
- polish framing and limitations

Deliverable:

- complete project submission with report, code, and analysis outputs

## Working Principle

The final project should be treated as:

- a complete security-project core
- plus a serious multimodal extension attempt

The security core is the non-negotiable foundation. The multimodal extension is a major goal, not an afterthought, but it should be built in a way that reuses the core instead of competing with it.
