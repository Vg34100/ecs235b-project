# MMMU Schema Mapping

## Goal

Map `MMMU` Computer_Science image-text examples into the same shared project
schema already used by `InjecAgent` and `HybridQA`.

The point is not to create a separate evaluation system. The point is to reuse:

- the same case structure
- the same trace outputs
- the same policy detector

while introducing a real image-based source.

## Raw MMMU fields

Observed local fields:

- `id`
- `question`
- `options`
- `explanation`
- `image_1` ... `image_7`
- `img_type`
- `answer`
- `topic_difficulty`
- `question_type`
- `subfield`

For the first `Computer_Science` pilot, most useful cases are:

- single-image
- multiple-choice

So the first mapping can stay simple.

## Local case mapping

### `case_id`

Use:

- `mmmu_<raw id>`

Example:

- `mmmu_validation_Computer_Science_4`

### `dataset_source`

Use:

- `MMMU`

### `domain`

Use:

- `computer_science_vision`

This keeps the image extension distinct from:

- `tabular_reasoning`
- the earlier text-only domains in `InjecAgent`

### `task_type`

Use:

- `image_text_reasoning`

This allows prompt-building logic to specialize later if needed, without
splitting the whole framework.

## Source mapping

### `user_prompt`

Source:

- the MMMU `question`

### `image_evidence`

Source:

- `image_1` for the first pilot

Represent it as:

- local image path or saved image object reference
- plus light metadata such as:
  - `img_type`
  - `subfield`

If later cases use multiple images, expand this to:

- ordered list of image slots actually present

### `system_policy`

Use a standard image-grounding instruction such as:

- use the question and the provided image evidence as the authoritative sources
- do not rely on unsupported hidden hints

### `options`

For multiple-choice MMMU, options should be preserved.

Recommendation:

- include options in the prompt text
- also store them in `benchmark_metadata`

This keeps the visible task faithful to the original benchmark while still
letting the shared schema stay compact.

## Expected behavior

### `expected_behavior.expected_answer`

Use:

- the benchmark `answer`

For multiple-choice questions, this may be:

- an option letter such as `A`

or:

- the option text, depending on how the local prompt is written

For the first pilot, it is cleaner to prompt the model to answer with:

- the option letter only

That makes consistency checking simpler.

### Additional expected behavior fields

Useful initial fields:

- `should_use_image`: `True`
- `question_type`
- `img_type`

## Required sources

For the first pilot, required sources should usually be:

- `user_prompt`
- `image_evidence`

`system_policy` should remain available and visible, but the primary required
evidence source is the image.

## Forbidden sources

For the first MMMU pilot:

- leave `forbidden_sources` empty

Later, if we add an injected text hint or misleading metadata field, the image
extension could also test:

- `forbidden_source_used`

But that is not required for the first pass.

## Consistency rules

For the first pilot, use a simple rule:

- final answer should be consistent with the image evidence

For multiple-choice questions, this means:

- the selected answer should match the benchmark-backed correct option

## Policy framing for the first pilot

The first realistic policy checks are:

1. `missing_required_source`
- image evidence was not credited or not used

2. `consistency_violation`
- final answer does not match the expected answer supported by the image

This keeps the first `MMMU` pass aligned with the current `HybridQA` extension:

- focus first on required-source use and evidence consistency

## Output target

The first converted output should probably look like:

- `data/processed/mmmu/mmmu_computer_science_pilot_subset.json`

That keeps the same processed-data pattern used by:

- `InjecAgent`
- `HybridQA`
