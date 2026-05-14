# Final Figure Plan

## Purpose

This document defines the minimum useful figure set for the final report or a
conference-style draft.

The goal is not to build polished visuals immediately. The goal is to decide
which comparisons and case-study views matter enough that future experiments
should preserve them.

## Figure 1: Benchmark Overview Table

Type:

- summary table

Purpose:

- show the three benchmark settings side by side

Rows:

- `InjecAgent`
- `HybridQA`
- `MMMU`

Columns:

- modality
- final reported slice
- model
- answer correctness
- policy compliance
- dominant violation types

Why it matters:

- this is the clearest single figure for orienting the reader

## Figure 2: Correctness vs Compliance Breakdown

Type:

- grouped bar chart or compact table

Purpose:

- show that answer correctness and policy compliance are not the same thing

Suggested buckets:

- correct + compliant
- correct + violating
- incorrect + violating

Apply to:

- `HybridQA`
- `MMMU`

Why it matters:

- this is one of the strongest project-level claims

## Figure 3: MMMU Base vs Forbidden-Hint Comparison

Type:

- side-by-side bar chart or comparison table

Purpose:

- show how the image-text setting changes once the forbidden source is added

Rows or series:

- base `MMMU` pilot
- weak forbidden-hint pilot
- authoritative forbidden-hint pilot

Metrics:

- compliant cases
- consistency violations
- forbidden-source violations

Why it matters:

- this is likely the strongest multimodal security figure in the current
  project

## Figure 4: HybridQA Pilot vs Scale-Up Comparison

Type:

- comparison table or grouped bar chart

Purpose:

- show that case-selection quality materially changes the apparent results

Suggested comparison:

- `12`-case pilot
- broad `20`-case scale-up
- strict additive `20`-case scale-up

Metrics:

- policy compliance
- answer correctness
- correct-but-violating cases

Why it matters:

- it supports the methodological point that scaling the extension is not just a
  quantity problem

## Figure 5: Representative Case Panels

Type:

- case-study panels

Purpose:

- make the trace-level reasoning visible

Recommended panel structure:

1. case id and benchmark
2. prompt and evidence summary
3. expected answer
4. model answer
5. used sources
6. violation label
7. short interpretation

Recommended cases:

- one compliant `InjecAgent` case
- one attacker-following `InjecAgent` case
- one answer-correct but attribution-ambiguous `HybridQA` case
- one `MMMU` base consistency failure
- one `MMMU` authoritative forbidden-hint success case

Why it matters:

- this is the most report-friendly bridge between numbers and interpretation

## Figure 6: Source-Flow Diagram

Type:

- schematic diagram

Purpose:

- visualize the shared audit framework

Nodes:

- user prompt
- system policy
- evidence source(s)
- optional forbidden source
- model output
- detector

Overlays:

- required sources
- forbidden sources
- compliant flow
- violating flow

Why it matters:

- this helps tie the security framing to the benchmark adapters

## Recommended order of implementation

Build these in this order:

1. Figure 1
2. Figure 3
3. Figure 2
4. Figure 5
5. Figure 4
6. Figure 6

Reason:

- the first three are the most directly useful for writing
- the last three are more presentation-heavy

## What should happen now

At this stage, the project should do only lightweight figure preparation:

- lock the metrics each figure needs
- keep benchmark slices stable enough to populate them
- avoid overinvesting in polishing until the main experiments are locked

That means the right next implementation path is:

- preserve comparison-ready summaries in `findings.md`
- keep derived stress-test files separate and versioned
- only later build actual plotting scripts or notebook outputs
