import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright
from django.contrib.auth import get_user_model
from projects.models import ProjectTemplate

User = get_user_model()

class ProjectE2ETests(StaticLiveServerTestCase):
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
        
        self.user = User.objects.create_user(username='demo@test.com', email='demo@test.com', password='password123')
        from accounts.models import UserProfile
        UserProfile.objects.create(user=self.user, full_name='Demo User')
        self.project = ProjectTemplate.objects.create(
            title="E2E Chatbot",
            description="Build a chatbot.",
            difficulty="beginner"
        )

    def tearDown(self):
        self.context.close()
        super().tearDown()

    def test_project_workflow(self):
        # Login
        self.page.goto(f"{self.live_server_url}/login/")
        self.page.fill('input[name="username"]', 'demo@test.com')
        self.page.fill('input[name="password"]', 'password123')
        self.page.click('button[type="submit"]')
        self.page.wait_for_url("**/dashboard/")
        
        # Navigate to Projects
        self.page.goto(f"{self.live_server_url}/projects/")
        self.page.wait_for_load_state("networkidle")
        
        # See the project and click it
        self.assertTrue(self.page.locator("text=E2E Chatbot").is_visible())
        self.page.click(f'a[href="/projects/{self.project.id}/"]')
        self.page.wait_for_url(f"**/projects/{self.project.id}/")
        
        # Start project
        self.page.click('button:has-text("Start Project")')
        self.page.wait_for_selector('text="Project in Progress"', timeout=10000)
        
        # Verify status is in progress
        self.assertTrue(self.page.locator("text=In Progress").first.is_visible())
        
        # Complete project
        
        # Handle JS confirm dialog for complete
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.click('button:has-text("Mark as Completed")')
        self.page.wait_for_selector('text="Project Completed!"', timeout=10000)
        
        # Verify status is completed
        self.assertTrue(self.page.locator('text="Project Completed!"').is_visible())
