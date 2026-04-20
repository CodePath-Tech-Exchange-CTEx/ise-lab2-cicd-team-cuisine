from playwright.sync_api import sync_playwright

from ..common import login


def test_friends_activity_navigation():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)
        page.locator('a:has-text("Friends Activity")').first.click()

        assert page.get_by_text("Friends activity for").wait_for(timeout=15000)
        assert page.get_by_text("Sort by most friends betting").is_visible()
        assert page.get_by_text("View Details").count() >= 1

        browser.close()
