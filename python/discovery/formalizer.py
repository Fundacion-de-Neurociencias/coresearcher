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

    def complete(
        self, messages: List[Dict[str, str]], temperature: float = 0.0, seed: int = 0, json_mode: bool = False
    ) -> str:
        """One completion. The defaults are the frozen benchmark decoding; the self-consistency gate
        (ADR-DISCOVERY-064) passes other seeds and a positive temperature to draw independent samples.
        `json_mode` asks the endpoint for a JSON object (OpenAI `response_format`); endpoints that ignore it are
        still parsed and validated the same way."""
        import httpx

        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
        body: Dict[str, Any] = {"model": self.model, "messages": messages, "temperature": temperature, "seed": seed}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            json=body,
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


# --- formalizer-v2 (ADR-DISCOVERY-093) -----------------------------------------------------------------------------
#
# v1 stays frozen for the round-0 benchmark and the gate's history. v2 adds, without trusting the model more:
#   1. explicit translation rules for the phrasings that failed in round 0, and worked examples on other topics;
#   2. JSON mode where the endpoint supports it;
#   3. a deterministic repair of surface syntax (never of meaning) before validation;
#   4. one self-repair round: the validator's exact error goes back to the model once.
# The output is still parsed, validated and evaluated by the exact evaluator. A repair only turns notation the
# evaluator rejects into the notation the text unambiguously spells. It never adds, drops or reorders a claim, never
# changes a comparison, and touches a variable's domain only when a schema was given.

PROMPT_VERSION_V2 = "formalizer-v2"

SYSTEM_PROMPT_V2 = (
    SYSTEM_PROMPT
    + """

Translation rules. Follow them literally:
- "P only if Q" means: whenever P holds, Q holds. Write "not (P) or (Q)". It does NOT mean "if Q then P".
- "If P then Q", "whenever P, Q", "P implies Q": write "not (P) or (Q)". "P if and only if Q": write both directions.
- "never decreases" or "does not decrease": the later value is >= the earlier value. "never increases": <=.
- Keep strictness exactly: "below", "less than", "under" are <; "at most", "no more than" are <=; "above",
  "exceeds", "more than", "greater than" are >; "at least", "no less than" are >=.
- Conditions that only say where or for whom the statement applies ("in adults", "where the predator is present",
  "among carriers") go in "scope". Conditions the text takes for granted as background facts go in "assumptions".
- Assert only what the text asserts. Do not add claims, do not split a claim into extra conditions the text does not
  state, and do not restate a definition as an extra claim.
- Never fix the text. If it is contradictory, vacuous or trivially true, translate it exactly as written, for
  example keep "younger than 40 and older than 80" as two conditions that must both hold.
- Boolean variables are used directly: write "active" or "not active", never "active == true".
- Use only the operators listed above: no "implies", "->", "=>", "&&", "||", "!", "^" or unicode symbols."""
)

FEW_SHOT_V2: List[Dict[str, Any]] = [
    {
        "prose": "A seedling survives only if soil moisture is at least 12 percent.",
        "schema": [
            {"name": "survives", "domain": [True, False]},
            {"name": "moisture", "continuous": True, "lower": 0, "upper": 100},
        ],
        "answer": {
            "variables": [
                {"name": "survives", "domain": [True, False]},
                {"name": "moisture", "continuous": True, "lower": 0, "upper": 100},
            ],
            "scope": None,
            "assumptions": [],
            "claims": ["not (survives) or (moisture >= 12)"],
            "alternatives": [],
        },
    },
    {
        "prose": "In lakes where nitrate is above 10 mg/L, algal cover stays below 30 percent.",
        "schema": [
            {"name": "nitrate", "continuous": True, "lower": 0, "upper": 100},
            {"name": "cover", "continuous": True, "lower": 0, "upper": 100},
        ],
        "answer": {
            "variables": [
                {"name": "nitrate", "continuous": True, "lower": 0, "upper": 100},
                {"name": "cover", "continuous": True, "lower": 0, "upper": 100},
            ],
            "scope": "nitrate > 10",
            "assumptions": [],
            "claims": ["cover < 30"],
            "alternatives": [],
        },
    },
    {
        "prose": "For birds that are both lighter than 20 g and heavier than 500 g, migration distance is at most "
        "100 km; and a bird's wingspan never decreases between its first and second year.",
        "schema": [
            {"name": "mass", "continuous": True, "lower": 0, "upper": 2000},
            {"name": "distance", "continuous": True, "lower": 0, "upper": 20000},
            {"name": "span_first", "continuous": True, "lower": 0, "upper": 300},
            {"name": "span_second", "continuous": True, "lower": 0, "upper": 300},
        ],
        "answer": {
            "variables": [
                {"name": "mass", "continuous": True, "lower": 0, "upper": 2000},
                {"name": "distance", "continuous": True, "lower": 0, "upper": 20000},
                {"name": "span_first", "continuous": True, "lower": 0, "upper": 300},
                {"name": "span_second", "continuous": True, "lower": 0, "upper": 300},
            ],
            "scope": None,
            "assumptions": ["mass < 20", "mass > 500"],
            "claims": ["distance <= 100", "span_second >= span_first"],
            "alternatives": [],
        },
    },
]


def prompt_sha256_v2() -> str:
    """Fingerprint of the frozen v2 prompt, including its worked examples."""
    blob = PROMPT_VERSION_V2 + SYSTEM_PROMPT_V2 + USER_TEMPLATE + json.dumps(FEW_SHOT_V2, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build_messages_v2(prose: str, variable_schema: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, str]]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT_V2}]
    for example in FEW_SHOT_V2:
        user = USER_TEMPLATE.format(prose=example["prose"], schema=json.dumps(example["schema"]))
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": json.dumps(example["answer"])})
    schema = json.dumps(variable_schema, ensure_ascii=False) if variable_schema is not None else "null"
    messages.append({"role": "user", "content": USER_TEMPLATE.format(prose=prose.strip(), schema=schema)})
    return messages


_SURFACE = [
    (re.compile(r"&&"), " and "),
    (re.compile(r"\|\|"), " or "),
    (re.compile(r"!(?!=)"), " not "),
    (re.compile("≤"), "<="),
    (re.compile("≥"), ">="),
    (re.compile("≠"), "!="),
    (re.compile("¬"), " not "),
    (re.compile("∧"), " and "),
    (re.compile("∨"), " or "),
    (re.compile(r"(?<![=!<>])=(?![=>])"), "=="),  # a lone "=" in a predicate can only mean equality
    (re.compile(r"\^"), "**"),
    (re.compile(r"\bTRUE\b|\btrue\b"), "True"),
    (re.compile(r"\bFALSE\b|\bfalse\b"), "False"),
]
_BOOL_TRUE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*==\s*True\b")
_BOOL_FALSE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*==\s*False\b")
_IMPLIES = re.compile("\\s*(?:\\bimplies\\b|->|=>|⇒|→)\\s*")


def _top_level_split(expr: str, sep: "re.Pattern[str]") -> Optional[List[str]]:
    """Splits at separators outside parentheses and quotes; None when there is none at top level."""
    parts, depth, quote, last, i = [], 0, "", 0, 0
    while i < len(expr):
        ch = expr[i]
        if quote:
            quote = "" if ch == quote else quote
        elif ch in "'\"":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0:
            m = sep.match(expr, i)
            if m and m.end() > i:
                parts.append(expr[last:i])
                last = i = m.end()
                continue
        i += 1
    if not parts:
        return None
    parts.append(expr[last:])
    return parts


def repair_predicate(expr: Any) -> Any:
    """Surface-syntax repair: rewrites notation the evaluator rejects into the notation it accepts, nothing else."""
    if not isinstance(expr, str):
        return expr
    parts = _top_level_split(expr.strip(), _IMPLIES)
    out = f"not ({parts[0].strip()}) or ({parts[1].strip()})" if parts and len(parts) == 2 else expr.strip()
    for pattern, replacement in _SURFACE:
        out = pattern.sub(replacement, out)
    out = _BOOL_TRUE.sub(lambda m: m.group(1), out)
    out = _BOOL_FALSE.sub(lambda m: f"not {m.group(1)}", out)
    return re.sub(r"\s+", " ", out).strip()


def repair_data(data: Dict[str, Any], variable_schema: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Repairs every predicate field. With a schema whose variable names the model kept, the schema's domains are
    restored: the prompt fixes them, so a changed domain is a transcription error, not a different hypothesis."""
    fixed = dict(data)
    for key in ("claims", "assumptions"):
        if isinstance(fixed.get(key), list):
            fixed[key] = [repair_predicate(p) for p in fixed[key]]
        elif fixed.get(key) is None:
            fixed[key] = []
    scope = fixed.get("scope")
    fixed["scope"] = repair_predicate(scope) if isinstance(scope, str) and scope.strip() else None
    if not isinstance(fixed.get("alternatives"), list):
        fixed["alternatives"] = []
    if variable_schema is not None and isinstance(fixed.get("variables"), list):
        names = sorted(str(v.get("name")) for v in fixed["variables"] if isinstance(v, dict))
        if names == sorted(str(v.get("name")) for v in variable_schema):
            fixed["variables"] = [dict(v) for v in variable_schema]
    return fixed


@dataclass
class FormalizationV2(Formalization):
    attempts: int = 1
    repaired_fields: List[str] = field(default_factory=list)
    final_text: str = ""


def formalize_v2(
    prose: str,
    client: "ChatClient",
    hypothesis_id: str = "H",
    variable_schema: Optional[List[Dict[str, Any]]] = None,
    max_self_repairs: int = 1,
    json_mode: bool = True,
    temperature: float = 0.0,
    seed: int = 0,
) -> FormalizationV2:
    """The v2 path: rules and examples, JSON mode, surface repair, one self-repair round fed with the exact error."""
    messages = build_messages_v2(prose, variable_schema)
    result: Optional[FormalizationV2] = None
    for attempt in range(1, max_self_repairs + 2):
        output = client.complete(messages, temperature=temperature, seed=seed, json_mode=json_mode)
        data = extract_json(output)
        repaired: List[str] = []
        text = output
        if data is not None:
            fixed = repair_data(data, variable_schema)
            repaired = [k for k in ("variables", "scope", "assumptions", "claims") if fixed.get(k) != data.get(k)]
            text = json.dumps(fixed, ensure_ascii=False)
        base = parse_formalization(text, hypothesis_id, variable_schema)
        result = FormalizationV2(base.status, base.hypothesis, base.error, output, base.data, attempt, repaired, text)
        if result.status == FormalizationStatus.PARSED or attempt > max_self_repairs:
            break
        messages = messages + [
            {"role": "assistant", "content": output},
            {
                "role": "user",
                "content": f"The validator rejected that output: {result.error} Return only the corrected JSON "
                "object. Do not change what the hypothesis asserts.",
            },
        ]
    return result
