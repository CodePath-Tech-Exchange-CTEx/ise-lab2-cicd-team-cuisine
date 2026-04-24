from unittest.mock import MagicMock

import streamlit as st

import app


def test_render_topbar_logout_resets_guest_session(monkeypatch):
    st.session_state.username = "existing_user"
    st.session_state.logged_in = True

    button_calls = []

    def fake_button(label, key=None, **kwargs):
        button_calls.append((label, key))
        return key == "logout_button"

    monkeypatch.setattr(st, "button", fake_button)
    monkeypatch.setattr(st, "markdown", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(st, "columns", lambda count: [MagicMock(), MagicMock()])

    app.render_topbar()

    assert st.session_state.username == ""
    assert st.session_state.logged_in is False
    assert ("Log out", "logout_button") in button_calls


def test_render_post_creator_adds_post_and_displays(monkeypatch):
    posted = []
    st.session_state.user_posts = []
    st.session_state.username = "alice"

    monkeypatch.setattr(st, "text_area", lambda *args, **kwargs: "This is a new post")
    monkeypatch.setattr(st, "button", lambda label, key=None, **kwargs: key == "submit_new_post")
    monkeypatch.setattr(st, "success", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(st, "write", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(st, "markdown", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(st, "expander", lambda *args, **kwargs: MagicMock(__enter__=lambda self: self, __exit__=lambda self, exc_type, exc, tb: None))

    def fake_display_post(username, user_image, timestamp, content, post_image):
        posted.append({
            "user_id": username,
            "content": content,
            "timestamp": timestamp,
        })

    monkeypatch.setattr(app, "display_post", fake_display_post)
    monkeypatch.setattr(app, "get_user_posts", lambda username: st.session_state.user_posts)
    monkeypatch.setattr(app, "get_user_profile", lambda username: {"profile_image": ""})

    app.render_post_creator("alice")

    assert len(st.session_state.user_posts) == 1
    assert st.session_state.user_posts[0]["user_id"] == "alice"
    assert posted[0]["content"] == "This is a new post"
