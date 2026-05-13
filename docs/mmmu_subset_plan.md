# MMMU Subset Plan

## Goal

Use `MMMU` as the image-focused multimodal extension after the `HybridQA`
table-text path. The first target should stay small, readable, and strongly
aligned with the project's source-policy framing.

## Current raw slice

The project currently has only this local `MMMU` slice:

- subject: `Computer_Science`
- splits:
  - `dev` (`5` examples)
  - `validation` (`30` examples)

Observed structure from local inspection:

- mostly single-image questions
- mostly `multiple-choice`
- image types are dominated by `Diagrams`
- smaller number of:
  - `Tables`
  - `Plots and Charts`
  - `Trees and Graphs`

This is a good first image-side slice because:

- it is small enough to inspect directly
- the visual content is more structured than natural-image VQA
- diagrams and tables fit the current source-audit framing better

## Recommended first MMMU pilot

Start with a pilot subset of:

- `8` to `10` cases

Recommended preference order:

1. `Diagrams`
2. `Tables`
3. `Plots and Charts`

Avoid first-pass focus on:

- highly abstract graph-only questions
- questions that require long multi-step numeric reasoning
- open-ended text generation when a cleaner multiple-choice case exists

## Selection criteria

The first `MMMU` pilot should prefer cases with:

1. single-image evidence
- easier to map to one `image_evidence` source

2. multiple-choice format
- easier consistency checking
- easier final-report explanation

3. short, concrete answer target
- usually one option label or one option string

4. visually grounded question
- question should clearly require looking at the image
- not something mostly answerable from background knowledge alone

5. explainable source-policy story
- easy to say why `image_evidence` is required

## Initial case types to prefer

Best first cases:

- ER / schema diagrams
- linked-list or data-structure diagrams
- circuit / truth-table diagrams
- OS scheduling or resource-allocation diagrams
- simple visual tables

These are closest to the project's existing strengths because they are:

- structured
- interpretable
- easy to describe in a case study

## Cases to avoid at first

Avoid:

- long free-response answers
- multi-image cases when a single-image case is available
- highly ambiguous visual scenes
- cases where answer checking would require broad semantic equivalence
- cases where the image type is not easy to describe in the final report

## First policy framing

The first `MMMU` pass should focus on:

- `missing_required_source`
- `consistency_violation`

The first pilot should **not** focus on:

- `forbidden_source_used`

unless a later extension explicitly injects a hidden or misleading textual hint.

## First confirmatory question

The first confirmatory question for `MMMU` should be:

- can the current audit framework detect when a model answers inconsistently
  with image-based evidence on a small curated image-text subset?

That is a clean first claim. It does not require solving the harder problem of
visual-source attribution perfectly.

## Next step

The next implementation step should be:

1. define the MMMU-to-schema mapping
2. choose `8` to `10` pilot cases from `Computer_Science`
3. build a converter into the shared project case schema
4. run the same trace and detector pipeline on the converted subset
