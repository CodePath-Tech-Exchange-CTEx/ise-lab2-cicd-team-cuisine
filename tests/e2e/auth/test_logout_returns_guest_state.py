# from playwright.sync_api import sync_playwright

# from ..common import BASE_URL, login


# def test_logout_returns_guest_state():
#     with sync_playwright() as playwright:
#         browser = playwright.chromium.launch(headless=True)
#         page = browser.new_page()

#         login(page)
#         page.locator('button:has-text("Log out")').first.click()
#         page.locator('button:has-text("👤 Account")').first.click()

#         assert page.get_by_text("Log in / Sign up").is_visible()

#         browser.close()
