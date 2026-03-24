#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

import random
try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

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
        print("google-cloud-bigquery is not installed.")
        return []

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


def get_user_profile(user_id):
    """Returns information about the given user.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    if user_id not in users:
        raise ValueError(f'User {user_id} not found.')
    return users[user_id]


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
    """Retrieves data for a specific bet from the ISE dataset in BigQuery.
    
    Returns a dictionary with keys corresponding to the arguments 
    of display_individual_bet_summary, or None if the bet is not found.
    """
    if bigquery is None:
        print("google-cloud-bigquery is not installed.")
        return None
        
    client = bigquery.Client()
    query = """
        SELECT BetName, YesValue, NoValue, YesPercent, NoPercent, Rules, Image 
        FROM `ISE.Bets`
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