import pytest

from data_fetcher import LOCAL_ACTIVE_PURCHASED_BETS, process_bet_transaction


def setup_function(function):
    LOCAL_ACTIVE_PURCHASED_BETS.clear()


def test_process_bet_transaction_buy_opposite_position_is_rejected():
    LOCAL_ACTIVE_PURCHASED_BETS.append({
        'UserID': 'user1',
        'BetID': 'bet001',
        'UserTookYes': False,
        'WagerAmount': '10.00',
    })

    success, message = process_bet_transaction(
        user_id='user1',
        bet_id='bet001',
        user_took_yes=True,
        wager_amount='5.00',
        mode='Buy',
        bet_name='Opposing Bet',
    )

    assert success is False
    assert 'already own the opposite position' in message
    assert len(LOCAL_ACTIVE_PURCHASED_BETS) == 1


def test_process_bet_transaction_sell_exact_amount_removes_position():
    LOCAL_ACTIVE_PURCHASED_BETS.append({
        'UserID': 'user1',
        'BetID': 'bet002',
        'UserTookYes': True,
        'WagerAmount': '25.00',
    })

    success, message = process_bet_transaction(
        user_id='user1',
        bet_id='bet002',
        user_took_yes=True,
        wager_amount='25.00',
        mode='Sell',
        bet_name='Exact Bet',
    )

    assert success is True
    assert 'Successfully sold $25.00' in message
    assert all(record['BetID'] != 'bet002' for record in LOCAL_ACTIVE_PURCHASED_BETS)
