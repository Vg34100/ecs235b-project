# Paper Outline

## Working Title

Auditing Information-Flow Violations in Multimodal LLM Pipelines

Alternative sharper title:

Accuracy Is Not Enough: Policy-Based Auditing of Information-Flow Violations in
Text-Agent, Table-Text, and Image-Text LLM Pipelines

## Central Claim

Standard benchmark accuracy is not enough to evaluate multimodal LLM pipelines.
A policy-based information-flow audit reveals distinct failure modes, including:

- forbidden-source influence
- missing required evidence
- evidence-answer inconsistency

These failure modes appear across:

- indirect prompt-injection agent settings
- table-text reasoning
- image-text reasoning

## One-Paragraph Abstract Draft

Multimodal LLM evaluations usually focus on final-task accuracy, safety labels,
or benchmark performance, but they rarely model how information moved through a
pipeline before an output was produced. We present a policy-based audit
framework that treats prompts, retrieved content, tables, images, and attacker
cues as information sources governed by required-source, forbidden-source, and
consistency policies. We apply the framework across three benchmark families:
`InjecAgent` for indirect prompt injection, `HybridQA` for table-text
reasoning, and curated `MMMU` subsets for image-text reasoning. Our results
show that answer correctness and policy compliance can diverge substantially,
that explicit source governance exposes failure modes ordinary accuracy misses,
and that image-text models can be pushed into forbidden-source-following
behavior by authoritative textual cues even when the task appears to be
primarily visual. These findings suggest that output-only evaluation obscures
important multimodal security failures and that source-level auditing offers a
useful complementary lens.

## Section Outline

## 1. Introduction

### Goal

Set up the paper as a security-and-evaluation paper, not just a tooling paper.

### Main points

- LLM pipelines combine multiple information sources.
- Standard evaluation typically scores only outputs.
- Source-sensitive failures matter for both safety and correctness.
- A policy-based audit gives a more precise account of what went wrong.

### End with contributions

Suggested contribution bullets:

1. a shared policy-based audit framework for source-governed multimodal traces
2. a multi-benchmark study spanning text-agent, table-text, and image-text
   settings
3. evidence that correctness and compliance diverge
4. a multimodal forbidden-source result on curated `MMMU` attack settings
5. a reproducible analysis/export layer for benchmark comparison and case
   studies

## 2. Related Work

### Subsections

#### 2.1 Prompt injection and indirect prompt injection

Use:

- `InjecAgent`
- BIPIA / instruction hierarchy references if already in your bibliography

#### 2.2 Multimodal safety and benchmark evaluation

Use:

- `MMMU`
- multimodal safety references from proposal and plan

#### 2.3 Visual analytics / inspection tools

Use:

- `VISTA`
- any ViDi-facing framing already discussed

### Main positioning

The gap is not that nobody evaluates multimodal models.
The gap is that most work does not evaluate source-governed information flow at
inference time.

## 3. Audit Framework

### Goal

Describe the formal and implementation framing clearly but compactly.

### Subsections

#### 3.1 Sources, policies, and traces

Define:

- source objects
- required-source policy
- forbidden-source policy
- consistency policy

#### 3.2 Trace schema

Explain the shared trace structure:

- prompt
- sources
- final answer
- reported / inferred used sources
- detector output

#### 3.3 Violation taxonomy

Define:

- `forbidden_source_used`
- `missing_required_source`
- `consistency_violation`

## 4. Benchmarks and Experimental Setup

### Goal

Explain why there are three benchmarks and what role each one plays.

### 4.1 `InjecAgent`

Role:

- core security anchor

Main reported result:

- `injecagent_final_core24_hidden_qwen3b`

Important note:

- distinguish `hidden` from harsher `explicit` prompt mode

### 4.2 `HybridQA`

Role:

- correctness vs compliance support benchmark

Main reported result:

- `hybridqa_final_eval_20_qwen3b`

### 4.3 `MMMU`

Role:

- main multimodal forbidden-source benchmark

Main reported runs:

- `mmmu_base_20`
- `mmmu_forbidden_authoritative_20`
- `mmmu_accounting_base_10`
- `mmmu_accounting_forbidden_authoritative_10`

### 4.4 Models and runtime

Primary model for final reported slices:

- `Qwen/Qwen2.5-3B-Instruct`
- `4bit`

### 4.5 Evaluation outputs

Explain:

- compliance
- answer correctness
- correct-but-violating
- violation-type counts

## 5. Results

This is the core of the paper.

## 5.1 Cross-benchmark overview

Use:

- `outputs/paper/main_results_table.md`
- `outputs/paper/overview_figure.svg`

Main message:

- benchmarks differ in difficulty and failure type
- policy auditing exposes cross-benchmark structure that output accuracy alone
  does not

## 5.2 `InjecAgent`: indirect prompt injection remains severe

Main points:

- hidden-mode `InjecAgent` is the cleaner main benchmark result
- explicit-mode `InjecAgent` is a stronger stress-test variant
- attacker-tainted content still drives many failures even in hidden mode

Suggested emphasis:

- this anchors the security story
- this shows the audit framework catches real attacker-following behavior

## 5.3 `HybridQA`: correctness and compliance diverge

Main points:

- `10/20` answer-correct vs `5/20` compliant
- correct answers can still violate required-source policy
- attribution is a real multimodal failure mode

Suggested emphasis:

- this is the cleanest demonstration that output correctness is not enough

## 5.4 `MMMU`: authoritative forbidden hints can override image-grounded reasoning

Main points:

- `Computer_Science` clean vs attack:
  - `12/20` correct to `6/20` correct
  - `14` forbidden-source violations in attack
- `Accounting` clean vs attack:
  - `6/10` correct to `1/10` correct
  - `10` forbidden-source violations in attack

Suggested emphasis:

- this is the strongest multimodal result
- the effect generalizes across at least two structured subjects

## 6. Case Studies

Use the exported paper panels:

- `outputs/paper/case_panels/injecagent_panel.html`
- `outputs/paper/case_panels/hybridqa_panel.html`
- `outputs/paper/case_panels/mmmu_panel.html`

### 6.1 `InjecAgent`

Show:

- attacker-tainted tool content
- policy
- final answer
- why this is not just low accuracy but source misuse

### 6.2 `HybridQA`

Show:

- correct answer
- missing required source
- why policy still flags it

### 6.3 `MMMU`

Show:

- image
- question
- forbidden hint
- model answer vs expected answer

## 7. Discussion

### Main interpretation points

1. output accuracy misses important security-relevant failure modes
2. source-governed multimodal evaluation exposes different classes of error
3. multimodal models are vulnerable not only to weak reasoning, but to
   disallowed-source influence

### Limitations

- curated benchmark slices
- one primary final model family
- policy labels are project-defined overlays rather than native benchmark
  annotations
- image-text attacks are lightweight injected textual cues, not all possible
  multimodal adversaries

### Future work

- larger slices
- more model families
- richer ViDi-style comparative inspection
- more benchmark-native source annotations

## 8. Conclusion

### End on this point

The paper’s conclusion should not be merely:

- “we built a detector”

It should be:

- source-level auditing reveals multimodal policy failures that standard
  accuracy-based evaluation misses

## Recommended Figure/Table Placement

### Main paper

1. main results table
2. overview figure
3. one compact correctness-vs-compliance or benchmark-specific comparison
4. selected case-study panels

### Appendix / supplementary

- extra dashboard screenshots if useful
- more case panels
- full run table if needed

## Immediate Writing Order

Write in this order:

1. Section 4: Benchmarks and setup
2. Section 5: Results
3. Section 1: Introduction
4. Section 7: Discussion
5. Section 3: Audit framework
6. Abstract

Reason:

- the results and benchmark roles are already stable
- writing the empirical sections first will force the intro claim to stay
  honest
