# Trajectory Report — LangGraph

> Generated from public GitHub data only.
> No instrumentation required. No private data used.

---

## 1. Project Overview

**Repository**: [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
**Created**: 2023-08-09T18:33:12Z
**Language**: Python
**Stars**: 38157
**Default branch**: main

**Description**: Build resilient agents.

**Objective (declared)**: LangGraph is a library for building stateful, multi-agent applications with LLMs.

---

## 2. Timeline

Lista cronológica de eventos relevantes extraídos del registro público.

| Fecha | Tipo | Evento |
|-------|------|--------|
| 2025-09-30 | release | [Release checkpointpostgres==2.0.24](https://github.com/langchain-ai/langgraph/releases/tag/checkpointpostgres%3D%3D2.0.24) |
| 2025-10-07 | release | [Release checkpoint==2.1.2](https://github.com/langchain-ai/langgraph/releases/tag/checkpoint%3D%3D2.1.2) |
| 2025-10-07 | release | [Release checkpointpostgres==2.0.25](https://github.com/langchain-ai/langgraph/releases/tag/checkpointpostgres%3D%3D2.0.25) |
| 2025-10-07 | release | [Release 0.6.9](https://github.com/langchain-ai/langgraph/releases/tag/0.6.9) |
| 2025-10-08 | release | [Release cli==0.4.3](https://github.com/langchain-ai/langgraph/releases/tag/cli%3D%3D0.4.3) |
| 2025-10-09 | release | [Release 0.6.10](https://github.com/langchain-ai/langgraph/releases/tag/0.6.10) |
| 2025-10-17 | release | [Release cli==0.4.4](https://github.com/langchain-ai/langgraph/releases/tag/cli%3D%3D0.4.4) |
| 2025-10-17 | release | [Release prebuilt==0.7.0rc1](https://github.com/langchain-ai/langgraph/releases/tag/prebuilt%3D%3D0.7.0rc1) |
| 2025-10-17 | release | [Release 1.0.0rc1](https://github.com/langchain-ai/langgraph/releases/tag/1.0.0rc1) |
| 2025-10-17 | release | [Release prebuilt==1.0.0](https://github.com/langchain-ai/langgraph/releases/tag/prebuilt%3D%3D1.0.0) |
| 2025-10-17 | release | [Release 1.0.0](https://github.com/langchain-ai/langgraph/releases/tag/1.0.0) |
| 2025-10-20 | release | [Release checkpoint==3.0.0](https://github.com/langchain-ai/langgraph/releases/tag/checkpoint%3D%3D3.0.0) |
| 2025-10-20 | release | [Release checkpointsqlite==3.0.0](https://github.com/langchain-ai/langgraph/releases/tag/checkpointsqlite%3D%3D3.0.0) |
| 2025-10-20 | release | [Release checkpointpostgres==3.0.0](https://github.com/langchain-ai/langgraph/releases/tag/checkpointpostgres%3D%3D3.0.0) |
| 2025-10-20 | release | [Release prebuilt==1.0.1](https://github.com/langchain-ai/langgraph/releases/tag/prebuilt%3D%3D1.0.1) |
| 2025-10-20 | release | [Release 1.0.1](https://github.com/langchain-ai/langgraph/releases/tag/1.0.1) |
| 2025-10-21 | release | [Release 0.6.11](https://github.com/langchain-ai/langgraph/releases/tag/0.6.11) |
| 2025-10-21 | release | [Release prebuilt==0.6.5](https://github.com/langchain-ai/langgraph/releases/tag/prebuilt%3D%3D0.6.5) |
| 2025-10-29 | release | [Release prebuilt==1.0.2](https://github.com/langchain-ai/langgraph/releases/tag/prebuilt%3D%3D1.0.2) |
| 2025-10-29 | release | [Release 1.0.2](https://github.com/langchain-ai/langgraph/releases/tag/1.0.2) |
| 2025-11-01 | release | [Release cli==0.4.5](https://github.com/langchain-ai/langgraph/releases/tag/cli%3D%3D0.4.5) |
| 2025-11-03 | release | [Release cli==0.4.6](https://github.com/langchain-ai/langgraph/releases/tag/cli%3D%3D0.4.6) |
| 2025-11-03 | release | [Release cli==0.4.7](https://github.com/langchain-ai/langgraph/releases/tag/cli%3D%3D0.4.7) |
| 2025-11-04 | release | [Release checkpoint==3.0.1](https://github.com/langchain-ai/langgraph/releases/tag/checkpoint%3D%3D3.0.1) |
| 2025-11-06 | release | [Release checkpointpostgres==3.0.1](https://github.com/langchain-ai/langgraph/releases/tag/checkpointpostgres%3D%3D3.0.1) |
| 2025-11-10 | release | [Release 1.0.3](https://github.com/langchain-ai/langgraph/releases/tag/1.0.3) |
| 2025-11-13 | release | [Release prebuilt==1.0.3](https://github.com/langchain-ai/langgraph/releases/tag/prebuilt%3D%3D1.0.3) |
| 2025-11-13 | release | [Release prebuilt==1.0.4](https://github.com/langchain-ai/langgraph/releases/tag/prebuilt%3D%3D1.0.4) |
| 2025-11-20 | release | [Release prebuilt==1.0.5](https://github.com/langchain-ai/langgraph/releases/tag/prebuilt%3D%3D1.0.5) |
| 2025-11-24 | release | [Release sdk==0.2.10](https://github.com/langchain-ai/langgraph/releases/tag/sdk%3D%3D0.2.10) |

---

## 3. Key Decisions

Decisiones identificables desde evidencia pública. Cada decisión incluye evidencia, fecha y artefactos relacionados.

### Decisión 1: fix(runtime): preserve explicitly falsy context and store in merge

- **Fuente**: issue #8450
- **Fecha**: 2026-07-26
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8450](https://github.com/langchain-ai/langgraph/pull/8450)
- **Keyword**: `instead of`
- **Texto**: ## Problem

`Runtime.merge()` uses `or` to check if the incoming runtime's values should be used. This breaks when context or store are **valid falsy values** — e.g. an empty dict `{}`, empty string `

### Decisión 2: PostgresSaver: get_delta_channel_history permanently poisons walk cursor when ta

- **Fuente**: issue #8447
- **Fecha**: 2026-07-25
- **URL**: [https://github.com/langchain-ai/langgraph/issues/8447](https://github.com/langchain-ai/langgraph/issues/8447)
- **Keyword**: `instead of`
- **Texto**: ### Description

`BasePostgresSaver._try_advance_walks` (and its async twin in `aio.py`) permanently poisons a channel's walk cursor to `None` when the target checkpoint hasn't been loaded yet by the 

### Decisión 3: chore(deps): bump js-yaml from 4.2.0 to 4.3.0 in /libs/cli/js-monorepo-example

- **Fuente**: issue #8438
- **Fecha**: 2026-07-25
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8438](https://github.com/langchain-ai/langgraph/pull/8438)
- **Keyword**: `replaced`
- **Texto**: Bumps [js-yaml](https://github.com/nodeca/js-yaml) from 4.2.0 to 4.3.0.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a href="https://github.com/nodeca/js-yaml/blob/master/CHANGELOG.md">

### Decisión 4: fix(sdk-py): unblock subscribers on stream close

- **Fuente**: issue #8436
- **Fecha**: 2026-07-25
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8436](https://github.com/langchain-ai/langgraph/pull/8436)
- **Keyword**: `selected`
- **Texto**: Fixes #8429

## Summary

- mark active subscriptions terminal before fanout cancellation
- apply one termination path to explicit close, run pause, and natural EOF
- preserve buffered events when a bo

### Decisión 5: chore(deps): bump setuptools from 80.9.0 to 83.0.0 in /libs/langgraph

- **Fuente**: issue #8435
- **Fecha**: 2026-07-25
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8435](https://github.com/langchain-ai/langgraph/pull/8435)
- **Keyword**: `replaced`
- **Texto**: Bumps [setuptools](https://github.com/pypa/setuptools) from 80.9.0 to 83.0.0.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a href="https://github.com/pypa/setuptools/blob/main/NEWS.rst"

### Decisión 6: chore(deps): bump setuptools from 82.0.1 to 83.0.0 in /libs/cli

- **Fuente**: issue #8434
- **Fecha**: 2026-07-25
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8434](https://github.com/langchain-ai/langgraph/pull/8434)
- **Keyword**: `instead of`
- **Texto**: Bumps [setuptools](https://github.com/pypa/setuptools) from 82.0.1 to 83.0.0.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a href="https://github.com/pypa/setuptools/blob/main/NEWS.rst"

### Decisión 7: fix(sdk-py): unblock subscribers on stream close

- **Fuente**: issue #8430
- **Fecha**: 2026-07-24
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8430](https://github.com/langchain-ai/langgraph/pull/8430)
- **Keyword**: `selected`
- **Texto**: Fixes #8429

## Summary

- mark active subscriptions terminal before fanout cancellation
- apply one termination path to explicit close, run pause, and natural EOF
- preserve buffered events when a bo

### Decisión 8: fix(checkpoint-postgres): allow disabling pipeline in AsyncPostgresSaver

- **Fuente**: issue #8421
- **Fecha**: 2026-07-23
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8421](https://github.com/langchain-ai/langgraph/pull/8421)
- **Keyword**: `instead of`
- **Texto**: ## Summary

`AsyncPostgresSaver` unconditionally enables PostgreSQL pipeline protocol (`conn.pipeline()`) when the server advertises support for it. When the connection path goes through **PgBouncer

### Decisión 9: fix(checkpoint-postgres): allow disabling pipeline in AsyncPostgresSaver

- **Fuente**: issue #8419
- **Fecha**: 2026-07-23
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8419](https://github.com/langchain-ai/langgraph/pull/8419)
- **Keyword**: `instead of`
- **Texto**: ## Summary

`AsyncPostgresSaver` unconditionally enables PostgreSQL pipeline protocol (`conn.pipeline()`) when the server advertises support for it. When the connection path goes through **PgBouncer

### Decisión 10: fix(checkpoint): add langgraph/store/__init__.py to fix reference docs showing c

- **Fuente**: issue #8407
- **Fecha**: 2026-07-22
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8407](https://github.com/langchain-ai/langgraph/pull/8407)
- **Keyword**: `instead of`
- **Texto**: Fixes #8405

`langgraph/store/` was missing a top-level `__init__.py`, so the reference docs site fell back to the `langgraph-checkpoint` wheel description (which describes checkpointers) instead of s

### Decisión 11: fix(checkpoint): add langgraph/store/__init__.py to fix reference docs showing c

- **Fuente**: issue #8404
- **Fecha**: 2026-07-21
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8404](https://github.com/langchain-ai/langgraph/pull/8404)
- **Keyword**: `instead of`
- **Texto**: Fixes #8405

`langgraph/store/` was missing a top-level `__init__.py`, so the reference docs site fell back to the `langgraph-checkpoint` wheel description (which describes checkpointers) instead of s

### Decisión 12: fix: compare task ID instead of task object in PUSH child dedup

- **Fuente**: issue #8398
- **Fecha**: 2026-07-21
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8398](https://github.com/langchain-ai/langgraph/pull/8398)
- **Keyword**: `instead of`
- **Texto**: ## Problem

When a parent task is retried while a PUSH child task is still in-flight, the deduplication logic in `_call` (sync) and `_acall` (async) should detect the existing child and reuse its futu

### Decisión 13: fix: ToolNode interrupt propagation and related audit fixes

- **Fuente**: issue #8395
- **Fecha**: 2026-07-21
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8395](https://github.com/langchain-ai/langgraph/pull/8395)
- **Keyword**: `instead of`
- **Texto**: Fixes #8394

Fixes ToolNode interrupt swallowing through wrap_tool_call, plus related audit defects (retry budgets, CLI telemetry hang, config aliasing, Postgres pending-sends migration, checkpoint/se

### Decisión 14: feat(langgraph): type v3 stream_events return and native projections

- **Fuente**: issue #8389
- **Fecha**: 2026-07-24
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8389](https://github.com/langchain-ai/langgraph/pull/8389)
- **Keyword**: `rather than`
- **Texto**: The `version="v3"` overloads of `stream_events`/`astream_events` returned `Any`, and `GraphRunStream`/`AsyncGraphRunStream` attached native projections via a runtime `setattr` loop invisible to type c

### Decisión 15: fix(checkpoint): preserve Counter and OrderedDict type through msgpack round-tri

- **Fuente**: issue #8380
- **Fecha**: 2026-07-19
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8380](https://github.com/langchain-ai/langgraph/pull/8380)
- **Keyword**: `selected`
- **Texto**: Fixes #8184

`JsonPlusSerializer` was silently downcasting dict subclasses (`Counter`, `OrderedDict`) to plain `dict` on checkpoint round-trip. A `Counter` held in graph state would lose `.most_common

---

## 4. Alternatives

Alternativas explícitamente observables en el registro público. NO se inferencia.

### Alternativa 1

- **Fuente**: issue #8450
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8450](https://github.com/langchain-ai/langgraph/pull/8450)
- **Keyword**: `instead of`
- **Texto**: ## Problem

`Runtime.merge()` uses `or` to check if the incoming runtime's values should be used. This breaks when context or store are **valid falsy values** — e.g. an empty dict `{}`, empty string `

### Alternativa 2

- **Fuente**: issue #8447
- **URL**: [https://github.com/langchain-ai/langgraph/issues/8447](https://github.com/langchain-ai/langgraph/issues/8447)
- **Keyword**: `instead of`
- **Texto**: ### Description

`BasePostgresSaver._try_advance_walks` (and its async twin in `aio.py`) permanently poisons a channel's walk cursor to `None` when the target checkpoint hasn't been loaded yet by the 

### Alternativa 3

- **Fuente**: issue #8438
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8438](https://github.com/langchain-ai/langgraph/pull/8438)
- **Keyword**: `instead of`
- **Texto**: Bumps [js-yaml](https://github.com/nodeca/js-yaml) from 4.2.0 to 4.3.0.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a href="https://github.com/nodeca/js-yaml/blob/master/CHANGELOG.md">

### Alternativa 4

- **Fuente**: issue #8435
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8435](https://github.com/langchain-ai/langgraph/pull/8435)
- **Keyword**: `instead of`
- **Texto**: Bumps [setuptools](https://github.com/pypa/setuptools) from 80.9.0 to 83.0.0.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a href="https://github.com/pypa/setuptools/blob/main/NEWS.rst"

### Alternativa 5

- **Fuente**: issue #8434
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8434](https://github.com/langchain-ai/langgraph/pull/8434)
- **Keyword**: `instead of`
- **Texto**: Bumps [setuptools](https://github.com/pypa/setuptools) from 82.0.1 to 83.0.0.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a href="https://github.com/pypa/setuptools/blob/main/NEWS.rst"

### Alternativa 6

- **Fuente**: issue #8421
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8421](https://github.com/langchain-ai/langgraph/pull/8421)
- **Keyword**: `instead of`
- **Texto**: ## Summary

`AsyncPostgresSaver` unconditionally enables PostgreSQL pipeline protocol (`conn.pipeline()`) when the server advertises support for it. When the connection path goes through **PgBouncer

### Alternativa 7

- **Fuente**: issue #8419
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8419](https://github.com/langchain-ai/langgraph/pull/8419)
- **Keyword**: `instead of`
- **Texto**: ## Summary

`AsyncPostgresSaver` unconditionally enables PostgreSQL pipeline protocol (`conn.pipeline()`) when the server advertises support for it. When the connection path goes through **PgBouncer

### Alternativa 8

- **Fuente**: issue #8407
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8407](https://github.com/langchain-ai/langgraph/pull/8407)
- **Keyword**: `instead of`
- **Texto**: Fixes #8405

`langgraph/store/` was missing a top-level `__init__.py`, so the reference docs site fell back to the `langgraph-checkpoint` wheel description (which describes checkpointers) instead of s

### Alternativa 9

- **Fuente**: issue #8404
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8404](https://github.com/langchain-ai/langgraph/pull/8404)
- **Keyword**: `instead of`
- **Texto**: Fixes #8405

`langgraph/store/` was missing a top-level `__init__.py`, so the reference docs site fell back to the `langgraph-checkpoint` wheel description (which describes checkpointers) instead of s

### Alternativa 10

- **Fuente**: issue #8398
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8398](https://github.com/langchain-ai/langgraph/pull/8398)
- **Keyword**: `instead of`
- **Texto**: ## Problem

When a parent task is retried while a PUSH child task is still in-flight, the deduplication logic in `_call` (sync) and `_acall` (async) should detect the existing child and reuse its futu

---

## 5. Selection Criteria

Criterios explícitos encontrados en el registro público, siempre acompañados de evidencia.

### Criterio 1

- **Fuente**: issue #8450
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8450](https://github.com/langchain-ai/langgraph/pull/8450)
- **Keyword**: `as`
- **Texto**: ## Problem

`Runtime.merge()` uses `or` to check if the incoming runtime's values should be used. This breaks when context or store are **valid falsy values** — e.g. an empty dict `{}`, empty string `

### Criterio 2

- **Fuente**: issue #8447
- **URL**: [https://github.com/langchain-ai/langgraph/issues/8447](https://github.com/langchain-ai/langgraph/issues/8447)
- **Keyword**: `because`
- **Texto**: ### Description

`BasePostgresSaver._try_advance_walks` (and its async twin in `aio.py`) permanently poisons a channel's walk cursor to `None` when the target checkpoint hasn't been loaded yet by the 

### Criterio 3

- **Fuente**: issue #8446
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8446](https://github.com/langchain-ai/langgraph/pull/8446)
- **Keyword**: `as`
- **Texto**: `JsonPlusSerializer` supports `decimal.Decimal` but raised on `fractions.Fraction`
and `complex`:

```python
s = JsonPlusSerializer()
s.dumps_typed(fractions.Fraction(3, 4))  # unsupported
s.dumps_typ

### Criterio 4

- **Fuente**: issue #8445
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8445](https://github.com/langchain-ai/langgraph/pull/8445)
- **Keyword**: `as`
- **Texto**: A node returning `Command[Literal["a"] | Literal["b"]]` produced no conditional
edges (so `draw_mermaid` omitted them), while the equivalent
`Command[Literal["a", "b"]]` worked:

```python
def router(

### Criterio 5

- **Fuente**: issue #8444
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8444](https://github.com/langchain-ai/langgraph/pull/8444)
- **Keyword**: `as`
- **Texto**: `JsonPlusSerializer` raised on `pathlib.PurePath` values and on `range`:

```python
s = JsonPlusSerializer()
s.dumps_typed(pathlib.PurePosixPath("/foo/bar"))  # unsupported
s.dumps_typed(range(0, 10, 

### Criterio 6

- **Fuente**: issue #8440
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8440](https://github.com/langchain-ai/langgraph/pull/8440)
- **Keyword**: `as`
- **Texto**: Bumps [jupyterlab](https://github.com/jupyterlab/jupyterlab) from 4.5.9 to 4.5.10.
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a href="https://github.com/jupyterlab/jupyterlab/rele

### Criterio 7

- **Fuente**: issue #8438
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8438](https://github.com/langchain-ai/langgraph/pull/8438)
- **Keyword**: `as`
- **Texto**: Bumps [js-yaml](https://github.com/nodeca/js-yaml) from 4.2.0 to 4.3.0.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a href="https://github.com/nodeca/js-yaml/blob/master/CHANGELOG.md">

### Criterio 8

- **Fuente**: issue #8436
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8436](https://github.com/langchain-ai/langgraph/pull/8436)
- **Keyword**: `as`
- **Texto**: Fixes #8429

## Summary

- mark active subscriptions terminal before fanout cancellation
- apply one termination path to explicit close, run pause, and natural EOF
- preserve buffered events when a bo

### Criterio 9

- **Fuente**: issue #8435
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8435](https://github.com/langchain-ai/langgraph/pull/8435)
- **Keyword**: `as`
- **Texto**: Bumps [setuptools](https://github.com/pypa/setuptools) from 80.9.0 to 83.0.0.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a href="https://github.com/pypa/setuptools/blob/main/NEWS.rst"

### Criterio 10

- **Fuente**: issue #8434
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8434](https://github.com/langchain-ai/langgraph/pull/8434)
- **Keyword**: `as`
- **Texto**: Bumps [setuptools](https://github.com/pypa/setuptools) from 82.0.1 to 83.0.0.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a href="https://github.com/pypa/setuptools/blob/main/NEWS.rst"

---

## 6. Evidence Chain

Para cada afirmación, se rastrea a: Issue, PR, Commit, Release o Documento.

### Evidencia 1

- **Fuente**: issue #8447
- **URL**: [https://github.com/langchain-ai/langgraph/issues/8447](https://github.com/langchain-ai/langgraph/issues/8447)
- **Keyword**: `test`
- **Texto**: ### Description

`BasePostgresSaver._try_advance_walks` (and its async twin in `aio.py`) permanently poisons a channel's walk cursor to `None` when the target checkpoint hasn't been loaded yet by the 

### Evidencia 2

- **Fuente**: issue #8446
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8446](https://github.com/langchain-ai/langgraph/pull/8446)
- **Keyword**: `test`
- **Texto**: `JsonPlusSerializer` supports `decimal.Decimal` but raised on `fractions.Fraction`
and `complex`:

```python
s = JsonPlusSerializer()
s.dumps_typed(fractions.Fraction(3, 4))  # unsupported
s.dumps_typ

### Evidencia 3

- **Fuente**: issue #8445
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8445](https://github.com/langchain-ai/langgraph/pull/8445)
- **Keyword**: `test`
- **Texto**: A node returning `Command[Literal["a"] | Literal["b"]]` produced no conditional
edges (so `draw_mermaid` omitted them), while the equivalent
`Command[Literal["a", "b"]]` worked:

```python
def router(

### Evidencia 4

- **Fuente**: issue #8444
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8444](https://github.com/langchain-ai/langgraph/pull/8444)
- **Keyword**: `test`
- **Texto**: `JsonPlusSerializer` raised on `pathlib.PurePath` values and on `range`:

```python
s = JsonPlusSerializer()
s.dumps_typed(pathlib.PurePosixPath("/foo/bar"))  # unsupported
s.dumps_typed(range(0, 10, 

### Evidencia 5

- **Fuente**: issue #8441
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8441](https://github.com/langchain-ai/langgraph/pull/8441)
- **Keyword**: `test`
- **Texto**: `_add_directory` pruned any directory matching the ignore spec, so `os.walk` never reached a file that a `!pattern` re-included underneath it — meaning `langgraph deploy` archives silently dropped fil

### Evidencia 6

- **Fuente**: issue #8440
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8440](https://github.com/langchain-ai/langgraph/pull/8440)
- **Keyword**: `test`
- **Texto**: Bumps [jupyterlab](https://github.com/jupyterlab/jupyterlab) from 4.5.9 to 4.5.10.
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a href="https://github.com/jupyterlab/jupyterlab/rele

### Evidencia 7

- **Fuente**: issue #8438
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8438](https://github.com/langchain-ai/langgraph/pull/8438)
- **Keyword**: `test`
- **Texto**: Bumps [js-yaml](https://github.com/nodeca/js-yaml) from 4.2.0 to 4.3.0.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a href="https://github.com/nodeca/js-yaml/blob/master/CHANGELOG.md">

### Evidencia 8

- **Fuente**: issue #8436
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8436](https://github.com/langchain-ai/langgraph/pull/8436)
- **Keyword**: `test`
- **Texto**: Fixes #8429

## Summary

- mark active subscriptions terminal before fanout cancellation
- apply one termination path to explicit close, run pause, and natural EOF
- preserve buffered events when a bo

### Evidencia 9

- **Fuente**: issue #8435
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8435](https://github.com/langchain-ai/langgraph/pull/8435)
- **Keyword**: `test`
- **Texto**: Bumps [setuptools](https://github.com/pypa/setuptools) from 80.9.0 to 83.0.0.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a href="https://github.com/pypa/setuptools/blob/main/NEWS.rst"

### Evidencia 10

- **Fuente**: issue #8431
- **URL**: [https://github.com/langchain-ai/langgraph/pull/8431](https://github.com/langchain-ai/langgraph/pull/8431)
- **Keyword**: `test`
- **Texto**: Pull Request Description
Summary
Fixes #8429.

Resolves an issue where calling AsyncThreadStream.close() leaves active consumer iterators (stream.subscribe(...)) blocked indefinitely if the contex

---

## 7. Information Gaps

Información necesaria para explicar la trayectoria pero no observable públicamente.

### Observable

- Issues, PRs, commits, releases y discusiones públicas son observables.
- Las decisiones explícitas documentadas en estos canales son observables.

### Inferible

- El contexto organizativo (recursos, prioridades, deadlines) no está documentado públicamente.
- Las alternativas consideradas pero no verbalizadas no son observables.

### Desconocido

Issues abiertos sin resolución documentada:

- [#8449](https://github.com/langchain-ai/langgraph/pull/8449) chore(deps): fix vulnerable dev dependencies
- [#8448](https://github.com/langchain-ai/langgraph/issues/8448) PostgresSaver: get_delta_channel_history permanently poisons walk cursor when ta
- [#8443](https://github.com/langchain-ai/langgraph/issues/8443) DeltaChannel: forking a thread replays the abandoned branch's writes into the fo
- [#8442](https://github.com/langchain-ai/langgraph/issues/8442) sdk-py: @overload stubs in runs.py omit parameters the implementations accept, s
- [#8439](https://github.com/langchain-ai/langgraph/issues/8439) Proposal: Runtime Verification Pre-processor for Tool Node Execution
- [#8433](https://github.com/langchain-ai/langgraph/issues/8433) Eval pointer: REFUTE for science-reading agent graphs
- [#8432](https://github.com/langchain-ai/langgraph/issues/8432) Mapping check: which LangGraph surfaces should count as a pipeline's own fault-d
- [#8429](https://github.com/langchain-ai/langgraph/issues/8429) AsyncThreadStream.close() does not unblock active subscribe() iterators
- [#8420](https://github.com/langchain-ai/langgraph/issues/8420) AsyncPostgresSaver: support disabling pipeline for PgBouncer transaction mode
- [#8417](https://github.com/langchain-ai/langgraph/issues/8417) Misleading PydanticSerializationUnexpectedValue(Expected `none`) warning for `co

---

## Methodology

Este informe se generó exclusivamente a partir de la API pública de GitHub.

**Fuentes utilizadas:**
- GitHub Issues (abiertos y cerrados)
- GitHub Pull Requests (merged y closed)
- GitHub Commits
- GitHub Releases

**Fuentes prohibidas (no utilizadas):**
- Entrevistas
- Instrumentación adicional
- Logs privados
- Telemetría
- Nuevas bases de datos

**Regla de extracción:**
- Prohibido escribir: 'probablemente', 'seguramente', 'el equipo pensó', 'la intención era'
- Solo: evidencia observable, ausencia de evidencia, incertidumbre explícita

---

## Metrics

| Métrica | Conteo |
|---------|--------|
| Eventos cronológicos | 30 |
| Decisiones identificadas | 15 |
| Alternativas identificadas | 10 |
| Criterios identificados | 10 |
| Evidencia identificada | 10 |
| Issues abiertos (gaps) | 10 |
