"""
python/discovery/provenance_sidecar_engine.py - Tool Provenance Sidecar & Epistemic Honesty Engine (ADR-DISCOVERY-078)
Inspired by Google Cloud's Open Agentic Science Engine (OASE, 2026).

Enforces:
1. Provenance Sidecar Generation: Every tool invocation, calculation, or external query emits
   a companion `.sidecar.json` file logging execution parameters, git SHA, timing, output digest,
   and reproducible rerun commands.
2. Epistemic Honesty (Radical Anti-Hallucination): If an upstream tool, API, or dataset is missing,
   the engine emits a formal BLOCKED_MISSING_DATA status instead of permitting ungrounded speculation.
3. Verification & Auditing: Independent human or agentic reviewers can inspect and re-execute
   analyses from the sidecar specification to confirm reproducibility.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Callable
import hashlib
import json
import time
import os
import pathlib


class ToolExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED_MISSING_DATA = "BLOCKED_MISSING_DATA"
    UNVERIFIED = "UNVERIFIED"


@dataclass
class ProvenanceSidecar:
    """Metadata sidecar tracking the provenance, parameters, and verification hash of a tool output."""
    sidecar_id: str
    tool_name: str
    execution_timestamp: float
    git_commit_sha: str
    input_parameters: Dict[str, Any]
    input_hash: str
    raw_output_digest: str
    execution_time_seconds: float
    reproducibility_command: str
    status: ToolExecutionStatus
    blocking_reason: Optional[str] = None
    output_artifact_path: Optional[str] = None
    verification_hash: str = ""

    def __post_init__(self):
        if not self.verification_hash:
            self.verification_hash = self.compute_verification_hash()

    def compute_verification_hash(self) -> str:
        """Compute SHA256 integrity signature across all provenance attributes."""
        payload = {
            "sidecar_id": self.sidecar_id,
            "tool_name": self.tool_name,
            "timestamp": round(self.execution_timestamp, 3),
            "git_commit": self.git_commit_sha,
            "input_hash": self.input_hash,
            "output_digest": self.raw_output_digest,
            "status": self.status.value,
            "blocking_reason": self.blocking_reason
        }
        canonical = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    def save(self, filepath: str) -> None:
        """Serialize sidecar metadata to disk."""
        path = pathlib.Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> ProvenanceSidecar:
        """Load sidecar metadata from disk."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        status = ToolExecutionStatus(data.pop("status"))
        return cls(status=status, **data)


class ProvenanceSidecarEngine:
    """
    Engine for wrapping tool executions, writing companion provenance sidecars,
    and enforcing radical epistemic honesty when data is missing.
    """

    def __init__(self, current_git_sha: str = "HEAD_REVISION"):
        self.current_git_sha = current_git_sha

    @staticmethod
    def hash_payload(data: Any) -> str:
        """Compute SHA256 hash of arbitrary Python dictionary or primitive."""
        try:
            canonical = json.dumps(data, sort_keys=True).encode("utf-8")
        except (TypeError, ValueError):
            canonical = str(data).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def wrap_tool_execution(
        self,
        tool_name: str,
        tool_fn: Callable[..., Any],
        inputs: Dict[str, Any],
        output_sidecar_path: Optional[str] = None,
        reproducibility_cmd: Optional[str] = None,
        *args,
        **kwargs
    ) -> Tuple[Any, ProvenanceSidecar]:
        """
        Execute tool_fn with inputs, measure execution time, capture raw output digest,
        and generate a verified ProvenanceSidecar.
        """
        t0 = time.perf_counter()
        timestamp = time.time()
        input_h = self.hash_payload(inputs)
        sidecar_id = f"SIDECAR_{tool_name}_{input_h[:12]}_{int(timestamp)}"

        try:
            merged_kwargs = {**inputs, **kwargs}
            result = tool_fn(*args, **merged_kwargs)
            elapsed = time.perf_counter() - t0
            output_h = self.hash_payload(result if not hasattr(result, "to_dict") else result.to_dict())
            status = ToolExecutionStatus.SUCCESS
            blocking_reason = None
        except Exception as e:
            elapsed = time.perf_counter() - t0
            result = None
            output_h = self.hash_payload({"error": str(e)})
            status = ToolExecutionStatus.FAILED
            blocking_reason = f"Execution failed: {str(e)}"

        cmd = reproducibility_cmd or f"python -m discovery.tools.{tool_name} --config-hash {input_h[:12]}"

        sidecar = ProvenanceSidecar(
            sidecar_id=sidecar_id,
            tool_name=tool_name,
            execution_timestamp=timestamp,
            git_commit_sha=self.current_git_sha,
            input_parameters=inputs,
            input_hash=input_h,
            raw_output_digest=output_h,
            execution_time_seconds=elapsed,
            reproducibility_command=cmd,
            status=status,
            blocking_reason=blocking_reason,
            output_artifact_path=output_sidecar_path
        )

        if output_sidecar_path:
            sidecar.save(output_sidecar_path)

        return result, sidecar

    def record_blocked_missing_data(
        self,
        tool_name: str,
        missing_resource: str,
        inputs: Dict[str, Any],
        output_sidecar_path: Optional[str] = None
    ) -> ProvenanceSidecar:
        """
        Explicitly record that a tool execution is BLOCKED because upstream data or models
        are unavailable. Prohibits hallucination or unverified default assumptions.
        """
        timestamp = time.time()
        input_h = self.hash_payload(inputs)
        sidecar_id = f"SIDECAR_BLOCKED_{tool_name}_{input_h[:12]}_{int(timestamp)}"

        sidecar = ProvenanceSidecar(
            sidecar_id=sidecar_id,
            tool_name=tool_name,
            execution_timestamp=timestamp,
            git_commit_sha=self.current_git_sha,
            input_parameters=inputs,
            input_hash=input_h,
            raw_output_digest="NONE_BLOCKED_UNAVAILABLE",
            execution_time_seconds=0.0,
            reproducibility_command=f"# Tool '{tool_name}' blocked due to missing resource: {missing_resource}",
            status=ToolExecutionStatus.BLOCKED_MISSING_DATA,
            blocking_reason=f"Resource or dataset unavailable: {missing_resource}. Hallucination strictly prohibited.",
            output_artifact_path=output_sidecar_path
        )

        if output_sidecar_path:
            sidecar.save(output_sidecar_path)

        return sidecar

    def record_completed_execution(
        self,
        tool_name: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        execution_time_seconds: float = 0.05,
        reproducibility_cmd: Optional[str] = None,
        output_sidecar_path: Optional[str] = None
    ) -> ProvenanceSidecar:
        """
        Record a completed tool execution with its outputs and save sidecar to disk if requested.
        """
        timestamp = time.time()
        input_h = self.hash_payload(inputs)
        output_h = self.hash_payload(outputs)
        sidecar_id = f"SIDECAR_{tool_name}_{input_h[:12]}_{int(timestamp)}"
        cmd = reproducibility_cmd or f"python -m discovery.tools.{tool_name} --config-hash {input_h[:12]}"

        sidecar = ProvenanceSidecar(
            sidecar_id=sidecar_id,
            tool_name=tool_name,
            execution_timestamp=timestamp,
            git_commit_sha=self.current_git_sha,
            input_parameters=inputs,
            input_hash=input_h,
            raw_output_digest=output_h,
            execution_time_seconds=execution_time_seconds,
            reproducibility_command=cmd,
            status=ToolExecutionStatus.SUCCESS,
            blocking_reason=None,
            output_artifact_path=output_sidecar_path
        )

        if output_sidecar_path:
            sidecar.save(output_sidecar_path)

        return sidecar

    def verify_sidecar(
        self,
        sidecar: ProvenanceSidecar,
        tool_fn: Callable[..., Any]
    ) -> Tuple[bool, str]:
        """
        Re-run the tool execution using parameters recorded in the sidecar
        and verify that the output digest matches exactly.
        """
        if sidecar.status == ToolExecutionStatus.BLOCKED_MISSING_DATA:
            return False, f"Cannot re-run: Sidecar was marked BLOCKED due to: {sidecar.blocking_reason}"

        try:
            reproduced_result = tool_fn(**sidecar.input_parameters)
            reproduced_digest = self.hash_payload(
                reproduced_result if not hasattr(reproduced_result, "to_dict") else reproduced_result.to_dict()
            )

            if reproduced_digest == sidecar.raw_output_digest:
                return True, f"Sidecar reproducibility verified: output hash matches ({reproduced_digest[:16]})."
            else:
                return False, f"Reproducibility divergence: original {sidecar.raw_output_digest[:16]} != reproduced {reproduced_digest[:16]}."
        except Exception as e:
            return False, f"Re-execution crashed with error: {str(e)}"
