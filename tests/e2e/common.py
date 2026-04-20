import os

BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:8080")


def login(page):
    page.goto(BASE_URL)
    username_input = page.locator('input[aria-label="Username"]')
    password_input = page.locator('input[type="password"]')
    login_button = page.locator('button:has-text("Log in")')

    username_input.wait_for(timeout=15000)
    username_input.fill("user1")
    password_input.fill("password123")
    login_button.click()

    page.get_by_text("Category").wait_for(timeout=10000)


def open_individual_bet_view(page):
    """Login and navigate into the individual bet view page."""
    login(page)
    individual_view_button = page.locator('button:has-text("Individual bet view")')
    individual_view_button.wait_for(timeout=15000)
    individual_view_button.click()

    bet_frame = page.frame_locator("iframe").first
    bet_frame.locator('button:has-text("Submit")').wait_for(timeout=15000)
    return bet_frame
