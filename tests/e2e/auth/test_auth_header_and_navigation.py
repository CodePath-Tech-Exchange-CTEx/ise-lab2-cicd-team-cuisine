import uuid

from playwright.sync_api import sync_playwright

from ..common import BASE_URL, login


def test_login_page_title_includes_home_and_auth_controls():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BASE_URL, wait_until='load', timeout=60000)
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

        page.goto(BASE_URL, wait_until='load', timeout=60000)
        page.get_by_text("AirBets").wait_for(timeout=30000)
        page.locator('button:has-text("👤 Account")').first.click()
        page.get_by_text("Log in / Sign up").wait_for(timeout=15000)
        page.locator('label:has-text("Sign up")').first.click(force=True)
        page.wait_for_timeout(500)
        page.get_by_label("Username").wait_for(timeout=15000)

        unique_username = f"e2e_signup_{uuid.uuid4().hex[:8]}"
        page.get_by_label("Username").fill(unique_username)
        page.get_by_role("textbox", name="Full name").fill("E2E Top Right")
        page.get_by_role("textbox", name="Date of birth (YYYY-MM-DD)").fill("1990-05-15")
        create_button = page.get_by_role("button", name="Create account")
        create_button.wait_for(timeout=15000)
        create_button.click()

        page.wait_for_timeout(5000)
        page.get_by_text("Friends list").wait_for(timeout=15000)
        assert page.get_by_text("Friends list").is_visible()

        browser.close()


def test_unauthenticated_account_button_opens_auth_modal():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BASE_URL, wait_until='load', timeout=60000)
        page.get_by_text("AirBets").wait_for(timeout=30000)

        assert page.get_by_text("Welcome back").is_visible()
        page.locator('button:has-text("👤 Account")').first.click()

        page.get_by_text("Auth mode").wait_for(timeout=15000)
        assert page.get_by_text("Auth mode").is_visible()
        assert page.get_by_label("Username").is_visible()
        assert page.locator('input[aria-label="Password"]').first.is_visible()
        assert page.get_by_role("button", name="Log in").is_visible()

        browser.close()


def test_unauthenticated_user_can_open_signup_flow():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BASE_URL, wait_until='load', timeout=60000)
        page.get_by_text("AirBets").wait_for(timeout=30000)
        page.locator('button:has-text("👤 Account")').first.click()

        page.get_by_text("Auth mode").wait_for(timeout=15000)
        page.locator('label:has-text("Sign up")').first.click(force=True)
        page.wait_for_timeout(500)

        assert page.get_by_label("Username").is_visible()
        assert page.get_by_role("textbox", name="Full name").is_visible()
        assert page.get_by_role("textbox", name="Date of birth (YYYY-MM-DD)").is_visible()
        assert page.get_by_role("button", name="Create account").is_visible()

        browser.close()


def test_unauthenticated_account_modal_close():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BASE_URL, wait_until='load', timeout=60000)
        page.get_by_text("AirBets").wait_for(timeout=30000)
        page.locator('button:has-text("👤 Account")').first.click()

        page.get_by_text("Auth mode").wait_for(timeout=15000)
        page.locator('button:has-text("Close")').first.click()

        page.wait_for_timeout(500)
        assert page.get_by_text("Welcome back").is_visible()
        assert page.get_by_text("Auth mode").count() == 0

        browser.close()


def test_unauthenticated_page_access_shows_login_warning():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BASE_URL, wait_until='load', timeout=60000)
        page.get_by_text("AirBets").wait_for(timeout=30000)

        # Profile page should ask the user to log in
        page.locator('button:has-text("👤 My Profile")').first.click()
        page.get_by_text("Please log in to view your profile and place bets.").wait_for(timeout=15000)
        assert page.get_by_text("← Back to Dashboard").is_visible()

        # Friends Activity should also show login warning via direct page route
        page.goto(f"{BASE_URL}/?page=pages/4_Friends_Activity.py")
        page.get_by_text("Please log in to view friends activity.").wait_for(timeout=15000)
        assert page.get_by_text("← Back to Dashboard").is_visible()

        browser.close()


def test_unauthenticated_read_only_bet_detail_shows_comments():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BASE_URL, wait_until='load', timeout=60000)
        page.get_by_text("AirBets").wait_for(timeout=30000)
        page.locator('button:has-text("View details")').first.click()

        page.get_by_text('Please log in to place bets.').wait_for(timeout=15000)
        page.get_by_text('Comment thread').wait_for(timeout=15000)
        assert page.get_by_text('Comment thread').is_visible()
        assert page.get_by_text('AI Agent').is_visible()
        assert page.get_by_text('Trader Sam').is_visible()

        browser.close()


def test_sidebar_navigation_labels_after_login():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)

        assert page.locator('button:has-text("🏠 Community")').first.is_visible()
        assert page.locator('button:has-text("📈 Marketplace")').first.is_visible()
        assert page.locator('button:has-text("🤖 AI Insights")').first.is_visible()
        assert page.locator('button:has-text("👤 My Profile")').first.is_visible()

        page.locator('button:has-text("📈 Marketplace")').first.click()
        page.get_by_text('AirBets Dashboard').wait_for(timeout=15000)

        browser.close()


def test_login_and_navigation_journey():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)

        page.locator('button:has-text("🤖 AI Insights")').first.click()
        page.locator('div.bubble-sender', has_text='AI Advisor').wait_for(timeout=15000)

        page.goto(f"{BASE_URL}/?page=pages/4_Friends_Activity.py")
        page.get_by_text('Friends activity for').wait_for(timeout=15000)

        page.locator('button:has-text("👤 My Profile")').first.click()
        page.get_by_text('Friends list').wait_for(timeout=15000)

        page.locator('button:has-text("📈 Marketplace")').first.click()
        page.get_by_text('AirBets Dashboard').wait_for(timeout=15000)

        browser.close()


def test_profile_page_back_to_dashboard_navigation():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)
        page.locator('button:has-text("👤 My Profile")').first.click()

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
