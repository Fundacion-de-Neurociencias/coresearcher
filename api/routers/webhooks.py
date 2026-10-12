"""Inbound webhooks (GitHub PR audit), authenticated by HMAC signature."""

from fastapi import APIRouter, Depends, HTTPException, Security  # noqa: F401

from api.schemas import (
    AuditPRWebhookRequest,
)
from api.security import verify_github_signature
from python.discovery.epistemic_pr_auditor import (
    FileDiffChunk,
    PullRequestDiffSnapshot,
    ScientificEpistemicPRAuditor,
)

router = APIRouter()


@router.post("/api/webhooks/github", dependencies=[Depends(verify_github_signature)])
# Legacy path kept so existing webhook configurations keep working.
@router.post(
    "/api/discovery/github/audit-pr-webhook",
    dependencies=[Depends(verify_github_signature)],
    include_in_schema=False,
)
def audit_pr_webhook(req: AuditPRWebhookRequest):
    try:
        auditor = ScientificEpistemicPRAuditor()
        diff_chunks = [
            FileDiffChunk(
                file_path=f.file_path, content=f.content, is_new_file=f.is_new_file, is_deleted_file=f.is_deleted_file
            )
            for f in req.files
        ]
        pr_snapshot = PullRequestDiffSnapshot(
            repo_name=req.repo_name,
            pull_request_number=req.pull_request_number,
            base_branch=req.base_branch,
            head_branch=req.head_branch,
            commit_sha=req.commit_sha,
            pr_title=req.pr_title,
            pr_description=req.pr_description,
            files=diff_chunks,
        )
        report = auditor.audit_pull_request(pr_snapshot)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
