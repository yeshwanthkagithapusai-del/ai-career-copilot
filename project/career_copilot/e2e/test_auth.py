import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright
from django.contrib.auth import get_user_model

User = get_user_model()

class PlaywrightTestCase(StaticLiveServerTestCase):
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
        
    def tearDown(self):
        self.context.close()
        super().tearDown()

class AuthE2ETests(PlaywrightTestCase):
    def test_user_registration_and_login_flow(self):
        # Go to landing page
        self.page.goto(self.live_server_url)
        self.page.wait_for_load_state("networkidle")
        
        # Click login/signup
        # Assuming landing page has a signup link
        self.page.goto(f"{self.live_server_url}/signup/")
        
        # Fill signup form
        self.page.fill('input[name="full_name"]', 'E2E User')
        self.page.fill('input[name="email"]', 'e2e@example.com')
        self.page.fill('input[name="password1"]', 'Password123!')
        self.page.fill('input[name="password2"]', 'Password123!')
        
        # Submit
        self.page.click('button[type="submit"]')
        
        # Should redirect to dashboard and show welcome message
        self.page.wait_for_url("**/dashboard/")
        self.assertTrue(self.page.locator("text=Welcome to AI Career Copilot").is_visible() or 
                        self.page.locator("text=Dashboard").is_visible())
        
        # Logout
        # Find logout link
        self.page.goto(f"{self.live_server_url}/logout/")
        self.page.click('button[type="submit"]') # Confirm logout
        self.page.wait_for_url("**/")
        
        # Now try to log in
        self.page.goto(f"{self.live_server_url}/login/")
        self.page.fill('input[name="username"]', 'e2e@example.com')
        self.page.fill('input[name="password"]', 'Password123!')
        self.page.click('button[type="submit"]')
        
        # Should redirect to dashboard
        self.page.wait_for_url("**/dashboard/")
        self.assertTrue(self.page.locator("text=Dashboard").is_visible())
