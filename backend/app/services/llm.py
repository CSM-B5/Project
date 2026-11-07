"""Chat / report generation.

LLM_PROVIDER=mock       -> rule-based reply built from the analysis (no key needed)
LLM_PROVIDER=anthropic  -> Claude via the Anthropic Messages API
"""
import httpx
from fastapi import HTTPException

from app.config import get_settings
from app.schemas import AnalysisResponse, ChatTurn

SYSTEM_PROMPT = (
    "You are a clinical-imaging assistant inside a radiology research prototype. "
    "You help a clinician interpret AI model outputs for a medical scan and draft "
    "report text. Base statements only on the provided findings; if something is "
    "not in the findings, say so. Be concise and professional. Always note that "
    "outputs are model-generated and require clinician verification."
)


def findings_text(case: AnalysisResponse | None) -> str:
    if case is None:
        return "No scan has been analysed in this session yet."
    c, s = case.classification, case.segmentation
    return (
        f"Case {case.caseId} ({case.patientInfo.scanType}). "
        f"Primary finding: {c.primaryLabel} ({c.confidenceScore}% confidence) in the "
        f"{c.anatomicalTarget}. Secondary: {c.secondaryLabel} ({c.secondaryScore}%). "
        f"Segmentation detected {s.detectedRegionsCount} region(s)."
    )


def initial_summary(case: AnalysisResponse) -> str:
    c, s = case.classification, case.segmentation
    return (
        f"Multimodal analysis suggests findings most consistent with {c.primaryLabel} "
        f"({c.confidenceScore}% model confidence) involving the {c.anatomicalTarget}; "
        f"{s.detectedRegionsCount} candidate region(s) were segmented. "
        "Recommend clinical correlation and radiologist review."
    )


def _mock_reply(message: str, case: AnalysisResponse | None) -> str:
    if case is None:
        return "Please upload a patient scan first so I can discuss its findings."
    c = case.classification
    m = message.lower()
    if "report" in m or "draft" in m:
        return (
            f"DRAFT REPORT — {case.caseId}\n"
            f"Technique: {case.patientInfo.scanType}.\n"
            f"Findings: AI analysis indicates {c.primaryLabel} in the {c.anatomicalTarget} "
            f"(confidence {c.confidenceScore}%). {case.segmentation.detectedRegionsCount} "
            "region(s) flagged by segmentation.\n"
            f"Impression: Findings suggestive of {c.primaryLabel}; clinical correlation advised.\n"
            "Note: model-generated draft, requires clinician verification."
        )
    if "confiden" in m or "sure" in m:
        return (
            f"The model assigns {c.confidenceScore}% to {c.primaryLabel} versus "
            f"{c.secondaryScore}% to {c.secondaryLabel}. Treat as decision support only."
        )
    return findings_text(case) + " Ask me to draft a report or explain any finding."


async def generate_reply(
    message: str, case: AnalysisResponse | None, history: list[ChatTurn]
) -> str:
    s = get_settings()
    if s.llm_provider == "mock":
        return _mock_reply(message, case)

    if s.llm_provider == "anthropic":
        if not s.anthropic_api_key:
            raise HTTPException(500, "ANTHROPIC_API_KEY is not configured.")
        msgs = [
            {"role": "user" if t.sender == "user" else "assistant", "content": t.text}
            for t in history
            if t.text.strip()
        ]
        # API requires the conversation to start with a user turn
        while msgs and msgs[0]["role"] != "user":
            msgs.pop(0)
        msgs.append({"role": "user", "content": message})
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": s.anthropic_api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": s.anthropic_model,
                        "max_tokens": 1000,
                        "system": f"{SYSTEM_PROMPT}\n\nCurrent findings:\n{findings_text(case)}",
                        "messages": msgs,
                    },
                )
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(502, f"LLM provider error: {e.__class__.__name__}")
        return "".join(b.get("text", "") for b in r.json().get("content", []))

    raise HTTPException(500, f"Unknown LLM_PROVIDER '{s.llm_provider}'.")
