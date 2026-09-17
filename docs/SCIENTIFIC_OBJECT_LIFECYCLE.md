#Scientific Object Lifecycle
## From Observation to Theory in CoResearcher

## The Path of Knowledge

```
Observation → Claim → Finding → Mechanism → Model → Theory
     ↓          ↓       ↓         ↓        ↓       ↓
   (cruda)   (atómica) (estruct.) (explic.) (conjunto) (paradigma)
```

---

## 1. Observation (Not registered)

Unstructured raw data:
- Paper text
- Experiment result
- Medical imaging
- Genomic signal

---

## 2. Claim (CLAIM-XXXXXX)

### Birth
```
Paper extraído → Claim identificado
```

### Attributes
- `text`: literal statement
- `entities`: entities involved
- `evidenceScore`: confidence in observation
- `supportingPapers`: [PMID-XXXXXX, ...]
- `domain`: knowledge area

### Operations
- `SUPPORT` - reinforce the claim
- `CHALLENGE` - question the claim
- `RETRACT` - remove the claim

### Life cycle
Low mutability. Go to archived.

---

## 3. Finding (FIND-XXXXXX)

### Birth
```
Claim + Claim + Claim → Finding distilado
(o
Paper → KnowledgeDistillationEngine → Finding)
```

### Attributes
- `subject`: main entity
- `predicate`: relationship (predicts, causes, associated)
- `object`: related entity
- `effect_size`: magnitude
- `p_value`: significance
- `derivedFrom`: [CLAIM-XXXXXX, ...]
- `quality_score`: 0.0-1.0

### Operations
- `CONFIRM` - additional evidence
- `REJECT` - empirical refutation
- `REPLICATE` - independent replication

### Life cycle
```
created → validated → replicated → challenged → merged → archived
```

---

## 4. Mechanism (MECH-XXXXXX)

### Birth
```
Anomaly + Finding → Mechanism proposito
(o
Finding + Finding → Mechanism inferido)
```

### Attributes
- `name`: friendly name
- `description`: detailed explanation
- `entities`: [entity,...]
- `arrows`: causal path
- `type`: causal_chain/feedback/threshold/compensatory/emergent
- `confidence`: 0.0-1.0
- `derived_from`: [FIND-XXXXXX, CLAIM-XXXXXX]
- `contradicts`: [MECH-XXXXXX, ...]
- `supports`: [MECH-XXXXXX, ...]

### Operations (Participation Layer)
- `SUPPORT` - evidence in favor
- `CHALLENGE` - critical analysis
- `REPLICATE` - replication mechanism
- `REJECT` - rebuttal
- `FORK` - mechanism variant
- `MERGE` - combination mechanisms

### Critical life cycle
```
proposed (confidence=0.1)
    ↓
explored (challenges, forks)
    ↓
validated (replications, confirms)
    ↓
adopted (high trust_score, institution_count)
    ↓
refuted OR remains dominant
```

---

## 5. Model (MODEL-XXXXXX)

### Birth
```
Mechanism + Mechanism + Mechanism → Model integrador
```

### Attributes
- `name`: model name
- `mechanisms`: [MECH-XXXXXX, ...]
- `boundaries`: model scope
- `assumptions`: key assumptions
- `predictions`: derived predictions

### Operations
- `FIT_TEST` - how well it explains data
- `CROSS_VALIDATE` - new predictions
- `EXTEND` - expand scope

---

## 6. Theory (THEORY-XXXXXX)

### Birth
```
Model + Model + Model → Theory unificadora
```

### Attributes
- `name`: theory name
- `models`: [MODEL-XXXXXX, ...]
- `domain_coverage`: areas covered
- `explanatory_power`: 0.0-1.0
- `consilience`: degree of unification

---

## Trusted Relationships

```
CLAIM.trust = evidenceScore
FINDING.trust = avg(claims.trust) + replications
MECHANISM.trust = participation_signals(support, challenge, replicate)
MODEL.trust = mechanisms.trust_avg
THEORY.trust = models.trust_avg + consilience
```

---

## Participation Signals Matrix

| Action | Object | Effect on Trust |
|--------|---------|------------------|
| SUPPORT | CLAIM | +0.1 |
| CHALLENGE | CLAIM | -0.1 |
| REPLICATE | FINDING | +0.2 |
| CONFIRM | MECHANISM | +0.3 |
| REJECT | MECHANISM | -0.5 |
| FORK | MECHANISM | +0.1 (variant) |

---

## The Golden Rule

**A scientific object does not exist for discovery until it can be refuted.**

- Claim: difficult to refute (it is an observation)
- Finding: refutable (quantitative prediction)
- Mechanism: highly refutable (specific predictions)
- Model: refutable (predictive constraints)
- Theory: easier to refute (many predictions)

---

## The Improvement Engine

```
MECHANISM.trust_low
      ↓
"Can this be refuted?"
      ↓
YES → Predictions generated
      ↓
Predictions tested
      ↓
Trust evolves (up/down)
      ↓
Survives OR dies
```

This is the loop that makes CoResearcher a discovery OS, not a database.