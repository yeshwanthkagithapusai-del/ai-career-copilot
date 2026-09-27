from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ChatEndpointTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='chatuser',
            email='chat@example.com',
            password='TestPass123!',
            full_name='Chat User',
        )

    def test_chat_endpoint_accepts_json_payload(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('ai_services:chat'),
            data='{"message": "Help me with my resume"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.json())
