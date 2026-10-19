# CoResearcher as OASE's formal hypothesis verifier (`oase formal`)

An adapter that lets Google's Open Agentic Science Engine (OASE, `GoogleCloudPlatform/LifeSciences`, Apache 2.0) use
CoResearcher to decide whether a hypothesis is formally sound — not vacuous, not self-contradictory, falsifiable — how
it relates to a rival and on which states they disagree, and whether a prediction follows. Design and decisions:
[ADR-DISCOVERY-069](../../docs/decisions/ADR-DISCOVERY-069-OASE-FORMAL-ADAPTER.md). Scope: formal soundness only; no
evidence, citation or data checks.

| Path | What it is |
| --- | --- |
| [`formal.py`](formal.py) | The OASE command module: `oase formal run`, `analyze`, `doctor` |
| [`apply.sh`](apply.sh), [`apply.py`](apply.py) | Installs it into an OASE checkout (`--dry-run` prints the diff) |
| [`skills/formal-hypothesis-verification/SKILL.md`](skills/formal-hypothesis-verification/SKILL.md) | The OASE skill, granted to hypex-reflection, scientific-reviewer and science-program-lead |
| [`gate/GP-001.formal-soundness.json`](gate/GP-001.formal-soundness.json) | Example Stage 1 gate policy with a `formal-soundness` cutoff |
| [`demo/`](demo/REPORT.md) | Illustrative end-to-end run, committed artifacts and report |
| [`tests/`](tests/test_oase_formal.py), [`ci/`](ci/conformance.sh) | Tests inside OASE and the CI job that runs OASE's conformance checks |

## Install

OASE is POSIX-only (it imports `fcntl`). In its tools environment:

```bash
git clone --filter=blob:none --sparse https://github.com/GoogleCloudPlatform/LifeSciences.git
git -C LifeSciences sparse-checkout set applications/open-agentic-science-engine
git -C LifeSciences checkout b7e5e3576668ba9630f053e93389b21bbc2e67f6
```

```bash
integrations/oase/apply.sh --dry-run LifeSciences/applications/open-agentic-science-engine
```

```bash
integrations/oase/apply.sh LifeSciences/applications/open-agentic-science-engine
```

```bash
export CORESEARCHER_HOME="$PWD"
```

`CORESEARCHER_HOME` points the adapter at this checkout; installing CoResearcher into the tools environment works too
(`pip install -r requirements.txt` here provides z3 and the engine's dependencies). Then `oase formal doctor`.

## Use

```bash
oase formal run H-0001.json --formal H-0001.formal.json --rival H-0002.formal.json
```

```bash
oase formal analyze raw/formal/fm-H-0001_vs_H-0002.meta.json
```

`run` records request, response and sidecar under `raw/formal/`; `analyze` re-runs the verdict offline, checks it
against the run and writes `fm-H-0001_vs_H-0002.analysis.json` under threshold set `formal@1.0`. Without `--formal`
the statement is formalized by the configured model (`FORMALIZER_MODEL`, `FORMALIZER_BASE_URL`) through the
self-consistency gate. `--transport http` sends formal objects to a running CoResearcher API (`CORESEARCHER_URL`,
`CORESEARCHER_API_KEY`) instead of importing the engine.

Exit codes: 0 decided (a decided defect too), 9 refusal (invalid input, ambiguous formalization), 4/7/8 blocked
(threshold, endpoint, dependency), 3 artifact checksum, 10 UNDECIDED, 12 analysis does not reproduce the run.
UNDECIDED, BLOCKED and ambiguity map to `not_assessed` in an assessment record, never to a negative.
