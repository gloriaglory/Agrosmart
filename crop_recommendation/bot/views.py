import openai
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

openai.api_key = settings.OPENAI_API_KEY  

@api_view(['POST'])
@permission_classes([AllowAny])
def agro_bot(request):
    question = request.data.get('question')
    if not question:
        return Response({'error': 'Please provide a question'}, status=400)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert agriculture assistant helping small-scale farmers in Africa. Answer clearly and concisely."},
                {"role": "user", "content": question}
            ],
            max_tokens=200,
            temperature=0.7
        )

        answer = response['choices'][0]['message']['content']
        return Response({'answer': answer})

    except Exception as e:
        return Response({'error': 'Failed to get answer from OpenAI', 'details': str(e)}, status=500)
