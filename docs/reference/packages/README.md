# Research packages

Each `.crpkg` file here is a research package
([ADR-DISCOVERY-065](../../decisions/ADR-DISCOVERY-065-RESEARCH-PACKAGES.md)). This index publishes each package's
lifecycle digest outside the package itself. Verification proves that a package is consistent with its own
history; this table lets you check that it is the history that was published.

```bash
python scripts/research_package.py inspect docs/reference/packages/<file>.crpkg
```

| Package | Release | Kind | Lifecycle digest (version 7) | Manifest SHA-256 |
| --- | --- | --- | --- | --- |
| [openai-math-lean-oracle.crpkg](openai-math-lean-oracle.crpkg) | openai-math-lean-oracle-v7 | PREREGISTERED, both criteria met | `af51fe0de2c02338e0d4a28c6897495488e476ad5e29dc4f421670181e74d58c` | `4cd6894fb219eeb4a7948b30c18d414b372b8767bba4e27976ad92f232c7dcad` |

The oracle package was built by [`build_oracle_package.py`](../../../scripts/packages/build_oracle_package.py) and
signed off by Manuel Menéndez González on 2026-10-17. The file's own SHA-256 is `bf34e093e8df8fa9201b5d7c1284d6f3b55379f5b83a0fb43c6d2dd2056ea626`. Rebuilding the package
records new times, so it gives a new digest and a new file. This table pins the ones that were published.
