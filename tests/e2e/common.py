import os

BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:8080")


def login(page):
    page.goto(BASE_URL)
    page.locator('button:has-text("👤 Account")').first.click()
    page.get_by_text("Log in / Sign up").wait_for(timeout=30000)

    page.locator('label:has-text("Log in")').first.click()
    username_input = page.locator('input[aria-label="Username"]').first
    password_input = page.locator('input[aria-label="Password"]').first
    login_button = page.locator('button:has-text("Log in")').first

    username_input.wait_for(timeout=30000)
    username_input.fill("user1")
    password_input.fill("password123")
    login_button.click()

    page.get_by_text('Signed in as').wait_for(timeout=30000)


def open_individual_bet_view(page):
    """Login and navigate into the individual bet view page."""
    login(page)
    view_button = page.locator('button:has-text("View details")').first
    view_button.wait_for(timeout=15000)
    view_button.click()

    bet_frame = page.frame_locator("iframe").first
    bet_frame.locator('button:has-text("Submit")').wait_for(timeout=15000)
    return bet_frame
