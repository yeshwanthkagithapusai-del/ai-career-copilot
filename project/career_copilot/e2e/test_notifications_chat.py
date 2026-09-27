import os
from unittest.mock import patch
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright
from django.contrib.auth import get_user_model
from accounts.models import Notification

User = get_user_model()

class NotificationsChatE2ETests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        
        # Capture console output for debugging
        self.page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
        
        self.user = User.objects.create_user(username='demo@test.com', email='demo@test.com', password='password123')
        from accounts.models import UserProfile
        UserProfile.objects.create(user=self.user, full_name='Demo User')
        
        # Create a notification
        Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification.',
            notification_type='info'
        )

    def tearDown(self):
        self.context.close()
        super().tearDown()

    def test_notifications_flow(self):
        self.page.goto(f"{self.live_server_url}/login/")
        self.page.fill('input[name="username"]', 'demo@test.com')
        self.page.fill('input[name="password"]', 'password123')
        self.page.click('button[type="submit"]')
        
        self.page.wait_for_url("**/dashboard/")
        
        # Check bell badge has '1' unread
        self.assertTrue(self.page.locator('#notificationBadge').is_visible())
        
        # Click the bell
        self.page.click('#notificationDropdown')
        
        # Check notification content
        self.assertTrue(self.page.locator("text=Test Notification").first.is_visible())
        
        # Mark as read
        self.page.click('text="Mark all read"')
        
        # Wait for ajax to complete (badge should hide or be 0)
        # Using a brief timeout or waiting for badge to be hidden
        self.page.wait_for_selector('#notificationBadge', state='hidden', timeout=3000)
        self.assertFalse(self.page.locator('#notificationBadge').is_visible())

    def test_chat_interaction(self):
        self.page.goto(f"{self.live_server_url}/login/")
        self.page.fill('input[name="username"]', 'demo@test.com')
        self.page.fill('input[name="password"]', 'password123')
        self.page.click('button[type="submit"]')
        self.page.wait_for_url("**/dashboard/")
        
        # Toggle chat
        self.page.click('#chatbot-toggle')
        self.assertTrue(self.page.locator('#chatbot-panel').is_visible())
        
        # Send message
        self.page.fill('#chatbot-input', 'Hello AI')
        # Wait for bot response by waiting for the network request
        with self.page.expect_response("**/api/ai/chat/", timeout=10000) as response_info:
            self.page.click('#chatbot-send')
            
        self.assertTrue(response_info.value.ok)
        self.page.wait_for_function('document.querySelectorAll(".chat-message.bot:not(#typing-indicator)").length > 1', timeout=10000)
        bot_messages = self.page.locator('.chat-message.bot:not(#typing-indicator)').all()
        self.assertGreater(len(bot_messages), 1) # Should have initial message + new message
