import json
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse


class ChatEndpointTests(TestCase):
    def setUp(self):
        self.url = reverse("chatbot:chat")

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_empty_message_rejected(self):
        response = self.client.post(
            self.url, data=json.dumps({"message": "  "}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_json_rejected(self):
        response = self.client.post(
            self.url, data="not json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    @override_settings(AI_API_KEY="")
    def test_missing_key_returns_503(self):
        response = self.client.post(
            self.url, data=json.dumps({"message": "hello"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)

    @override_settings(AI_API_KEY="test-key")
    @patch("chatbot.views.call_ai_model", return_value="Hi there!")
    def test_successful_reply(self, mock_call):
        response = self.client.post(
            self.url, data=json.dumps({"message": "hello"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reply"], "Hi there!")
        mock_call.assert_called_once_with("hello")
