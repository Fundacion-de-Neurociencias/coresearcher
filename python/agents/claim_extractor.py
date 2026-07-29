"""
Claim Extraction Agent
The core differentiator: converts unstructured scientific text into structured
Claim → Evidence → Confidence triples stored in Neo4j.

Inspired by WiPhy (Wisdom from Physics) paradigm.
"""
import json
import re
import sys
from typing import Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode


class ClaimExtractor:
    """
    Extracts scientific claims from paper abstracts/text.
    
    Pipeline:
    1. Chunk text into claim-sized segments
    2. Identify claim statements (assertions, findings, conclusions)
    3. Extract evidence (statistical, experimental, observational)
    4. Assign confidence score
    5. Link to sources (PMIDs, DOIs)
    """

    # Patterns that indicate scientific claims
    CLAIM_PATTERNS = [
        # Direct findings
        r"(?:We|Our|This study) (?:show|demonstrate|find|report|provide evidence that|suggest|indicate)",
        r"(?:Results|Data|Findings) (?:show|demonstrate|suggest|indicate|reveal|support)",
        r"(?:These|Our) (?:findings|results|data|observations) (?:suggest|indicate|support|demonstrate)",
        # Associations and correlations
        r"(?:is|are) (?:significantly|strongly|positively|negatively) (?:associated|correlated|related)",
        r"(?:increased|decreased|elevated|reduced) (?:risk|level|expression|activity|function)",
        # Predictive statements
        r"(?:predict|predicts|predictive of|predictor of|associated with|linked to)",
        r"(?:plays a|play a) (?:critical|key|important|significant|major) role in",
        # Causal statements
        r"(?:leads to|results in|contributes to|mediated by|regulated by|driven by)",
        r"(?:mechanism|pathway|process) (?:by which|through which|underlying)",
        # Clinical findings
        r"(?:diagnostic|prognostic|therapeutic) (?:marker|biomarker|target|potential)",
        r"(?:AUC|sensitivity|specificity|accuracy) of (?:0\.\d+|[\d.]+%)",
    ]

    EVIDENCE_PATTERNS = [
        r"p\s*[<≤]\s*0\.\d+",
        r"HR\s*[=≈]\s*[\d.]+",
        r"OR\s*[=≈]\s*[\d.]+",
        r"RR\s*[=≈]\s*[\d.]+",
        r"CI:\s*[\d.]+\s*[-–]\s*[\d.]+",
        r"95%\s*(?:%20)?CI",
        r"n\s*[=≈]\s*\d+",
        r"AUC\s*[=≈]\s*0\.\d+",
        r"correlation\s*(?:coefficient)?\s*[=≈]\s*[\d.]+",
        r"r\s*[=≈]\s*[\d.]+",
    ]

    def extract_claims(self, text: str, source_pmid: Optional[str] = None, 
                       source_doi: Optional[str] = None) -> list[dict]:
        """
        Extract all claims from a scientific text.
        
        Returns list of:
        {
            "id": "C-{uuid}",
            "statement": "Plasma pTau217 predicts progression from MCI to AD",
            "type": "association" | "mechanism" | "biomarker" | "clinical",
            "confidence": 0.87,
            "evidence": [{"type": "statistical", "value": "p<0.001"}],
            "source_pmid": "38273008",
            "source_doi": "10.1038/s41591-023-02343-6",
            "domain": "neurodegeneration",
            "entities": ["pTau217", "MCI", "AD"],
        }
        """
        if not text or len(text.strip()) < 50:
            return []

        claims = []
        sentences = self._chunk_sentences(text)
        
        for sentence in sentences:
            claim = self._analyze_sentence(sentence, source_pmid, source_doi)
            if claim:
                claims.append(claim)

        # Merge overlapping claims and deduplicate
        claims = self._deduplicate(claims)
        
        return claims

    def _chunk_sentences(self, text: str) -> list[str]:
        """Split text into sentences, handling scientific abbreviations."""
        # Protect common scientific abbreviations from splitting
        text = re.sub(r'(e\.g\.|i\.e\.|et al\.|vs\.|Fig\.|Figs\.)', 
                     lambda m: m.group(0).replace('.', '<DOT>'), text)
        
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"])', text)
        
        # Restore dots
        sentences = [s.replace('<DOT>', '.') for s in sentences if s.strip()]
        
        return sentences

    def _analyze_sentence(self, sentence: str, source_pmid: Optional[str], 
                          source_doi: Optional[str]) -> Optional[dict]:
        """Analyze a single sentence for claim content."""
        sentence_lower = sentence.lower()
        
        # Check if sentence contains a claim pattern
        matched_pattern = None
        for pattern in self.CLAIM_PATTERNS:
            if re.search(pattern, sentence_lower):
                matched_pattern = pattern
                break
        
        if not matched_pattern:
            return None

        # Extract evidence from sentence
        evidence = []
        has_statistical = False
        for ev_pattern in self.EVIDENCE_PATTERNS:
            matches = re.findall(ev_pattern, sentence_lower)
            for match in matches:
                evidence.append({
                    "type": "statistical",
                    "value": match,
                    "extracted_from": "sentence",
                })
                if "p" in match or "p&" in match:
                    has_statistical = True

        # Determine claim type
        claim_type = self._classify_claim(sentence_lower, evidence)
        
        # Calculate confidence
        confidence = self._calculate_confidence(sentence, evidence, has_statistical)

        # Extract entities (simple noun phrase extraction)
        entities = self._extract_entities(sentence)

        # Normalize the claim statement
        statement = self._normalize_claim(sentence)

        return {
            "statement": statement,
            "type": claim_type,
            "confidence": round(confidence, 2),
            "evidence": evidence,
            "source_pmid": source_pmid,
            "source_doi": source_doi,
            "domain": self._classify_domain(entities),
            "entities": entities,
        }

    def _classify_claim(self, text: str, evidence: list) -> str:
        """Classify the type of scientific claim."""
        if any(w in text for w in ["biomarker", "marker", "predict", "diagnos"]):
            return "biomarker"
        if any(w in text for w in ["mechanism", "pathway", "regulated", "mediated"]):
            return "mechanism"
        if any(w in text for w in ["trial", "treatment", "therapy", "drug", "efficacy"]):
            return "clinical"
        if any(w in text for w in ["associated", "correlated", "risk"]):
            return "association"
        if any(w in text for w in ["gene", "mutation", "variant", "genetic"]):
            return "genetic"
        return "finding"

    def _calculate_confidence(self, sentence: str, evidence: list, 
                              has_statistical: bool) -> float:
        """Calculate confidence score for a claim."""
        confidence = 0.5  # Base confidence

        # Statistical evidence boosts confidence
        if has_statistical:
            confidence += 0.2

        # Strong wording
        strong_words = ["significantly", "strongly", "demonstrate", "prove", "conclusive"]
        if any(w in sentence.lower() for w in strong_words):
            confidence += 0.1

        # Number of evidence items
        confidence += min(len(evidence) * 0.05, 0.15)

        # Caveats reduce confidence
        caveats = ["suggest", "may", "could", "possibly", "indicate", "might"]
        if any(w in sentence.lower() for w in caveats):
            confidence -= 0.1

        # Sample size mention boosts
        if re.search(r'n\s*[=≈]\s*(\d+)', sentence):
            n = int(re.search(r'n\s*[=≈]\s*(\d+)', sentence).group(1))
            if n > 100:
                confidence += 0.1
            elif n > 1000:
                confidence += 0.2

        return max(0.1, min(1.0, confidence))

    def _extract_entities(self, text: str) -> list[str]:
        """Extract capitalized scientific entities from text."""
        # Extract capitalized terms (potential scientific entities)
        entities = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', text)
        
        # Filter to likely scientific entities
        scientific = []
        skip_words = {"We", "Our", "This", "These", "The", "However", "Although", 
                      "While", "Because", "But", "Therefore", "Thus", "Moreover",
                      "Furthermore", "Additionally", "In", "Of", "For", "With"}
        
        for entity in entities:
            if entity not in skip_words and len(entity) > 2:
                scientific.append(entity)
        
        # Also extract gene/protein notation (e.g., pTau217, Aβ42)
        protein_patterns = re.findall(r'\b[A-Za-z]+[0-9]*[A-Za-z]*[0-9]+\b', text)
        for p in protein_patterns:
            if p not in scientific:
                scientific.append(p)
        
        return list(set(scientific))[:10]  # Max 10 entities

    def _normalize_claim(self, sentence: str) -> str:
        """Clean and normalize a claim sentence."""
        # Remove leading discourse markers
        discourse = r"^(We|Our|These|This study) (found that|show that|demonstrate that|suggest that|indicate that|report that)\s+"
        sentence = re.sub(discourse, "", sentence, flags=re.IGNORECASE)
        
        # Capitalize first letter
        sentence = sentence[0].upper() + sentence[1:] if sentence else sentence
        
        # Remove trailing whitespace/punctuation
        sentence = sentence.strip().rstrip(".;,") + "."
        
        return sentence

    def _deduplicate(self, claims: list) -> list:
        """Remove duplicate or near-duplicate claims."""
        unique = []
        seen_statements = set()
        
        for claim in claims:
            # Create a simplified key for deduplication
            key = re.sub(r'[^a-z0-9]', '', claim["statement"].lower())
            if key not in seen_statements:
                seen_statements.add(key)
                unique.append(claim)
        
        return unique

    def _classify_domain(self, entities: list) -> str:
        """Classify the biomedical domain based on entities."""
        neurodegenerative = ["Alzheimer", "Parkinson", "Huntington", "Dementia", 
                           "MCI", "ALS", "FTD", "DLB", "MultipleSclerosis",
                           "MS", "Neurodegenerative"]
        
        oncology = ["Cancer", "Tumor", "Carcinoma", "Metastasis", "Oncology"]
        
        cardiovascular = ["Cardiac", "Heart", "Cardiovascular", "Myocardial"]
        
        all_text = " ".join(entities)
        
        for term in neurodegenerative:
            if term.lower() in all_text.lower():
                return "neurodegeneration"
        for term in oncology:
            if term.lower() in all_text.lower():
                return "oncology"
        for term in cardiovascular:
            if term.lower() in all_text.lower():
                return "cardiovascular"
        
        return "general_biomedical"


def batch_extract_claims(papers: list[dict]) -> list[dict]:
    """
    Batch extract claims from a list of papers.
    
    papers: list of {"pmid": "...", "doi": "...", "abstract": "...", "title": "..."}
    """
    extractor = ClaimExtractor()
    results = []
    
    for paper in papers:
        # Combine title and abstract for extraction
        text = f"{paper.get('title', '')}. {paper.get('abstract', '')}"
        claims = extractor.extract_claims(
            text=text,
            source_pmid=paper.get("pmid"),
            source_doi=paper.get("doi"),
        )
        
        results.append({
            "source": {
                "pmid": paper.get("pmid"),
                "doi": paper.get("doi"),
                "title": paper.get("title"),
            },
            "claims": claims,
            "claim_count": len(claims),
        })
    
    return results


if __name__ == "__main__":
    import sys

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"

    extractor = ClaimExtractor()
    
    if len(sys.argv) > 1:
        # Read paper data from stdin
        input_data = json.loads(sys.stdin.read())
        
        if isinstance(input_data, dict):
            text = input_data.get("text", "")
            pmid = input_data.get("pmid")
            doi = input_data.get("doi")
            claims = extractor.extract_claims(text, pmid, doi)
            print(json.dumps({"claims": claims, "count": len(claims)}, indent=2))
        elif isinstance(input_data, list):
            results = batch_extract_claims(input_data)
            print(json.dumps({"papers": results, "total_claims": 
                  sum(r["claim_count"] for r in results)}, indent=2))
    else:
        # Demo mode
        sample = (
            "We found that plasma pTau217 is significantly associated with cognitive decline "
            "in patients with mild cognitive impairment (MCI). The AUC for predicting progression "
            "to Alzheimer's disease was 0.87 (95% CI: 0.82-0.91, p<0.001). These findings suggest "
            "that pTau217 could serve as a valuable biomarker for early diagnosis of Alzheimer's disease."
        )
        print(json.dumps(extractor.extract_claims(sample), indent=2))