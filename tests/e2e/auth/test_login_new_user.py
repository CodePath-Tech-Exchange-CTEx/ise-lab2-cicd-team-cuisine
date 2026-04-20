import pytest


def test_login_new_user_sets_session_state(monkeypatch):
    import app

    # Ensure clean login state
    monkeypatch.setitem(app.st.session_state, 'logged_in', False)
    monkeypatch.setitem(app.st.session_state, 'username', None)

    def fake_text_input(label, type=None):
        return 'new_test_user' if 'Username' in label else 'supersecret'

    def fake_button(label, key=None):
        return True

    monkeypatch.setattr(app.st, 'text_input', fake_text_input)
    monkeypatch.setattr(app.st, 'button', fake_button)

    result = app.login()

    assert app.st.session_state.logged_in is True
    assert app.st.session_state.username == 'new_test_user'
    assert result is False


def test_login_fallback_username_if_blank(monkeypatch):
    import app

    monkeypatch.setitem(app.st.session_state, 'logged_in', False)
    monkeypatch.setitem(app.st.session_state, 'username', None)

    def fake_text_input(label, type=None):
        return ''

    def fake_button(label, key=None):
        return True

    monkeypatch.setattr(app.st, 'text_input', fake_text_input)
    monkeypatch.setattr(app.st, 'button', fake_button)

    result = app.login()

    assert app.st.session_state.logged_in is True
    assert app.st.session_state.username == app.userId
    assert result is False
