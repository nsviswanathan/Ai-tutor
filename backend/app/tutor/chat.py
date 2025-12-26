from __future__ import annotations
import json, os, re
from typing import Any, Dict, List

import httpx
from .prompts import system_prompt

JSON_RE = re.compile(r"\{\s*\"skills\"\s*:\s*\[.*\]\s*\}\s*$", re.DOTALL)

def _extract_reply_and_skills(content: str) -> Dict[str, Any]:
    content = (content or "").strip()
    skills = []
    m = JSON_RE.search(content)
    if m:
        json_block = m.group(0)
        try:
            obj = json.loads(json_block)
            skills = obj.get("skills", [])
        except Exception:
            skills = []
        reply = content[: m.start()].rstrip()
    else:
        reply = content
    return {"reply": reply, "skills": skills}

async def _call_openai_compat(context: str, level: str, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").strip()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()

    if not api_key:
        return _fallback_local(message)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt(context, level)},
            *[{"role": m["role"], "content": m["content"]} for m in history],
            {"role": "user", "content": message},
        ],
        "temperature": 0.4,
    }

    headers = {"Authorization": f"Bearer {api_key}"}
    async with httpx.AsyncClient(base_url=base_url, timeout=40) as client:
        r = await client.post("/chat/completions", headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]

    return _extract_reply_and_skills(content)

async def _call_gemini(context: str, level: str, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

    if not api_key:
        return _fallback_local(message, hint="Set GEMINI_API_KEY in backend/.env to use Gemini.")

    # Lazy import so project can still run without Gemini installed (though requirements include it)
    from google import genai

    client = genai.Client(api_key=api_key)

    # Convert history into a compact transcript (reliable with Gemini)
    transcript = []
    for turn in history[-10:]:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        transcript.append(("User: " if role == "user" else "Tutor: ") + content)

    prompt = (
        system_prompt(context, level)
        + "\n\nConversation so far:\n"
        + "\n".join(transcript)
        + "\n\nUser: " + message
        + "\nTutor:"
    )

    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        config={"temperature": 0.4},
    )

    content = (resp.text or "").strip()
    return _extract_reply_and_skills(content)

def _fallback_local(message: str, hint: str | None = None) -> Dict[str, Any]:
    # Simple local response + naive skill tags (keeps adaptive engine working)
    skills = []
    low = message.lower()
    if "bag" in low or "overweight" in low:
        skills.append({"skill_id": "vocab:overweight_bag", "quality": 4})
    if "please" not in low:
        skills.append({"skill_id": "phrase:polite_request", "quality": 2})
    if not skills:
        skills.append({"skill_id": "phrase:basic_response", "quality": 3})

    reply = (
        ("(" + hint + ")\n\n" if hint else "")
        + "Let’s do this in a real situation.\n"
        + "Try: ‘Hi, I’m checking in for my flight. My bag might be overweight — what are my options?’\n"
        + "Now you: ask if you can move items to a carry-on."
    )
    return {"reply": reply, "skills": skills}

async def call_llm(context: str, level: str, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    """LLM router.
    Set LLM_PROVIDER=gemini to use Gemini (recommended).
    Or LLM_PROVIDER=openai_compat to use OpenAI-compatible endpoints.
    """
    provider = os.getenv("LLM_PROVIDER", "openai_compat").strip().lower()
    if provider == "gemini":
        return await _call_gemini(context, level, message, history)
    return await _call_openai_compat(context, level, message, history)
