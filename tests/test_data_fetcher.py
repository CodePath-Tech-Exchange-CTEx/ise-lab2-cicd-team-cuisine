#############################################################################
# tests/test_data_fetcher.py — tests for data_fetcher.py
#############################################################################
import unittest
from unittest.mock import patch, MagicMock
import datetime
import decimal

from data_fetcher import (
    create_user,
    get_user_friends,
    get_user_trades,
    get_bet_data,
    process_bet_transaction,
    get_friends_activity,
    get_user_profile,
    get_user_posts,
    get_genai_advice,
)


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
    def test_process_bet_transaction_buy_new(self, mock_bigquery, mock_environ):
        """Should return True and insert when buying a new bet."""
        mock_client = MagicMock()
        mock_check_job = MagicMock()
        mock_check_job.result.return_value = [] # No existing row
        
        mock_opposite_check_job = MagicMock()
        mock_opposite_check_job.result.return_value = [] # No opposite position row
        
        mock_insert_job = MagicMock()
        mock_insert_job.errors = None
        
        mock_client.query.side_effect = [mock_check_job, mock_opposite_check_job, mock_insert_job]
        mock_bigquery.Client.return_value = mock_client

        success, msg = process_bet_transaction(
            user_id='user1',
            bet_id='bet001',
            user_took_yes=True,
            wager_amount=10.50,
            mode='Buy'
        )

        self.assertTrue(success)
        self.assertIn("Successfully purchased", msg)
        self.assertEqual(mock_client.query.call_count, 3)

    @patch('data_fetcher.os.environ.get', return_value='test-project')
    @patch('data_fetcher.bigquery')
    def test_process_bet_transaction_sell_too_much(self, mock_bigquery, mock_environ):
        """Should return False if selling more than owned."""
        mock_client = MagicMock()
        mock_check_job = MagicMock()
        mock_check_job.result.return_value = [MockRow(WagerAmount=5.0)] # Owns 5.0
        
        mock_client.query.return_value = mock_check_job
        mock_bigquery.Client.return_value = mock_client

        success, msg = process_bet_transaction('user1', 'bet001', True, 10.50, 'Sell')
        self.assertFalse(success)
        self.assertIn("cannot sell more than you own", msg)
        self.assertEqual(mock_client.query.call_count, 1)

    @patch('data_fetcher.os.environ.get', return_value='test-project')
    @patch('data_fetcher.bigquery')
    def test_process_bet_transaction_error(self, mock_bigquery, mock_environ):
        """Should return False if a DB error occurs."""
        mock_client = MagicMock()
        mock_client.query.side_effect = Exception("DB crash")
        mock_bigquery.Client.return_value = mock_client

        success, msg = process_bet_transaction('user1', 'bet001', True, 10.50, 'Buy')
        self.assertFalse(success)
        self.assertIn("Database error", msg)

class TestGetFriendsActivity(unittest.TestCase):
    """Tests for the get_friends_activity function."""

    @patch('data_fetcher.bigquery', None)
    def test_get_friends_activity_fallback(self):
        """Should return hardcoded fallback data when bigquery is not available."""
        activity = get_friends_activity('user1')
        self.assertIsInstance(activity, list)
        self.assertEqual(len(activity), 2)
        self.assertEqual(activity[0]['bet_id'], 'btc-100k')

    @patch('data_fetcher.bigquery')
    def test_get_friends_activity_success(self, mock_bigquery):
        """Should correctly map BigQuery results to the activity dictionary."""
        mock_client = MagicMock()
        mock_query_job = MagicMock()
        
        mock_row = MockRow(
            BetID='bet123',
            BetName='Test Friends Bet',
            YesValue=0.75,
            NoValue=0.25,
            YesPercent=75.0,
            NoPercent=25.0,
            friends=['Alice', 'Bob']
        )
        
        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job
        mock_bigquery.Client.return_value = mock_client

        activity = get_friends_activity('user1')
        self.assertEqual(len(activity), 1)
        self.assertEqual(activity[0]['bet_id'], 'bet123')
        self.assertEqual(activity[0]['friends'], ['Alice', 'Bob'])
        self.assertEqual(activity[0]['yes_value'], 0.75)

    @patch('data_fetcher.bigquery')
    def test_get_friends_activity_query_fails(self, mock_bigquery):
        """Should return an empty list if the database query fails."""
        mock_client = MagicMock()
        mock_client.query.side_effect = Exception("BQ Error")
        mock_bigquery.Client.return_value = mock_client

        activity = get_friends_activity('user1')
        self.assertEqual(activity, [])

class TestDataFetcherSimpleHelpers(unittest.TestCase):
    """Tests for simple helper methods in data_fetcher.py."""

    def test_get_user_profile_existing_user(self):
        profile = get_user_profile('user1')
        self.assertIsInstance(profile, dict)
        self.assertEqual(profile['username'], 'remi_the_rems')
        self.assertIn('friends', profile)

    def test_get_user_profile_missing_user(self):
        with self.assertRaises(ValueError):
            get_user_profile('unknown_user')

    def test_get_user_friends_returns_profiles(self):
        friends = get_user_friends('user1')
        self.assertIsInstance(friends, list)
        self.assertTrue(all('username' in friend for friend in friends))
        self.assertTrue(all('full_name' in friend for friend in friends))

    def test_create_user_adds_account(self):
        new_user_id = create_user('new_test_user', full_name='New Test', date_of_birth='1995-01-01')
        self.assertEqual(new_user_id, 'new_test_user')
        profile = get_user_profile(new_user_id)
        self.assertEqual(profile['username'], 'new_test_user')
        self.assertEqual(profile['full_name'], 'New Test')

    def test_get_user_posts_returns_list(self):
        posts = get_user_posts('user1')
        self.assertIsInstance(posts, list)
        self.assertGreater(len(posts), 0)
        self.assertEqual(posts[0]['user_id'], 'user1')
        self.assertIn('content', posts[0])

    def test_get_genai_advice_returns_dict(self):
        advice = get_genai_advice('user1')
        self.assertIsInstance(advice, dict)
        self.assertIn('advice_id', advice)
        self.assertIn('content', advice)

if __name__ == "__main__":
    unittest.main()
