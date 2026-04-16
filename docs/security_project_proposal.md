# Project Proposal and Implementation Plan

## Title
**Auditing Information Flow Violations in Multimodal LLM Pipelines with Access Control Models**

## Student / Team
- Pablo Rodriguez

## Project Type
Programming project with a formal security model component.

## One-Paragraph Proposal
This project studies whether mistakes made by multimodal large language model pipelines can be understood as **information flow violations** under a formal security model. The core idea is to model a simplified multimodal LLM pipeline as a protection system using an **Access Control Matrix (ACM)**. Components such as the user prompt, image evidence, retrieved context, memory, safety policy, and final output are treated as objects, while the model or submodules act as subjects with defined rights over those objects. The system will simulate or replay a small set of pipeline executions, record which sources were available and which sources influenced the output, and then detect when the final answer depended on information that should not have been used or ignored information that should have been required. The contribution is a prototype audit tool that makes the security framing explicit: instead of treating model failures only as bad outputs, it treats them as violations of allowed information flow. This fits the course by implementing and applying a formal model to a modern AI system and showing how the model helps reason about correctness and safety.

## Problem Statement
Current multimodal model evaluations usually judge whether the final output is safe, correct, or useful. They do not usually model **how information moved through the system** before that output was produced. This project asks whether a formal security model can be used to represent allowed and disallowed information flow in a multimodal LLM pipeline, and whether that representation can help detect, explain, and categorize pipeline failures.

## Why This Fits the Security Class
This project is explicitly a security project because it centers on the following security ideas:

1. **Access control**: which components may read from or write to which sources.
2. **Information flow policy**: which sources are allowed to influence a given output.
3. **Violation detection**: identifying cases where the system used disallowed information, failed to use required information, or combined sources in a way that broke policy.
4. **Model-based reasoning**: the project implements and applies a formalism from the class rather than only building an ML demo.

This is closest in spirit to the course suggestion about building a run-time system that detects flows violating a security or integrity policy, except the target system here is a simplified multimodal LLM pipeline.

## Research Angle and Novelty Claim
### Careful novelty claim
This project does **not** claim to invent a new security model or solve multimodal alignment in general. The more defensible claim is:

> Existing multimodal safety work mainly evaluates outputs and benchmark performance, while this project applies a formal access-control and information-flow framing to analyze *why* certain failures occur inside a pipeline.

### Why this claim is reasonable
Recent work shows that multimodal systems have serious safety and alignment problems, especially when safety depends on visual context or when image-text features are subtly misaligned. But those papers mainly benchmark outcomes, measure alignment quality, or provide visual analytics for data quality. This project shifts the focus to **formal policy-based auditing of inference-time information flow**.

## Closest Related Work
### 1. VISTA
**VISTA: A Visual Analytics Framework to Enhance Foundation Model-Generated Data Labels** studies how visual analytics can help humans inspect and improve foundation-model-generated labels, especially when no ground truth is available. The paper positions its contribution around data validation and data quality improvement, not formal security policy analysis. That makes it a useful inspiration for the interface and human-in-the-loop analysis style, but leaves room for this project to focus on **policy violations during inference** rather than **label quality during dataset curation**.

### 2. Multimodal Situational Safety
**Multimodal Situational Safety** argues that current multimodal models struggle when safe behavior depends on combining a user query with its visual situation. The paper says models struggle with this nuanced problem and highlights it as an area for future research. This directly supports the idea that the way information is combined across modalities matters and that a structured way to audit such combination is needed.

### 3. MM-SafetyBench
**MM-SafetyBench** shows that multimodal large language models can be compromised by simple query-relevant images paired with malicious text. This is strong evidence that visual context can change model behavior in ways that matter for safety. The paper evaluates safety outcomes, while this project aims to model and inspect the information-flow conditions behind those outcomes.

### 4. ModalChorus
**ModalChorus: Visual Probing and Alignment of Multi-modal Embeddings via Modal Fusion Map** offers a visual analytics system for probing and repairing multimodal embedding misalignment. It is a useful anchor for the visual side of the project, especially if the project includes a small alignment or provenance inspection view, but it does not frame misalignment as a security policy problem.

## Requirements for a Solution
For this programming project, a valid solution must:

1. Define a formal representation of a pipeline using an **Access Control Matrix**.
2. Define at least one explicit **information flow policy** over pipeline components.
3. Represent or simulate a set of executions with logged provenance, influence, or dependency information.
4. Detect at least three kinds of cases:
   - allowed flow
   - disallowed flow
   - missing required flow
5. Produce a clear audit result for each case, showing **which policy was violated and why**.
6. Provide a simple analysis interface, trace view, or structured report that helps explain each violation.
7. Include at least one small evaluation showing the utility of the model on a chosen set of examples.

## Scope Choices
### Recommended scope
Keep the project small and controlled. Use a **toy or simplified pipeline** instead of a full production model stack.

### Best scope for one person
- Use a **simulated or replay-based multimodal pipeline**.
- Avoid model training.
- Avoid collecting a large new dataset.
- Use hand-constructed or small benchmark examples.
- Prefer **policy reasoning and auditing** over pure ML performance.

## Core Design

### Simplified pipeline objects
Possible objects in the ACM:
- `prompt`
- `image_evidence`
- `retrieved_context`
- `memory`
- `safety_policy`
- `tool_output`
- `intermediate_reasoning`
- `final_output`
- `ground_truth_label` or `expected_required_source`

### Subjects
Possible subjects in the ACM:
- `vision_encoder`
- `retriever`
- `reasoner`
- `safety_filter`
- `generator`
- `auditor`

### Rights
Keep the rights simple:
- `r` = read
- `w` = write
- `i` = influence
- `a` = approve
- `d` = deny or block

You do not need to use all of these. At minimum, `read`, `write`, and an audit notion of `influence` are enough.

## Policy Types
You only need a few policy templates.

### Policy A: required-source policy
Some outputs must depend on certain sources.

Example:
- If the task asks about visual safety, the output must depend on `image_evidence` and `prompt`.

Violation:
- The model answers a visual-safety question without actually using image evidence.

### Policy B: forbidden-source policy
Some outputs must not depend on some sources.

Example:
- Final safety decision must not depend on hidden metadata or a disallowed memory field.

Violation:
- The output depends on a source marked forbidden.

### Policy C: consistency policy
When a source is used, the output must remain consistent with it.

Example:
- If image evidence indicates a safe situation, the output must not claim an unsafe one without another supporting source.

Violation:
- The image says one thing, the output says another, and no allowed source justifies the difference.

## What Counts as an “Information Flow Violation”
Use a simple definition in the report.

An execution violates policy when one or more of the following holds:
- The output was influenced by a source that policy forbids.
- The output failed to use a source that policy requires.
- The output used multiple sources in a way that breaks a consistency rule.

## Project Deliverables
1. **Proposal**
2. **Progress report**
3. **Code repository**
4. **Small evaluation dataset or case suite**
5. **Final report**
6. **Figures** for the report
7. Optional: lightweight interactive viewer

## Recommended Repository Structure
```text
project/
  README.md
  requirements.txt
  data/
    cases.json
    policies.json
  src/
    acm.py
    pipeline.py
    provenance.py
    policies.py
    detector.py
    evaluate.py
    visualize.py
  outputs/
    traces/
    figures/
    reports/
  docs/
    proposal.md
    progress_report.md
    final_report.md
```

## Implementation Plan

### Phase 0: Lock the framing
**Goal:** Make sure the title and one-paragraph proposal are solid.

Tasks:
1. Finalize the project title.
2. Finalize the exact problem statement.
3. Decide whether the system is:
   - simulated, or
   - backed by a real model API / local model.
4. Decide whether to include images in the MVP.

**Recommendation:**
Start with a **text-plus-structured-visual-state simulation** even if the final framing says multimodal. You can model image evidence as a structured field first, then swap in real images later only if time allows.

### Phase 1: Define the formal model
**Goal:** Build the ACM and policy language.

Tasks:
1. List subjects, objects, and rights.
2. Write the ACM structure in code.
3. Implement policy objects:
   - required sources
   - forbidden sources
   - consistency rules
4. Create a small notation for cases.

Outputs:
- `acm.py`
- `policies.py`
- example JSON files

### Phase 2: Define the execution trace format
**Goal:** Represent how a pipeline run is logged.

Each trace should store:
- case id
- prompt
- image or image-surrogate description
- available sources
- intermediate module outputs
- final output
- provenance or influence set
- expected policy outcome

Example trace fields:
```json
{
  "case_id": "001",
  "task_type": "situational_safety",
  "prompt": "Is this action safe?",
  "image_evidence": "person cutting vegetables with a knife",
  "retrieved_context": "kitchen safety tips",
  "allowed_sources": ["prompt", "image_evidence"],
  "required_sources": ["prompt", "image_evidence"],
  "forbidden_sources": ["hidden_metadata"],
  "used_sources": ["prompt"],
  "final_output": "unsafe",
  "expected_label": "safe"
}
```

Outputs:
- `provenance.py`
- `data/cases.json`

### Phase 3: Build the detector
**Goal:** Detect policy violations from a trace.

Tasks:
1. Check forbidden-source use.
2. Check missing required sources.
3. Check consistency rules.
4. Emit structured findings.

Output format:
```json
{
  "case_id": "001",
  "violation": true,
  "violation_types": ["missing_required_source", "consistency_failure"],
  "explanation": "The output answered a visual-safety question without using image evidence."
}
```

Outputs:
- `detector.py`

### Phase 4: Build a small case suite
**Goal:** Create enough examples to show the model is useful.

Minimum case categories:
1. Correct flow, correct output
2. Correct flow, wrong output
3. Missing required visual evidence
4. Forbidden source used
5. Conflicting sources
6. Over-reliance on text when image should dominate
7. Over-reliance on image when text constraint should dominate

Recommended number of cases:
- 20 to 40 total

How to build them:
- Start with hand-made cases.
- If time allows, adapt a few examples from multimodal safety papers.
- Keep them small and well explained.

Outputs:
- `data/cases.json`

### Phase 5: Add a simple analysis view
**Goal:** Help a reader inspect what happened.

Options from easiest to hardest:
1. Markdown or HTML report per case
2. Static plots and tables
3. Small Streamlit dashboard

Recommended MVP:
- table of cases
- policy status
- used sources
- violation type
- short explanation

Nice figure ideas:
- bar chart of violation counts by type
- flow matrix of source-to-output dependencies
- per-case trace card

Outputs:
- `visualize.py`
- figures in `outputs/figures/`

### Phase 6: Evaluate utility
**Goal:** Show the formal model helps in some measurable way.

Possible evaluation questions:
1. Can the detector separate policy-compliant and policy-violating cases?
2. Can it distinguish different kinds of multimodal failures?
3. Does the audit view make it easier to explain failures than plain accuracy alone?

Simple metrics:
- detection precision and recall on your hand-labeled cases
- count of correctly categorized violation types
- case-study analysis of 3 to 5 examples

Do not overcomplicate this. For a class project, a careful small evaluation is enough.

### Phase 7: Write the final report
**Goal:** Turn the project into a polished course submission with publication-style structure.

## Suggested Final Report Outline
1. **Introduction**
   - Why multimodal failures matter
   - Why output-only evaluation is limited
   - Why a formal security framing is useful
2. **Background**
   - ACM basics
   - information flow policy
   - multimodal safety and alignment work
3. **Problem Definition**
   - what system is modeled
   - what counts as a violation
4. **Method**
   - ACM design
   - policy language
   - provenance and detection
5. **Implementation**
   - code structure
   - case format
   - analysis interface
6. **Evaluation**
   - dataset or cases
   - metrics
   - results
7. **Case Studies**
   - 3 to 5 detailed examples
8. **Discussion**
   - what the model captures well
   - what it misses
   - relation to multimodal alignment and safety
9. **Limitations and Future Work**
10. **Conclusion**

## Progress Report Plan
Your progress report should include:
- the final problem framing
- the formal model design
- the current implementation status
- the planned dataset or case suite
- early example outputs
- bibliography

## Minimal Viable Product
If time gets tight, finish this version:
- ACM implementation
- 20 hand-made cases
- three policy types
- detector with explanations
- static figures and tables
- final report with case studies

That is enough for a strong class project.

## Stronger Version
If time goes well, add one or more of these:
- a small Streamlit interface
- real image cases instead of text-only image surrogates
- provenance extraction from an actual multimodal model pipeline
- a comparison between output accuracy and policy-compliance rate
- a VISTA-inspired inspection workflow for auditors

## Why Starting Without Real Images Is Fine
You said you do not love having to use images. That is okay.

A very good version of this project can start with a **symbolic multimodal setup**, where image evidence is represented as a structured description or label set. The key research question is not image processing itself. It is whether a formal security model can represent and audit **cross-source information use**. If that works, real images become a later extension, not a requirement for the core contribution.

## Concrete Step-by-Step Build Order

### Week 1
1. Finalize title and proposal paragraph.
2. Make repo.
3. Implement ACM classes.
4. Define policies JSON schema.
5. Create 5 toy cases.

### Week 2
1. Implement detector.
2. Expand to 15 to 20 cases.
3. Write unit tests for each violation type.
4. Generate first output tables.

### Week 3
1. Add simple visualization.
2. Refine policy definitions.
3. Add 10 to 20 more cases.
4. Start progress report draft.

### Week 4
1. Run evaluation.
2. Select best case studies.
3. Save figures.
4. Draft report sections 1 to 5.

### Week 5
1. Draft evaluation and discussion.
2. Add limitations and future work.
3. Clean repository and outputs.
4. Final polish.

## Suggested Coding Tasks for Codex
You can hand these one by one to Codex.

### Task 1
Create Python dataclasses for an Access Control Matrix with subjects, objects, rights, and helper methods for granting, revoking, and checking rights.

### Task 2
Create a JSON schema and Python loader for policy definitions including required sources, forbidden sources, and consistency rules.

### Task 3
Create a case format and loader for pipeline traces with available sources, used sources, final output, and expected label.

### Task 4
Implement a detector that reads one case and returns whether policy was violated, the violation types, and a human-readable explanation.

### Task 5
Write unit tests for at least 10 cases covering compliant runs and each violation type.

### Task 6
Generate summary tables and plots showing violation counts, case categories, and simple confusion-style summaries.

### Task 7
Create a minimal Streamlit or static HTML viewer for browsing cases and detector outputs.

## Evaluation Plan

### Main evaluation question
Can a formal access-control and information-flow representation help identify and explain multimodal pipeline failures better than output correctness alone?

### Sub-questions
1. Does the detector find the intended violations on labeled cases?
2. Can it separate wrong-output cases caused by bad information flow from wrong-output cases caused by other causes?
3. Does the case trace make failures easier to explain?

### Evaluation method
- Hand-label cases with expected policy result.
- Run detector.
- Compare detected violation labels to expected labels.
- Present case studies.

## Risks and Mitigations

### Risk 1: Too abstract
**Mitigation:** keep the pipeline concrete and case-based.

### Risk 2: Too much ML, not enough security
**Mitigation:** foreground the ACM and policy logic in every section.

### Risk 3: Too much VIS, not enough class fit
**Mitigation:** present visualization as support for inspecting model-based policy violations, not as the main contribution.

### Risk 4: Real images slow you down
**Mitigation:** start with symbolic image evidence and only add real images later.

## Optional Alternative Framing
If you want to reduce the multimodal emphasis while keeping the same structure, rename the project to:

**Auditing Information Flow Violations in LLM Pipelines with Access Control Models**

Then explain that multimodal cases are one application domain rather than the whole project.

## Strong Title Variants
1. Auditing Information Flow Violations in Multimodal LLM Pipelines with Access Control Models
2. Applying Access Control Models to Detect Information Flow Violations in Multimodal LLM Pipelines
3. A Policy-Based Audit Framework for Information Flow in Multimodal LLM Pipelines
4. Modeling and Detecting Information Flow Violations in Multimodal AI Systems

## Short Novelty Statement for the Report
Existing multimodal safety and alignment work mainly evaluates outputs, benchmark scores, or embedding quality. This project instead applies a formal access-control and information-flow perspective to model and detect inference-time policy violations inside a multimodal LLM pipeline.

## Suggested Bibliography Seed
- Xiwei Xuan, Xiaoqi Wang, Wenbin He, Jorge Piazentin Ono, Liang Gou, Kwan-Liu Ma, and Liu Ren. **VISTA: A Visual Analytics Framework to Enhance Foundation Model-Generated Data Labels.** IEEE TVCG / VIS 2025 workshop context.
- Kaiwen Zhou, Chengzhi Liu, Xuandong Zhao, Anderson Compalas, Dawn Song, and Xin Eric Wang. **Multimodal Situational Safety.** ICLR 2025.
- Xin Liu, Yichen Zhu, Jindong Gu, Yunshi Lan, Chao Yang, and Yu Qiao. **MM-SafetyBench: A Benchmark for Safety Evaluation of Multimodal Large Language Models.** ECCV 2024.
- Yilin Ye, Shishi Xiao, Xingchen Zeng, and Wei Zeng. **ModalChorus: Visual Probing and Alignment of Multi-modal Embeddings via Modal Fusion Map.** IEEE VIS 2024.
- Matt Bishop. **Computer Security: Art and Science.** Relevant chapters on reference monitor, ACM, safety, and information flow.

## Final Recommendation
For the course, the best version of this project is:
- security-forward
- model-first
- small but polished
- light on heavy ML
- optionally inspired by VISTA in presentation style

If you build the ACM, policies, detector, and a small but clear case analysis workflow, that is already a strong and defensible solo project.
