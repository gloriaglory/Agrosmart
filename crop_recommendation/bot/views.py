import json
import re

import httpx
from django.conf import settings
from django.http import StreamingHttpResponse
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


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def groq_request(question, stream=False):
    """Headers and body for a Groq chat completion."""
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
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
        **({"stream": True} if stream else {}),
    }
    return headers, payload


@api_view(['POST'])
@permission_classes([AllowAny])
def agro_bot(request):
    question = request.data.get('question')
    if not question:
        return Response({'error': 'Please provide a question'}, status=400)

    if not settings.GROQ_API_KEY:
        return Response({'error': 'API key not configured'}, status=500)

    headers, payload = groq_request(question)

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(GROQ_URL, headers=headers, json=payload)
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


def answer_chunks(lines):
    """
    Answer text from Groq's streamed lines ("data: {...}"). Reasoning arrives in a
    separate field and is skipped; only the answer is passed on.
    """
    for line in lines:
        if not line.startswith("data: "):
            continue
        data = line[len("data: "):].strip()
        if data == "[DONE]":
            return
        try:
            delta = json.loads(data)["choices"][0]["delta"]
        except (ValueError, KeyError, IndexError):
            continue
        if delta.get("content"):
            yield delta["content"]


@api_view(['POST'])
@permission_classes([AllowAny])
def agro_bot_stream(request):
    """
    Same as agro_bot, but sends the answer as plain text while it is being written,
    so the chat window can show it appearing word by word. The chat window removes
    Markdown markers as it displays the text.
    """
    question = request.data.get('question')
    if not question:
        return Response({'error': 'Please provide a question'}, status=400)
    if not settings.GROQ_API_KEY:
        return Response({'error': 'API key not configured'}, status=500)

    headers, payload = groq_request(question, stream=True)
    client = httpx.Client(timeout=httpx.Timeout(15.0, read=60.0))
    try:
        upstream = client.send(client.build_request("POST", GROQ_URL, headers=headers, json=payload), stream=True)
    except Exception as e:
        client.close()
        return Response({'error': 'Failed to get answer from Groq API', 'details': str(e)}, status=502)
    if upstream.status_code != 200:
        details = upstream.read().decode(errors="replace")
        upstream.close()
        client.close()
        return Response({'error': f'API returned status {upstream.status_code}', 'details': details},
                        status=upstream.status_code)

    def relay():
        try:
            yield from answer_chunks(upstream.iter_lines())
        except Exception as e:
            print(f"Chat stream interrupted: {e}")
        finally:
            upstream.close()
            client.close()

    response = StreamingHttpResponse(relay(), content_type="text/plain; charset=utf-8")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # stop proxies such as nginx from holding the stream back
    return response
