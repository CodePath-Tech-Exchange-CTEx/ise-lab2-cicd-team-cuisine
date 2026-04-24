"""

from playwright.sync_api import sync_playwright

from ..common import BASE_URL, login


def test_profile_page_shows_friends_and_past_bets():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)
        page.locator('button:has-text("👤 My Profile")').first.click()

        assert page.get_by_text("Profile & Trade Summary").is_visible()
        assert page.get_by_text("Friends list").is_visible()
        assert page.get_by_text("Past bets").is_visible()
        assert page.get_by_text("Friends' current bets").is_visible()

        browser.close()


def test_signup_flow_creates_new_user():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BASE_URL)
        page.locator('button:has-text("👤 Account")').first.click()
        page.get_by_text("Auth mode").wait_for(timeout=15000)
        page.locator('label:has-text("Sign up")').first.click(force=True)
        page.wait_for_timeout(500)
        page.get_by_label("Username").fill("e2e_signup_user")
        page.get_by_role("textbox", name="Full name").fill("E2E Signup User")
        page.get_by_role("textbox", name="Date of birth (YYYY-MM-DD)").fill("1995-01-01")
        page.get_by_role("button", name="Create account").click()

        assert page.get_by_text("Profile & Trade Summary").wait_for(timeout=15000)
        assert page.get_by_text("Friends list").is_visible()

        browser.close()

"""