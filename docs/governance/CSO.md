# CoResearcher Scientific Ontology (CSO)

**Version 0.1.0** - Public Scientific Knowledge Ontology

## Overview

The CoResearcher Scientific Ontology (CSO) provides a universal framework for scientific knowledge representation. It transforms unstructured scientific literature into structured, computable knowledge.

## Core Concepts

| Concept | URI | Description |
|---------|-----|-------------|
| cso:Claim | https://cso.coresearcher.org/claim/{id} | A scientific assertion extracted from literature |
| cso:Evidence | https://cso.coresearcher.org/evidence/{id} | Empirical support for a claim |
| cso:Hypothesis | https://cso.coresearcher.org/hypothesis/{id} | A testable scientific proposition |
| cso:Experiment | https://cso.coresearcher.org/experiment/{id} | A designed test |
| cso:Finding | https://cso.coresearcher.org/finding/{id} | An observed result |
| cso:Contradiction | https://cso.coresearcher.org/contradiction/{id} | Conflicting claims |
| cso:Consensus | https://cso.coresearcher.org/consensus/{id} | Community-agreed knowledge |

## Relationships

| Relationship | URI | Description |
|-------------|-----|-------------|
| cso:supportedBy | https://cso.coresearcher.org/supportedBy | Claim supported by evidence |
| cso:contradicts | https://cso.coresearcher.org/contradicts | Claim contradicts another |
| cso:derivesFrom | https://cso.coresearcher.org/derivesFrom | Hypothesis derived from claims |
| cso:tests | https://cso.coresearcher.org/tests | Experiment tests hypothesis |
| cso:validates | https://cso.coresearcher.org/validates | Evidence validates claim |

## Qualifiers

| Qualifier | URI | Description |
|-----------|-----|-------------|
| cso:trustIndex | https://cso.coresearcher.org/trustIndex | 0-100 trust score |
| cso:qualityScore | https://cso.coresearcher.org/qualityScore | Evidence quality (0-1) |
| cso:evidenceScore | https://cso.coresearcher.org/evidenceScore | Claim evidence score |
| cso:sampleSize | https://cso.coresearcher.org/sampleSize | Number of subjects |
| cso:pValue | https://cso.coresearcher.org/pValue | Statistical significance |
| cso:effectSize | https://cso.coresearcher.org/effectSize | Effect magnitude |

## Knowledge Hierarchy

```
Observation → Evidence → Claim → SupportedClaim → ConsensusClaim → Theory
```

## Usage

**Citing a claim:**
```
CoResearcher Scientific Ontology. CLAIM-003921. 
https://cso.coresearcher.org/claim/CLAIM-003921
```

**Querying via API:**
```python
api = ScientificKnowledgeAPI()
result = api.get_claim("CLAIM-003921")
```

## Contributing

Submit new concepts or conversions via GitHub pull request to the CSO repository.

## License

CC-BY 4.0 - Free for scientific use with attribution.