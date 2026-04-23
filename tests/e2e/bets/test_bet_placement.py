from playwright.sync_api import sync_playwright

from ..common import open_individual_bet_view


def test_buy_yes_position_submits_successfully():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        bet_frame = open_individual_bet_view(page)
        bet_frame.locator('button:has-text("Yes $")').click()
        bet_frame.get_by_placeholder("0.00").fill("15")
        bet_frame.locator('button:has-text("Submit")').click()

        page.get_by_text("Successfully purchased the 'Yes' position", exact=False).wait_for(timeout=15000)

        context.close()
        browser.close()


def test_buy_no_position_submits_successfully():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        bet_frame = open_individual_bet_view(page)
        bet_frame.locator('button:has-text("No $")').click()
        bet_frame.get_by_placeholder("0.00").fill("20")
        bet_frame.locator('button:has-text("Submit")').click()

        page.get_by_text("Successfully purchased the 'No' position", exact=False).wait_for(timeout=15000)

        context.close()
        browser.close()


def test_sell_without_position_shows_error_toast():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        bet_frame = open_individual_bet_view(page)
        bet_frame.locator('button:has-text("Sell")').click()
        bet_frame.get_by_placeholder("0.00").fill("10")
        bet_frame.locator('button:has-text("Submit")').click()

        page.get_by_text("You do not own the 'Yes' position", exact=False).wait_for(timeout=15000)

        context.close()
        browser.close()
