from playwright.sync_api import sync_playwright

from ..common import login


def test_ai_advice_navigation():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)

        page.locator('a:has-text("AI Advice")').first.click()

        assert page.get_by_text("AI Advisor").wait_for(timeout=15000)
        assert page.get_by_text("AI Analysis").is_visible()
        assert page.get_by_text("Trend Insight").is_visible()
        assert page.get_by_text("Risk Flag").is_visible()

        browser.close()
