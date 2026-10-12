from unittest import mock

from django.test import override_settings
from rest_framework.test import APITestCase

from .views import answer_chunks, plain_text


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


STREAM_LINES = [
    'data: {"choices":[{"delta":{"role":"assistant","content":""}}]}',
    'data: {"choices":[{"delta":{"reasoning":"Think about beans"}}]}',
    "",
    'data: {"choices":[{"delta":{"content":"Plant beans "}}]}',
    'data: {"choices":[{"delta":{"content":"in March."}}]}',
    "data: [DONE]",
]


class ChatbotStreamTests(APITestCase):
    def test_only_answer_text_is_passed_on(self):
        self.assertEqual("".join(answer_chunks(STREAM_LINES)), "Plant beans in March.")

    def fake_client(self, status=200, lines=STREAM_LINES):
        upstream = mock.Mock(status_code=status)
        upstream.iter_lines.return_value = iter(lines)
        upstream.read.return_value = b'{"error": "rate limited"}'
        client = mock.Mock()
        client.send.return_value = upstream
        return client, upstream

    @override_settings(GROQ_API_KEY="test-key", CHAT_MODEL="openai/gpt-oss-120b")
    def test_streams_the_answer(self):
        client, upstream = self.fake_client()
        with mock.patch("bot.views.httpx.Client", return_value=client):
            res = self.client.post("/api/bot/ask/stream/", {"question": "When to plant beans?"}, format="json")
            self.assertEqual(res.status_code, 200)
            self.assertTrue(res.streaming)
            self.assertEqual(b"".join(res.streaming_content).decode(), "Plant beans in March.")
        sent = client.build_request.call_args.kwargs["json"]
        self.assertTrue(sent["stream"])
        upstream.close.assert_called()
        client.close.assert_called()

    @override_settings(GROQ_API_KEY="test-key")
    def test_upstream_error_is_reported(self):
        client, _ = self.fake_client(status=429)
        with mock.patch("bot.views.httpx.Client", return_value=client):
            res = self.client.post("/api/bot/ask/stream/", {"question": "hi"}, format="json")
        self.assertEqual(res.status_code, 429)
        client.close.assert_called()

    def test_stream_needs_a_question(self):
        self.assertEqual(self.client.post("/api/bot/ask/stream/", {}, format="json").status_code, 400)
