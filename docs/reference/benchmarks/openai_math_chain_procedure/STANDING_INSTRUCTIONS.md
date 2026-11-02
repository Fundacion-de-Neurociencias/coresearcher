# Standing-assumption extraction instructions (given verbatim to each extractor)

You will receive packets. Each packet comes from one mathematical manuscript and holds:

- `standing_text`: the paragraphs of the manuscript that state conventions, notation or assumptions holding
  throughout (or throughout a section);
- `variables_of_interest`: quantity names, each with a one-line meaning, about which a checker needs to know what the
  manuscript assumes.

For each packet, write the **standing context**: what the standing text fixes, once for the whole manuscript, about
the variables of interest.

1. **`variables`.** Declare each variable of interest that the standing text constrains, and any auxiliary variable
   you need to state the constraint (for example k in "n = 2k"). Use these forms:
   - an integer: `{"name": ..., "integer": true, "lower": <int>, "upper": <int>}`, giving bounds only if the text
     states them; an integer may be unbounded;
   - a finite set: `{"name": ..., "domain": [values]}`;
   - a real: `{"name": ..., "continuous": true, "lower": ..., "upper": ...}`.

   A name in the standing text may differ from the variable of interest. Map it only when the text makes the
   identification clear, and say so in `notes`.
2. **`assumptions`.** The conditions the standing text states on those variables. Use comparisons, `and`, `or`,
   `not`, `+ - *`, and `%` or `//` by a positive integer constant (`n == 2*k`, `k >= 2`, `lam > 0`).
3. **What to leave out.**
   - A variable of interest the standing text does not constrain is left out.
   - An assumption that holds only in one section, when it is not clear that this section is the one where the
     citations are, is left out and mentioned in `notes`.
4. **`notes`.** One to three sentences on anything uncertain.

Encode only what the standing text states. Do not infer from outside it and do not use what you know about the
subject. Do not open any file, web page or repository other than your packet file and these instructions. Write helper
scripts only in the tools folder named in your task, and never run a script you did not write.

Return a JSON list, one object per packet:

```json
{"id": "<packet id>", "variables": [], "assumptions": [], "notes": "..."}
```
