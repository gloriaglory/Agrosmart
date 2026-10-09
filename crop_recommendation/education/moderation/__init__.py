"""
Content moderation for education posts and comments.

Two layers:
  1. A blocked-words list (blocked_words.txt), always on.
  2. AI safety checks via Groq (needs GROQ_API_KEY in .env): text is classified
     against TEXT_POLICY by MODERATION_MODEL, thumbnails by IMAGE_MODERATION_MODEL.

`moderate(...)` returns one of:
  - Decision("allow")   both layers passed
  - Decision("block", reason)   content is not allowed
  - Decision("review", reason)  words passed but the AI check could not run;
                                 callers decide whether to hold it for an admin
"""
import base64
import io
import logging
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import httpx
from django.conf import settings
from PIL import Image

logger = logging.getLogger(__name__)

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
MAX_IMAGE_SIDE = 1024  # thumbnails are shrunk to this before checking (cheaper and faster)

# Policy the text safety model classifies against. Farming has words that sound
# violent or sexual out of context (killing pests, slaughter, breeding), so the
# policy spells out what is normal here.
TEXT_POLICY = """You are the content safety classifier for AgroSmart, a farming education and \
produce marketplace platform used in Tanzania. Content may be in English or Kiswahili.

UNSAFE content includes:
- sexual or pornographic content, nudity, or sexual services
- violence, threats, or encouraging harm against people
- hate speech or harassment targeting tribe, religion, race, nationality, gender or disability
- insults, profanity or bullying directed at people
- encouraging suicide or self-harm
- selling or promoting illegal drugs, weapons, or stolen goods
- scams, fraud, or requests for money or personal details under false pretences
- instructions for using chemicals, pesticides or poisons to harm people or animals on purpose

SAFE content includes normal farming topics, even when the words sound harsh out of context:
killing or controlling pests, weeds and diseases; slaughtering, castrating or culling livestock;
animal breeding and mating; legal use of pesticides and fertilisers; crop and animal diseases;
prices, markets, weather, and polite disagreement.

Reply with exactly one line: "safe", or "unsafe: <short category>"."""

IMAGE_POLICY = """Is this image appropriate for a family-friendly farming education website?
NOT appropriate: nudity or sexual content, graphic violence or gore against people, hate symbols,
weapons aimed at people, illegal drugs.
Appropriate: crops, farm animals (including normal slaughter or veterinary scenes), tools, machinery,
markets, landscapes, and people working.
Reply with exactly one line: "safe", or "unsafe: <short category>"."""


@dataclass
class Decision:
    action: str  # "allow", "block" or "review"
    reason: str = ""

    @property
    def blocked(self):
        return self.action == "block"


@lru_cache(maxsize=1)
def _blocked_patterns():
    path = Path(__file__).with_name("blocked_words.txt")
    words = [
        line.strip().lower()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    patterns = []
    for word in words:
        # Whole words only; a space in a phrase matches any whitespace
        body = r"\s+".join(re.escape(part) for part in word.split())
        patterns.append(re.compile(r"(?<!\w)" + body + r"(?!\w)", re.IGNORECASE))
    return patterns


def blocked_word(text):
    """Return the first blocked word found in the text, or None."""
    for pattern in _blocked_patterns():
        if pattern.search(text or ""):
            return pattern.pattern
    return None


def _parse_verdict(reply):
    """Read "safe" / "unsafe: category" from a model reply (ignoring any reasoning before it)."""
    text = re.sub(r"<think>.*?</think>", "", reply or "", flags=re.S).strip().lower()
    last = text.splitlines()[-1].strip().strip('"') if text else ""
    if last.startswith("unsafe"):
        # Keep the category short, e.g. "hate speech or harassment targeting tribe"
        category = last.split(":", 1)[1].split(",")[0].strip(" .") if ":" in last else ""
        return "unsafe", [category] if category else []
    if last.startswith("safe"):
        return "safe", []
    logger.warning("Unexpected moderation verdict: %r", reply)
    return "error", []


def _ask_groq(models, messages, max_tokens):
    """
    Send a chat request to Groq, trying each model in turn if one is rate-limited
    or unavailable. Returns the reply text, or None if every model failed.
    """
    api_key = getattr(settings, "GROQ_API_KEY", "")
    if not api_key:
        return None
    for model in [m for m in models if m]:
        body = {"model": model, "messages": messages, "temperature": 0, "max_tokens": max_tokens}
        if model.startswith("openai/gpt-oss"):
            body["reasoning_effort"] = "low"
        try:
            response = httpx.post(
                GROQ_CHAT_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json=body,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"].get("content") or ""
        except Exception as exc:
            detail = getattr(getattr(exc, "response", None), "text", "") or ""
            logger.warning("Moderation check failed (%s): %s %s", model, exc, detail[:200])
    return None


def _as_jpeg(data):
    """Convert any image Pillow can read to a JPEG no larger than MAX_IMAGE_SIDE."""
    with Image.open(io.BytesIO(data)) as img:
        img = img.convert("RGB")
        img.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=85)
        return out.getvalue()


def _check_text(text):
    reply = _ask_groq(
        [settings.MODERATION_MODEL, settings.MODERATION_FALLBACK_MODEL],
        [{"role": "system", "content": TEXT_POLICY}, {"role": "user", "content": text or "(empty)"}],
        max_tokens=800,
    )
    return ("error", []) if reply is None else _parse_verdict(reply)


def _check_image(image):
    data, _mime = image
    try:
        jpeg = _as_jpeg(data)
    except Exception as exc:
        logger.warning("Could not read image for moderation: %s", exc)
        return "error", []
    url = f"data:image/jpeg;base64,{base64.b64encode(jpeg).decode()}"
    reply = _ask_groq(
        [settings.IMAGE_MODERATION_MODEL],
        [{"role": "user", "content": [
            {"type": "text", "text": IMAGE_POLICY},
            {"type": "image_url", "image_url": {"url": url}},
        ]}],
        max_tokens=1500,
    )
    return ("error", []) if reply is None else _parse_verdict(reply)


def _ai_check(text, image=None):
    """
    Returns ("safe", []), ("unsafe", [categories]) or ("error", []) if a check could not run.
    Text and image are checked separately; any unsafe result wins.
    """
    results = [_check_text(text)]
    if image:
        results.append(_check_image(image))
    for status, categories in results:
        if status == "unsafe":
            return status, categories
    if any(status == "error" for status, _ in results):
        return "error", []
    return "safe", []


def moderate(text, image=None):
    """
    Check text (and optionally an image, given as (bytes, mime_type)).
    """
    if blocked_word(text):
        return Decision("block", "This contains language that is not allowed on AgroSmart.")

    status, categories = _ai_check(text, image)
    if status == "unsafe":
        detail = f" ({', '.join(categories)})" if categories else ""
        return Decision("block", f"This content was flagged as inappropriate{detail} and cannot be posted.")
    if status == "safe":
        return Decision("allow")
    return Decision("review", "Automatic safety check unavailable")
