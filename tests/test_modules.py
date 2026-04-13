#############################################################################
# tests/test_modules.py — tests for modules.py
#############################################################################
from __future__ import annotations
import unittest
from unittest.mock import patch, MagicMock

from modules import (
    display_post,
    display_individual_bet_summary,
    display_genai_advice,
    display_recent_workouts,
    compute_trade_metrics,
    display_trade_summary,
    filter_bets_by_category,
    display_friends_activity_card,
)


def call_display(**kwargs):
    """Call display_individual_bet_summary with safe defaults, overridden by kwargs."""
    defaults = dict(
        bet_id="test_bet",
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


def get_kwargs(mock_component) -> dict:
    """Extract the kwargs dict from the last component call."""
    return mock_component.call_args.kwargs


class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    @patch("modules.st.subheader")
    @patch("modules.st.write")
    @patch("modules.st.image")
    def test_display_post_renders(self, mock_image, mock_write, mock_subheader):
        display_post("alice", "https://example.com/avatar.png", "now", "Hello world", "https://example.com/post.png")
        mock_subheader.assert_called_once_with("alice – now")
        mock_write.assert_called_once_with("Hello world")
        mock_image.assert_called_once_with("https://example.com/post.png")


class TestDisplayIndividualBetSummary(unittest.TestCase):
    """Tests the display_individual_bet_summary function.

    Verifies data dict passed to create_component (rounding, fallback image, field names).
    """

    @patch("modules._bet_summary_component")
    def test_negative_value_still_runs(self, mock_component):
        """Negative yes_value/no_value: function should not raise."""
        try:
            call_display(yes_value=-5.00, no_value=-1.00)
        except Exception as e:
            self.fail(f"Raised unexpectedly on negative value: {e}")
        self.assertTrue(mock_component.called)

    @patch("modules._bet_summary_component")
    def test_too_many_decimal_places_rounds_to_two(self, mock_component):
        """Values with excess decimal digits should be rounded to 2 places."""
        call_display(yes_value=0.6789, no_value=0.3211)
        kwargs = get_kwargs(mock_component)
        self.assertEqual(kwargs["yes_value"], "0.68")
        self.assertEqual(kwargs["no_value"], "0.32")

    @patch("modules._bet_summary_component")
    def test_too_many_pre_decimal_digits_still_runs(self, mock_component):
        """Very large dollar values should not raise."""
        try:
            call_display(yes_value=999999999.99, no_value=0.01)
        except Exception as e:
            self.fail(f"Raised unexpectedly on large pre-decimal value: {e}")
        kwargs = get_kwargs(mock_component)
        self.assertEqual(kwargs["yes_value"], "999999999.99")

    @patch("modules._bet_summary_component")
    def test_special_symbols_in_rules_still_runs(self, mock_component):
        """Non-numeric symbols in the rules string should not crash."""
        try:
            call_display(rules="Resolves if price > $1,000 & volume != 0 @ close!")
        except Exception as e:
            self.fail(f"Raised unexpectedly on special symbols in rules: {e}")
        kwargs = get_kwargs(mock_component)
        self.assertIn("$1,000", kwargs["rules"])

    @patch("modules._bet_summary_component")
    def test_all_values_passed_as_kwargs(self, mock_component):
        """All bet data should be passed as keyword arguments to the component."""
        call_display(
            bet_id="bet123",
            bet_name="Test Name",
            bet_image_link="test_link",
            yes_value=0.1,
            no_value=0.9,
            yes_percent=10,
            no_percent=90,
            rules="Test rules",
        )
        kwargs = get_kwargs(mock_component)
        self.assertEqual(kwargs["bet_id"], "bet123")
        self.assertEqual(kwargs["bet_name"], "Test Name")
        self.assertEqual(kwargs["bet_image_link"], "test_link")
        self.assertEqual(kwargs["yes_value"], "0.10")
        self.assertEqual(kwargs["no_value"], "0.90")
        self.assertEqual(kwargs["yes_percent"], "10")
        self.assertEqual(kwargs["no_percent"], "90")
        self.assertEqual(kwargs["rules"], "Test rules")


    @patch("modules.st.toast")
    @patch("modules.st.session_state", new_callable=unittest.mock.PropertyMock)
    @patch("modules.process_bet_transaction")
    @patch("modules._bet_summary_component")
    def test_submit_success(self, mock_component, mock_process_bet, mock_session_state, mock_toast):
        """On successful submission, process_bet_transaction is called and a toast is shown."""
        mock_component.return_value = {'action': 'submit_transaction', 'choice': 'Yes', 'amount': '50', 'mode': 'Buy'}
        mock_process_bet.return_value = (True, "Successfully purchased the 'Yes' position on 'Test Bet' for $50.00.")
        mock_session_state.get.return_value = 'test_user'

        call_display(bet_id="bet_success")

        mock_process_bet.assert_called_once_with(
            user_id='test_user',
            bet_id='bet_success',
            user_took_yes=True,
            wager_amount='50',
            mode='Buy',
            bet_name='Test Bet'
        )
        mock_toast.assert_called_once_with("Successfully purchased the 'Yes' position on 'Test Bet' for $50.00.", icon="✅")

    @patch("modules.st.toast")
    @patch("modules.st.session_state", new_callable=unittest.mock.PropertyMock)
    @patch("modules.process_bet_transaction")
    @patch("modules._bet_summary_component")
    def test_submit_failure(self, mock_component, mock_process_bet, mock_session_state, mock_toast):
        """On failed submission, process_bet_transaction is called and a toast is shown."""
        mock_component.return_value = {'action': 'submit_transaction', 'choice': 'No', 'amount': '100', 'mode': 'Sell'}
        mock_process_bet.return_value = (False, "You do not own the 'No' position on 'Test Bet' to sell.")
        mock_session_state.get.return_value = 'test_user'

        call_display(bet_id="bet_fail")

        mock_process_bet.assert_called_once()
        self.assertEqual(mock_process_bet.call_args.kwargs['bet_name'], 'Test Bet')
        self.assertEqual(mock_process_bet.call_args.kwargs['user_took_yes'], False)
        self.assertEqual(mock_process_bet.call_args.kwargs['mode'], 'Sell')
        mock_toast.assert_called_once_with("You do not own the 'No' position on 'Test Bet' to sell.", icon="❌")


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    @patch("modules.os.path.exists", return_value=False)
    @patch("modules.st.error")
    def test_genai_advice_file_missing(self, mock_error, mock_exists):
        display_genai_advice("2026-01-01", "Some advice", None)
        mock_error.assert_called_once()


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    @patch("modules.st.write")
    def test_display_recent_workouts_nonempty(self, mock_write):
        display_recent_workouts([{"name": "run", "distance": 5}])
        mock_write.assert_called_once_with("Recent workouts placeholder")

    @patch("modules.st.write")
    def test_display_recent_workouts_empty(self, mock_write):
        display_recent_workouts([])
        mock_write.assert_not_called()


class TestFilterBetsByCategory(unittest.TestCase):
    """Tests the category filtering helper in modules."""

    def setUp(self):
        self.bets = [
            {"bet_id": "btc", "category": "Crypto"},
            {"bet_id": "eth", "category": "Crypto"},
            {"bet_id": "pres", "category": "Politics"},
        ]

    def test_filter_all_categories(self):
        result = filter_bets_by_category(self.bets, "All")
        self.assertEqual(result, self.bets)

    def test_filter_specific_category(self):
        result = filter_bets_by_category(self.bets, "Crypto")
        self.assertEqual(len(result), 2)
        self.assertTrue(all(bet["category"] == "Crypto" for bet in result))


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



if __name__ == "__main__":
    unittest.main()
