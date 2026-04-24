import streamlit as st
import pytest


class SessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value


@pytest.fixture(autouse=True)
def streamlit_session_state(monkeypatch):
    state = SessionState()
    monkeypatch.setattr(st, 'session_state', state)
    monkeypatch.setattr(st, 'experimental_rerun', lambda: None, raising=False)
    return state
