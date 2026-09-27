import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright
from django.contrib.auth import get_user_model
from careers.models import CareerRole

User = get_user_model()

class DashboardRoadmapE2ETests(StaticLiveServerTestCase):
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
        
        # Create user and role
        self.user = User.objects.create_user(username='demo@test.com', email='demo@test.com', password='password123')
        from accounts.models import UserProfile
        UserProfile.objects.create(user=self.user, full_name='Demo User')
        self.role = CareerRole.objects.create(name='Data Scientist', description='Data Role')

    def tearDown(self):
        self.context.close()
        super().tearDown()

    def test_dashboard_roadmap_flow(self):
        # Login
        self.page.goto(f"{self.live_server_url}/login/")
        self.page.fill('input[name="username"]', 'demo@test.com')
        self.page.fill('input[name="password"]', 'password123')
        self.page.click('button[type="submit"]')
        self.page.wait_for_url("**/dashboard/")
        
        # Expect empty state since no target role
        self.assertTrue(self.page.locator("text=No target role set").is_visible())
        
        # Click "Set Target Role"
        self.page.click('text="Set Target Role"')
        # Wait for guidance page
        self.page.wait_for_url("**/roadmaps/guidance/")
        
        # Go to profile to set career goal
        self.page.click('a[href="/profile/"]')
        self.page.wait_for_url("**/profile/")
        
        self.page.fill('input[name="career_goal"]', 'Data Scientist')
        self.page.click('button:has-text("Save Changes")')
        
        # Now go to roadmap
        self.page.goto(f"{self.live_server_url}/roadmaps/roadmap/")
        self.page.wait_for_load_state("networkidle")
        
        # Generate new roadmap
        self.page.fill('input[name="target_career"]', 'Data Scientist')
        self.page.click('button:has-text("Generate My Roadmap")')
        self.page.wait_for_url("**/roadmaps/roadmap/?id=*")
        
        # Verify roadmap is generated
        self.assertTrue(self.page.locator('text="PHASE COMPLETION"').is_visible())
        
        # Go back to dashboard to check NBA
        self.page.goto(f"{self.live_server_url}/dashboard/")
        self.page.wait_for_load_state("networkidle")
        
        # Verify Next Best Action is visible
        self.assertTrue(self.page.locator("text=Next Best Action").is_visible())
        
        # Now simulate user selecting a canonical role via backend (since UI isn't fully wired yet)
        from careers.models import UserCareerGoal
        UserCareerGoal.objects.create(user=self.user, target_role=self.role)
        
        # Reload dashboard
        self.page.reload()
        self.page.wait_for_load_state("networkidle")
        
        # Target role should now be set
        self.assertTrue(self.page.locator("text=Target Role: Data Scientist").is_visible())
