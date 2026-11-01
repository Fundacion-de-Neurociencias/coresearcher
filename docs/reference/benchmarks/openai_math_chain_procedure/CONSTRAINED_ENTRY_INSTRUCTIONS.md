# Typing instructions for registry conventions, with constraints and cases (given verbatim to each typist)

You will receive registry entries. Each entry records a published mathematical result: its source and locator, its
statement, its hypotheses, and its conventions as text tags (for example `sign`, `normalization`, `indexing`), plus
notes from the person who wrote it from the source.

Your task is to make each convention **typed**, so that a checker can compare it with another paper's convention by
meaning rather than by wording. For each entry, return its conventions as an object `{tag: typed value}`, where a
typed value is:

```json
{
  "text": "<the existing text of the convention, unchanged>",
  "fields": {"<name>": "<short atom: a word, number or boolean>"},
  "signs": {"<quantity>": "<integer formula over the params, e.g. (-1)**(k-1)>"},
  "params": {"<name>": [low, high]},
  "where": ["<condition on the params, e.g. n % 2 == 0>"],
  "cases": {"<name>": ["<each case the statement covers>"]}
}
```

- **`fields`.** One per named choice the statement depends on, with the source's value, written as a short
  lower-case atom. Examples:
  - orientation of a branch or of a boundary;
  - the direction in which a homotopy or trace runs;
  - inward or outward normal;
  - which factor carries a sign;
  - the lattice or distance normalization.

  Use atoms another paper could state about the same choice (`"matching"` or `"opposite"`, `"outward"` or `"inward"`,
  `"forward"` or `"reverse"`), not sentences.
- **`signs`.** One per sign or normalization the statement fixes as a function of integer parameters, as an
  arithmetic formula. Allowed: integers, the parameter names, `+ - * // % **` and parentheses. A sign that the
  source leaves undetermined is not a sign entry; record it as a field (e.g. `"global_sign": "undetermined"`).
- **`params`.** For each parameter used in `signs`, the integer range the statement covers. Use at most 0 to 40.
- **`where`.** Every condition the statement puts on those parameters besides the range, as a condition in the same
  syntax plus comparisons and `and`, `or`, `not`. Examples: `n % 2 == 0` when the sign is stated for even n only,
  `k >= 2`. A sign that holds only under a condition must carry that condition.
- **`cases`.** When the statement covers several cases of one choice that a user picks from (for example a
  homotopy and its reverse, the forward and the backward trace, part (1) and part (2)), list the cases covered under
  a name. **Which case a user picks is not a convention.** Do not record a case as a field.
- **`notes`.** Name every field and sign quantity with a one-line meaning, so that someone typing a citing paper can
  use the same names.

Rules:

- **Keep `text` exactly as given.**
- **Add a tag** only if the cited statement depends on a convention the text tags missed.
- **Do not change** the statement or the hypotheses.
- **A tag with nothing to type** keeps only its `text`.
- **Sources.** You may re-read the cited work through the arXiv or author link in `source`, to check a sign. Put
  downloads in a new empty directory and never execute anything from them. Do not read anything about papers that
  cite these results, about the `openai/math` collection, or about corrections or withdrawals. Do not open files of
  the CoResearcher repository.

Return a JSON list with one object per entry:

```json
{"id": "<entry id>", "conventions": {"<tag>": {"text": "...", "fields": {}, "signs": {}, "params": {}}},
 "notes": "<meaning of every field and sign name>"}
```
