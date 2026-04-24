import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import streamlit as st

SCRIPT_ROOT = Path(__file__).resolve().parents[2]


def _load_script(path):
    spec = importlib.util.spec_from_file_location("page_module", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_profile_page_without_friends_shows_no_friend_bets(monkeypatch):
    st.session_state.clear()
    st.session_state.username = "new_user"
    st.session_state.logged_in = True

    monkeypatch.setattr(st, "info", lambda message, **kwargs: setattr(st, "last_info", message))
    monkeypatch.setattr(st, "sidebar", MagicMock())
    monkeypatch.setattr(st, "image", lambda *args, **kwargs: None)

    import data_fetcher

    monkeypatch.setattr(data_fetcher, "get_user_friends", lambda username: [])
    monkeypatch.setattr(data_fetcher, "get_friends_activity", lambda username: [])
    monkeypatch.setattr(data_fetcher, "get_user_profile", lambda username: {"username": "new_user", "display_name": "New User"})

    _load_script(SCRIPT_ROOT / "pages" / "5_Profile.py")

    assert "No friend bets available right now." in st.last_info


def test_home_topbar_logout_transitions_to_guest(monkeypatch):
    import app

    st.session_state.clear()
    st.session_state.username = "existing_user"
    st.session_state.logged_in = True

    monkeypatch.setattr(st, "columns", lambda count: [MagicMock(), MagicMock()])
    monkeypatch.setattr(st, "markdown", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(st, "button", lambda label, key=None, **kwargs: key == "logout_button")

    app.render_topbar()

    assert st.session_state.logged_in is False
    assert st.session_state.username == ""
