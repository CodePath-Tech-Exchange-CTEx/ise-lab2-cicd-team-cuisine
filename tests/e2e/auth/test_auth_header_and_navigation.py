import uuid

from playwright.sync_api import sync_playwright

from ..common import BASE_URL, login


def test_login_page_title_includes_home_and_auth_controls():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")

        page.get_by_text("AirBets").wait_for(timeout=30000)
        page.locator('button:has-text("👤 Account")').first.wait_for(timeout=30000)
        page.get_by_text("Log in / Sign up").wait_for(timeout=30000)
        page.get_by_text("Welcome back").wait_for(timeout=30000)

        assert page.get_by_text("AirBets").is_visible()
        assert page.locator('button:has-text("👤 Account")').first.is_visible()
        assert page.get_by_text("Log in / Sign up").is_visible()
        assert page.get_by_text("Welcome back").is_visible()
        assert page.get_by_text("Please log in or sign up").count() == 0

        browser.close()


def test_signup_flow_in_top_right_header():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        page.locator('button:has-text("👤 Account")').first.click()
        page.get_by_text("Log in / Sign up").wait_for(timeout=15000)
        page.locator('label:has-text("Sign up")').first.click()
        page.wait_for_timeout(500)
        page.get_by_label("Username").wait_for(timeout=15000)

        unique_username = f"e2e_signup_{uuid.uuid4().hex[:8]}"
        page.get_by_label("Username").fill(unique_username)
        page.get_by_label("Full name").fill("E2E Top Right")
        page.get_by_label("Date of birth (YYYY-MM-DD)").fill("1990-05-15")
        create_button = page.get_by_role("button", name="Create account")
        create_button.wait_for(timeout=15000)
        create_button.click()

        page.wait_for_timeout(5000)
        page.get_by_text("Friends list").wait_for(timeout=15000)
        assert page.get_by_text("Friends list").is_visible()

        browser.close()


def test_sidebar_navigation_labels_after_login():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)

        assert page.locator('a:has-text("Available bets")').first.is_visible()
        assert page.locator('a:has-text("AI Advice")').first.is_visible()
        assert page.locator('a:has-text("Friends Activity")').first.is_visible()
        assert page.locator('a:has-text("Profile")').first.is_visible()

        page.locator('a:has-text("Available bets")').first.click()
        page.get_by_text('Available bets').wait_for(timeout=15000)

        browser.close()


def test_login_and_navigation_journey():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)

        page.locator('a:has-text("AI Advice")').first.click()
        page.locator('div.bubble-sender', has_text='AI Advisor').wait_for(timeout=15000)

        page.locator('a:has-text("Friends Activity")').first.click()
        page.get_by_text('Friends activity for').wait_for(timeout=15000)

        page.locator('a:has-text("Profile")').first.click()
        page.get_by_text('Friends list').wait_for(timeout=15000)

        page.locator('a:has-text("Available bets")').first.click()
        page.get_by_text('Available bets').wait_for(timeout=15000)

        browser.close()


def test_profile_page_back_to_dashboard_navigation():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)
        page.locator('a:has-text("Profile")').first.click()

        profile_heading = page.get_by_text("Profile & Trade Summary")
        profile_heading.wait_for(timeout=15000)
        assert profile_heading.is_visible()
        assert page.get_by_text("Friends list").is_visible()
        back_button = page.locator('button:has-text("← Back to Dashboard")').first
        assert back_button.is_visible()

        back_button.click()
        page.get_by_text('Available bets').wait_for(timeout=15000)
        assert page.get_by_text('Available bets').is_visible()

        browser.close()
