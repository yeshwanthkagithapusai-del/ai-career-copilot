import json

from django.test import TestCase
from django.urls import reverse
from .models import User, UserProfile


class AccountsIntegrationTests(TestCase):
    def test_user_registration(self):
        response = self.client.post(reverse('accounts:signup'), {
            'full_name': 'New User',
            'email': 'newuser@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!'
        })
        self.assertEqual(response.status_code, 302) # Redirect to login or dashboard
        
        user = User.objects.get(email='newuser@example.com')
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('Password123!'))
        
    def test_user_login(self):
        user = User.objects.create_user(
            username='loginuser@example.com',
            email='loginuser@example.com',
            password='Password123!'
        )
        response = self.client.post(reverse('accounts:login'), {
            'username': 'loginuser@example.com',
            'password': 'Password123!'
        })
        self.assertRedirects(response, reverse('dashboard:dashboard'))
        
        # Test session contains user ID, meaning they are logged in
        self.assertIn('_auth_user_id', self.client.session)

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
