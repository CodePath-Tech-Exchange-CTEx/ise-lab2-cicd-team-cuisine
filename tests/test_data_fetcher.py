#############################################################################
# tests/test_data_fetcher.py — tests for data_fetcher.py
#############################################################################
import unittest
from unittest.mock import patch, MagicMock
import datetime
import decimal

from data_fetcher import get_user_trades, get_bet_data, add_active_bet
 

# A mock row object to simulate BigQuery results
class MockRow:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestDataFetcher(unittest.TestCase):
    @patch('data_fetcher.bigquery')
    def test_get_user_trades_structure(self, mock_bigquery):
        """Returned list should contain dicts with expected keys."""
        # Mock the BigQuery client and query results
        mock_client = MagicMock()
        mock_query_job = MagicMock()

        # Mock results for UNION ALL
        mock_results = [
            # From ActivePurchasedBets
            MockRow(trade_id='bet1', symbol='Active Bet 1', action='BUY YES', quantity=1, price=50.0, timestamp=None),
            # From PastUserBets
            MockRow(trade_id='past_bet1', symbol='Past Bet 1', action='WIN', quantity=1, price=100.0, timestamp=datetime.datetime(2024, 1, 1, 12, 0, 0))
        ]

        mock_query_job.result.return_value = mock_results
        mock_client.query.return_value = mock_query_job
        mock_bigquery.Client.return_value = mock_client

        trades = get_user_trades('user1')

        self.assertIsInstance(trades, list)
        self.assertEqual(len(trades), 2)

        # Check first trade (active)
        trade1 = trades[0]
        self.assertIsInstance(trade1, dict)
        expected_keys = ('trade_id', 'symbol', 'action', 'quantity', 'price', 'timestamp')
        for key in expected_keys:
            self.assertIn(key, trade1)
        self.assertEqual(trade1['timestamp'], 'N/A')

        # Check second trade (past)
        trade2 = trades[1]
        self.assertIsInstance(trade2, dict)
        for key in expected_keys:
            self.assertIn(key, trade2)
        self.assertEqual(trade2['timestamp'], '2024-01-01T12:00:00')

    @patch('data_fetcher.bigquery', None)
    def test_get_user_trades_no_bigquery(self):
        """Should return an empty list if bigquery library is not installed."""
        trades = get_user_trades('user1')
        self.assertEqual(trades, [])

    @patch('data_fetcher.bigquery')
    def test_get_user_trades_query_fails(self, mock_bigquery):
        """Should return an empty list if the BigQuery query fails."""
        mock_client = MagicMock()
        mock_client.query.side_effect = Exception("Query failed")
        mock_bigquery.Client.return_value = mock_client

        trades = get_user_trades('user1')
        self.assertEqual(trades, [])

    @patch('data_fetcher.os.environ.get', return_value='test-project')
    @patch('data_fetcher.bigquery')
    def test_get_bet_data_success(self, mock_bigquery, mock_environ_get):
        """Should return a bet dictionary when a bet is found."""
        mock_client = MagicMock()
        mock_query_job = MagicMock()
        mock_result_row = MockRow(
            BetName='Test Bet', YesValue=60.0, NoValue=40.0,
            YesPercent=0.6, NoPercent=0.4, Rules='Test Rules',
            Image='http://example.com/image.png'
        )
        mock_query_job.result.return_value = [mock_result_row]
        mock_client.query.return_value = mock_query_job
        mock_bigquery.Client.return_value = mock_client

        bet_data = get_bet_data('bet1')

        self.assertIsInstance(bet_data, dict)
        self.assertEqual(bet_data['bet_name'], 'Test Bet')
        self.assertEqual(bet_data['yes_value'], 60.0)
        self.assertEqual(bet_data['bet_image_link'], 'http://example.com/image.png')
        # Check that the query was called with the project ID
        mock_client.query.assert_called_once()
        called_query = mock_client.query.call_args[0][0]
        self.assertIn('`test-project.ISE.Bets`', called_query)

    @patch('data_fetcher.bigquery')
    def test_get_bet_data_not_found(self, mock_bigquery):
        """Should return None when no bet is found."""
        mock_client = MagicMock()
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []  # Empty result set
        mock_client.query.return_value = mock_query_job
        mock_bigquery.Client.return_value = mock_client

        bet_data = get_bet_data('nonexistent_bet')
        self.assertIsNone(bet_data)

    @patch('data_fetcher.bigquery', None)
    def test_get_bet_data_no_bigquery(self):
        """Should return None if bigquery library is not installed."""
        bet_data = get_bet_data('bet1')
        self.assertIsNone(bet_data)

    @patch('data_fetcher.bigquery')
    def test_get_bet_data_query_fails(self, mock_bigquery):
        """Should return None if the BigQuery query fails."""
        mock_client = MagicMock()
        mock_client.query.side_effect = Exception("Query failed")
        mock_bigquery.Client.return_value = mock_client

        bet_data = get_bet_data('bet1')
        self.assertIsNone(bet_data)

    @patch('data_fetcher.os.environ.get', return_value='test-project')
    @patch('data_fetcher.bigquery')
    def test_add_active_bet_success(self, mock_bigquery, mock_environ):
        """Should return True when a bet is successfully inserted."""
        mock_client = MagicMock()
        mock_query_job = MagicMock()
        mock_query_job.errors = None
        mock_query_job.num_dml_affected_rows = 1
        
        mock_client.query.return_value = mock_query_job
        mock_bigquery.Client.return_value = mock_client

        success = add_active_bet(
            user_id='user1',
            bet_id='bet001',
            user_took_yes=True,
            wager_amount=10.50
        )

        self.assertTrue(success)
        mock_client.query.assert_called_once()
        
        # Check that the query parameters are correct
        _, kwargs = mock_client.query.call_args
        job_config = kwargs['job_config']
        params = {p.name: p for p in job_config.query_parameters}
        
        self.assertEqual(params['user_id'].value, 'user1')
        self.assertEqual(params['bet_id'].value, 'bet001')
        self.assertEqual(params['user_took_yes'].value, True)
        self.assertEqual(params['wager_amount'].value, decimal.Decimal('10.5'))

    @patch('data_fetcher.os.environ.get', return_value='test-project')
    @patch('data_fetcher.bigquery')
    def test_add_active_bet_failure_no_rows_affected(self, mock_bigquery, mock_environ):
        """Should return False if no rows are affected."""
        mock_client = MagicMock()
        mock_query_job = MagicMock()
        mock_query_job.errors = None
        mock_query_job.num_dml_affected_rows = 0 # Simulate no rows affected
        
        mock_client.query.return_value = mock_query_job
        mock_bigquery.Client.return_value = mock_client

        success = add_active_bet('user1', 'bet001', True, 10.50)
        self.assertFalse(success)

    @patch('data_fetcher.os.environ.get', return_value='test-project')
    @patch('data_fetcher.bigquery')
    def test_add_active_bet_failure_query_error(self, mock_bigquery, mock_environ):
        """Should return False if the query has errors."""
        mock_client = MagicMock()
        mock_query_job = MagicMock()
        mock_query_job.errors = [{'message': 'An error occurred'}]
        mock_query_job.num_dml_affected_rows = None
        
        mock_client.query.return_value = mock_query_job
        mock_bigquery.Client.return_value = mock_client

        success = add_active_bet('user1', 'bet001', True, 10.50)
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()
