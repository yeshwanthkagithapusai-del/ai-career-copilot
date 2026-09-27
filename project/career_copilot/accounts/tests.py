import json

from django.test import TestCase
from django.urls import reverse
from .models import User, UserProfile


class ProfileAccountLinksTests(TestCase):
    def test_profile_page_shows_account_actions(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            full_name='Test User',
        )
        UserProfile.objects.create(user=user, full_name='Test User')

        self.client.login(username='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('accounts:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Account Actions')
        self.assertContains(response, 'Settings')
        self.assertContains(response, 'My Progress')
        self.assertContains(response, 'Logout')

    def test_logout_redirects_to_landing_page(self):
        user = User.objects.create_user(
            username='logoutuser',
            email='logout@example.com',
            password='TestPass123!',
            full_name='Logout User',
        )
        UserProfile.objects.create(user=user, full_name='Logout User')

        self.client.force_login(user)
        response = self.client.post(reverse('accounts:logout'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:landing'))


class PreviewFallbackTests(TestCase):
    def test_malformed_preview_path_redirects_to_landing_page(self):
        response = self.client.get('/%E2%80%9D')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:landing'))
