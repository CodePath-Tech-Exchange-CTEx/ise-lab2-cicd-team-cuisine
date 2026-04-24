"""

from playwright.sync_api import sync_playwright

from ..common import login


def test_login_flow_with_new_user():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)

        assert page.get_by_text("Category").is_visible()
        assert page.get_by_text("Friends Activity").is_visible()
        assert "AirBets" in page.title() or "AirBets" in page.content()

        browser.close()

"""