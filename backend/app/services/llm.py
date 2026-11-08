"""Report drafting and chat.

LLM_PROVIDER=mock       -> rule-based text built from the findings (no key needed)
LLM_PROVIDER=anthropic  -> Claude via the Anthropic Messages API (chat only)
"""
import httpx
from fastapi import HTTPException

from app.config import get_settings
from app.models import Study
from app.schemas import ChatTurn
from app.services.classifier import NO_TUMOR

SYSTEM_PROMPT = (
    "You are a clinical-imaging assistant inside a brain-MRI research prototype. "
    "You help clinicians interpret AI model outputs and draft report text. Base "
    "statements only on the provided findings; if something is not in the findings, "
    "say so. Be concise and professional. Always note that outputs are "
    "model-generated and require clinician verification."
)


def findings_text(study: Study | None) -> str:
    if study is None:
        return "No scan has been selected in this conversation."
    probs = ", ".join(f"{k} {v}%" for k, v in sorted(study.probabilities.items(), key=lambda kv: -kv[1]))
    return (
        f"Brain MRI study #{study.id}. Predicted class: {study.predicted_class} "
        f"(probabilities: {probs}). Segmentation: {study.seg_status}, "
        f"{study.seg_regions} region(s), tumour area {study.tumor_area_percent}% of the slice."
    )


def draft_report(predicted_class: str, probabilities: dict[str, float], regions: int, area: float | None) -> str:
    p = probabilities.get(predicted_class, 0)
    if predicted_class == NO_TUMOR:
        return (
            f"AI-assisted draft: the model finds no features of a brain tumour in this MRI "
            f"slice (No Tumor, {p}% probability). No tumour region was segmented. "
            "This draft requires review and approval by the responsible doctor."
        )
    return (
        f"AI-assisted draft: the model suggests findings most consistent with {predicted_class} "
        f"({p}% probability). Segmentation outlined {regions} candidate region(s) covering about "
        f"{area}% of the slice. Clinical correlation and specialist review are recommended. "
        "This draft requires review and approval by the responsible doctor."
    )


def _mock_reply(message: str, study: Study | None) -> str:
    if study is None:
        return "Please select or upload a scan first so I can discuss its findings."
    m = message.lower()
    if "report" in m or "draft" in m:
        return f"DRAFT REPORT\n{study.report_summary}\nNote: model-generated, requires clinician verification."
    if "confiden" in m or "sure" in m or "probab" in m:
        return findings_text(study) + " Treat these numbers as decision support only."
    return findings_text(study) + " Ask me to draft a report or explain any finding."


async def generate_reply(message: str, study: Study | None, history: list[ChatTurn]) -> str:
    s = get_settings()
    if s.llm_provider == "mock":
        return _mock_reply(message, study)

    if s.llm_provider == "anthropic":
        if not s.anthropic_api_key:
            raise HTTPException(500, "ANTHROPIC_API_KEY is not configured.")
        msgs = [
            {"role": "user" if t.sender == "user" else "assistant", "content": t.text}
            for t in history
            if t.text.strip()
        ]
        while msgs and msgs[0]["role"] != "user":  # API needs a user turn first
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
                        "system": f"{SYSTEM_PROMPT}\n\nCurrent findings:\n{findings_text(study)}",
                        "messages": msgs,
                    },
                )
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(502, f"LLM provider error: {e.__class__.__name__}")
        return "".join(b.get("text", "") for b in r.json().get("content", []))

    raise HTTPException(500, f"Unknown LLM_PROVIDER '{s.llm_provider}'.")
