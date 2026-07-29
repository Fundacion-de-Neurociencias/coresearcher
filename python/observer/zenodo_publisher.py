"""
Zenodo Publisher - Sprint 37
Publishes ScientificLedger objects to Zenodo via REST API.
"""

from __future__ import annotations

import json
import os
import tempfile
from typing import Optional, Dict, List

import requests

from observer.scientific_ledger import ScientificLedger
from observer.ledger_normalizer import normalize_for_zenodo

SANDBOX_API = "https://sandbox.zenodo.org/api"
PRODUCTION_API = "https://zenodo.org/api"


class ZenodoPublisher:
    """Publishes a ScientificLedger to Zenodo as a dataset deposit."""

    def __init__(self, api_token: str, use_sandbox: bool = True) -> None:
        if not api_token:
            raise ValueError("api_token is required for Zenodo publishing")
        self.api_token = api_token
        self.api_root = SANDBOX_API if use_sandbox else PRODUCTION_API

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def deposit(self, ledger: ScientificLedger, publish: bool = False) -> Dict:
        """
        Create a Zenodo deposit from a ScientificLedger.

        Returns the Zenodo deposition dict (including 'id', 'status', etc.).
        If publish=False, the deposit remains in 'draft' state and has no DOI.
        """
        payload = normalize_for_zenodo(ledger)
        url = f"{self.api_root}/deposit/depositions"

        # Create deposit with metadata
        r = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        if r.status_code not in (201, 202):
            raise RuntimeError(
                f"Zenodo deposit creation failed: {r.status_code} {r.text}"
            )
        deposition = r.json()
        deposition_id = deposition["id"]

        # Upload ledger JSON as a file
        self._upload_ledger_file(deposition_id, ledger)

        if publish:
            return self.publish(deposition_id)

        return deposition

    def publish(self, deposition_id: int) -> Dict:
        """
        Publish an existing draft deposit to get a DOI.

        Returns the published deposition dict containing 'doi'.
        """
        url = f"{self.api_root}/deposit/depositions/{deposition_id}/actions/publish"
        r = requests.post(url, headers=self._headers(), timeout=30)
        if r.status_code != 202:
            raise RuntimeError(
                f"Zenodo publish failed: {r.status_code} {r.text}"
            )
        data = r.json()
        return data

    def publish_and_get_doi(self, ledger: ScientificLedger) -> str:
        """
        Deposit and publish in one step.

        Returns the DOI string (e.g. '10.5281/zenodo.XXXXXX').
        """
        result = self.deposit(ledger, publish=True)
        doi = result.get("doi")
        if not doi:
            raise RuntimeError(
                "Deposit published but no DOI returned from Zenodo."
            )
        return doi

    def get_deposition(self, deposition_id: int) -> Optional[Dict]:
        """Retrieve a deposit by its Zenodo deposition id."""
        url = f"{self.api_root}/deposit/depositions/{deposition_id}"
        r = requests.get(url, headers=self._headers(), timeout=30)
        if r.status_code == 200:
            return r.json()
        return None

    def _upload_ledger_file(self, deposition_id: int, ledger: ScientificLedger) -> Dict:
        """Upload the ledger JSON as a file to the deposit."""
        bucket_url = f"{self.api_root}/deposit/depositions/{deposition_id}/files"

        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(ledger.to_dict(), f, indent=2, default=str)
            tmp_path = f.name

        try:
            file_name = f"ledger-{ledger.ledger_id}.json"
            with open(tmp_path, "rb") as fh:
                r = requests.post(
                    bucket_url,
                    headers={"Authorization": f"Bearer {self.api_token}"},
                    data={"name": file_name},
                    files={"file": (file_name, fh, "application/json")},
                    timeout=60,
                )
            if r.status_code not in (201, 202):
                raise RuntimeError(
                    f"Zenodo file upload failed: {r.status_code} {r.text}"
                )
            return r.json()
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass