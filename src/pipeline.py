import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PipelineResponse:
    # Keep the raw output because parser failures are common and worth inspecting.
    answer: str
    used_sources: list[str]
    reason: str
    raw_output: str


class LLMRunner:
    """Small wrapper so we can switch between real HF model and mock mode.

    This is not meant to be a full serving layer. It just gives us one place to
    swap between a real local model and a mock path.
    """

    def __init__(self, model_id: str, mock_mode: bool = False) -> None:
        self.model_id = model_id
        self.mock_mode = mock_mode
        self._generator = None
        self._tokenizer = None

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
            self._tokenizer = tokenizer

            # Pipeline API keeps the MVP simple. We can drop lower later if needed.
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

        # For ablations we can blank out one source without rewriting the case.
        prompt = build_prompt(case, source_overrides)
        generation_input = prompt
        has_chat_template = bool(getattr(self._tokenizer, "chat_template", None))
        if self._tokenizer is not None and has_chat_template and hasattr(self._tokenizer, "apply_chat_template"):
            # Some instruction models behave better with the native chat template.
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are part of an audited pipeline. "
                        "Return only a JSON object with keys answer, used_sources, reason."
                    ),
                },
                {"role": "user", "content": prompt},
            ]
            generation_input = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

        if self.mock_mode:
            return self._mock_response(case, source_overrides)

        if self._generator is None:
            raise RuntimeError("Model is not loaded. Call load() first.")

        result = self._generator(generation_input, max_new_tokens=max_new_tokens, do_sample=False)
        text = result[0]["generated_text"]
        return parse_model_json(text)

    def _mock_response(self, case: dict[str, Any], source_overrides: dict[str, str]) -> PipelineResponse:
        # Mock mode is just for fast policy/debug runs.
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
            raw_output=json.dumps({"answer": answer, "used_sources": used, "reason": "mock response"}),
        )


def build_prompt(case: dict[str, Any], source_overrides: dict[str, str]) -> str:
    # Keep source names explicit because the detector reasons over these labels.
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
    allowed_sources = {"prompt", "image_evidence", "retrieved_context", "hidden_metadata"}

    # Try strict JSON first, then fall back to a looser heuristic path.
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return heuristic_parse(text, "no json object found", allowed_sources)

    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return heuristic_parse(text, "invalid json", allowed_sources)

    answer = str(payload.get("answer", ""))
    used_sources = payload.get("used_sources", [])
    reason = str(payload.get("reason", ""))

    if not isinstance(used_sources, list):
        used_sources = []

    # Keep only source names we actually model.
    used_sources = [str(s) for s in used_sources if str(s) in allowed_sources]

    if not answer.strip():
        answer = "parse_fallback_empty_answer"
    if not used_sources:
        # Try to recover a usable source signal before giving up.
        used_sources = infer_used_sources_from_text(text, allowed_sources)
        if not used_sources:
            used_sources = ["prompt"]

    return PipelineResponse(answer=answer, used_sources=used_sources, reason=reason, raw_output=text)


def heuristic_parse(text: str, parse_reason: str, allowed_sources: set[str]) -> PipelineResponse:
    # This is the "salvage what we can" path.
    answer = extract_answer_line(text)
    used_sources = infer_used_sources_from_text(text, allowed_sources)

    if not answer:
        answer = "parse_error"
    if not used_sources:
        # Assume at least prompt was consulted unless we have clear evidence otherwise.
        used_sources = ["prompt"]

    return PipelineResponse(
        answer=answer,
        used_sources=used_sources,
        reason=f"{parse_reason}; heuristic_parse",
        raw_output=text,
    )


def extract_answer_line(text: str) -> str:
    # Weak outputs still often include "answer: ..." even without valid JSON.
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        low = line.lower()
        if low.startswith("answer"):
            cleaned = re.sub(r"^[Aa]nswer\s*[:=]\s*", "", line).strip()
            if cleaned:
                return cleaned
    if lines:
        return lines[-1][:300]
    return ""


def infer_used_sources_from_text(text: str, allowed_sources: set[str]) -> list[str]:
    # This is not true attribution, just a fallback signal.
    found = []
    low = text.lower()
    for source in sorted(allowed_sources):
        if source.lower() in low:
            found.append(source)
    return found


def resolve_model_source(model_id: str) -> str:
    """
    Resolve a model id to a local path when possible so we can run offline.
    """
    if os.path.isdir(model_id):
        return model_id

    # Prefer local snapshots because some runs happen without network access.
    normalized = model_id.replace("/", "--")
    cache_root = Path.home() / ".cache" / "huggingface" / "hub" / f"models--{normalized}" / "snapshots"
    if cache_root.exists():
        snapshots = sorted([p for p in cache_root.iterdir() if p.is_dir()])
        if snapshots:
            return str(snapshots[-1])

    return model_id
