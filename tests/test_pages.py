import importlib.util
import os
import uuid
import streamlit as st
import data_fetcher
import modules
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load_script(filename):
    path = os.path.join(ROOT, filename)
    module_name = f"test_{os.path.basename(filename).replace('.', '_')}_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _patch_streamlit_basics(monkeypatch):
    monkeypatch.setattr(st, 'set_page_config', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'title', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'write', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'markdown', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'info', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'image', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'subheader', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'caption', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'header', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'metric', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'table', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'divider', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'columns', lambda *args, **kwargs: [MagicMock(), MagicMock()])


from unittest.mock import MagicMock


def test_friends_activity_page_requires_login(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    monkeypatch.setattr(st, 'session_state', {})
    mock_warning = MagicMock()
    mock_button = MagicMock(return_value=False)
    mock_stop = MagicMock(side_effect=RuntimeError("st.stop called"))

    monkeypatch.setattr(st, 'warning', mock_warning)
    monkeypatch.setattr(st, 'button', mock_button)
    monkeypatch.setattr(st, 'stop', mock_stop)

    with pytest.raises(RuntimeError, match="st.stop called"):
        _load_script(os.path.join("pages", "4_Friends_Activity.py"))

    mock_warning.assert_called_once_with("Please log in to view friends activity.")
    mock_button.assert_called_once()
    mock_stop.assert_called_once()


def test_profile_page_requires_login(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    monkeypatch.setattr(st, 'session_state', {})
    mock_warning = MagicMock()
    mock_button = MagicMock(return_value=False)
    mock_stop = MagicMock(side_effect=RuntimeError("st.stop called"))

    monkeypatch.setattr(st, 'warning', mock_warning)
    monkeypatch.setattr(st, 'button', mock_button)
    monkeypatch.setattr(st, 'stop', mock_stop)

    with pytest.raises(RuntimeError, match="st.stop called"):
        _load_script(os.path.join("pages", "5_Profile.py"))

    mock_warning.assert_called_once_with("Please log in to view your profile and place bets.")
    mock_button.assert_called_once()
    mock_stop.assert_called_once()


def test_profile_page_renders_with_valid_user(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    monkeypatch.setattr(st, 'session_state', {'logged_in': True, 'username': 'user1'})
    monkeypatch.setattr(data_fetcher, 'get_user_profile', lambda uid: {
        'full_name': 'Test User',
        'username': 'testuser',
        'date_of_birth': '1995-01-01',
        'profile_image': 'https://example.com/avatar.png',
    })
    monkeypatch.setattr(data_fetcher, 'get_user_friends', lambda uid: [
        {'full_name': 'Friend One', 'username': 'friend1'},
        {'full_name': 'Friend Two', 'username': 'friend2'},
    ])
    monkeypatch.setattr(data_fetcher, 'get_user_trades', lambda uid: [
        {'quantity': 1, 'price': 20.0, 'symbol': 'Test Bet'},
    ])
    monkeypatch.setattr(data_fetcher, 'get_friends_activity', lambda uid: [
        {'bet_id': 'bet1', 'bet_name': 'Lucky Bet', 'yes_percent': 70, 'no_percent': 30, 'yes_value': 10.0, 'no_value': 5.0, 'friends': ['friend1']},
    ])

    mock_trade_summary = MagicMock()
    mock_activity_card = MagicMock()
    monkeypatch.setattr(modules, 'display_trade_summary', mock_trade_summary)
    monkeypatch.setattr(modules, 'display_friends_activity_card', mock_activity_card)
    monkeypatch.setattr(st, 'button', MagicMock(return_value=False))

    module = _load_script(os.path.join("pages", "5_Profile.py"))

    mock_trade_summary.assert_called_once()
    mock_activity_card.assert_called_once()
    assert module is not None


def test_friends_activity_page_renders_activity(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    monkeypatch.setattr(st, 'session_state', {'logged_in': True, 'username': 'user1'})
    monkeypatch.setattr(data_fetcher, 'get_friends_activity', lambda uid: [
        {'bet_id': 'bet1', 'bet_name': 'Top Bet', 'yes_percent': 55, 'no_percent': 45, 'yes_value': 15.0, 'no_value': 10.0, 'friends': ['user2', 'user3']},
    ])
    monkeypatch.setattr(st, 'toggle', lambda *args, **kwargs: True)
    mock_activity_card = MagicMock()
    monkeypatch.setattr(modules, 'display_friends_activity_card', mock_activity_card)
    monkeypatch.setattr(st, 'button', MagicMock(return_value=False))

    _load_script(os.path.join("pages", "4_Friends_Activity.py"))

    mock_activity_card.assert_called_once()
