# Typing instructions for citing conventions (given verbatim to each typist)

You will receive packets. Each packet is one place where a mathematical paper uses a cited result:

- `cited_key`, `cited_locator`, `result_used`;
- `passage`: the numbered lines of the citing file around the citation (`citation_line`);
- `registry_entry`: the cited work's statement, hypotheses and **typed conventions**. Each convention tag has:
  - `text`;
  - `fields`: named choices with the cited work's value;
  - `signs`: sign quantities as integer formulas, with `params` and their ranges.

For each packet, give the **citing passage's own conventions**, typed with the same names. For each tag of the
entry:

- **A field.** If the passage itself states or fixes the same choice, give the passage's value as a short atom of the
  same kind (for example `"matching"` or `"opposite"`, `"forward"` or `"reverse"`). Leave the field out if the passage
  does not fix it.
- **A sign quantity.** If the passage states or uses a value for the same quantity, give it as an integer formula in
  the same parameter names, with `params` for their ranges as the passage allows them (at most 0 to 40). Leave it out
  if the passage does not fix it.
- **`text`.** One sentence quoting or paraphrasing what the passage says about this convention. Leave it empty if
  the passage says nothing.
- **A tag the passage says nothing about** is left out entirely.

Encode only what the passage states, explicitly or by a definition visible in the passage. Do not infer from outside
the passage, do not use what you know about the subject, and do not judge whether the use is correct. Do not open any
file, web page or repository other than your packet file and these instructions.

Return a JSON list, one object per packet:

```json
{"id": "<packet id>", "conventions": {"<tag>": {"text": "...", "fields": {}, "signs": {}, "params": {}}},
 "notes": "<anything uncertain>"}
```
