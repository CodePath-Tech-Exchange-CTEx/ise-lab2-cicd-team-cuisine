import pytest

import home


def test_login_new_user_sets_session_state(monkeypatch):
    # Ensure clean login state
    monkeypatch.setitem(home.st.session_state, 'logged_in', False)
    monkeypatch.setitem(home.st.session_state, 'username', None)

    def fake_text_input(label, key=None, type=None):
        return 'new_test_user' if 'Username' in label else 'supersecret'

    def fake_button(label, key=None):
        return True

    monkeypatch.setattr(home.st, 'text_input', fake_text_input)
    monkeypatch.setattr(home.st, 'button', fake_button)

    result = home.login()

    assert home.st.session_state.logged_in is True
    assert home.st.session_state.username == 'new_test_user'
    assert result is False


def test_login_fallback_username_if_blank(monkeypatch):
    monkeypatch.setitem(home.st.session_state, 'logged_in', False)
    monkeypatch.setitem(home.st.session_state, 'username', None)

    def fake_text_input(label, key=None, type=None):
        return ''

    def fake_button(label, key=None):
        return True

    monkeypatch.setattr(home.st, 'text_input', fake_text_input)
    monkeypatch.setattr(home.st, 'button', fake_button)

    result = home.login()

    assert home.st.session_state.logged_in is True
    assert home.st.session_state.username == home.userId
    assert result is False
