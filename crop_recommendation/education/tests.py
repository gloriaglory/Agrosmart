from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Comment, Content

User = get_user_model()


class CommentTests(APITestCase):
    url = "/api/education/comments/"

    def setUp(self):
        self.asha = User.objects.create_user("asha", "a@example.com", "p", first_name="Asha", last_name="Juma")
        self.juma = User.objects.create_user("juma_k", "j@example.com", "p")
        self.post = Content.objects.create(title="Soil health", url_or_text="Text", status=Content.APPROVED)

    def comment(self, user, text, parent=None):
        self.client.force_authenticate(user)
        data = {"content": self.post.id, "text": text}
        if parent:
            data["parent"] = parent
        return self.client.post(self.url, data, format="json")

    def test_comment_records_author(self):
        res = self.comment(self.asha, "Great tips")
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["author"]["username"], "asha")
        self.assertEqual(res.data["author"]["name"], "Asha Juma")

    def test_anonymous_cannot_comment(self):
        res = self.client.post(self.url, {"content": self.post.id, "text": "hi"}, format="json")
        self.assertIn(res.status_code, (401, 403))

    def test_empty_comment_rejected(self):
        self.assertEqual(self.comment(self.asha, "   ").status_code, 400)

    def test_mentions_are_saved_case_insensitively(self):
        res = self.comment(self.asha, "Thanks @Juma_K and @nobody, email me at x@y.com")
        self.assertEqual(res.data["mentions"], ["juma_k"])

    def test_tagging_yourself_is_ignored(self):
        res = self.comment(self.asha, "@asha note to self")
        self.assertEqual(res.data["mentions"], [])

    def test_reply_to_reply_attaches_to_top_level(self):
        top = self.comment(self.asha, "Question").data["id"]
        reply = self.comment(self.juma, "@asha answer", parent=top).data["id"]
        res = self.comment(self.asha, "@juma_k thanks", parent=reply)
        self.assertEqual(res.data["parent"], top)

    def test_list_returns_top_level_with_replies(self):
        top = self.comment(self.asha, "Question").data["id"]
        self.comment(self.juma, "Answer", parent=top)
        self.client.force_authenticate(None)
        res = self.client.get(self.url, {"content": self.post.id})
        self.assertEqual(len(res.data), 1)
        self.assertEqual(len(res.data[0]["replies"]), 1)
        self.assertEqual(res.data[0]["replies"][0]["author"]["username"], "juma_k")

    def test_like_toggles(self):
        cid = self.comment(self.asha, "Like me").data["id"]
        self.client.force_authenticate(self.juma)
        first = self.client.post(f"{self.url}{cid}/like/")
        self.assertEqual(first.data, {"liked": True, "likes_count": 1})
        second = self.client.post(f"{self.url}{cid}/like/")
        self.assertEqual(second.data, {"liked": False, "likes_count": 0})

    def test_only_author_can_delete(self):
        cid = self.comment(self.asha, "Mine").data["id"]
        self.client.force_authenticate(self.juma)
        self.assertEqual(self.client.delete(f"{self.url}{cid}/").status_code, 403)
        self.client.force_authenticate(self.asha)
        self.assertEqual(self.client.delete(f"{self.url}{cid}/").status_code, 204)

    def test_content_shows_comment_count(self):
        top = self.comment(self.asha, "One").data["id"]
        self.comment(self.juma, "Two", parent=top)
        res = self.client.get("/api/education/contents/")
        self.assertEqual(res.data[0]["comments_count"], 2)


class UserSearchTests(APITestCase):
    url = "/api/auth/users/search/"

    def setUp(self):
        self.user = User.objects.create_user("asha", "a@example.com", "p", first_name="Asha")
        User.objects.create_user("ashura", "b@example.com", "p")
        User.objects.create_user("juma", "c@example.com", "p", first_name="Ashley")

    def test_requires_login(self):
        self.assertIn(self.client.get(self.url, {"q": "as"}).status_code, (401, 403))

    def test_matches_username_or_name_and_hides_private_fields(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(self.url, {"q": "@ash"})
        self.assertEqual([u["username"] for u in res.data], ["asha", "ashura", "juma"])
        self.assertNotIn("email", res.data[0])
        self.assertNotIn("id_number", res.data[0])


# --- Posts: ownership and moderation -------------------------------------------
from unittest import mock

from django.test import override_settings

from . import moderation


def guard_reply(verdict):
    """Fake Groq response carrying a safety verdict ("safe" or "unsafe: <category>")."""
    response = mock.Mock()
    response.raise_for_status = mock.Mock()
    response.json.return_value = {"choices": [{"message": {"content": verdict}}]}
    return mock.patch.object(moderation.httpx, "post", return_value=response)


class PostTests(APITestCase):
    url = "/api/education/contents/"

    def setUp(self):
        self.author = User.objects.create_user("author", "au@example.com", "p")
        self.other = User.objects.create_user("other", "ot@example.com", "p")
        self.admin = User.objects.create_user("admin", "ad@example.com", "p", is_staff=True)

    def create(self, user, **data):
        self.client.force_authenticate(user)
        payload = {"title": "Composting basics", "type": "article", "url_or_text": "Mix greens and browns."}
        payload.update(data)
        return self.client.post(self.url, payload, format="multipart")

    def test_records_author(self):
        res = self.create(self.author)
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["author"]["username"], "author")

    def test_only_author_or_admin_can_delete(self):
        post_id = self.create(self.author).data["id"]
        Content.objects.filter(id=post_id).update(status=Content.APPROVED)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.delete(f"{self.url}{post_id}/").status_code, 403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.delete(f"{self.url}{post_id}/").status_code, 204)

    def test_blocked_words_are_rejected(self):
        res = self.create(self.author, url_or_text="This is shit advice")
        self.assertEqual(res.status_code, 400)
        self.assertFalse(Content.objects.exists())

    def test_blocked_swahili_word(self):
        res = self.create(self.author, title="Habari malaya")
        self.assertEqual(res.status_code, 400)

    def test_harmless_words_containing_blocked_text_are_fine(self):
        # "Scunthorpe problem": whole words only
        res = self.create(self.author, url_or_text="Shiitake mushrooms grow on logs in Essex.")
        self.assertEqual(res.status_code, 201, res.data)

    def test_without_ai_check_post_waits_for_review(self):
        res = self.create(self.author)
        self.assertEqual(res.data["status"], "pending")
        self.assertIn("review", res.data["moderation_note"])
        # Hidden from others, visible to the author and admins
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(self.url).data, [])
        self.client.force_authenticate(self.author)
        self.assertEqual(len(self.client.get(self.url).data), 1)
        self.client.force_authenticate(self.admin)
        self.assertEqual(len(self.client.get(self.url).data), 1)

    def test_admin_posts_are_published(self):
        res = self.create(self.admin)
        self.assertEqual(res.data["status"], "approved")

    @override_settings(GROQ_API_KEY="test-key")
    def test_ai_safe_post_is_published(self):
        with guard_reply("safe"):
            res = self.create(self.author)
        self.assertEqual(res.data["status"], "approved")
        self.assertEqual(res.data["moderation_note"], "")

    @override_settings(GROQ_API_KEY="test-key")
    def test_ai_unsafe_post_is_rejected_with_reason(self):
        with guard_reply("unsafe: sexual content"):
            res = self.create(self.author)
        self.assertEqual(res.status_code, 400)
        self.assertIn("sexual content", str(res.data))
        self.assertFalse(Content.objects.exists())

    @override_settings(GROQ_API_KEY="test-key")
    def test_thumbnail_is_sent_to_ai_check(self):
        import io

        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        buffer = io.BytesIO()
        Image.new("RGB", (8, 8), "green").save(buffer, format="PNG")
        image = SimpleUploadedFile("t.png", buffer.getvalue(), content_type="image/png")
        with guard_reply("safe") as post:
            res = self.create(self.author, thumbnail=image)
        self.assertEqual(res.status_code, 201, res.data)
        content = post.call_args.kwargs["json"]["messages"][0]["content"]
        self.assertTrue(any(part["type"] == "image_url" for part in content))

    def test_youtube_link_is_checked_and_normalised(self):
        with mock.patch("education.youtube.video_info", return_value={"title": "Drip irrigation", "channel": "Farm TV"}):
            res = self.create(self.author, type="youtube", url_or_text="https://youtu.be/dQw4w9WgXcQ")
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["url_or_text"], "https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_youtube_video_title_is_moderated(self):
        with mock.patch("education.youtube.video_info", return_value={"title": "free porn here", "channel": "x"}):
            res = self.create(self.author, type="youtube", url_or_text="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(res.status_code, 400)

    def test_missing_or_private_video_rejected(self):
        with mock.patch("education.youtube.video_info", return_value=None):
            res = self.create(self.author, type="youtube", url_or_text="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(res.status_code, 400)
        self.assertIn("not found", str(res.data))

    def test_non_youtube_link_rejected(self):
        res = self.create(self.author, type="youtube", url_or_text="https://example.com/video")
        self.assertEqual(res.status_code, 400)

    def test_cannot_comment_on_pending_post(self):
        post_id = self.create(self.author).data["id"]
        self.client.force_authenticate(self.author)
        res = self.client.post("/api/education/comments/", {"content": post_id, "text": "hi"}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_offensive_comment_rejected(self):
        post = Content.objects.create(title="T", url_or_text="x", status=Content.APPROVED)
        self.client.force_authenticate(self.other)
        res = self.client.post("/api/education/comments/", {"content": post.id, "text": "you bitch"}, format="json")
        self.assertEqual(res.status_code, 400)


class ModerationFallbackTests(APITestCase):
    @override_settings(GROQ_API_KEY="test-key", MODERATION_MODEL="primary", MODERATION_FALLBACK_MODEL="backup")
    def test_falls_back_when_primary_is_rate_limited(self):
        import httpx

        limited = httpx.Response(429, request=httpx.Request("POST", moderation.GROQ_CHAT_URL), text="rate limit")
        ok = mock.Mock()
        ok.raise_for_status = mock.Mock()
        ok.json.return_value = {"choices": [{"message": {"content": "unsafe: violence"}}]}
        with mock.patch.object(moderation.httpx, "post", side_effect=[limited, ok]) as post:
            decision = moderation.moderate("some text")
        self.assertEqual([c.kwargs["json"]["model"] for c in post.call_args_list], ["primary", "backup"])
        self.assertTrue(decision.blocked)
        self.assertIn("violence", decision.reason)

    def test_reasoning_before_verdict_is_ignored(self):
        self.assertEqual(moderation._parse_verdict("<think>looks fine</think>\nsafe"), ("safe", []))
        self.assertEqual(moderation._parse_verdict("Analysis...\nunsafe: hate speech"), ("unsafe", ["hate speech"]))
