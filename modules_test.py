#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################
from __future__ import annotations #Similar to example from Ms. Koo
import unittest
from streamlit.testing.v1 import AppTest
from modules import display_post, display_individual_bet_summary, display_genai_advice, display_recent_workouts

# Imports for Testing Individual Bet Summary:
from unittest.mock import patch
from modules import display_individual_bet_summary

# Helper functions for Testing Individual Bet Summary:
def call_display(**kwargs):
    """Call display_individual_bet_summary with safe defaults, overridden by kwargs."""
    defaults = dict(
        bet_name="Test Bet",
        bet_image_link="https://example.com/image.png",
        yes_value=0.65,
        no_value=0.35,
        yes_percent=65.0,
        no_percent=35.0,
        rules="Resolves YES if the condition is met.",
    )
    defaults.update(kwargs)
    display_individual_bet_summary(**defaults)

def get_data(mock_create) -> dict:
    """Extract the data dict from the first positional arg of the last create_component call."""
    return mock_create.call_args[0][0]

# Write your tests below

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayIndividualBetSummary(unittest.TestCase):
    """Tests the display_individual_bet_summary function.

    Tests Included + Expected Values:
        Invalid dollar values:
        - Negative value: still runs, JS layer shows error message
        - Too many decimal places: still runs, rounds to 2 decimal places
        - Too many pre-decimal digits: still runs, passes value through
        - Non-numeric symbols in rules: still runs, passes string through

        Missing image:
        - None image: still runs, IMAGE_HTML set to "No Image Available"
        - Empty string image: still runs, IMAGE_HTML set to "No Image Available"
        - Valid image link: IMAGE_HTML contains an <img> tag with the URL

        Happy paths (all verify data dict is fully and correctly populated):
        - User buys valid amount, Yes
        - User sells valid amount, Yes
        - User buys valid amount, No
        - User sells valid amount, No

    Since display_individual_bet_summary has no return value and all rendering happens inside an HTML iframe that Python's test harness can't see, the tests verify correctness by patching create_component with a mock and inspecting what gets passed to it. 
    Every test asserts on the data dict in create_component's first argument, confirming that the Python layer transforms its inputs correctly (rounding, fallback image text, correct field names) before handing off to the HTML component.    
    """

    @patch("modules.create_component")
    def test_negative_value_still_runs(self, mock_create):
        """Negative yes_value/no_value: function should not raise. JS layer shows error message."""
        try:
            call_display(yes_value=-5.00, no_value=-1.00)
        except Exception as e:
            self.fail(f"Raised unexpectedly on negative value: {e}")
        self.assertTrue(mock_create.called)

    @patch("modules.create_component")
    def test_too_many_decimal_places_rounds_to_two(self, mock_create):
        """Values with excess decimal digits should be rounded to 2 places in the data dict."""
        call_display(yes_value=0.6789, no_value=0.3211)
        data = get_data(mock_create)
        self.assertEqual(data["YES_VALUE"], "0.68")
        self.assertEqual(data["NO_VALUE"],  "0.32")

    @patch("modules.create_component")
    def test_too_many_pre_decimal_digits_still_runs(self, mock_create):
        """Very large dollar values should not raise and should pass through correctly."""
        try:
            call_display(yes_value=999999999.99, no_value=0.01)
        except Exception as e:
            self.fail(f"Raised unexpectedly on large pre-decimal value: {e}")
        data = get_data(mock_create)
        self.assertEqual(data["YES_VALUE"], "999999999.99")

    @patch("modules.create_component")
    def test_special_symbols_in_rules_still_runs(self, mock_create):
        """Non-numeric symbols in the rules string should not crash the function."""
        try:
            call_display(rules="Resolves if price > $1,000 & volume != 0 @ close!")
        except Exception as e:
            self.fail(f"Raised unexpectedly on special symbols in rules: {e}")
        data = get_data(mock_create)
        self.assertIn("$1,000", data["RULES"])

    @patch("modules.create_component")
    def test_none_image_still_runs_with_fallback(self, mock_create):
        """None bet_image_link: should not raise and IMAGE_HTML should be fallback text."""
        try:
            call_display(bet_image_link=None)
        except Exception as e:
            self.fail(f"Raised unexpectedly with None image: {e}")
        data = get_data(mock_create)
        self.assertEqual(data["IMAGE_HTML"], "No Image Available")

    @patch("modules.create_component")
    def test_empty_string_image_uses_fallback(self, mock_create):
        """Empty string bet_image_link should also produce the fallback."""
        call_display(bet_image_link="")
        data = get_data(mock_create)
        self.assertEqual(data["IMAGE_HTML"], "No Image Available")

    @patch("modules.create_component")
    def test_valid_image_link_produces_img_tag(self, mock_create):
        """A valid URL should produce an <img> tag containing the URL in IMAGE_HTML."""
        call_display(bet_image_link="https://example.com/bet.png")
        data = get_data(mock_create)
        self.assertIn("<img", data["IMAGE_HTML"])
        self.assertIn("https://example.com/bet.png", data["IMAGE_HTML"])

    @patch("modules.create_component")
    def test_buy_yes_valid_amount(self, mock_create):
        """Buy + Yes: data dict should be fully populated with correct yes-side values."""
        call_display(yes_value=0.72, no_value=0.28, yes_percent=72, no_percent=28)
        data = get_data(mock_create)
        self.assertEqual(data["YES_VALUE"],   "0.72")
        self.assertEqual(data["NO_VALUE"],    "0.28")
        self.assertEqual(data["YES_PERCENT"], "72")
        self.assertEqual(data["NO_PERCENT"],  "28")
        self.assertEqual(data["BET_NAME"],    "Test Bet")
        self.assertIn("<img",                  data["IMAGE_HTML"])

    @patch("modules.create_component")
    def test_sell_yes_valid_amount(self, mock_create):
        """Sell + Yes: data dict should reflect yes-side values."""
        call_display(yes_value=0.55, no_value=0.45, yes_percent=55, no_percent=45)
        data = get_data(mock_create)
        self.assertEqual(data["YES_VALUE"],   "0.55")
        self.assertEqual(data["YES_PERCENT"], "55")

    @patch("modules.create_component")
    def test_buy_no_valid_amount(self, mock_create):
        """Buy + No: data dict should reflect no-side values."""
        call_display(yes_value=0.40, no_value=0.60, yes_percent=40, no_percent=60)
        data = get_data(mock_create)
        self.assertEqual(data["NO_VALUE"],    "0.60")
        self.assertEqual(data["NO_PERCENT"],  "60")

    @patch("modules.create_component")
    def test_sell_no_valid_amount(self, mock_create):
        """Sell + No: all fields correctly passed through for a fully specified bet."""
        call_display(
            bet_name="Will ETH flip BTC?",
            bet_image_link="https://example.com/eth.png",
            yes_value=0.30,
            no_value=0.70,
            yes_percent=30,
            no_percent=70,
            rules="Resolves YES if ETH market cap exceeds BTC before 2026.",
        )
        data = get_data(mock_create)
        self.assertEqual(data["BET_NAME"],    "Will ETH flip BTC?")
        self.assertEqual(data["NO_VALUE"],    "0.70")
        self.assertEqual(data["NO_PERCENT"],  "70")
        self.assertEqual(data["YES_VALUE"],   "0.30")
        self.assertEqual(data["YES_PERCENT"], "30")
        self.assertIn("ETH market cap",        data["RULES"])
        self.assertIn("https://example.com/eth.png", data["IMAGE_HTML"])

    @patch("modules.create_component")
    def test_correct_html_file_name_always_used(self, mock_create):
        """create_component should always be called with 'individual_bet_summary'."""
        call_display()
        html_file_name = mock_create.call_args[0][1]
        self.assertEqual(html_file_name, "individual_bet_summary")


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()
