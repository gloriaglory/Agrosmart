import re

import httpx

OEMBED_URL = "https://www.youtube.com/oembed"

# watch?v=ID, youtu.be/ID, /embed/ID, /shorts/ID, /live/ID
_ID_PATTERNS = [
    re.compile(r"(?:youtube\.com/watch\?(?:.*&)?v=)([\w-]{11})"),
    re.compile(r"(?:youtu\.be/)([\w-]{11})"),
    re.compile(r"(?:youtube\.com/(?:embed|shorts|live)/)([\w-]{11})"),
]


def video_id(url):
    """The 11-character YouTube video id in a link, or None if it is not a YouTube video link."""
    for pattern in _ID_PATTERNS:
        match = pattern.search(url or "")
        if match:
            return match.group(1)
    return None


def canonical_url(vid):
    return f"https://www.youtube.com/watch?v={vid}"


def video_info(vid):
    """
    Title and channel of a public, embeddable video, or None if YouTube does not
    know it (deleted, private, or embedding disabled). Raises on network errors.
    """
    response = httpx.get(OEMBED_URL, params={"url": canonical_url(vid), "format": "json"}, timeout=10.0)
    if response.status_code in (400, 401, 403, 404):
        return None
    response.raise_for_status()
    data = response.json()
    return {"title": data.get("title", ""), "channel": data.get("author_name", "")}
