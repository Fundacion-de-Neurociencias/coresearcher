# Citing-context variable instructions, with unbounded integers (given verbatim to each encoder)

You will receive packets. Each packet is one place where a mathematical paper uses a cited result. It holds:

- `cited_key`, `cited_locator`, `result_used`;
- `passage`: the numbered lines of the citing file around the citation (`citation_line`);
- `registry_entry`: the cited work's statement, hypotheses (some with a `formal` predicate over named variables) and
  conventions.

For each packet, encode the **quantities and conditions** the passage states at the place where it uses the result.
Encode only what the passage states, explicitly or by a definition visible in the passage. Do not infer from outside
the passage, do not use what you know about the subject, and do not judge whether the use is correct.

1. **`variables`.** For each variable named in a `formal` predicate of the entry, if the passage (or the statement it
   is proving, when visible) fixes, bounds or constrains that quantity, declare it with the same name:
   - **An integer quantity the passage fixes to finitely many values:**
     `{"name": ..., "domain": [the values, at most 40]}`.
   - **Any other integer quantity:** `{"name": ..., "integer": true, "lower": <int>, "upper": <int>}`. Give `lower`
     and `upper` only if the passage states them, and omit them otherwise. An integer may be unbounded. **Never
     replace an unbounded range by a representative finite range.**
   - **A real quantity:** `{"name": ..., "continuous": true, "lower": ..., "upper": ...}`, with bounds only as the
     passage states them.

   If the passage says nothing about a quantity, do not declare it. If no entry hypothesis has a `formal` predicate,
   give `[]`.
2. **`assumptions`.** The conditions the passage states on those variables, in Python-like syntax: comparisons,
   `and`, `or`, `not`, `+ - *`, and `%` or `//` by a positive integer constant. Examples: `n % 2 == 0` for "n = 2k",
   `n >= 3`, `hJ == bplus - 1`. Only conditions the passage states. `[]` if none.
3. **`notes`.** One or two sentences on anything uncertain.

Do not open any file, web page or repository other than your packet file and these instructions.

Return a JSON list, one object per packet:

```json
{"id": "<packet id>", "variables": [], "assumptions": [], "notes": "..."}
```
