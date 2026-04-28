# Security Project Reference Guide

This file explains why each reference matters for the project and how it supports the kind of term project described in `docs/reference/term_project.txt`.

## How these references map to the class project

The course handout says a good project can be either:

- a programming project that implements a model or formalism, or
- a project that develops and applies a model to reason about a security problem.

This project fits most directly under:

- "Build a run-time system that detects flows that violate a policy specifying security or integrity levels"
- "Develop and apply a model that provides information or verification to a system or some other entity"

The references below support one of four roles:

- formal security framing
- LLM / multimodal safety motivation
- attack and benchmark evidence
- visualization / inspection support

## Core references already in the project

### 1. Multimodal Situational Safety

- Citation key: `zhou2025multimodal`
- Local file: `docs/papers/multimodal_situational_safety-kaiwen_zhou.pdf`
- Why it matters:
  - Shows that model safety often depends on combining the user query with the surrounding context.
  - This supports the core project idea that "which sources influenced the answer" matters, not just whether the final answer looks good or bad.
- Best use in report:
  - Motivation for required-source policies.
  - Example: some answers should require both the prompt and visual evidence.

### 2. MM-SafetyBench

- Citation key: `liu2024mmsafetybench`
- Local file: `docs/papers/mm-safetybench-xin_liu.pdf`
- Why it matters:
  - Shows that multimodal models can be manipulated by image-relevant content.
  - This helps justify forbidden-source or adversarial-source policies.
- Best use in report:
  - Background showing that multimodal context can alter behavior in security-relevant ways.
  - Good support for attack-driven case design.

### 3. ModalChorus

- Citation key: `ye2024modalchorus`
- Local file: `docs/papers/modalchorus-yilin_ye.pdf`
- Why it matters:
  - This is mainly useful for the VIS side of the project.
  - It supports the idea that cross-modal behavior benefits from visual inspection tools, not just scalar benchmark scores.
- Best use in report:
  - Justify a small trace view, matrix view, or case inspection interface.
  - Not core to the security claim, but useful for presentation and analysis.

### 4. VISTA

- Citation key: `xuan2024vista`
- Local file: `docs/papers/vista-xiwei_xuan.pdf`
- Why it matters:
  - Useful as a visual analytics connection and as a mentor-relevant paper.
  - Supports human-in-the-loop inspection and the value of structured visual analysis when automated outputs are imperfect.
- Best use in report:
  - Justify the analysis interface.
  - Explain the VIS contribution as support for the security model, not as the main result.

## Additional references to add for the progress report

### 5. The Instruction Hierarchy

- Citation key: `wallace2024instructionhierarchy`
- URL: https://arxiv.org/abs/2404.13208
- PDF: https://arxiv.org/pdf/2404.13208
- Why it matters:
  - This is one of the strongest additions for your project.
  - It explicitly argues that different inputs to an LLM have different privilege levels: system messages, user messages, and tool outputs should not all be treated equally.
  - That idea is very close to your ACM / access-control framing.
- Best use in report:
  - Connect access-control ideas to modern LLM behavior.
  - Support the claim that a privilege-aware or policy-aware analysis of source use is meaningful.
- Relation to course expectations:
  - Strong support for the "apply a security model to a modern system" angle.

### 6. Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models

- Citation key: `yi2023bipia`
- URL: https://arxiv.org/abs/2312.14197
- PDF: https://arxiv.org/pdf/2312.14197
- Why it matters:
  - Introduces BIPIA, an early benchmark for indirect prompt injection.
  - The key idea is that external content can act like a malicious instruction source.
  - That maps well to your project's notion of disallowed or mis-prioritized information flow.
- Best use in report:
  - Evidence that "untrusted context influences outputs" is a real security problem.
  - Good justification for forbidden-source policy cases.
- Relation to course expectations:
  - Strong support for building a detector for policy violations in a pipeline.

### 7. INJECAGENT

- Citation key: `zhan2024injecagent`
- URL: https://aclanthology.org/2024.findings-acl.624/
- PDF: https://aclanthology.org/2024.findings-acl.624.pdf
- Why it matters:
  - Extends the indirect prompt injection idea into tool-using LLM agents.
  - Very relevant if your progress-report version includes a simplified pipeline with retrieval, memory, or tool output.
- Best use in report:
  - Support future expansion from plain prompt-context-output to a richer multi-step pipeline.
  - Helps justify treating tool outputs and retrieved context as separate objects in the ACM.
- Relation to course expectations:
  - Supports the "run-time detection of policy-violating flows" direction in a more realistic application setting.

### 8. Computer Security: Art and Science

- Citation key: `bishop2018cas`
- Why it matters:
  - This is the formal security anchor.
  - It gives you course-aligned language for access control, protection systems, security models, and information flow.
- Best use in report:
  - Background section on ACM, policy, and security reasoning.
  - Keeps the project grounded in class concepts rather than becoming only an LLM evaluation project.

## Recommended bibliography shape for the progress report

For the one-page progress report, you do not need a huge bibliography. A good set would be:

- `bishop2018cas`
- `wallace2024instructionhierarchy`
- `yi2023bipia`
- `zhan2024injecagent`
- `zhou2025multimodal`
- `liu2024mmsafetybench`
- `xuan2024vista`
- `ye2024modalchorus`

That is already a strong and balanced list:

- 1 formal security reference
- 3 direct LLM security / injection references
- 2 multimodal safety references
- 2 visual analytics / inspection references

## Practical recommendation

For the progress report, the strongest narrative is:

- Bishop gives the formal security grounding.
- Instruction Hierarchy gives the privilege / policy intuition inside LLM systems.
- BIPIA and INJECAGENT show why untrusted context is a real attack surface.
- Multimodal Situational Safety and MM-SafetyBench motivate context-sensitive case design.
- VISTA and ModalChorus justify the analysis / inspection part without making VIS the main claim.
