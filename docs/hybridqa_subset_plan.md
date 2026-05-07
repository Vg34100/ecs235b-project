# HybridQA Subset Plan

## Goal

Start the `HybridQA` extension with a small pilot subset that is large enough to test the schema, policies, and trace pipeline, but small enough to inspect manually.

## Recommended starting size

Use an initial curated subset of:

- `12` cases

Why `12`:

- large enough to show more than a few isolated examples
- small enough to inspect by hand
- enough to cover several question styles without turning the extension into a full evaluation too early

This should be treated as:

- the first curated extension subset

not:

- the final HybridQA evaluation set

## Current selection strategy

The current plan is:

1. keep the `4` strongest cases found in the first pilot pass
2. add `8` more cases of similar quality
3. convert only those selected case ids

This is better than trying to force weaker pilot cases into the extension just
to keep the count at `12`.

The selected ids are tracked in:

- `data/processed/hybridqa/hybridqa_selected_ids.txt`

## Selection criteria

The first subset should prefer cases with:

1. clear table structure
- readable headers
- at least a few rows

2. usable linked text
- at least two linked summaries available
- summaries that are not empty

3. concise answers
- short enough to inspect easily
- not overly open-ended

4. likely multi-source reasoning
- cases where the table gives the structural anchor
- linked text adds the detail needed to answer

5. readable prompts
- questions that are easy to explain in the final report

## What to avoid in the first subset

Avoid cases with:

- missing linked summaries
- extremely long answers
- highly noisy or unclear table structure
- cases that are hard to explain as a source-policy example
- cases that only barely meet the filter but do not tell a clean story

## Initial policy framing

The first HybridQA pilot should start with two policy styles.

### Policy style A: required table source

Required sources:

- `user_prompt`
- `table_evidence`

Use when:

- the answer should not be possible without the table

### Policy style B: required table plus linked text

Required sources:

- `user_prompt`
- `table_evidence`
- `linked_text`

Use when:

- the table identifies the relevant row or entity
- the linked text provides the answer detail

## Initial violation types to test

The first pilot should reuse the same detector categories already present in the core:

- `missing_required_source`
- `forbidden_source_used`
- `consistency_violation`

For the first pass, the most realistic focus is:

- required-source checks
- consistency checks

Forbidden-source cases can be added later by injecting a hint or hidden field.

## Current seed cases

The first retained `4` strong cases are:

- `hybridqa_00009b9649d0dd0a`
- `hybridqa_0003d159df86ed53`
- `hybridqa_0005a713626c28a0`
- `hybridqa_000bc36c03f433dc`

The broader curated `12`-case seed set also includes:

- `hybridqa_00046dbd53dd3200`
- `hybridqa_000d0258517492bb`
- `hybridqa_00136a47aba3ae45`
- `hybridqa_0015116d416d9775`
- `hybridqa_0017ed9b0d641d8a`
- `hybridqa_00192b737629eda1`
- `hybridqa_001b79f54ba2e956`
- `hybridqa_001de292836914d1`

## Pilot deliverables

The first HybridQA pilot should produce:

1. a converted curated `12`-case subset
2. readable compact table/text source blocks
3. stable schema-compatible cases
4. at least a few hand-inspected examples to confirm the extension is worth scaling

## Next step after the pilot

If the 12-case pilot looks good, the next extension phase should be:

- expand to around `20` converted cases
- define a small set of explicit policy-labeled cases
- run the same trace and detector pipeline on that subset
