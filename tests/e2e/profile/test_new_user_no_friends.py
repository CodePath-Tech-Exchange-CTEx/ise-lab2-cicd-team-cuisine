# from playwright.sync_api import sync_playwright

# from ..common import BASE_URL


# def test_new_user_profile_shows_no_friend_activity():
#     with sync_playwright() as playwright:
#         browser = playwright.chromium.launch(headless=True)
#         page = browser.new_page()

#         page.goto(BASE_URL)
#         page.locator('button:has-text("👤 Account")').first.click()
#         page.get_by_text("Auth mode").wait_for(timeout=15000)
#         page.locator('label:has-text("Sign up")').first.click(force=True)
#         page.wait_for_timeout(500)
#         page.get_by_label("Username").fill("e2e_no_friends_user")
#         page.get_by_role("textbox", name="Full name").fill("E2E No Friends")
#         page.get_by_role("textbox", name="Date of birth (YYYY-MM-DD)").fill("1990-01-01")
#         page.get_by_role("button", name="Create account").click()

#         page.get_by_text("Profile & Trade Summary").wait_for(timeout=15000)
#         page.locator('button:has-text("👤 My Profile")').first.click()

#         assert page.get_by_text("No friend bets available right now.").is_visible()

#         browser.close()
