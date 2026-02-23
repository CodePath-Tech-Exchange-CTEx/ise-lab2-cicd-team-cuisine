#############################################################################
# tests/test_modules.py — tests for modules.py
#############################################################################
from __future__ import annotations
import unittest
from unittest.mock import patch

from modules import (
    display_post,
    display_individual_bet_summary,
    display_genai_advice,
    display_recent_workouts,
)


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


class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayIndividualBetSummary(unittest.TestCase):
    """Tests the display_individual_bet_summary function.

    Verifies data dict passed to create_component (rounding, fallback image, field names).
    """

    @patch("modules.create_component")
    def test_negative_value_still_runs(self, mock_create):
        """Negative yes_value/no_value: function should not raise."""
        try:
            call_display(yes_value=-5.00, no_value=-1.00)
        except Exception as e:
            self.fail(f"Raised unexpectedly on negative value: {e}")
        self.assertTrue(mock_create.called)

    @patch("modules.create_component")
    def test_too_many_decimal_places_rounds_to_two(self, mock_create):
        """Values with excess decimal digits should be rounded to 2 places."""
        call_display(yes_value=0.6789, no_value=0.3211)
        data = get_data(mock_create)
        self.assertEqual(data["YES_VALUE"], "0.68")
        self.assertEqual(data["NO_VALUE"], "0.32")

    @patch("modules.create_component")
    def test_too_many_pre_decimal_digits_still_runs(self, mock_create):
        """Very large dollar values should not raise."""
        try:
            call_display(yes_value=999999999.99, no_value=0.01)
        except Exception as e:
            self.fail(f"Raised unexpectedly on large pre-decimal value: {e}")
        data = get_data(mock_create)
        self.assertEqual(data["YES_VALUE"], "999999999.99")

    @patch("modules.create_component")
    def test_special_symbols_in_rules_still_runs(self, mock_create):
        """Non-numeric symbols in the rules string should not crash."""
        try:
            call_display(rules="Resolves if price > $1,000 & volume != 0 @ close!")
        except Exception as e:
            self.fail(f"Raised unexpectedly on special symbols in rules: {e}")
        data = get_data(mock_create)
        self.assertIn("$1,000", data["RULES"])

    @patch("modules.create_component")
    def test_none_image_still_runs_with_fallback(self, mock_create):
        """None bet_image_link: IMAGE_HTML should be fallback text."""
        try:
            call_display(bet_image_link=None)
        except Exception as e:
            self.fail(f"Raised unexpectedly with None image: {e}")
        data = get_data(mock_create)
        self.assertEqual(data["IMAGE_HTML"], "No Image Available")

    @patch("modules.create_component")
    def test_empty_string_image_uses_fallback(self, mock_create):
        """Empty string bet_image_link should produce the fallback."""
        call_display(bet_image_link="")
        data = get_data(mock_create)
        self.assertEqual(data["IMAGE_HTML"], "No Image Available")

    @patch("modules.create_component")
    def test_valid_image_link_produces_img_tag(self, mock_create):
        """Valid URL should produce an <img> tag in IMAGE_HTML."""
        call_display(bet_image_link="https://example.com/bet.png")
        data = get_data(mock_create)
        self.assertIn("<img", data["IMAGE_HTML"])
        self.assertIn("https://example.com/bet.png", data["IMAGE_HTML"])

    @patch("modules.create_component")
    def test_buy_yes_valid_amount(self, mock_create):
        """Buy + Yes: data dict fully populated with yes-side values."""
        call_display(yes_value=0.72, no_value=0.28, yes_percent=72, no_percent=28)
        data = get_data(mock_create)
        self.assertEqual(data["YES_VALUE"], "0.72")
        self.assertEqual(data["NO_VALUE"], "0.28")
        self.assertEqual(data["YES_PERCENT"], "72")
        self.assertEqual(data["NO_PERCENT"], "28")
        self.assertEqual(data["BET_NAME"], "Test Bet")
        self.assertIn("<img", data["IMAGE_HTML"])

    @patch("modules.create_component")
    def test_sell_yes_valid_amount(self, mock_create):
        """Sell + Yes: data dict reflects yes-side values."""
        call_display(yes_value=0.55, no_value=0.45, yes_percent=55, no_percent=45)
        data = get_data(mock_create)
        self.assertEqual(data["YES_VALUE"], "0.55")
        self.assertEqual(data["YES_PERCENT"], "55")

    @patch("modules.create_component")
    def test_buy_no_valid_amount(self, mock_create):
        """Buy + No: data dict reflects no-side values."""
        call_display(yes_value=0.40, no_value=0.60, yes_percent=40, no_percent=60)
        data = get_data(mock_create)
        self.assertEqual(data["NO_VALUE"], "0.60")
        self.assertEqual(data["NO_PERCENT"], "60")

    @patch("modules.create_component")
    def test_sell_no_valid_amount(self, mock_create):
        """Sell + No: all fields passed through for a fully specified bet."""
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
        self.assertEqual(data["BET_NAME"], "Will ETH flip BTC?")
        self.assertEqual(data["NO_VALUE"], "0.70")
        self.assertEqual(data["NO_PERCENT"], "70")
        self.assertEqual(data["YES_VALUE"], "0.30")
        self.assertEqual(data["YES_PERCENT"], "30")
        self.assertIn("ETH market cap", data["RULES"])
        self.assertIn("https://example.com/eth.png", data["IMAGE_HTML"])

    @patch("modules.create_component")
    def test_correct_html_file_name_always_used(self, mock_create):
        """create_component should be called with 'individual_bet_summary'."""
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


class TestTradeSummary(unittest.TestCase):
    """Unit tests for trade-related helpers."""

    def test_compute_trade_metrics(self):
        trades = [
            {'trade_id': 't1', 'symbol': 'AAPL', 'action': 'BUY', 'quantity': 10, 'price': 100},
            {'trade_id': 't2', 'symbol': 'TSLA', 'action': 'SELL', 'quantity': 5, 'price': 200},
        ]
        metrics = compute_trade_metrics(trades)
        self.assertEqual(metrics['total_trades'], 2)
        self.assertEqual(metrics['total_volume'], 15)
        self.assertAlmostEqual(metrics['total_value'], 10 * 100 + 5 * 200)

    def test_display_trade_summary_no_crash(self):
        # simply calling the function should not raise any exception
        try:
            display_trade_summary([])
            display_trade_summary([
                {'trade_id': 'x', 'symbol': 'GOOG', 'action': 'BUY', 'quantity': 1, 'price': 50}
            ])
        except Exception as e:
            self.fail(f"display_trade_summary raised unexpectedly: {e}")

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()
