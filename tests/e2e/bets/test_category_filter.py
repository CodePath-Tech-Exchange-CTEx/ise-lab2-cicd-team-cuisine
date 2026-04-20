from playwright.sync_api import sync_playwright

from ..common import login


def test_category_filter_shows_only_crypto_bets():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)

        category_input = page.get_by_label("Category")
        category_input.click()
        category_input.fill("Crypto")
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)

        assert page.get_by_text("Will Bitcoin hit $100k?").is_visible()
        assert not page.get_by_text("Will Democrats hold Senate majority after 2026 midterms?").is_visible()

        browser.close()
