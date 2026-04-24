import importlib.util
import os
import uuid
import streamlit as st
import data
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


def _make_context_manager():
    cm = MagicMock()
    cm.__enter__.return_value = cm
    cm.__exit__.return_value = False
    return cm


def _patch_streamlit_basics(monkeypatch):
    monkeypatch.setattr(st, 'set_page_config', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'title', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'write', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'markdown', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'info', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'error', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'image', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'subheader', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'caption', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'header', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'metric', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'table', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'divider', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'text_area', lambda *args, **kwargs: "")
    monkeypatch.setattr(st, 'query_params', {})
    monkeypatch.setattr(st, 'selectbox', lambda *args, **kwargs: "All")
    monkeypatch.setattr(st, 'rerun', lambda *args, **kwargs: None)
    monkeypatch.setattr(st, 'switch_page', lambda *args, **kwargs: None)
    def _mock_columns(count, *args, **kwargs):
        length = len(count) if isinstance(count, (list, tuple)) else count
        return [_make_context_manager() for _ in range(length)]

    monkeypatch.setattr(st, 'columns', _mock_columns)
    monkeypatch.setattr(st, 'container', lambda *args, **kwargs: _make_context_manager())


from unittest.mock import MagicMock


def test_friends_activity_page_requires_login(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    mock_warning = MagicMock()
    mock_button = MagicMock(return_value=False)
    mock_stop = MagicMock(side_effect=RuntimeError("st.stop called"))

    monkeypatch.setattr(st, 'warning', mock_warning)
    monkeypatch.setattr(st, 'button', mock_button)
    monkeypatch.setattr(st, 'stop', mock_stop)

    with pytest.raises(RuntimeError, match="st.stop called"):
        _load_script(os.path.join("pages", "4_Friends_Activity.py"))

    mock_warning.assert_called_once_with("Please log in to view friends activity.")
    mock_button.assert_any_call("← Back to Dashboard")
    mock_stop.assert_called_once()


def test_profile_page_requires_login(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    mock_warning = MagicMock()
    mock_button = MagicMock(return_value=False)
    mock_stop = MagicMock(side_effect=RuntimeError("st.stop called"))

    monkeypatch.setattr(st, 'warning', mock_warning)
    monkeypatch.setattr(st, 'button', mock_button)
    monkeypatch.setattr(st, 'stop', mock_stop)

    with pytest.raises(RuntimeError, match="st.stop called"):
        _load_script(os.path.join("pages", "5_Profile.py"))

    mock_warning.assert_called_once_with("Please log in to view your profile and place bets.")
    mock_button.assert_any_call("← Back to Dashboard")
    mock_stop.assert_called_once()


def test_profile_page_renders_with_valid_user(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    st.session_state.logged_in = True
    st.session_state.username = 'user1'
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
    st.session_state.logged_in = True
    st.session_state.username = 'user1'
    monkeypatch.setattr(data_fetcher, 'get_friends_activity', lambda uid: [
        {'bet_id': 'bet1', 'bet_name': 'Top Bet', 'yes_percent': 55, 'no_percent': 45, 'yes_value': 15.0, 'no_value': 10.0, 'friends': ['user2', 'user3']},
    ])
    monkeypatch.setattr(st, 'toggle', lambda *args, **kwargs: True)
    mock_activity_card = MagicMock()
    monkeypatch.setattr(modules, 'display_friends_activity_card', mock_activity_card)
    monkeypatch.setattr(st, 'button', MagicMock(return_value=False))

    _load_script(os.path.join("pages", "4_Friends_Activity.py"))

    mock_activity_card.assert_called_once()


def test_available_bets_page_renders_list(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    monkeypatch.setattr(data, 'get_bet_categories', lambda: ['Sports'])
    monkeypatch.setattr(data, 'get_available_bets', lambda: [
        {
            'bet_id': 'bet1',
            'bet_name': 'Big Match Winners',
            'category': 'Sports',
            'yes_percent': 55,
            'no_percent': 45,
            'yes_value': 25.0,
            'no_value': 20.0,
            'rules': 'Resolves if the home team wins.',
        }
    ])
    mock_display = MagicMock()
    monkeypatch.setattr(modules, 'display_individual_bet_summary', mock_display)
    mock_button = MagicMock(return_value=False)
    monkeypatch.setattr(st, 'button', mock_button)
    mock_columns = MagicMock(side_effect=lambda count, *args, **kwargs: [_make_context_manager() for _ in range(count)])
    monkeypatch.setattr(st, 'columns', mock_columns)

    _load_script(os.path.join("pages", "1_Available_bets.py"))

    mock_display.assert_not_called()
    mock_columns.assert_called_once_with(3)


def test_available_bets_page_shows_selected_bet(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    st.session_state.dashboard_selected_bet = {
        'bet_id': 'bet1',
        'bet_name': 'Selected Bet',
        'category': 'Sports',
        'yes_percent': 70,
        'no_percent': 30,
        'yes_value': 40.0,
        'no_value': 18.0,
        'rules': 'Resolves if the chosen team scores first.',
    }
    mock_display = MagicMock()
    monkeypatch.setattr(modules, 'display_individual_bet_summary', mock_display)
    monkeypatch.setattr(st, 'button', MagicMock(return_value=False))
    mock_stop = MagicMock(side_effect=RuntimeError("st.stop called"))
    monkeypatch.setattr(st, 'stop', mock_stop)

    with pytest.raises(RuntimeError, match="st.stop called"):
        _load_script(os.path.join("pages", "1_Available_bets.py"))

    mock_display.assert_called_once()
    mock_stop.assert_called_once()


def test_bet_detail_page_displays_bet_and_comments(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    monkeypatch.setattr(st, 'query_params', {})
    monkeypatch.setattr(data_fetcher, 'get_bet_data', lambda bet_id: {
        'bet_name': 'Test Bet',
        'bet_image_link': 'https://example.com/image.png',
        'yes_value': 0.55,
        'no_value': 0.45,
        'yes_percent': 55.0,
        'no_percent': 45.0,
        'rules': 'Resolves if test conditions are met.',
    })
    mock_display = MagicMock()
    mock_comments = MagicMock()
    monkeypatch.setattr(modules, 'display_individual_bet_summary', mock_display)
    monkeypatch.setattr(modules, 'display_comment_thread', mock_comments)

    _load_script(os.path.join("pages", "2_Bet_detail.py"))

    mock_display.assert_called_once()
    mock_comments.assert_called_once()


def test_ai_advice_page_main_renders_buttons(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    monkeypatch.setattr(modules, 'render_sidebar', MagicMock())
    mock_button = MagicMock(return_value=False)
    monkeypatch.setattr(st, 'button', mock_button)

    module = _load_script(os.path.join("pages", "3_AI_Advice.py"))
    module.main()

    assert mock_button.call_count == 4


def test_render_sidebar_shows_balance_and_navigation(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    st.session_state.logged_in = True
    st.session_state.username = 'user1'
    monkeypatch.setattr(modules, 'get_user_profile', lambda uid: {'balance': 6543.21})
    mock_metric = MagicMock()
    monkeypatch.setattr(st, 'metric', mock_metric)
    mock_button = MagicMock(return_value=False)
    monkeypatch.setattr(st, 'button', mock_button)

    modules.render_sidebar()

    mock_metric.assert_called_once_with('Wallet balance', '$6,543.21')
    mock_button.assert_any_call('🏠 Community', key='sidebar_community', use_container_width=True)
    mock_button.assert_any_call('📈 Marketplace', key='sidebar_marketplace', use_container_width=True)
    mock_button.assert_any_call('🤖 AI Insights', key='sidebar_ai_insights', use_container_width=True)
    mock_button.assert_any_call('👤 My Profile', key='sidebar_my_profile', use_container_width=True)


def test_available_bets_page_selects_bet(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    monkeypatch.setattr(data, 'get_bet_categories', lambda: ['Sports', 'Politics'])
    monkeypatch.setattr(data, 'get_available_bets', lambda: [
        {
            'bet_id': 'bet1',
            'bet_name': 'Home Team Wins',
            'category': 'Sports',
            'yes_percent': 55,
            'no_percent': 45,
            'yes_value': 25.0,
            'no_value': 20.0,
            'rules': 'Resolves if the home team wins.',
        },
        {
            'bet_id': 'bet2',
            'bet_name': 'Election Outcome',
            'category': 'Politics',
            'yes_percent': 60,
            'no_percent': 40,
            'yes_value': 30.0,
            'no_value': 22.0,
            'rules': 'Resolves if candidate A wins.',
        }
    ])
    monkeypatch.setattr(st, 'selectbox', lambda *args, **kwargs: 'Sports')
    def mock_button(label, key=None, *args, **kwargs):
        return key == 'view_bet1'
    monkeypatch.setattr(st, 'button', mock_button)
    monkeypatch.setattr(st, 'rerun', lambda *args, **kwargs: None)

    _load_script(os.path.join('pages', '1_Available_bets.py'))

    assert st.session_state.dashboard_selected_bet['bet_id'] == 'bet1'
    assert st.session_state.dashboard_selected_bet['category'] == 'Sports'


def test_bet_detail_page_shows_error_when_bet_missing(monkeypatch):
    _patch_streamlit_basics(monkeypatch)
    monkeypatch.setattr(st, 'query_params', {})
    monkeypatch.setattr(data_fetcher, 'get_bet_data', lambda bet_id: None)
    mock_error = MagicMock()
    monkeypatch.setattr(st, 'error', mock_error)

    _load_script(os.path.join('pages', '2_Bet_detail.py'))

    mock_error.assert_called_once()
