"""
python/discovery/formalizer.py - Prose to formal hypothesis (ADR-DISCOVERY-061).

A language model turns a hypothesis written in prose into the formal object of ADR-DISCOVERY-059/060. The model is
only a translator: its output is parsed, validated and evaluated by the formal evaluator, which is the verifier
(ADR-DISCOVERY-002). Nothing the model says about the hypothesis is trusted; only the object it emits is checked.

The model is reached through any OpenAI-compatible chat endpoint (Ollama, LM Studio, vLLM, llama.cpp server).
Configuration comes from the environment: FORMALIZER_BASE_URL (for example http://localhost:11434/v1),
FORMALIZER_MODEL, and optionally FORMALIZER_API_KEY. No key value is ever logged.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from python.discovery.formal_hypothesis import (
    FormalHypothesisError,
    Hypothesis,
    HypothesisEvaluator,
    hypothesis_from_dict,
)

PROMPT_VERSION = "formalizer-v1"

SYSTEM_PROMPT = """You translate scientific hypotheses written in prose into a formal object. You do not judge the \
hypothesis, add knowledge, or fix it. You state exactly what the text asserts, under the conditions the text gives.

Output one JSON object and nothing else, with these keys:
- "variables": list of {"name": identifier, "domain": [values]} for finite variables, or
  {"name": identifier, "continuous": true, "lower": number or null, "upper": number or null} for real quantities.
- "scope": a predicate saying where the hypothesis applies, or null.
- "assumptions": list of predicates the text takes for granted (auxiliary conditions).
- "claims": list of predicates the text asserts must hold wherever scope and assumptions hold.
- "alternatives": list of short prose names of rival explanations the text mentions (may be empty).

Predicates are Python-like boolean expressions over the variables only: comparisons (== != < <= > >=), and, or,
not, + - * /, constant integer powers (x**2), and membership in literal lists (x in ('a', 'b')). Strings are
quoted. No function calls, no attributes, no variables other than those declared.

An implication "if P then Q" is written as the claim "not (P) or (Q)". If a variable schema is given, use exactly
those variable names and domains and do not add variables."""

USER_TEMPLATE = """Hypothesis:
{prose}

Variable schema (use exactly these variables; null means choose them yourself):
{schema}"""


def prompt_sha256() -> str:
    """Fingerprint of the frozen prompt, recorded in the benchmark pre-registration."""
    return hashlib.sha256((PROMPT_VERSION + SYSTEM_PROMPT + USER_TEMPLATE).encode("utf-8")).hexdigest()


def build_messages(prose: str, variable_schema: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, str]]:
    schema = json.dumps(variable_schema, ensure_ascii=False) if variable_schema is not None else "null"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_TEMPLATE.format(prose=prose.strip(), schema=schema)},
    ]


class FormalizationStatus(str, Enum):
    NO_JSON = "NO_JSON"  # The output contains no JSON object.
    INVALID = "INVALID"  # JSON found, but it is not a valid formal hypothesis.
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"  # Valid, but the variables differ from the schema it was given.
    PARSED = "PARSED"


@dataclass
class Formalization:
    status: FormalizationStatus
    hypothesis: Optional[Hypothesis] = None
    error: str = ""
    raw_output: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """First JSON object in the text: inside a code fence if there is one, else the first balanced {...}."""
    candidates = [m.group(1) for m in _FENCE.finditer(text)]
    start = text.find("{")
    while start != -1:
        depth, in_string, escape, end = 0, False, False, -1
        for i in range(start, len(text)):
            ch = text[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
            elif ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidates.append(text[start : i + 1])
                    end = i
                    break
        start = text.find("{", (end if end != -1 else start) + 1)
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def _variable_spec(variables: List[Dict[str, Any]]) -> List[tuple]:
    return sorted(
        (
            v.get("name"),
            tuple(v.get("domain") or ()),
            bool(v.get("continuous", False)),
            v.get("lower"),
            v.get("upper"),
        )
        for v in variables
    )


def parse_formalization(
    text: str, hypothesis_id: str = "H", variable_schema: Optional[List[Dict[str, Any]]] = None
) -> Formalization:
    """Parses a model output into a validated Hypothesis, or says precisely why it could not."""
    data = extract_json(text)
    if data is None:
        return Formalization(FormalizationStatus.NO_JSON, error="No JSON object in the output.", raw_output=text)
    data = {**data, "hypothesis_id": hypothesis_id}
    try:
        hypothesis = hypothesis_from_dict(data)
    except (FormalHypothesisError, TypeError, ValueError) as exc:
        return Formalization(FormalizationStatus.INVALID, error=str(exc), raw_output=text, data=data)
    if variable_schema is not None and _variable_spec(data.get("variables", [])) != _variable_spec(variable_schema):
        return Formalization(
            FormalizationStatus.SCHEMA_MISMATCH,
            hypothesis=hypothesis,
            error="Variables differ from the schema given in the prompt.",
            raw_output=text,
            data=data,
        )
    return Formalization(FormalizationStatus.PARSED, hypothesis=hypothesis, raw_output=text, data=data)


class ChatClient:
    """Minimal OpenAI-compatible chat client. Deterministic decoding (temperature 0, fixed seed)."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 300.0,
    ):
        self.base_url = (base_url or os.getenv("FORMALIZER_BASE_URL") or "http://localhost:11434/v1").rstrip("/")
        self.model = model or os.getenv("FORMALIZER_MODEL") or ""
        self._api_key = api_key or os.getenv("FORMALIZER_API_KEY") or ""
        self.timeout = timeout
        if not self.model:
            raise ValueError("Set FORMALIZER_MODEL (or pass model=) to the model name served at the endpoint.")

    def complete(self, messages: List[Dict[str, str]]) -> str:
        import httpx

        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            json={"model": self.model, "messages": messages, "temperature": 0, "seed": 0},
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def formalize(
    prose: str,
    client: ChatClient,
    hypothesis_id: str = "H",
    variable_schema: Optional[List[Dict[str, Any]]] = None,
) -> Formalization:
    output = client.complete(build_messages(prose, variable_schema))
    return parse_formalization(output, hypothesis_id, variable_schema)


def formalize_and_evaluate(
    prose: str,
    client: ChatClient,
    hypothesis_id: str = "H",
    variable_schema: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """The end-to-end path: prose -> formal object -> exact evaluation. The evaluation only covers the object."""
    result = formalize(prose, client, hypothesis_id, variable_schema)
    payload: Dict[str, Any] = {"status": result.status.value, "error": result.error, "formal_hypothesis": result.data}
    if result.hypothesis is not None and result.status == FormalizationStatus.PARSED:
        payload["evaluation"] = HypothesisEvaluator.evaluate(result.hypothesis).to_dict()
    return payload
