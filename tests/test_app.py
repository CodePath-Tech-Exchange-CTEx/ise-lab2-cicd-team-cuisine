import importlib
import streamlit as st
from unittest.mock import MagicMock

import home


class SessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value


def _fake_text_input(label, key=None, type=None):
    if key == 'login_username':
        return ''
    if key == 'login_password':
        return ''
    return ''


def test_login_blanks_use_default_user(monkeypatch):
    monkeypatch.setattr(st, 'session_state', SessionState())
    monkeypatch.setattr(st, 'radio', lambda *args, **kwargs: 'Log in')
    monkeypatch.setattr(st, 'text_input', _fake_text_input)
    monkeypatch.setattr(st, 'button', lambda *args, **kwargs: True)
    monkeypatch.setattr(home, 'get_user_id_by_username', lambda username: None)
    monkeypatch.setattr(home, 'create_user', lambda username, full_name, date_of_birth: 'user1')

    result = home.login()

    assert result is False
    assert st.session_state['logged_in'] is True
    assert st.session_state['username'] == 'user1'


def test_signup_creates_new_user_and_redirects(monkeypatch):
    monkeypatch.setattr(st, 'session_state', SessionState())
    monkeypatch.setattr(st, 'radio', lambda *args, **kwargs: 'Sign up')

    def fake_text_input(label, key=None, type=None):
        if key == 'signup_username':
            return 'newuser'
        if key == 'signup_full_name':
            return 'New User'
        if key == 'signup_dob':
            return '1995-05-05'
        return ''

    monkeypatch.setattr(st, 'text_input', fake_text_input)
    monkeypatch.setattr(st, 'button', lambda *args, **kwargs: True)
    monkeypatch.setattr(home, 'get_user_id_by_username', lambda username: None)
    monkeypatch.setattr(home, 'create_user', lambda username, full_name, date_of_birth: 'newuser_id')

    result = home.login()

    assert result is False
    assert st.session_state['logged_in'] is True
    assert st.session_state['username'] == 'newuser_id'
    assert st.session_state['next_page'] == 'profile'
