import json
import os
from typing import Any, Dict, Optional

from django.conf import settings

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore


def _get_client() -> Optional["OpenAI"]:
    api_key = getattr(settings, "OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    if not api_key or OpenAI is None:
        return None
    base = getattr(settings, "OPENAI_BASE_URL", "") or os.getenv("OPENAI_BASE_URL", None)
    if base:
        return OpenAI(api_key=api_key, base_url=base)
    return OpenAI(api_key=api_key)


def _json_response(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        # 尝试截取花括号包裹的 JSON
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                pass
        raise


def llm_json(prompt: str, schema_hint: str) -> Optional[Dict[str, Any]]:
    """
    调用 LLM，期望返回 JSON；失败返回 None。
    """
    client = _get_client()
    if client is None:
        return None
    model = getattr(settings, "OPENAI_MODEL", "gpt-4o")
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严格返回JSON的助手。仅输出有效的JSON对象，不要输出多余文本。",
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\n务必严格输出JSON。JSON结构示例：\n{schema_hint}",
                },
            ],
            temperature=0.6,
            response_format={"type": "json_object"},
        )
        text = resp.choices[0].message.content or "{}"
        return _json_response(text)
    except Exception:
        return None


