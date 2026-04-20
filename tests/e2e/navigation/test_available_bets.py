from playwright.sync_api import sync_playwright

from ..common import login


def test_available_bets_navigation_shows_bet_cards():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)
        page.locator('a:has-text("Available bets")').first.click()

        page.get_by_text('Available bets').wait_for(timeout=15000)
        assert page.get_by_text('Available bets').is_visible()
        assert page.get_by_role('button', name='View details').count() >= 1
        assert page.get_by_text('Yes $').count() >= 1 or page.get_by_text('No $').count() >= 1

        browser.close()
