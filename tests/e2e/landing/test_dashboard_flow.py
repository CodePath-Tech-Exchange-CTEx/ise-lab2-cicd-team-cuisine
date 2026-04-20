from playwright.sync_api import sync_playwright

from tests.e2e.common import login


def test_dashboard_view_details_opens_individual_bet():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)
        page.get_by_role("button", name="View details").first.click()

        bet_frame = page.frame_locator("iframe").first
        bet_frame.locator('button:has-text("Submit")').wait_for(timeout=15000)

        assert bet_frame.locator('button:has-text("Submit")').is_visible()

        browser.close()


def test_dashboard_can_create_a_post():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)
        page.get_by_label("What's on your mind?").fill("Testing a post from E2E")
        page.get_by_role("button", name="Post").click()

        assert page.get_by_text("Post created successfully.").wait_for(timeout=15000)
        assert page.get_by_text("Testing a post from E2E").is_visible()

        browser.close()
