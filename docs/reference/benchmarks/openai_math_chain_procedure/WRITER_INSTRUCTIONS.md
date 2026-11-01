# Registry writer instructions (given verbatim to each writer)

You are writing entries for a registry of published mathematical results. Each entry records what a cited result
says, so that a checker can later compare it with the places where the result is used. You will receive a list of
packets. Each packet names one result: a locator (for example "Lemma 3.2") and the bibliography entries through which
some papers cite its source.

For each packet, in the order given:

1. Obtain the cited work in the version the bibliography names. Prefer the arXiv version (the LaTeX source from
   `https://arxiv.org/e-print/<id>` or the abstract page and PDF), then the publisher's page. Put any download in a new
   empty directory of its own, never run anything from it, and read it only as text.
   - If the source is a manuscript of the `openai/math` collection, read only that manuscript's `.tex` files at
     commit `adc7f1241b42e322a6451854ab7e4b4c146bf78a`, using
     `git -C <clone> show adc7f1241b42e322a6451854ab7e4b4c146bf78a:preprints/<directory>/<file>`.
     Do not read its README, version notes, `history.md`, any other manuscript or any later commit.
2. Find the result named by the locator, with the numbering the bibliography entry states (for example "numbering as
   in arXiv:1303.0588v2").
3. Write the entry from the cited work alone:
   - `statement`: the result's statement, faithfully, in LaTeX-like text (at most about 1200 characters; abridge
     notation, never the content).
   - `hypotheses`: every hypothesis the result needs, including those fixed in the surrounding section ("throughout
     this section, X is ..."). For each: `text` (the hypothesis), `phrases` (two to five short literal phrases, lower
     case, that a paper using the result would likely write when it states this hypothesis), and `formal` only when
     the hypothesis is an arithmetic condition on named integer or real quantities. `formal` uses Python-like syntax
     over variable names you choose and list in `variables` (for example `hJ == bplus - 1`, `n >= 3`,
     `k % 2 == 0`). Otherwise leave `formal` empty.
   - `variables`: for each name used in a `formal` predicate, a one-line meaning.
   - `conventions`: every convention the statement depends on and that a user of it must share for the statement to
     transfer unchanged, as tags with the source's value. Use the tags `sign` (signs and orientations),
     `normalization`, `grading`, `indexing` or another short tag if none fits. Write the value as the source fixes it,
     in one sentence. If the result depends on no such convention, give `{}`.
4. If you cannot obtain the work or cannot find the result, record `"status": "UNAVAILABLE"` with the reason.

Do not search for, open or read anything about the papers that cite these results, about the `openai/math` collection
(other than the case in step 1), or about corrections or withdrawals of any paper. Do not open files of the
CoResearcher repository. You are recording what the cited work says, nothing else.

Return a JSON list, one object per packet, in this form:

```json
{
  "result": "<the packet's result field, unchanged>",
  "ref": "<the packet's ref field, unchanged>",
  "status": "WRITTEN",
  "entry_id": "<short id: first-author initials + year + locator, e.g. EEMS13-L3.2>",
  "source": "<authors, title, venue, and the exact version you read>",
  "entry": {
    "statement": "...",
    "hypotheses": [{"text": "...", "phrases": ["..."], "formal": ""}],
    "variables": {"name": "meaning"},
    "conventions": {"sign": "..."}
  },
  "notes": "<anything a reader should know, e.g. numbering differences>"
}
```
