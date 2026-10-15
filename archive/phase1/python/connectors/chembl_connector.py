"""
ChEMBL Connector - CoResearcher OS Sprint 21

Real connector for ChEMBL REST API.
Queries bioactive molecule data, drug targets, activities, and compound properties.

Domain-agnostic infrastructure. No medical/neurodiagnoses logic.
"""

from __future__ import annotations

import json
from typing import Any, Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode

from .base_connector import ScientificConnector, ConnectorResult, EvidenceItem


class ChEMBLConnector(ScientificConnector):
    """
    Connector for ChEMBL REST API (v33+).

    Provides access to:
    - Bioactive molecules and their properties
    - Drug-target interactions and activities
    - Compound mechanisms of action
    - Target bioactivity data (IC50, Ki, etc.)
    """

    SOURCE_NAME = "chembl"

    # API base URL
    API_URL = "https://www.ebi.ac.uk/chembl/api/data"

    def _request(self, endpoint: str, params: dict = None) -> dict:
        """Make a request to the ChEMBL API and return JSON."""
        url = f"{self.API_URL}/{endpoint}"
        if params:
            url = f"{url}?{urlencode(params)}"
        req = Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "CoResearcherOS/0.1",
        })
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    def search(self, query: str, max_results: int = 20, **filters) -> ConnectorResult:
        """
        Search ChEMBL for molecules, targets, or drugs.

        Args:
            query: Search term (compound name, target name, drug name).
        """
        cache_key = f"search:{query}:{max_results}:{json.dumps(filters, sort_keys=True)}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        try:
            # Search across multiple entity types
            molecules = self._request("molecule.json", {
                "q": query,
                "limit": str(min(max_results, 50)),
            })

            molecule_matches = molecules.get("molecules", [])
            items = []

            for mol in molecule_matches[:max_results]:
                mol_chembl_id = mol.get("molecule_chembl_id", "")
                approved_name = ""
                synonyms = mol.get("molecule_synonyms", [])
                if synonyms:
                    approved_name = synonyms[0].get("synonyms", "")
                    if isinstance(approved_name, list) and approved_name:
                        approved_name = approved_name[0]

                items.append({
                    "id": mol_chembl_id,
                    "source": self.SOURCE_NAME,
                    "title": mol.get("pref_name", mol_chembl_id),
                    "description": mol.get("molecule_type", ""),
                    "url": f"https://www.ebi.ac.uk/chembl/compound_report_card/{mol_chembl_id}" if mol_chembl_id else "",
                    "approved_name": approved_name or mol.get("pref_name", ""),
                    "molecule_type": mol.get("molecule_type", ""),
                    "max_phase": mol.get("max_phase"),
                    "molecular_weight": next(
                        (p.get("mw_freebase", 0) for p in mol.get("molecule_properties", [])
                         if isinstance(p, dict)),
                        None,
                    ),
                    "smiles": next(
                        (s.get("structure", "") for s in mol.get("molecule_structures", [])
                         if isinstance(s, dict)),
                        None,
                    ),
                    "first_approval": mol.get("first_approval", None),
                })

            result = ConnectorResult(
                source=self.SOURCE_NAME,
                operation="search",
                query=query,
                total=molecules.get("page_meta", {}).get("total_count", len(items)),
                items=items,
            )

        except Exception as e:
            result = self._error_result("search", query, str(e))

        self._set_cache(cache_key, result)
        self._log_provenance("search", query, result)
        return result

    def get(self, identifier: str) -> ConnectorResult:
        """
        Get a molecule or target by ChEMBL ID.

        Args:
            identifier: ChEMBL ID (e.g. "CHEMBL120" for Aspirin, CHEMBL ID for target).
        """
        cache_key = f"get:{identifier}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        try:
            # Try as molecule first
            molecule = self._request(f"molecule/{identifier}.json")

            if molecule and molecule.get("molecule_chembl_id"):
                mol = molecule
                mol_chembl_id = mol.get("molecule_chembl_id", identifier)

                # Get activities for this molecule
                try:
                    activities = self._request("activity.json", {
                        "molecule_chembl_id": mol_chembl_id,
                        "limit": "20",
                    })
                except Exception:
                    activities = {"activities": []}

                items = [{
                    "id": mol_chembl_id,
                    "source": self.SOURCE_NAME,
                    "title": mol.get("pref_name", mol_chembl_id),
                    "description": mol.get("molecule_type", ""),
                    "url": f"https://www.ebi.ac.uk/chembl/compound_report_card/{mol_chembl_id}",
                    "molecule_type": mol.get("molecule_type", ""),
                    "max_phase": mol.get("max_phase"),
                    "first_approval": mol.get("first_approval"),
                    "oral_dose": mol.get("oral_dose_g_per_day"),
                    "parenteral_dose": mol.get("parenteral_dose_g_per_day"),
                    "molecular_weight": next(
                        (p.get("mw_freebase") for p in mol.get("molecule_properties", [])
                         if isinstance(p, dict)),
                        None,
                    ),
                    "alogp": next(
                        (p.get("alogp") for p in mol.get("molecule_properties", [])
                         if isinstance(p, dict)),
                        None,
                    ),
                    "smiles": next(
                        (s.get("canonical_smiles", "") for s in mol.get("molecule_structures", [])
                         if isinstance(s, dict)),
                        None,
                    ),
                    "inchi_key": next(
                        (s.get("standard_inchi_key", "") for s in mol.get("molecule_structures", [])
                         if isinstance(s, dict)),
                        None,
                    ),
                    "activities": [
                        {
                            "type": act.get("standard_type", ""),
                            "value": act.get("standard_value"),
                            "units": act.get("standard_units", ""),
                            "relation": act.get("standard_relation", ""),
                            "target": {
                                "id": act.get("target_chembl_id", ""),
                                "name": act.get("target_pref_name", ""),
                            },
                            "assay": act.get("assay_description", ""),
                        }
                        for act in activities.get("activities", [])
                    ],
                }]

                result = ConnectorResult(
                    source=self.SOURCE_NAME,
                    operation="get",
                    query=identifier,
                    total=1,
                    items=items,
                )
            else:
                # Try target
                target = self._request(f"target/{identifier}.json")
                if target and target.get("target_chembl_id"):
                    target_data = target
                    tgt_chembl_id = target_data.get("target_chembl_id", identifier)

                    # Get activities for this target
                    try:
                        activities = self._request("activity.json", {
                            "target_chembl_id": tgt_chembl_id,
                            "limit": "20",
                        })
                    except Exception:
                        activities = {"activities": []}

                    items = [{
                        "id": tgt_chembl_id,
                        "source": self.SOURCE_NAME,
                        "title": target_data.get("pref_name", tgt_chembl_id),
                        "description": target_data.get("target_type", ""),
                        "url": f"https://www.ebi.ac.uk/chembl/target_report_card/{tgt_chembl_id}",
                        "target_type": target_data.get("target_type", ""),
                        "organism": target_data.get("organism", ""),
                        "tax_id": target_data.get("tax_id"),
                        "activities": [
                            {
                                "type": act.get("standard_type", ""),
                                "value": act.get("standard_value"),
                                "units": act.get("standard_units", ""),
                                "relation": act.get("standard_relation", ""),
                                "molecule": {
                                    "id": act.get("molecule_chembl_id", ""),
                                    "name": act.get("molecule_pref_name", ""),
                                },
                            }
                            for act in activities.get("activities", [])
                        ],
                    }]

                    result = ConnectorResult(
                        source=self.SOURCE_NAME,
                        operation="get",
                        query=identifier,
                        total=1,
                        items=items,
                    )
                else:
                    result = self._error_result("get", identifier,
                                                f"No molecule or target found: {identifier}")

        except Exception as e:
            result = self._error_result("get", identifier, str(e))

        self._set_cache(cache_key, result)
        self._log_provenance("get", identifier, result)
        return result

    def related(self, identifier: str, max_results: int = 10) -> ConnectorResult:
        """
        Find related compounds by similar targets or similar structures.

        Args:
            identifier: ChEMBL molecule ID.
        """
        molecule = self.get(identifier)
        if molecule.error or not molecule.items:
            return self._error_result("related", identifier,
                                      f"Cannot find molecule: {identifier}")

        # Get target IDs from activities
        activities = molecule.items[0].get("activities", [])
        target_ids = list(set(
            act["target"]["id"] for act in activities
            if act.get("target", {}).get("id")
        ))

        related_items = []
        for target_id in target_ids[:3]:  # For first 3 targets
            try:
                activities = self._request("activity.json", {
                    "target_chembl_id": target_id,
                    "limit": str(max_results // len(target_ids[:3])),
                })
                # Get unique molecules from this target's activities
                seen_mols = set()
                for act in activities.get("activities", []):
                    mol_id = act.get("molecule_chembl_id", "")
                    mol_name = act.get("molecule_pref_name", "")
                    if mol_id and mol_id != identifier and mol_id not in seen_mols:
                        seen_mols.add(mol_id)
                        related_items.append({
                            "id": mol_id,
                            "title": mol_name or mol_id,
                            "via_target": target_id,
                            "activity_type": act.get("standard_type", ""),
                            "activity_value": act.get("standard_value"),
                        })
            except Exception:
                continue

        result = ConnectorResult(
            source=self.SOURCE_NAME,
            operation="related",
            query=identifier,
            total=len(related_items),
            items=related_items[:max_results],
        )

        self._log_provenance("related", identifier, result)
        return result

    def evidence(self, claim_or_concept: str, max_results: int = 20) -> ConnectorResult:
        """
        Find bioactivity evidence for a claim or concept.

        Searches ChEMBL and returns compound-target activity data as evidence.
        """
        search_result = self.search(claim_or_concept, max_results=5)

        evidence_items = []
        for item in search_result.items:
            molecule_id = item["id"]
            molecule_detail = self.get(molecule_id)

            if not molecule_detail.error and molecule_detail.items:
                for activity in molecule_detail.items[0].get("activities", []):
                    evidence_items.append(EvidenceItem(
                        id=f"{molecule_id}|{activity.get('type', '')}|{activity.get('target', {}).get('id', '')}",
                        source=self.SOURCE_NAME,
                        title=f"{item['title']} - {activity.get('type', '')}: "
                              f"{activity.get('value', '')} {activity.get('units', '')}",
                        description=f"Target: {activity.get('target', {}).get('name', 'Unknown')} | "
                                    f"Relation: {activity.get('relation', '=')}",
                        url=f"https://www.ebi.ac.uk/chembl/compound_report_card/{molecule_id}",
                        relevance_score=0.5 if activity.get("value") else 0.0,
                        metadata={
                            "molecule_chembl_id": molecule_id,
                            "activity_type": activity.get("type"),
                            "activity_value": activity.get("value"),
                            "activity_units": activity.get("units"),
                            "target_chembl_id": activity.get("target", {}).get("id"),
                        },
                    ))

        # Deduplicate
        seen: set[str] = set()
        deduped = []
        for ev in evidence_items:
            if ev.id not in seen:
                seen.add(ev.id)
                deduped.append(ev.to_dict())

        result = ConnectorResult(
            source=self.SOURCE_NAME,
            operation="evidence",
            query=claim_or_concept,
            total=len(deduped),
            items=deduped[:max_results],
        )

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


    connector = ChEMBLConnector()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else "Aspirin"
            result = connector.search(query)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "get":
            ident = sys.argv[2] if len(sys.argv) > 2 else "CHEMBL120"
            result = connector.get(ident)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "related":
            ident = sys.argv[2] if len(sys.argv) > 2 else "CHEMBL120"
            result = connector.related(ident)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "evidence":
            claim = sys.argv[2] if len(sys.argv) > 2 else "Aspirin anti-inflammatory"
            result = connector.evidence(claim)
            print(json.dumps(result.to_dict(), indent=2))

        else:
            print(f"Unknown command: {cmd}")
    else:
        # Demo mode
        print("=" * 70)
        print("ChEMBL Connector - Sprint 21")
        print("=" * 70)

        print("\n--- Search: Aspirin ---")
        result = connector.search("Aspirin", max_results=3)
        print(f"  Total: {result.total}")
        for item in result.items[:3]:
            print(f"  - {item['title']} ({item['id']})")

        print("\n--- Get CHEMBL120 (Aspirin) ---")
        target = connector.get("CHEMBL120")
        if not target.error and target.items:
            print(f"  Name: {target.items[0]['title']}")
            print(f"  Type: {target.items[0]['molecule_type']}")
            print(f"  Activities: {len(target.items[0].get('activities', []))}")

        print("\n--- Related to CHEMBL120 ---")
        related = connector.related("CHEMBL120", max_results=5)
        print(f"  Total related: {related.total}")

        print("\n--- Evidence for 'Aspirin COX inhibition' ---")
        ev = connector.evidence("Aspirin COX inhibition", max_results=3)
        print(f"  Total evidence: {ev.total}")
        for item in ev.items[:3]:
            print(f"  - {item['title']}")

        print("\n--- Provenance ---")
        for entry in connector.get_provenance_log():
            print(f"  {entry['operation']}: {entry['query']} → {entry['total_results']} results")

        print("\nDone.")