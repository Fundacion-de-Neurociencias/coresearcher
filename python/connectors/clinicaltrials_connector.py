"""
ClinicalTrials.gov Connector - CoResearcher OS Sprint 21

Real connector for ClinicalTrials.gov API (AACT).
Queries trial registry data, study details, and related trials.

Domain-agnostic infrastructure. No medical/neurodiagnoses logic.
"""

from __future__ import annotations

import json
from typing import Any, Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode

from .base_connector import ScientificConnector, ConnectorResult, EvidenceItem


class ClinicalTrialsConnector(ScientificConnector):
    """
    Connector for ClinicalTrials.gov API.

    Provides access to:
    - Registered clinical trials worldwide
    - Study details (eligibility, outcomes, interventions)
    - Related trials by condition or intervention
    """

    SOURCE_NAME = "clinicaltrials"

    # API endpoints
    SEARCH_URL = "https://clinicaltrials.gov/api/v2/studies"
    STUDY_URL = "https://clinicaltrials.gov/api/v2/studies/{nct_id}"
    RELATED_URL = "https://clinicaltrials.gov/api/v2/studies"
    BASE_URL = "https://clinicaltrials.gov"

    def search(self, query: str, max_results: int = 20, **filters) -> ConnectorResult:
        """
        Search ClinicalTrials.gov for studies matching *query*.

        Supported filters:
            status: str - e.g. "RECRUITING", "COMPLETED", "ACTIVE_NOT_RECRUITING"
            phase: str - e.g. "PHASE2", "PHASE3"
            study_type: str - e.g. "INTERVENTIONAL", "OBSERVATIONAL"
        """
        cache_key = f"search:{query}:{max_results}:{json.dumps(filters, sort_keys=True)}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        params = {
            "query.term": query,
            "pageSize": str(min(max_results, 100)),
            "format": "json",
        }

        # Map common filters to API parameters
        filter_map = {
            "status": "filter.overallStatus",
            "phase": "filter.phase",
            "study_type": "filter.studyType",
        }
        for api_key, filter_key in filter_map.items():
            if api_key in filters:
                params[filter_key] = filters[api_key]

        try:
            url = f"{self.SEARCH_URL}?{urlencode(params)}"
            req = Request(url, headers={"User-Agent": "CoResearcherOS/0.1"})

            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())

            studies = data.get("studies", [])
            items = []
            for study in studies:
                protocol = study.get("protocolSection", {})
                id_module = protocol.get("identificationModule", {})
                status_module = protocol.get("statusModule", {})
                design_module = protocol.get("designModule", {})
                conditions_module = protocol.get("conditionsModule", {})

                nct_id = id_module.get("nctId", "")
                items.append({
                    "id": nct_id,
                    "source": self.SOURCE_NAME,
                    "title": id_module.get("briefTitle", ""),
                    "description": design_module.get("enrollmentInfo", {}).get("count", ""),
                    "url": f"{self.BASE_URL}/ct2/show/{nct_id}" if nct_id else "",
                    "status": status_module.get("overallStatus", ""),
                    "phase": design_module.get("phases", []),
                    "conditions": conditions_module.get("conditions", []),
                    "interventions": [
                        i.get("name", "") for i in
                        protocol.get("armsInterventionsModule", {}).get("interventions", [])
                    ],
                    "sponsor": protocol.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", ""),
                    "start_date": status_module.get("startDateStruct", {}).get("date", ""),
                    "completion_date": status_module.get("completionDateStruct", {}).get("date", ""),
                    "study_type": design_module.get("studyType", ""),
                })

            result = ConnectorResult(
                source=self.SOURCE_NAME,
                operation="search",
                query=query,
                total=data.get("totalCount", len(items)),
                items=items,
            )

        except Exception as e:
            result = self._error_result("search", query, str(e))

        self._set_cache(cache_key, result)
        self._log_provenance("search", query, result)
        return result

    def get(self, identifier: str) -> ConnectorResult:
        """
        Get a single study by NCT number.

        Args:
            identifier: NCT number (e.g. "NCT04267848").
        """
        cache_key = f"get:{identifier}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        try:
            url = self.STUDY_URL.format(nct_id=identifier)
            req = Request(
                f"{url}?format=json",
                headers={"User-Agent": "CoResearcherOS/0.1"},
            )

            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())

            study = data.get("study", data)
            protocol = study.get("protocolSection", study)

            id_module = protocol.get("identificationModule", {})
            status_module = protocol.get("statusModule", {})
            design_module = protocol.get("designModule", {})
            conditions_module = protocol.get("conditionsModule", {})
            eligibility_module = protocol.get("eligibilityModule", {})
            outcomes_module = protocol.get("outcomesModule", {})

            nct_id = id_module.get("nctId", identifier)
            items = [{
                "id": nct_id,
                "source": self.SOURCE_NAME,
                "title": id_module.get("briefTitle", ""),
                "official_title": id_module.get("officialTitle", ""),
                "description": id_module.get("briefTitle", ""),
                "url": f"{self.BASE_URL}/ct2/show/{nct_id}",
                "status": status_module.get("overallStatus", ""),
                "phase": design_module.get("phases", []),
                "conditions": conditions_module.get("conditions", []),
                "eligibility": {
                    "criteria": eligibility_module.get("eligibilityCriteria", ""),
                    "sex": eligibility_module.get("sex", ""),
                    "min_age": eligibility_module.get("minimumAge", ""),
                    "max_age": eligibility_module.get("maximumAge", ""),
                    "healthy_volunteers": eligibility_module.get("healthyVolunteers", ""),
                },
                "primary_outcomes": [
                    o.get("measure", "") for o in
                    outcomes_module.get("primaryOutcomes", [])
                ],
                "secondary_outcomes": [
                    o.get("measure", "") for o in
                    outcomes_module.get("secondaryOutcomes", [])
                ],
                "start_date": status_module.get("startDateStruct", {}).get("date", ""),
                "completion_date": status_module.get("completionDateStruct", {}).get("date", ""),
            }]

            result = ConnectorResult(
                source=self.SOURCE_NAME,
                operation="get",
                query=identifier,
                total=1,
                items=items,
            )

        except Exception as e:
            result = self._error_result("get", identifier, str(e))

        self._set_cache(cache_key, result)
        self._log_provenance("get", identifier, result)
        return result

    def related(self, identifier: str, max_results: int = 10) -> ConnectorResult:
        """
        Find related studies by sharing conditions with the given NCT.

        Args:
            identifier: NCT number to find related studies for.
        """
        # First fetch the study to get its conditions
        study_result = self.get(identifier)
        if study_result.error or not study_result.items:
            return self._error_result("related", identifier,
                                      f"Cannot find study {identifier}")

        conditions = study_result.items[0].get("conditions", [])
        if not conditions:
            return self._error_result("related", identifier,
                                      "No conditions found for this study")

        # Search using the first condition
        primary_condition = conditions[0]
        return self.search(primary_condition, max_results=max_results)

    def evidence(self, claim_or_concept: str, max_results: int = 20) -> ConnectorResult:
        """
        Find clinical trial evidence for a claim or concept.

        Args:
            claim_or_concept: A claim or concept to find supporting/refuting trials for.
        """
        result = self.search(claim_or_concept, max_results=max_results)

        # Convert to EvidenceItem format
        evidence_items = []
        for item in result.items:
            phase_list = item.get("phase") or []
            conditions_list = item.get("conditions") or []
            evidence_items.append(EvidenceItem(
                id=item["id"],
                source=self.SOURCE_NAME,
                title=item["title"],
                description=f"Status: {item.get('status', 'Unknown')} | "
                            f"Phase: {', '.join(phase_list)} | "
                            f"Conditions: {', '.join(conditions_list)}",
                url=item["url"],
                relevance_score=0.8 if item.get("status") == "COMPLETED" else 0.5,
                metadata={
                    "status": item.get("status"),
                    "phase": item.get("phase"),
                    "study_type": item.get("study_type"),
                },
            ).to_dict())

        result.items = evidence_items
        self._log_provenance("evidence", claim_or_concept, result)
        return result


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    import sys

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"


    connector = ClinicalTrialsConnector()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else "Alzheimer"
            result = connector.search(query)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "get":
            nct = sys.argv[2] if len(sys.argv) > 2 else "NCT04267848"
            result = connector.get(nct)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "related":
            nct = sys.argv[2] if len(sys.argv) > 2 else "NCT04267848"
            result = connector.related(nct)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "evidence":
            claim = sys.argv[2] if len(sys.argv) > 2 else "Amyloid PET imaging"
            result = connector.evidence(claim)
            print(json.dumps(result.to_dict(), indent=2))

        else:
            print(f"Unknown command: {cmd}")
    else:
        # Demo mode
        print("=" * 70)
        print("ClinicalTrials.gov Connector - Sprint 21")
        print("=" * 70)

        print("\n--- Search: Alzheimer ---")
        result = connector.search("Alzheimer", max_results=3)
        print(f"  Total: {result.total}")
        for item in result.items[:3]:
            print(f"  - {item['title'][:60]}...")

        print("\n--- Related to NCT04267848 ---")
        related = connector.related("NCT04267848", max_results=3)
        print(f"  Total: {related.total}")

        print("\n--- Evidence for 'Amyloid PET' ---")
        ev = connector.evidence("Amyloid PET", max_results=3)
        print(f"  Total: {ev.total}")
        for item in ev.items[:3]:
            print(f"  - [{item['source']}] {item['title'][:60]}...")

        print("\n--- Provenance ---")
        for entry in connector.get_provenance_log():
            print(f"  {entry['operation']}: {entry['query']} → {entry['total_results']} results")

        print("\nDone.")