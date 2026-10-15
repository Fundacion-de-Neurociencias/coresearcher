"""
Claim Graph Builder — CoResearcher OS Sprint 2
Transforms Neo4j from document repository to scientific reasoning engine.

Capabilities:
  1. Entity Resolution: Canonical Concept Registry with alias merging
  2. Claim Graph Builder: Rich scientific relationships
  3. Contradiction Detection: Find conflicting claims
  4. Evidence Ranking: Score claims by evidence strength
  5. Scientific Traversals: Advanced graph queries

Architecture:
  pipeline_result → Entity Resolution → Claim Graph → Contradiction Check → Neo4j
"""

import json
import re
import sys
from collections import defaultdict, Counter
from typing import Optional

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"



# ---------------------------------------------------------------------------
# 1. Entity Resolution Layer
# ---------------------------------------------------------------------------

# Canonical entity registry for neurodegenerative diseases
CANONICAL_ENTITIES = {
    # Diseases
    "alzheimer": {"id": "DISEASE:AD", "canonical": "Alzheimer's disease", "type": "Disease",
                   "aliases": ["alzheimer", "alzheimer's", "alzheimer disease", "ad", "alzheimers"]},
    "mci": {"id": "DISEASE:MCI", "canonical": "Mild Cognitive Impairment", "type": "Disease",
             "aliases": ["mci", "mild cognitive impairment", "mild cognitive"]},
    "parkinson": {"id": "DISEASE:PD", "canonical": "Parkinson's disease", "type": "Disease",
                   "aliases": ["parkinson", "parkinson's", "parkinson disease", "pd"]},
    "dementia_with_lewy": {"id": "DISEASE:DLB", "canonical": "Dementia with Lewy Bodies", "type": "Disease",
                            "aliases": ["dlb", "lewy body", "lewy bodies", "dementia with lewy"]},
    "ftd": {"id": "DISEASE:FTD", "canonical": "Frontotemporal Dementia", "type": "Disease",
             "aliases": ["ftd", "frontotemporal", "frontotemporal dementia"]},
    "psp": {"id": "DISEASE:PSP", "canonical": "Progressive Supranuclear Palsy", "type": "Disease",
             "aliases": ["psp", "progressive supranuclear"]},
    "cbd": {"id": "DISEASE:CBD", "canonical": "Corticobasal Degeneration", "type": "Disease",
             "aliases": ["cbd", "corticobasal"]},
    "als": {"id": "DISEASE:ALS", "canonical": "Amyotrophic Lateral Sclerosis", "type": "Disease",
             "aliases": ["als", "amyotrophic lateral sclerosis", "lou gehrig"]},
    "huntington": {"id": "DISEASE:HD", "canonical": "Huntington's disease", "type": "Disease",
                    "aliases": ["huntington", "huntington's", "hd"]},
    "multiple_sclerosis": {"id": "DISEASE:MS", "canonical": "Multiple Sclerosis", "type": "Disease",
                            "aliases": ["ms", "multiple sclerosis"]},
    # Biomarkers
    "ptau217": {"id": "BIOMARKER:pTau217", "canonical": "Phosphorylated tau 217", "type": "Biomarker",
                 "aliases": ["ptau217", "p-tau217", "p tau217", "phosphorylated tau 217",
                             "phospho-tau217", "phospho tau217", "ptau-217"]},
    "ptau181": {"id": "BIOMARKER:pTau181", "canonical": "Phosphorylated tau 181", "type": "Biomarker",
                 "aliases": ["ptau181", "p-tau181", "p tau181", "phosphorylated tau 181",
                             "phospho-tau181", "phospho tau181", "ptau-181"]},
    "abeta42": {"id": "BIOMARKER:Aβ42", "canonical": "Amyloid beta 42", "type": "Biomarker",
                 "aliases": ["abeta42", "aβ42", "amyloid beta 42", "aβ-42",
                             "amyloid-beta 42", "abeta-42"]},
    "abeta40": {"id": "BIOMARKER:Aβ40", "canonical": "Amyloid beta 40", "type": "Biomarker",
                 "aliases": ["abeta40", "aβ40", "amyloid beta 40", "aβ-40",
                             "amyloid-beta 40", "abeta-40"]},
    "nfl": {"id": "BIOMARKER:NfL", "canonical": "Neurofilament light chain", "type": "Biomarker",
             "aliases": ["nfl", "neurofilament light", "neurofilament light chain"]},
    "gfap": {"id": "BIOMARKER:GFAP", "canonical": "Glial fibrillary acidic protein", "type": "Biomarker",
              "aliases": ["gfap", "glial fibrillary acidic"]},
    "tau_pet": {"id": "BIOMARKER:TauPET", "canonical": "Tau PET", "type": "Biomarker",
                 "aliases": ["tau pet", "tau-pet", "tau pet imaging", "tau PET"]},
    "amyloid_pet": {"id": "BIOMARKER:AmyloidPET", "canonical": "Amyloid PET", "type": "Biomarker",
                     "aliases": ["amyloid pet", "amyloid-pet", "aβ pet", "aβ-pet", "amyloid PET imaging"]},
    # Genes
    "apoe": {"id": "GENE:APOE", "canonical": "APOE", "type": "Gene",
              "aliases": ["apoe", "apoe4", "apoe ε4", "apoe-ε4", "apolipoprotein e"]},
    "app": {"id": "GENE:APP", "canonical": "APP", "type": "Gene",
             "aliases": ["app", "amyloid precursor protein"]},
    "psen1": {"id": "GENE:PSEN1", "canonical": "PSEN1", "type": "Gene",
               "aliases": ["psen1", "presenilin 1"]},
    "psen2": {"id": "GENE:PSEN2", "canonical": "PSEN2", "type": "Gene",
               "aliases": ["psen2", "presenilin 2"]},
    "mapt": {"id": "GENE:MAPT", "canonical": "MAPT", "type": "Gene",
              "aliases": ["mapt", "microtubule associated protein tau", "tau gene"]},
    # Proteins
    "tau_protein": {"id": "PROTEIN:Tau", "canonical": "Tau protein", "type": "Protein",
                     "aliases": ["tau", "tau protein", "microtubule-associated protein tau"]},
    "abeta": {"id": "PROTEIN:Abeta", "canonical": "Amyloid beta", "type": "Protein",
               "aliases": ["amyloid beta", "aβ", "beta-amyloid", "amyloid-β"]},
    "alpha_synuclein": {"id": "PROTEIN:AlphaSynuclein", "canonical": "Alpha-synuclein", "type": "Protein",
                         "aliases": ["alpha-synuclein", "α-synuclein", "alpha synuclein"]},
    # Drugs
    "lecanemab": {"id": "DRUG:Lecanemab", "canonical": "Lecanemab", "type": "Drug",
                   "aliases": ["lecanemab", "lecanemab-irmb", "leqembi"]},
    "donanemab": {"id": "DRUG:Donanemab", "canonical": "Donanemab", "type": "Drug",
                   "aliases": ["donanemab"]},
    "aducanumab": {"id": "DRUG:Aducanumab", "canonical": "Aducanumab", "type": "Drug",
                    "aliases": ["aducanumab", "aducanumab-avwa", "aduhelm"]},
    # Mechanisms (Eje 2 — Pathophysiology)
    "amyloid_aggregation": {"id": "MECHANISM:AmyloidAggregation", "canonical": "Amyloid aggregation", "type": "Mechanism",
                              "aliases": ["amyloid aggregation", "amyloid plaque", "aβ aggregation",
                                          "amyloid deposition", "amyloid accumulation"]},
    "tau_hyperphosphorylation": {"id": "MECHANISM:TauHyperphosphorylation", "canonical": "Tau hyperphosphorylation", "type": "Mechanism",
                                  "aliases": ["tau hyperphosphorylation", "tau phosphorylation",
                                              "tau hyper-phosphorylation", "abnormal tau"]},
    "lipid_dysregulation": {"id": "MECHANISM:LipidDysregulation", "canonical": "Lipid dysregulation", "type": "Mechanism",
                             "aliases": ["lipid dysregulation", "lipid metabolism", "cholesterol dysregulation",
                                         "lipid homeostasis"]},
    "neuroinflammation": {"id": "MECHANISM:Neuroinflammation", "canonical": "Neuroinflammation", "type": "Mechanism",
                           "aliases": ["neuroinflammation", "inflammation", "microglial activation",
                                       "inflammatory response"]},
    "synaptic_dysfunction": {"id": "MECHANISM:SynapticDysfunction", "canonical": "Synaptic dysfunction", "type": "Mechanism",
                              "aliases": ["synaptic dysfunction", "synaptic loss", "synaptic failure",
                                          "synaptic impairment"]},
    "oxidative_stress": {"id": "MECHANISM:OxidativeStress", "canonical": "Oxidative stress", "type": "Mechanism",
                         "aliases": ["oxidative stress", "oxidative damage", "reactive oxygen species"]},
    # Axes (Neurodiagnoses native citizens)
    "axis0_context": {"id": "AXIS0:Context", "canonical": "Eje 0: Contexto", "type": "Axis0",
                      "aliases": ["eje 0", "axis 0", "contexto", "context factor", "demographic", "environment"]},
    "axis1_genetic": {"id": "AXIS1:Genetic", "canonical": "Eje 1: Genética", "type": "Axis1",
                      "aliases": ["eje 1", "axis 1", "genetic", "genética", "genetic factor", "hereditary"]},
    "axis2_mechanism": {"id": "AXIS2:Mechanism", "canonical": "Eje 2: Mecanismos", "type": "Axis2",
                        "aliases": ["eje 2", "axis 2", "mecanismo", "mechanism", "pathophysiology", "etiology"]},
}

# Build inverse lookup: lowercase alias → canonical key
_ALIAS_MAP = {}
for key, entity in CANONICAL_ENTITIES.items():
    for alias in entity["aliases"]:
        _ALIAS_MAP[alias.lower()] = key


class EntityResolver:
    """Resolves raw entity strings to canonical scientific entities."""

    def __init__(self):
        self.canonical_registry = CANONICAL_ENTITIES
        self.alias_map = _ALIAS_MAP
        self._custom_entities = {}  # For dynamically discovered entities

    def resolve(self, entity: str) -> dict:
        """
        Resolve a raw entity string to its canonical form.
        
        Returns:
            {"id": "BIOMARKER:pTau217", "canonical": "Phosphorylated tau 217", 
             "type": "Biomarker", "matched": True}
        """
        cleaned = entity.lower().strip().rstrip(".")
        
        # Direct alias match
        if cleaned in self.alias_map:
            key = self.alias_map[cleaned]
            return {**self.canonical_registry[key], "matched": True}
        
        # Partial match: check if any alias is contained in or contains the entity
        for key, canonical in self.canonical_registry.items():
            for alias in canonical["aliases"]:
                if alias in cleaned or cleaned in alias:
                    return {**canonical, "matched": True}
        
        # Check custom entities (previously resolved unknowns)
        if cleaned in self._custom_entities:
            return {**self._custom_entities[cleaned], "matched": True}
        
        # Unknown entity: register as custom
        custom_id = f"ENTITY:{cleaned.replace(' ', '_').title()}"
        custom = {
            "id": custom_id,
            "canonical": entity.strip(),
            "type": self._infer_type(entity),
            "aliases": [cleaned],
            "matched": False,
        }
        self._custom_entities[cleaned] = custom
        return custom

    def _infer_type(self, entity: str) -> str:
        """Infer entity type from naming patterns."""
        # Greek letters or protein notation
        if re.search(r'[αβγδεκλμνοπρσ τω]', entity.lower()):
            return "Protein"
        # Capital+number patterns (pTau217, Aβ42)
        if re.search(r'[A-Z][a-z]*\d+', entity):
            return "Biomarker"
        # Gene notation (all caps, 2-5 chars)
        if re.search(r'^[A-Z]{2,5}$', entity.strip()):
            return "Gene"
        # Common disease suffixes
        if any(s in entity.lower() for s in ["disease", "syndrome", "disorder", "dementia"]):
            return "Disease"
        return "Concept"

    def resolve_entities(self, entities: list[str]) -> list[dict]:
        """Resolve a list of raw entities."""
        return [self.resolve(e) for e in entities if e and len(e) > 1]


# ---------------------------------------------------------------------------
# 2. Evidence Ranking Engine
# ---------------------------------------------------------------------------

EVIDENCE_WEIGHTS = {
    "meta_analysis": 1.0,
    "systematic_review": 0.95,
    "randomized_controlled_trial": 0.9,
    "clinical_trial": 0.85,
    "cohort_study": 0.7,
    "case_control": 0.6,
    "cross_sectional": 0.5,
    "genetic_study": 0.55,
    "biomarker_study": 0.65,
    "review": 0.4,
    "case_report": 0.3,
    "editorial": 0.1,
}

SAMPLE_SIZE_BOOSTS = [
    (10000, 0.2),
    (1000, 0.15),
    (500, 0.1),
    (100, 0.05),
]


class EvidenceRanker:
    """Ranks scientific claims by evidence strength."""

    @staticmethod
    def rank_claim(claim: dict, paper_metadata: dict = None) -> dict:
        """
        Calculate evidence score for a claim.
        
        Factors:
        - Study type weight
        - Sample size
        - Statistical significance
        - Confidence from extractor
        - Publication venue (via metadata)
        """
        score = claim.get("confidence", 0.5)  # Base from extractor
        
        # Study type boost (from paper metadata)
        study_type = (paper_metadata or {}).get("type", "").lower()
        if study_type in EVIDENCE_WEIGHTS:
            score = score * 0.7 + EVIDENCE_WEIGHTS[study_type] * 0.3
        
        # Statistical evidence boost
        evidence = claim.get("evidence", [])
        has_p_value = any("p<" in e.get("value", "") or "p≤" in e.get("value", "") for e in evidence)
        has_hr = any(e.get("value", "").startswith("HR") for e in evidence)
        has_auc = any("AUC" in e.get("value", "") for e in evidence)
        
        if has_p_value:
            score = min(1.0, score + 0.1)
        if has_hr:
            score = min(1.0, score + 0.08)
        if has_auc:
            score = min(1.0, score + 0.08)
        
        # Sample size boost (from text)
        claim_text = claim.get("statement", "")
        n_matches = re.findall(r'n\s*[=≈]\s*(\d+)', claim_text)
        if n_matches:
            n = int(n_matches[0])
            for threshold, boost in SAMPLE_SIZE_BOOSTS:
                if n >= threshold:
                    score = min(1.0, score + boost)
                    break
        
        # Determine evidence strength label
        if score >= 0.8:
            strength = "HIGH"
        elif score >= 0.6:
            strength = "MODERATE"
        elif score >= 0.4:
            strength = "LOW"
        else:
            strength = "INSUFFICIENT"
        
        return {
            "evidence_score": round(score, 3),
            "evidence_strength": strength,
            "study_type": study_type if study_type else "unknown",
            "has_statistical_evidence": has_p_value or has_hr or has_auc,
            "n_evidence_items": len(evidence),
        }


# ---------------------------------------------------------------------------
# 3. Contradiction Detection
# ---------------------------------------------------------------------------

# Negation patterns that indicate contradictory findings
NEGATION_PATTERNS = [
    r"(?:not|no|none|without|absence of|lack of|failed to|does not|do not|did not)",
    r"(?:no significant|not significant|non-significant|not associated|no association)",
    r"(?:no difference|did not differ|not different|similar between|comparable)",
    r"(?:no evidence|no support|not support|does not support|do not support)",
    r"(?:remains unclear|remains unknown|not yet established|inconclusive)",
]

POSITIVE_PATTERNS = [
    r"(?:significantly|strongly|positively|negatively) (?:associated|correlated|related)",
    r"(?:increased|decreased|elevated|reduced|higher|lower)",
    r"(?:predict|predicts|predictive|predictor|associated with|linked to)",
    r"(?:demonstrate|show|find|report|provide evidence)",
    r"(?:AUC|area under|sensitivity|specificity) of (?:0\.\d+|[\d.]+%)",
]


class ContradictionDetector:
    """Detects contradictions between scientific claims."""

    def __init__(self):
        self.negation_re = re.compile('|'.join(NEGATION_PATTERNS), re.IGNORECASE)
        self.positive_re = re.compile('|'.join(POSITIVE_PATTERNS), re.IGNORECASE)

    def classify_sentiment(self, claim_text: str) -> str:
        """Classify claim as 'positive', 'negative', or 'neutral'."""
        has_negation = bool(self.negation_re.search(claim_text))
        has_positive = bool(self.positive_re.search(claim_text))
        
        if has_negation and not has_positive:
            return "negative"
        elif has_positive and not has_negation:
            return "positive"
        elif has_positive and has_negation:
            # Complex: "No significant association" → negative
            # "Not only associated but also" → positive
            if self.negation_re.search(claim_text.split("but")[0] if "but" in claim_text else claim_text):
                return "negative"
            return "positive"
        return "neutral"

    def extract_subject_predicate(self, claim_text: str) -> tuple:
        """Extract (subject, predicate) pair for comparison."""
        # Simple extraction: first entity-like term + verb phrase
        text = claim_text.lower()
        
        # Try to find "X predicts/associated with Y" pattern
        subject = None
        obj = None
        
        # Pattern: "X is associated with Y"
        m = re.search(r'(\w+(?:\s+\w+){0,3})\s+(?:is|are)\s+(?:significantly|strongly|)?\s*(?:associated|correlated|predictive)\s+(?:with|of)\s+(\w+(?:\s+\w+){0,3})', text)
        if m:
            subject, obj = m.group(1).strip(), m.group(2).strip()
        
        # Pattern: "X predicts Y"
        m = re.search(r'(\w+(?:\s+\w+){0,3})\s+predicts?\s+(\w+(?:\s+\w+){0,3})', text)
        if m and not subject:
            subject, obj = m.group(1).strip(), m.group(2).strip()
        
        # Pattern: "X levels are higher/lower in Y"
        m = re.search(r'(\w+(?:\s+\w+){0,2})\s+(?:levels|concentration|expression)\s+(?:are|is|were)\s+(\w+)', text)
        if m and not subject:
            subject = f"{m.group(1)} {m.group(2)}"
        
        return subject, obj

    def find_contradictions(self, claims: list[dict]) -> list[dict]:
        """
        Find contradictions among a list of claims.
        
        Two claims contradict if:
        - They share subject/predicate
        - One is positive and the other negative
        """
        contradictions = []
        
        for i, c1 in enumerate(claims):
            s1, o1 = self.extract_subject_predicate(c1.get("statement", ""))
            sentiment1 = self.classify_sentiment(c1.get("statement", ""))
            
            for j, c2 in enumerate(claims[i+1:], i+1):
                s2, o2 = self.extract_subject_predicate(c2.get("statement", ""))
                sentiment2 = self.classify_sentiment(c2.get("statement", ""))
                
                # Check if they share subject or object
                shares_subject = s1 and s2 and (
                    s1 in s2 or s2 in s1 or 
                    any(w in s2 for w in s1.split()[:2])
                )
                
                # Check opposite sentiments
                if shares_subject and sentiment1 != sentiment2:
                    if (sentiment1 == "positive" and sentiment2 == "negative") or \
                       (sentiment1 == "negative" and sentiment2 == "positive"):
                        contradictions.append({
                            "claim_1": c1.get("statement", ""),
                            "claim_1_sentiment": sentiment1,
                            "claim_1_confidence": c1.get("confidence", 0),
                            "claim_2": c2.get("statement", ""),
                            "claim_2_sentiment": sentiment2,
                            "claim_2_confidence": c2.get("confidence", 0),
                            "shared_subject": s1 if s1 == s2 else f"{s1} / {s2}",
                            "contradiction_type": "DIRECT" if sentiment1 != sentiment2 else "PARTIAL",
                        })
        
        return contradictions


# ---------------------------------------------------------------------------
# 4. Main Claim Graph Builder
# ---------------------------------------------------------------------------

class ClaimGraphBuilder:
    """
    Orchestrates the full Sprint 2 pipeline:
    
    Raw claims → Entity Resolution → Evidence Ranking → 
    Contradiction Detection → Neo4j graph
    """

    def __init__(self, neo4j_client=None):
        self.resolver = EntityResolver()
        self.ranker = EvidenceRanker()
        self.detector = ContradictionDetector()

    def process_pipeline_result(self, pipeline_result: dict, neo4j_client=None) -> dict:
        """
        Process a pipeline result through the full Sprint 2 pipeline.
        
        Returns enriched result with:
        - Resolved entities (canonical)
        - Evidence-ranked claims
        - Contradiction detection
        """
        client = neo4j_client
        total_resolved = 0
        total_contradictions = 0
        
        for paper_data in pipeline_result.get("papers", []):
            for claim in paper_data.get("claims", []):
                # 1. Entity Resolution
                raw_entities = claim.get("entities", [])
                resolved = self.resolver.resolve_entities(raw_entities)
                claim["resolved_entities"] = resolved
                total_resolved += len(resolved)
                
                # Update domain based on resolved entities
                for ent in resolved:
                    if ent.get("type") == "Disease":
                        claim["domain"] = "neurodegeneration"
                        break
                
                # 2. Evidence Ranking
                rank = self.ranker.rank_claim(claim, paper_data.get("source", {}))
                claim["evidence_ranking"] = rank
                
                # Replace confidence with evidence score
                claim["confidence"] = rank["evidence_score"]
            
            # 3. Contradiction Detection (within this paper)
            contradictions = self.detector.find_contradictions(paper_data.get("claims", []))
            total_contradictions += len(contradictions)
            
            if contradictions:
                if "contradictions" not in paper_data:
                    paper_data["contradictions"] = []
                paper_data["contradictions"].extend(contradictions)
        
        # Cross-paper contradiction detection
        all_claims = []
        for paper_data in pipeline_result.get("papers", []):
            for claim in paper_data.get("claims", []):
                all_claims.append(claim)
        
        cross_contradictions = self.detector.find_contradictions(all_claims)
        
        enriched = {
            "total_resolved_entities": total_resolved,
            "total_contradictions": total_contradictions + len(cross_contradictions),
            "cross_paper_contradictions": len(cross_contradictions),
            "cross_contradictions": cross_contradictions[:20],  # Limit output
        }
        
        pipeline_result["claim_graph"] = enriched
        return pipeline_result

    def generate_neo4j_queries(self, pipeline_result: dict) -> list[str]:
        """
        Generate Cypher queries for the enriched claim graph.
        
        Neurodiagnoses Reasoning Graph model:
        - (:Disease), (:Biomarker), (:Gene), (:Protein), (:Drug), (:Mechanism), (:Trial)
        - (Claim)-[:CONTRADICTS]->(Claim)
        - (Claim)-[:SUPPORTED_BY]->(Evidence) with evidence scoring
        - (Biomarker)-[:PREDICTS]->(Disease)
        - (Gene)-[:ASSOCIATED_WITH]->(Disease)
        - (Gene)-[:INFLUENCES]->(Mechanism)
        - (Mechanism)-[:CAUSES]->(Biomarker)
        - (Mechanism)-[:CONTRIBUTES_TO]->(Disease)
        - (Disease)-[:HAS_AXIS0|HAS_AXIS1|HAS_AXIS2]->(Axis)
        """
        queries = []
        
        for paper_data in pipeline_result.get("papers", []):
            source = paper_data.get("source", {})
            pmid = source.get("pmid", "")
            
            for claim in paper_data.get("claims", []):
                claim_id = f"C{abs(hash(claim.get('statement', ''))) % 10**12}"
                
                # Create typed entity nodes based on resolved entities
                for ent in claim.get("resolved_entities", []):
                    entity_id = ent.get("id", "")
                    canonical = ent.get("canonical", "")
                    etype = ent.get("type", "Concept")
                    
                    # Create typed node
                    safe_name = canonical.replace("'", "\\'")
                    queries.append(
                        f"MERGE (e:{etype} {{id: '{entity_id}'}}) "
                        f"SET e.name = '{safe_name}'"
                    )
                    
                    # Link Claim to typed entity with proper relationship
                    rel_type = self._get_claim_entity_relation(claim.get("type", ""), etype)
                    queries.append(
                        f"MATCH (c:Claim {{id: '{claim_id}'}}), "
                        f"(e:{etype} {{id: '{entity_id}'}}) "
                        f"MERGE (c)-[:{rel_type}]->(e)"
                    )
                    
                    # Create inter-entity relationships for known connections
                    if etype == "Biomarker":
                        # Biomarker → PREDICTS → Disease (based on claim)
                        for ent2 in claim.get("resolved_entities", []):
                            if ent2.get("type") == "Disease":
                                e2_id = ent2["id"]
                                queries.append(
                                    f"MATCH (b:Biomarker {{id: '{entity_id}'}}), "
                                    f"(d:Disease {{id: '{e2_id}'}}) "
                                    f"MERGE (b)-[:PREDICTS]->(d)"
                                )
                    elif etype == "Gene":
                        for ent2 in claim.get("resolved_entities", []):
                            if ent2.get("type") == "Disease":
                                e2_id = ent2["id"]
                                queries.append(
                                    f"MATCH (g:Gene {{id: '{entity_id}'}}), "
                                    f"(d:Disease {{id: '{e2_id}'}}) "
                                    f"MERGE (g)-[:ASSOCIATED_WITH]->(d)"
                                )
                    elif etype == "Mechanism":
                        # Mechanism → CONTRIBUTES_TO → Disease
                        for ent2 in claim.get("resolved_entities", []):
                            if ent2.get("type") == "Disease":
                                e2_id = ent2["id"]
                                queries.append(
                                    f"MATCH (m:Mechanism {{id: '{entity_id}'}}), "
                                    f"(d:Disease {{id: '{e2_id}'}}) "
                                    f"MERGE (m)-[:CONTRIBUTES_TO]->(d)"
                                )
                        # Mechanism → CAUSES → Biomarker
                        for ent2 in claim.get("resolved_entities", []):
                            if ent2.get("type") == "Biomarker":
                                e2_id = ent2["id"]
                                queries.append(
                                    f"MATCH (m:Mechanism {{id: '{entity_id}'}}), "
                                    f"(b:Biomarker {{id: '{e2_id}'}}) "
                                    f"MERGE (m)-[:CAUSES]->(b)"
                                )
                    elif etype == "Axis2":
                        # Axis2 → Mechanism (native citizen connection)
                        for ent2 in claim.get("resolved_entities", []):
                            if ent2.get("type") == "Mechanism":
                                e2_id = ent2["id"]
                                queries.append(
                                    f"MATCH (a:Axis2 {{id: '{entity_id}'}}), "
                                    f"(m:Mechanism {{id: '{e2_id}'}}) "
                                    f"MERGE (a)-[:HAS_MECHANISM]->(m)"
                                )
                
                # Evidence score as node property + claim metadata
                rank = claim.get("evidence_ranking", {})
                if rank:
                    queries.append(
                        f"MATCH (c:Claim {{id: '{claim_id}'}}) "
                        f"SET c.evidenceScore = {rank.get('evidence_score', 0.5)}, "
                        f"c.evidenceStrength = '{rank.get('evidence_strength', 'LOW')}', "
                        f"c.studyType = '{rank.get('study_type', 'unknown')}', "
                        f"c.createdAt = datetime(), "
                        f"c.supportCount = 0, "
                        f"c.contradictionCount = 0"
                    )
                
                # Evidence nodes with full scoring
                for ev_idx, evidence in enumerate(claim.get("evidence", [])):
                    ev_value = evidence.get("value", "").replace("'", "\\'")[:200]
                    ev_type = evidence.get("type", "statistical")
                    ev_id = f"E{abs(hash(str(evidence))) % 10**12}"
                    queries.append(
                        f"MATCH (c:Claim {{id: '{claim_id}'}}) "
                        f"MERGE (c)-[:SUPPORTED_BY]->(e:Evidence {{id: '{ev_id}'}}) "
                        f"SET e.value = '{ev_value}', "
                        f"e.evidenceType = '{ev_type}', "
                        f"e.qualityScore = {rank.get('evidence_score', 0.5) if rank else 0.5}, "
                        f"e.hasStatisticalEvidence = {str(rank.get('has_statistical_evidence', False) if rank else False).lower()}"
                    )
            
            # Create CONTRADICTS relationships
            for contra in paper_data.get("contradictions", []):
                c1_text = contra.get("claim_1", "")
                c2_text = contra.get("claim_2", "")
                c1_id = f"C{abs(hash(c1_text)) % 10**12}"
                c2_id = f"C{abs(hash(c2_text)) % 10**12}"
                ctype = contra.get("contradiction_type", "DIRECT")
                queries.append(
                    f"MATCH (c1:Claim {{id: '{c1_id}'}}), "
                    f"(c2:Claim {{id: '{c2_id}'}}) "
                    f"MERGE (c1)-[:CONTRADICTS {{type: '{ctype}'}}]->(c2)"
                )
                # Track contradiction count on both claims
                queries.append(
                    f"MATCH (c1:Claim {{id: '{c1_id}'}}) "
                    f"SET c1.contradictionCount = c1.contradictionCount + 1"
                )
                queries.append(
                    f"MATCH (c2:Claim {{id: '{c2_id}'}}) "
                    f"SET c2.contradictionCount = c2.contradictionCount + 1"
                )
        
        return queries

    def _get_claim_entity_relation(self, claim_type: str, entity_type: str) -> str:
        """Determine the relationship type between a claim and an entity."""
        if entity_type == "Disease":
            return "ABOUT_DISEASE"
        elif entity_type == "Biomarker":
            return "MENTIONS_BIOMARKER"
        elif entity_type == "Gene":
            return "MENTIONS_GENE"
        elif entity_type == "Protein":
            return "MENTIONS_PROTEIN"
        elif entity_type == "Drug":
            return "MENTIONS_DRUG"
        else:
            return "ABOUT"


# ---------------------------------------------------------------------------
# 5. Scientific Traversals (Neurodiagnoses Reasoning Graph)
# ---------------------------------------------------------------------------

class ScientificTraversals:
    """
    Advanced graph queries for scientific discovery on the reasoning graph.
    
    Enables:
    - Mechanism chaining: Gene → Mechanism → Biomarker → Disease
    - Axis-aware queries: Disease HAS_AXIS0/Axis1/Axis2
    - Contradiction-aware evidence queries
    - High-quality biomarker discovery
    """

    @staticmethod
    def biomarker_mechanism_chain(disease: str) -> str:
        """Find full causal chain: Gene → Mechanism → Biomarker → Disease."""
        return f"""
        MATCH (g:Gene)-[:ASSOCIATED_WITH]->(d:Disease {{name: '{disease}'}})
        OPTIONAL MATCH (g)-[:INFLUENCES]->(m:Mechanism)-[:CAUSES]->(b:Biomarker)-[:PREDICTS]->(d)
        RETURN g.name AS gene, m.name AS mechanism, b.name AS biomarker, d.name AS disease
        """

    @staticmethod
    def high_quality_biomarkers(min_score: float = 0.8) -> str:
        """Find biomarkers supported by high-quality evidence only."""
        return f"""
        MATCH (c:Claim)-[:SUPPORTED_BY]->(e:Evidence)
        WHERE c.evidenceScore >= {min_score} AND e.hasStatisticalEvidence = true
        MATCH (c)-[:MENTIONS_BIOMARKER]->(b:Biomarker)-[:PREDICTS]->(d:Disease)
        RETURN b.name AS biomarker, d.name AS disease, 
               avg(c.evidenceScore) AS avg_score, count(c) AS n_claims
        ORDER BY avg_score DESC
        """

    @staticmethod
    def contradiction_aware_query(entity: str) -> str:
        """Find supporting vs contradicting claims for an entity."""
        return f"""
        MATCH (c:Claim)-[:MENTIONS_BIOMARKER|ABOUT_DISEASE]->(n)
        WHERE n.name = '{entity}'
        OPTIONAL MATCH (c)-[:CONTRADICTS]->(c2:Claim)
        RETURN c.text AS claim, c.evidenceScore AS score, 
               c.contradictionCount AS contradictions,
               count(c2) AS contradicting_claims
        ORDER BY c.evidenceScore DESC
        """

    @staticmethod
    def axis_reasoning(disease: str) -> str:
        """Native Neurodiagnoses axis traversal for a disease."""
        return f"""
        MATCH (d:Disease {{name: '{disease}'}})
        OPTIONAL MATCH (d)-[:HAS_AXIS0]->(a0:Axis0)
        OPTIONAL MATCH (d)-[:HAS_AXIS1]->(a1:Axis1)
        OPTIONAL MATCH (d)-[:HAS_AXIS2]->(a2:Axis2)-[:HAS_MECHANISM]->(m:Mechanism)
        RETURN d.name AS disease, a0.name AS axis0, a1.name AS axis1, 
               a2.name AS axis2, collect(m.name) AS mechanisms
        """

    @staticmethod
    def drug_trial_traversal() -> str:
        """Drug → Trial → Disease → Biomarker (Sprint 3 foundation)."""
        return """
        MATCH (dr:Drug)-[:TESTED_IN]->(t:Trial)-[:TARGETS]->(d:Disease)
        OPTIONAL MATCH (t)-[:MEASURES]->(b:Biomarker)
        OPTIONAL MATCH (t)-[:SUPPORTS]->(c:Claim)
        RETURN dr.name AS drug, t.name AS trial, d.name AS disease, 
               collect(b.name) AS biomarkers, count(c) AS supported_claims
        """


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    builder = ClaimGraphBuilder()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test with sample data
        sample = {
            "query": "Alzheimer tau PET biomarker",
            "source": "pubmed",
            "total_papers": 2,
            "total_claims": 4,
            "papers": [
                {
                    "source": {"pmid": "38273008", "doi": "10.1016/S1474-4422(22)00168-5",
                              "title": "Tau biomarkers in Alzheimer's disease"},
                    "claims": [
                        {"statement": "Plasma pTau217 predicts progression from MCI to Alzheimer's disease",
                         "type": "biomarker", "confidence": 0.85, "domain": "neurodegeneration",
                         "evidence": [{"type": "statistical", "value": "AUC=0.87, p<0.001"}],
                         "entities": ["pTau217", "MCI", "Alzheimer"]},
                        {"statement": "Plasma pTau181 does not predict progression from MCI to AD",
                         "type": "biomarker", "confidence": 0.65, "domain": "neurodegeneration",
                         "evidence": [{"type": "statistical", "value": "p=0.23"}],
                         "entities": ["pTau181", "MCI", "AD"]},
                    ],
                    "claim_count": 2,
                },
                {
                    "source": {"pmid": "37273009", "doi": "10.1038/s41591-023-02343-6",
                              "title": "Plasma biomarkers for Alzheimer's disease"},
                    "claims": [
                        {"statement": "GFAP is associated with cognitive decline in Alzheimer's disease",
                         "type": "biomarker", "confidence": 0.78, "domain": "neurodegeneration",
                         "evidence": [{"type": "statistical", "value": "p<0.01"}],
                         "entities": ["GFAP", "Alzheimer"]},
                        {"statement": "NfL levels are elevated in Alzheimer's disease but not specific",
                         "type": "biomarker", "confidence": 0.72, "domain": "neurodegeneration",
                         "evidence": [{"type": "statistical", "value": "AUC=0.82"}],
                         "entities": ["NfL", "Alzheimer"]},
                    ],
                    "claim_count": 2,
                },
            ],
        }
        
        print("=" * 70)
        print("Claim Graph Builder - Test Run")
        print("=" * 70)
        
        # Process
        result = builder.process_pipeline_result(sample)
        
        # Show results
        for i, paper in enumerate(result["papers"]):
            print(f"\n[Paper {i+1}] {paper['source']['title'][:70]}")
            for j, claim in enumerate(paper["claims"]):
                print(f"  Claim {j+1}: {claim['statement'][:80]}...")
                print(f"    Evidence Score: {claim['evidence_ranking']['evidence_score']}")
                print(f"    Strength: {claim['evidence_ranking']['evidence_strength']}")
                print(f"    Resolved entities:")
                for ent in claim.get("resolved_entities", []):
                    print(f"      - {ent['canonical']} ({ent['type']}) [{ent['id']}]")
                if paper.get("contradictions"):
                    print(f"    CONTRADICTS:")
                    for c in paper["contradictions"]:
                        print(f"      - vs: {c['claim_2'][:60]}...")
        
        print(f"\nCross-paper contradictions: {result['claim_graph']['cross_paper_contradictions']}")
        
        # Generate Cypher
        print("\n--- Generated Cypher ---")
        queries = builder.generate_neo4j_queries(result)
        for q in queries:
            print(f"  {q}")
        
        print(f"\nTotal Cypher queries: {len(queries)}")