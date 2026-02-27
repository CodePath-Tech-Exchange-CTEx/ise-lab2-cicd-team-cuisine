#############################################################################
# tests/test_data_fetcher.py — tests for data_fetcher.py
#############################################################################
import unittest
from data_fetcher import get_user_trades


class TestDataFetcher(unittest.TestCase):
    def test_get_user_trades_structure(self):
        """Returned list should contain dicts with expected keys."""
        trades = get_user_trades('user1')
        self.assertIsInstance(trades, list)
        for trade in trades:
            self.assertIsInstance(trade, dict)
            for key in ('trade_id', 'symbol', 'action', 'quantity', 'price', 'timestamp'):
                self.assertIn(key, trade)



if __name__ == "__main__":
    unittest.main()
