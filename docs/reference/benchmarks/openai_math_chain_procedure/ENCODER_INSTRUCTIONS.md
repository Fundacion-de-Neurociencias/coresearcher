# Citing-context encoder instructions (given verbatim to each encoder)

You will receive packets. Each packet is one place where a mathematical paper uses a cited result. It holds:

- `cited_key`, `cited_locator`, `result_used`: how the passage cites the result;
- `passage`: the lines of the citing file around the citation, numbered, with `citation_line` the line of the cite;
- `registry_entry`: what the cited work says: its statement, its hypotheses (some with a `formal` predicate over
  named variables) and its conventions (tags with the cited work's value).

For each packet, encode the **citing context**: what the passage itself states at the place where it uses the
result. Encode only what the passage states, explicitly or by a definition visible in the passage. Do not infer from
outside the passage, do not use what you know about the subject, and do not judge whether the use is correct.

1. `variables`: for each variable named in a `formal` predicate of the entry, if the passage (or the statement it is
   proving, when visible) fixes or bounds that quantity, declare it with the same name: an integer quantity as
   `{"name": ..., "domain": [list of the values the passage allows, at most 40]}`, a real one as
   `{"name": ..., "continuous": true, "lower": ..., "upper": ...}`. When the passage allows every value in an
   unbounded range, use a finite representative range (for integers, 0 to 12) and say so in `notes`. If the passage
   says nothing about a quantity, do not declare it. If no entry hypothesis has a `formal` predicate, give `[]`.
2. `assumptions`: the conditions the passage states on those variables, in the same Python-like syntax
   (`hJ == bplus - 1`, `n >= 3`). Only conditions the passage states. `[]` if none.
3. `conventions`: for each convention tag of the entry, the passage's convention for that same matter:
   - the entry's value, copied verbatim, if the passage explicitly adopts the same convention;
   - the passage's own convention, in its own words, if the passage explicitly states a different one;
   - leave the tag out if the passage does not state a convention for it.
4. `citing_text`: the sentence of the passage that contains the citation, verbatim (at most 600 characters).
5. `notes`: one or two sentences on anything uncertain.

Do not open any file, web page or repository. The packet is everything you may use.

Return a JSON list, one object per packet:

```json
{"id": "<packet id>", "variables": [], "assumptions": [], "conventions": {}, "citing_text": "...", "notes": "..."}
```
