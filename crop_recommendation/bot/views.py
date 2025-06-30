import httpx
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

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
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": "You are an expert agriculture assistant helping small-scale farmers in Africa. Answer clearly and concisely."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            # OpenAI-compatible response format:
            answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not answer:
                return Response({'error': 'No answer received from Groq API'}, status=500)

            return Response({'answer': answer})

    except httpx.HTTPStatusError as exc:
        return Response({'error': f'API returned status {exc.response.status_code}', 'details': exc.response.text}, status=exc.response.status_code)
    except Exception as e:
        return Response({'error': 'Failed to get answer from Groq API', 'details': str(e)}, status=500)
