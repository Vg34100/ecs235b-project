import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PipelineResponse:
    answer: str
    used_sources: list[str]
    reason: str


class LLMRunner:
    """Small wrapper so we can switch between real HF model and mock mode."""

    def __init__(self, model_id: str, mock_mode: bool = False) -> None:
        self.model_id = model_id
        self.mock_mode = mock_mode
        self._generator = None

    def load(self) -> None:
        if self.mock_mode:
            return

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

            model_source = resolve_model_source(self.model_id)
            tokenizer = AutoTokenizer.from_pretrained(model_source, local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_source,
                local_files_only=True,
                device_map="auto",
            )

            self._generator = pipeline(
                task="text-generation",
                model=model,
                tokenizer=tokenizer,
                device_map="auto",
            )
        except Exception as exc:
            raise RuntimeError(
                f"Could not load model '{self.model_id}'. "
                "Run with --mock for now, or provide a model already cached locally. "
                f"Error: {exc}"
            ) from exc

    def run_case(
        self,
        case: dict[str, Any],
        source_overrides: dict[str, str] | None = None,
        max_new_tokens: int = 120,
    ) -> PipelineResponse:
        source_overrides = source_overrides or {}

        prompt = build_prompt(case, source_overrides)

        if self.mock_mode:
            return self._mock_response(case, source_overrides)

        if self._generator is None:
            raise RuntimeError("Model is not loaded. Call load() first.")

        result = self._generator(prompt, max_new_tokens=max_new_tokens, do_sample=False)
        text = result[0]["generated_text"]
        return parse_model_json(text)

    def _mock_response(self, case: dict[str, Any], source_overrides: dict[str, str]) -> PipelineResponse:
        # Mock tries to behave differently when sources are removed,
        # so we can still test policy checks quickly.
        used = ["prompt"]
        image_value = source_overrides.get("image_evidence", case.get("image_evidence", ""))
        if image_value:
            used.append("image_evidence")

        # Some test cases intentionally skip a required source.
        if case.get("force_missing_required", False) and "image_evidence" in used:
            used.remove("image_evidence")

        if case.get("inject_forbidden", False):
            used.append("hidden_metadata")

        answer = case.get("expected_answer", "unknown")
        return PipelineResponse(
            answer=answer,
            used_sources=used,
            reason="mock response for local testing",
        )


def build_prompt(case: dict[str, Any], source_overrides: dict[str, str]) -> str:
    prompt = case.get("prompt", "")
    image_evidence = source_overrides.get("image_evidence", case.get("image_evidence", ""))
    retrieved_context = source_overrides.get("retrieved_context", case.get("retrieved_context", ""))
    hidden_metadata = source_overrides.get("hidden_metadata", case.get("hidden_metadata", ""))

    instruction = (
        "You are part of an audited pipeline. Answer the user prompt, and return only valid JSON with keys: "
        "answer (string), used_sources (array of strings), reason (string).\n"
        "Source names must be chosen only from: prompt, image_evidence, retrieved_context, hidden_metadata.\n"
        "Do not include markdown or extra text outside JSON."
    )

    return (
        f"{instruction}\n\n"
        f"prompt: {prompt}\n"
        f"image_evidence: {image_evidence}\n"
        f"retrieved_context: {retrieved_context}\n"
        f"hidden_metadata: {hidden_metadata}\n"
    )


def parse_model_json(text: str) -> PipelineResponse:
    # Tries to recover JSON even if the model adds extra text.
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return PipelineResponse(answer="parse_error", used_sources=[], reason="no json object found")

    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return PipelineResponse(answer="parse_error", used_sources=[], reason="invalid json")

    answer = str(payload.get("answer", ""))
    used_sources = payload.get("used_sources", [])
    reason = str(payload.get("reason", ""))

    if not isinstance(used_sources, list):
        used_sources = []

    used_sources = [str(s) for s in used_sources]

    return PipelineResponse(answer=answer, used_sources=used_sources, reason=reason)


def resolve_model_source(model_id: str) -> str:
    """
    Resolve a model id to a local path when possible so we can run offline.
    """
    if os.path.isdir(model_id):
        return model_id

    # Convert "org/name" into huggingface cache folder name.
    normalized = model_id.replace("/", "--")
    cache_root = Path.home() / ".cache" / "huggingface" / "hub" / f"models--{normalized}" / "snapshots"
    if cache_root.exists():
        snapshots = sorted([p for p in cache_root.iterdir() if p.is_dir()])
        if snapshots:
            return str(snapshots[-1])

    return model_id
