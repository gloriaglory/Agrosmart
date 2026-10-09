import re

import httpx
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

def plain_text(answer):
    """Remove Markdown markers the model sometimes adds anyway (**bold**, # headings)."""
    answer = re.sub(r"(\*\*|__)(.+?)\1", r"\2", answer)
    answer = re.sub(r"^\s{0,3}#{1,6}\s*", "", answer, flags=re.M)
    return answer.strip()


# The chat window shows plain text, so ask for short answers without Markdown.
SYSTEM_PROMPT = (
    "You are AgroSmart's farming assistant, helping small-scale farmers in Tanzania. "
    "Answer in the same language as the question (Kiswahili or English). "
    "Be practical and concise: at most about 120 words. "
    "Use plain text only: no tables, no Markdown, no bold or headings. "
    "Short numbered steps are fine when giving instructions."
)


@api_view(['POST'])
@permission_classes([AllowAny])
def agro_bot(request):
    question = request.data.get('question')
    if not question:
        return Response({'error': 'Please provide a question'}, status=400)

    api_key = settings.GROQ_API_KEY
    if not api_key:
        return Response({'error': 'API key not configured'}, status=500)

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.CHAT_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        # gpt-oss models reason before answering; reasoning counts toward max_tokens
        "max_tokens": 1200,
        "temperature": 0.7,
        **({"reasoning_effort": "low"} if settings.CHAT_MODEL.startswith("openai/gpt-oss") else {}),
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            # OpenAI-compatible response format:
            answer = plain_text(data.get("choices", [{}])[0].get("message", {}).get("content") or "")

            if not answer:
                return Response({'error': 'No answer received from Groq API'}, status=500)

            return Response({'answer': answer})

    except httpx.HTTPStatusError as exc:
        return Response({'error': f'API returned status {exc.response.status_code}', 'details': exc.response.text}, status=exc.response.status_code)
    except Exception as e:
        return Response({'error': 'Failed to get answer from Groq API', 'details': str(e)}, status=500)
