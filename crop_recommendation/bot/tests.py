from unittest import mock

from django.test import override_settings
from rest_framework.test import APITestCase

from .views import plain_text


class ChatbotTests(APITestCase):
    def test_markdown_is_removed(self):
        self.assertEqual(plain_text("## Tips\n1. **Plant** early\n__Water__ daily"), "Tips\n1. Plant early\nWater daily")

    @override_settings(GROQ_API_KEY="test-key", CHAT_MODEL="openai/gpt-oss-120b")
    def test_answers_with_configured_model(self):
        response = mock.Mock()
        response.raise_for_status = mock.Mock()
        response.json.return_value = {"choices": [{"message": {"content": "Plant beans in **March**."}}]}
        client = mock.MagicMock()
        client.__enter__.return_value.post.return_value = response
        with mock.patch("bot.views.httpx.Client", return_value=client):
            res = self.client.post("/api/bot/ask/", {"question": "When to plant beans?"}, format="json")
        self.assertEqual(res.data, {"answer": "Plant beans in March."})
        sent = client.__enter__.return_value.post.call_args.kwargs["json"]
        self.assertEqual(sent["model"], "openai/gpt-oss-120b")
        self.assertEqual(sent["reasoning_effort"], "low")

    def test_missing_key_is_reported(self):
        res = self.client.post("/api/bot/ask/", {"question": "hi"}, format="json")
        self.assertEqual(res.status_code, 500)
