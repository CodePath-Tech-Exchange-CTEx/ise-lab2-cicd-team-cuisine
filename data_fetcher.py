#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

import os
import random
import decimal
try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

from data.bets import get_available_bets

users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Blake',
        'username': 'blake',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1'],
    },
    'user3': {
        'full_name': 'Jordan',
        'username': 'jordanjordanjordan',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user4'],
    },
    'user4': {
        'full_name': 'Gemmy',
        'username': 'gems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user3'],
    },
}

LOCAL_ACTIVE_PURCHASED_BETS = []


def get_user_sensor_data(user_id, workout_id):
    """Returns a list of timestampped information for a given workout.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    sensor_data = []
    sensor_types = [
        'accelerometer',
        'gyroscope',
        'pressure',
        'temperature',
        'heart_rate',
    ]
    for index in range(random.randint(5, 100)):
        random_minute = str(random.randint(0, 59))
        if len(random_minute) == 1:
            random_minute = '0' + random_minute
        timestamp = '2024-01-01 00:' + random_minute + ':00'
        data = random.random() * 100
        sensor_type = random.choice(sensor_types)
        sensor_data.append(
            {'sensor_type': sensor_type, 'timestamp': timestamp, 'data': data}
        )
    return sensor_data


def get_user_workouts(user_id):
    """Returns a list of user's workouts.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    workouts = []
    for index in range(random.randint(1, 3)):
        random_lat_lng_1 = (
            1 + random.randint(0, 100) / 100,
            4 + random.randint(0, 100) / 100,
        )
        random_lat_lng_2 = (
            1 + random.randint(0, 100) / 100,
            4 + random.randint(0, 100) / 100,
        )
        workouts.append({
            'workout_id': f'workout{index}',
            'start_timestamp': '2024-01-01 00:00:00',
            'end_timestamp': '2024-01-01 00:30:00',
            'start_lat_lng': random_lat_lng_1,
            'end_lat_lng': random_lat_lng_2,
            'distance': random.randint(0, 200) / 10.0,
            'steps': random.randint(0, 20000),
            'calories_burned': random.randint(0, 100),
        })
    return workouts


def get_user_trades(user_id):
    """Returns a list of trades (active and past bets) for a given user from BigQuery.
    
    Combines records from ActivePurchasedBets and PastUserBets.
    """
    if bigquery is None:
        trades = []
        for record in LOCAL_ACTIVE_PURCHASED_BETS:
            if record['UserID'] != user_id:
                continue
            bet = get_bet_data(record['BetID']) or {}
            trades.append({
                'trade_id': record.get('BetID', 'N/A'),
                'symbol': bet.get('bet_name', 'Unknown Bet'),
                'action': 'BUY YES' if record['UserTookYes'] else 'BUY NO',
                'quantity': 1,
                'price': float(record['WagerAmount']),
                'timestamp': 'N/A',
            })
        return trades

    client = bigquery.Client()
    query = """
        SELECT 
            a.BetID as trade_id, 
            b.BetName as symbol, 
            IF(a.UserTookYes, 'BUY YES', 'BUY NO') as action, 
            1 as quantity, 
            a.WagerAmount as price, 
            CAST(NULL AS DATETIME) as timestamp 
        FROM `ISE.ActivePurchasedBets` a
        LEFT JOIN `ISE.Bets` b ON a.BetID = b.BetID
        WHERE a.UserID = @user_id

        UNION ALL

        SELECT 
            p.PastBetID as trade_id, 
            b.BetName as symbol, 
            p.Result as action, 
            1 as quantity, 
            p.Payout as price, 
            p.Timestamp as timestamp 
        FROM `ISE.PastUserBets` p
        LEFT JOIN `ISE.Bets` b ON p.BetID = b.BetID
        WHERE p.UserID = @user_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )
    
    trades = []
    try:
        query_job = client.query(query, job_config=job_config)
        for row in query_job.result():
            trades.append({
                'trade_id': row.trade_id if row.trade_id else 'N/A',
                'symbol': row.symbol if row.symbol else 'Unknown Bet',
                'action': row.action if row.action else 'UNKNOWN',
                'quantity': row.quantity,
                'price': float(row.price) if row.price is not None else 0.0,
                'timestamp': row.timestamp.isoformat() if row.timestamp else 'N/A',
            })
    except Exception as e:
        print(f"Error fetching trades from BigQuery: {e}")
        
    return trades


def process_bet_transaction(user_id, bet_id, user_took_yes, wager_amount, mode='Buy', bet_name=''):
    """Handles Buy/Sell logic for a bet, updating or inserting into ActivePurchasedBets."""
    if user_id not in users:
        return False, f"User '{user_id}' not found. Please log in with a valid account."

    project_id = os.environ.get('GCP_PROJECT')
    if bigquery is None or not project_id:
        wager_decimal = decimal.Decimal(str(wager_amount))
        bet_display = f" '{bet_name}'" if bet_name else " this bet"
        position_str = "Yes" if user_took_yes else "No"

        existing = next(
            (record for record in LOCAL_ACTIVE_PURCHASED_BETS
             if record['UserID'] == user_id and record['BetID'] == bet_id and record['UserTookYes'] == user_took_yes),
            None,
        )
        existing_amount = decimal.Decimal(str(existing['WagerAmount'])) if existing else decimal.Decimal('0.0')

        opposite = next(
            (record for record in LOCAL_ACTIVE_PURCHASED_BETS
             if record['UserID'] == user_id and record['BetID'] == bet_id and record['UserTookYes'] != user_took_yes),
            None,
        )

        if mode == 'Sell':
            if not existing:
                return False, f"You do not own the '{position_str}' position on{bet_display} to sell."
            if existing_amount < wager_decimal:
                return False, f"You cannot sell more than you own (${existing_amount:.2f}) of the '{position_str}' position on{bet_display}."

            new_amount = existing_amount - wager_decimal
            if new_amount == 0:
                LOCAL_ACTIVE_PURCHASED_BETS.remove(existing)
            else:
                existing['WagerAmount'] = str(new_amount)
            return True, f"Successfully sold ${wager_decimal:.2f} of the '{position_str}' position on{bet_display}."

        if opposite:
            return False, f"You cannot buy this position on{bet_display} as you already own the opposite position."

        if existing:
            new_amount = existing_amount + wager_decimal
            existing['WagerAmount'] = str(new_amount)
            return True, f"Successfully added ${wager_decimal:.2f} to your existing '{position_str}' wager on{bet_display}."

        LOCAL_ACTIVE_PURCHASED_BETS.append({
            'UserID': user_id,
            'BetID': bet_id,
            'UserTookYes': user_took_yes,
            'WagerAmount': str(wager_decimal),
        })
        return True, f"Successfully purchased the '{position_str}' position on{bet_display} for ${wager_decimal:.2f}."

    client = bigquery.Client()
    project_id = os.environ.get('GCP_PROJECT')
    if not project_id:
        print("Warning: GCP_PROJECT environment variable not set. Using default project for BigQuery.")
        table_id = '`ISE.ActivePurchasedBets`'
    else:
        table_id = f'`{project_id}.ISE.ActivePurchasedBets`'

    wager_decimal = decimal.Decimal(str(wager_amount))
    bet_display = f" '{bet_name}'" if bet_name else " this bet"
    position_str = "Yes" if user_took_yes else "No"

    check_query = f"""
        SELECT WagerAmount 
        FROM {table_id}
        WHERE UserID = @user_id AND BetID = @bet_id AND UserTookYes = @user_took_yes
    """
    check_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("bet_id", "STRING", bet_id),
            bigquery.ScalarQueryParameter("user_took_yes", "BOOL", user_took_yes),
        ]
    )

    try:
        check_job = client.query(check_query, job_config=check_config)
        results = list(check_job.result())
        
        existing_amount = decimal.Decimal(str(results[0].WagerAmount)) if results else decimal.Decimal('0.0')

        if mode == 'Sell':
            if not results:
                return False, f"You do not own the '{position_str}' position on{bet_display} to sell."
            if existing_amount < wager_decimal:
                return False, f"You cannot sell more than you own (${existing_amount:.2f}) of the '{position_str}' position on{bet_display}."
            
            new_amount = existing_amount - wager_decimal
            if new_amount == 0:
                sql = f"DELETE FROM {table_id} WHERE UserID = @user_id AND BetID = @bet_id AND UserTookYes = @user_took_yes"
                params = [
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("bet_id", "STRING", bet_id),
                    bigquery.ScalarQueryParameter("user_took_yes", "BOOL", user_took_yes),
                ]
            else:
                sql = f"UPDATE {table_id} SET WagerAmount = @new_amount WHERE UserID = @user_id AND BetID = @bet_id AND UserTookYes = @user_took_yes"
                params = [
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("bet_id", "STRING", bet_id),
                    bigquery.ScalarQueryParameter("user_took_yes", "BOOL", user_took_yes),
                    bigquery.ScalarQueryParameter("new_amount", "NUMERIC", new_amount),
                ]
            
            client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
            return True, f"Successfully sold ${wager_decimal:.2f} of the '{position_str}' position on{bet_display}."

        else:  # mode == 'Buy'
            # Check if user owns the opposite position for this bet
            opposite_check_query = f"""
                SELECT 1
                FROM {table_id}
                WHERE UserID = @user_id AND BetID = @bet_id AND UserTookYes = @opposite_user_took_yes
            """
            opposite_check_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("bet_id", "STRING", bet_id),
                    bigquery.ScalarQueryParameter("opposite_user_took_yes", "BOOL", not user_took_yes),
                ]
            )
            if list(client.query(opposite_check_query, job_config=opposite_check_config).result()):
                return False, f"You cannot buy this position on{bet_display} as you already own the opposite position."

            if results:
                new_amount = existing_amount + wager_decimal
                sql = f"UPDATE {table_id} SET WagerAmount = @new_amount WHERE UserID = @user_id AND BetID = @bet_id AND UserTookYes = @user_took_yes"
                params = [
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("bet_id", "STRING", bet_id),
                    bigquery.ScalarQueryParameter("user_took_yes", "BOOL", user_took_yes),
                    bigquery.ScalarQueryParameter("new_amount", "NUMERIC", new_amount),
                ]
                client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
                return True, f"Successfully added ${wager_decimal:.2f} to your existing '{position_str}' wager on{bet_display}."
            else:
                sql = f"INSERT INTO {table_id} (UserID, BetID, UserTookYes, WagerAmount) VALUES (@user_id, @bet_id, @user_took_yes, @wager_amount)"
                params = [
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("bet_id", "STRING", bet_id),
                    bigquery.ScalarQueryParameter("user_took_yes", "BOOL", user_took_yes),
                    bigquery.ScalarQueryParameter("wager_amount", "NUMERIC", wager_decimal),
                ]
                client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
                return True, f"Successfully purchased the '{position_str}' position on{bet_display} for ${wager_decimal:.2f}."

    except Exception as e:
        print(f"Error processing transaction in BigQuery: {e}")
        return False, "Database error occurred during transaction."


def get_user_profile(user_id):
    """Returns information about the given user.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    if user_id not in users:
        raise ValueError(f'User {user_id} not found.')
    return users[user_id]


def get_user_id_by_username(username):
    """Return a local user id from a username or direct user id lookup."""
    if not username:
        return None
    username = username.strip()
    if username in users:
        return username
    for user_id, profile in users.items():
        if profile.get('username') == username:
            return user_id
    return None


def create_user(username, full_name=None, date_of_birth=None, friends=None):
    """Create a simple local user profile for signup and testing."""
    if not username or not username.strip():
        raise ValueError('Username is required.')
    normalized_username = username.strip()
    if get_user_id_by_username(normalized_username):
        raise ValueError('Username already exists.')

    users[normalized_username] = {
        'full_name': full_name or normalized_username.title(),
        'username': normalized_username,
        'date_of_birth': date_of_birth or '2000-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': friends or [],
    }
    return normalized_username


def get_user_friends(user_id):
    """Return a list of friend profiles for the given user."""
    profile = get_user_profile(user_id)
    friends = []
    for friend_id in profile.get('friends', []):
        if friend_id in users:
            friend_profile = users[friend_id]
            friends.append({
                'user_id': friend_id,
                'username': friend_profile['username'],
                'full_name': friend_profile['full_name'],
                'profile_image': friend_profile.get('profile_image'),
            })
    return friends


def get_user_posts(user_id):
    """Returns a list of a user's posts.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    content = random.choice([
        'Had a great workout today!',
        'The AI really motivated me to push myself further, I ran 10 miles!',
    ])
    return [{
        'user_id': user_id,
        'post_id': 'post1',
        'timestamp': '2024-01-01 00:00:00',
        'content': content,
        'image': 'image_url',
    }]


def get_genai_advice(user_id):
    """Returns the most recent advice from the genai model.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    advice = random.choice([
        'Your heart rate indicates you can push yourself further. You got this!',
        "You're doing great! Keep up the good work.",
        'You worked hard yesterday, take it easy today.',
        'You have burned 100 calories so far today!',
    ])
    image = random.choice([
        'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        None,
    ])
    return {
        'advice_id': 'advice1',
        'timestamp': '2024-01-01 00:00:00',
        'content': advice,
        'image': image,
    }


def get_bet_data(bet_id):
    """Retrieves data for a specific bet from BigQuery or local fallback data.
    
    Returns a dictionary with keys corresponding to the arguments 
    of display_individual_bet_summary, or None if the bet is not found.
    """
    project_id = os.environ.get('GCP_PROJECT')
    if bigquery is None or not project_id:
        available = get_available_bets()
        for bet in available:
            if bet.get('bet_id') == bet_id:
                return {
                    'bet_name': bet['bet_name'],
                    'yes_value': float(bet['yes_value']),
                    'no_value': float(bet['no_value']),
                    'yes_percent': float(bet['yes_percent']),
                    'no_percent': float(bet['no_percent']),
                    'rules': bet['rules'],
                    'bet_image_link': bet['bet_image_link'],
                }
        return None

    client = bigquery.Client()
    if not project_id:
        print("Warning: GCP_PROJECT environment variable not set. Using default project for BigQuery.")
        table_name = '`ISE.Bets`'
    else:
        table_name = f'`{project_id}.ISE.Bets`'

    client = bigquery.Client()
    query = f"""
        SELECT BetName, YesValue, NoValue, YesPercent, NoPercent, Rules, Image 
        FROM {table_name}
        WHERE BetID = @bet_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("bet_id", "STRING", bet_id)
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        for row in query_job.result():
            return {
                'bet_name': row.BetName,
                'yes_value': float(row.YesValue) if row.YesValue is not None else 0.0,
                'no_value': float(row.NoValue) if row.NoValue is not None else 0.0,
                'yes_percent': float(row.YesPercent) if row.YesPercent is not None else 0.0,
                'no_percent': float(row.NoPercent) if row.NoPercent is not None else 0.0,
                'rules': row.Rules,
                'bet_image_link': row.Image,
            }
    except Exception as e:
        print(f"Error fetching bet from BigQuery: {e}")
        
    return None

def get_friends_activity(user_id):
    """Returns bets that the user's friends are currently betting on from BigQuery."""
    if bigquery is None:
        # Fallback for local development when BigQuery is not available
        return [
            {
                "bet_id": "btc-100k",
                "bet_name": "Will Bitcoin hit $100k?",
                "yes_value": 0.72,
                "no_value": 0.28,
                "yes_percent": 72.0,
                "no_percent": 28.0,
                "category": "Crypto",
                "friends": ["Shavaughn", "Sangam", "Brian", "Kameron"]
            },
            {
                "bet_id": "eth-5k",
                "bet_name": "Will Ethereum reach $5,000 in 2025?",
                "yes_value": 0.45,
                "no_value": 0.55,
                "yes_percent": 45.0,
                "no_percent": 55.0,
                "category": "Crypto",
                "friends": ["Remi", "Blake"]
            }
        ]

    client = bigquery.Client()
    project_id = os.environ.get('GCP_PROJECT')
    prefix = f"`{project_id}.ISE" if project_id else "`ISE"
    
    # This query finds friends via the Friendships table and joins their active bets
    query = f"""
        WITH user_friends AS (
            SELECT UserID2 as friend_id FROM {prefix}.Friendships` WHERE UserID1 = @user_id
            UNION DISTINCT
            SELECT UserID1 as friend_id FROM {prefix}.Friendships` WHERE UserID2 = @user_id
        ),
        activity AS (
            SELECT 
                b.BetID, b.BetName, b.YesValue, b.NoValue, b.YesPercent, b.NoPercent,
                u.Name as friend_name
            FROM {prefix}.ActivePurchasedBets` apb
            JOIN user_friends f ON apb.UserID = f.friend_id
            JOIN {prefix}.Users` u ON apb.UserID = u.UserID
            JOIN {prefix}.Bets` b ON apb.BetID = b.BetID
        )
        SELECT 
            BetID, BetName, YesValue, NoValue, YesPercent, NoPercent,
            ARRAY_AGG(DISTINCT friend_name) as friends
        FROM activity
        GROUP BY 1, 2, 3, 4, 5, 6
    """
    
    try:
        query_job = client.query(query, job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        ))
        results = []
        for row in query_job.result():
            results.append({
                'bet_id': row.BetID,
                'bet_name': row.BetName,
                'yes_value': float(row.YesValue) if row.YesValue is not None else 0.0,
                'no_value': float(row.NoValue) if row.NoValue is not None else 0.0,
                'yes_percent': row.YesPercent,
                'no_percent': row.NoPercent,
                'category': 'Trending', # Fallback category
                'friends': list(row.friends),
            })
        return results
    except Exception as e:
        print(f"Error fetching friends activity from BigQuery: {e}")
        return []