from playwright.sync_api import sync_playwright

from ..common import login


def test_ai_advice_navigation():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)

        page.get_by_text("AI Advice").click()
        page.wait_for_url("**/AI_Advice", timeout=15000)

        assert page.title() == "AI Advisor — AirBets"
        assert page.get_by_text("AI Analysis").is_visible()
        assert page.get_by_text("TREND INSIGHT").is_visible()
        assert page.get_by_text("RISK FLAG").is_visible()

        browser.close()
