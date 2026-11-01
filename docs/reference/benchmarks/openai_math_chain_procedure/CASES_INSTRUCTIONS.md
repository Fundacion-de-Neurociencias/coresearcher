# Case-scoping instructions for cited hypotheses (given verbatim to the tagger)

You will receive registry entries for published mathematical results. Each entry has:

- `statement`;
- `cases`: named choices a user of the result picks from (for example part (1) and part (2), or two options for a
  sign);
- `hypotheses`: the list of the result's hypotheses, in order.

For each entry, say to which cases each hypothesis applies.

- **A scoped hypothesis.** If a hypothesis is needed only for some cases, give `{"<case name>": ["<case>", ...]}`.
  Use the case names and the case strings exactly as listed in `cases`.
- **A general hypothesis.** If it is needed whatever case is used, give `{}`.
- **Reading the scope.** Decide only from the statement and the hypothesis texts. Wording such as "for part (1)",
  "for the option …" or "in case …" marks a scoped hypothesis.

Do not open any file, web page or repository other than your packet file and these instructions.

Return a JSON list, one object per entry, with exactly one scope per hypothesis, in the same order:

```json
{"id": "<entry id>", "hypothesis_cases": [{}, {"part": ["..."]}], "notes": "<anything uncertain>"}
```
