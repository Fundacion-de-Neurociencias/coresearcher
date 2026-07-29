# Scientific Object Canonical Language
## All Research Objects Are English Internally

**Version 1.0.0** - Protocol Foundation  
**Status**: Mandatory Language Rule

---

## The Rule

All scientific objects in CoResearcher MUST be stored in English internally, regardless of user interface language.

```
User asks: "¿Puede GFAP predecir Alzheimer preclínico?"
↓
Internally stored: "Can plasma GFAP predict preclinical Alzheimer's disease?"
```

---

## Why English Internally

### 1. Scientific Literature is English
- 70%+ of papers are in English
- All major databases use English
- AI models perform best on English

### 2. Semantic Deduplication Works Better
Same question in different languages = duplicates:
```
❌ "¿Puede GFAP predecir Alzheimer?" (Spanish)
❌ "Puede GFAP predecir Alzheimer?" (Portuguese with tilde removed)
❌ "Can GFAP predict Alzheimer?" (English)
```
All are the same research question. Canonical English prevents this.

### 3. Cross-Language Collaboration
Researchers from different countries can instantly align on English questions.

### 4. Agent Intelligence Works Better
Current AI models show superior performance on English for scientific tasks.

---

## The Translation Layer

### User → System
```text
Spanish UI → English QUESTION
French UI → English QUESTION  
Japanese UI → English QUESTION
```

### System → User
```text
English QUESTION → Local language when possible
English CLAIM → Original language preserved + English metadata
```

Scientific content (claims, evidence) preserves original language but gets English metadata.

---

## User Interface Freedom

Users interact in their preferred language:
- UI can be localized
- Prompts can be in local language
- But stored as English canonical

This separates **interface** from **protocol**.

---

## The Implementation

Every scientific object has:
```yaml
id: QUESTION-001234
canonical_text: "Can plasma GFAP predict preclinical Alzheimer's disease?"
original_text: "¿Puede GFAP predecir Alzheimer preclínico?"
language_ui: "es"
language_original: "es"
```

---

## Consequences

Before adding more constitutions, implement:
- [ ] Language detection on input
- [ ] Translation to canonical English
- [ ] Backward translation for display
- [ ] Original language preservation

---

*This rule prevents semantic fragmentation. English internally, any language externally.*