import json
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from .models import ChatFeedback, ChatMessage, ChatSession, CollegeKnowledge
from .utils import build_knowledge_base, get_ai_response, get_conversation_history


class ChatApiTests(TestCase):
    def setUp(self):
        self.chat_url = reverse("chatbot:chat")
        self.feedback_url = reverse("chatbot:feedback")
        self.history_url = reverse("chatbot:history")
        self.clear_url = reverse("chatbot:clear")
        self.session = ChatSession.objects.create(session_id="session-1")

    def test_chat_api_returns_400_for_empty_message(self):
        response = self.client.post(
            self.chat_url,
            data=json.dumps({"message": "   "}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Message cannot be empty")

    def test_chat_api_returns_400_for_invalid_json(self):
        response = self.client.post(self.chat_url, data="{invalid", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid JSON")

    @patch("chatbot.views.get_ai_response")
    @patch("chatbot.views.get_conversation_history")
    @patch("chatbot.views.get_or_create_session")
    def test_chat_api_saves_user_and_bot_messages(self, mock_get_session, mock_history, mock_ai):
        mock_get_session.return_value = self.session
        mock_history.return_value = []
        mock_ai.return_value = {"response": "Hello!", "success": True}

        response = self.client.post(
            self.chat_url,
            data=json.dumps({"message": "Hi"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["response"], "Hello!")
        self.assertEqual(ChatMessage.objects.filter(session=self.session).count(), 2)

    def test_feedback_api_requires_message_id_and_rating(self):
        response = self.client.post(
            self.feedback_url,
            data=json.dumps({"message_id": 1}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("required", response.json()["error"])

    def test_feedback_api_returns_404_when_message_not_found(self):
        response = self.client.post(
            self.feedback_url,
            data=json.dumps({"message_id": 999, "rating": 2}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_feedback_api_creates_or_updates_feedback(self):
        msg = ChatMessage.objects.create(session=self.session, sender="bot", message="Answer")
        response = self.client.post(
            self.feedback_url,
            data=json.dumps({"message_id": msg.id, "rating": 3, "comment": "Good"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ChatFeedback.objects.filter(message=msg, rating=3).exists())

    def test_chat_history_api_returns_messages(self):
        ChatMessage.objects.create(session=self.session, sender="user", message="Hello")
        ChatMessage.objects.create(session=self.session, sender="bot", message="Hi there")

        session_obj = self.client.session
        session_obj["chatbot_session_id"] = self.session.session_id
        session_obj.save()

        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["history"]), 2)

    def test_clear_chat_api_removes_session_key(self):
        session_obj = self.client.session
        session_obj["chatbot_session_id"] = self.session.session_id
        session_obj.save()

        response = self.client.post(self.clear_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("chatbot_session_id", self.client.session)


class ChatbotUtilsTests(TestCase):
    def test_build_knowledge_base_returns_fallback_when_empty(self):
        self.assertIn("No specific college knowledge", build_knowledge_base())

    def test_build_knowledge_base_groups_entries_by_category(self):
        CollegeKnowledge.objects.create(
            category="fees",
            topic="CSE Fees",
            information="INR 50000 per year",
            is_active=True,
        )
        CollegeKnowledge.objects.create(
            category="fees",
            topic="Hostel Fees",
            information="INR 20000 per year",
            is_active=True,
        )
        text = build_knowledge_base()
        self.assertIn("=== FEE STRUCTURE ===", text)
        self.assertIn("• CSE Fees", text)
        self.assertIn("• Hostel Fees", text)

    def test_get_conversation_history_returns_last_10_in_chronological_order(self):
        session = ChatSession.objects.create(session_id="history-session")
        for i in range(12):
            ChatMessage.objects.create(session=session, sender="user", message=f"msg-{i}")

        history = get_conversation_history(session)
        self.assertEqual(len(history), 10)
        self.assertEqual(history[0]["message"], "msg-2")
        self.assertEqual(history[-1]["message"], "msg-11")

    @patch("chatbot.utils.model.start_chat")
    @patch("chatbot.utils.build_system_prompt")
    def test_get_ai_response_handles_api_key_errors(self, mock_prompt, mock_start_chat):
        mock_prompt.return_value = "prompt"
        mock_start_chat.side_effect = Exception("API_KEY missing")

        result = get_ai_response("hello")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Invalid API Key")

    @patch("chatbot.utils.model.start_chat")
    @patch("chatbot.utils.build_system_prompt")
    def test_get_ai_response_handles_quota_errors(self, mock_prompt, mock_start_chat):
        mock_prompt.return_value = "prompt"
        mock_start_chat.side_effect = Exception("quota exceeded")

        result = get_ai_response("hello")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Rate limit exceeded")

    @patch("chatbot.utils.model.start_chat")
    @patch("chatbot.utils.build_system_prompt")
    def test_get_ai_response_returns_success_payload(self, mock_prompt, mock_start_chat):
        mock_prompt.return_value = "prompt"
        mock_chat = Mock()
        mock_chat.send_message.return_value = Mock(text="Admissions are open.")
        mock_start_chat.return_value = mock_chat

        result = get_ai_response("Is admission open?")
        self.assertTrue(result["success"])
        self.assertEqual(result["response"], "Admissions are open.")
