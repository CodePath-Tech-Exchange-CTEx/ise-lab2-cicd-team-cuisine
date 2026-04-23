from unittest.mock import MagicMock

import streamlit as st

from modules import compute_trade_metrics, display_comment_thread, display_trade_summary


def test_compute_trade_metrics_sums_all_values():
    trades = [
        {"contract_name": "A", "quantity": 2, "price": 10},
        {"contract_name": "B", "quantity": 1, "price": 5},
    ]

    metrics = compute_trade_metrics(trades)

    assert metrics["total_trades"] == 2
    assert metrics["total_volume"] == 3
    assert metrics["total_value"] == 25


def test_display_comment_thread_renders_nested_replies(monkeypatch):
    calls = []
    monkeypatch.setattr(st, "markdown", lambda text, **kwargs: calls.append(("markdown", text)))
    monkeypatch.setattr(st, "info", lambda message, **kwargs: calls.append(("info", message)))

    comment = {
        "comment_id": "c1",
        "author": "alice",
        "content": "Hello world",
        "timestamp": "2026-04-20",
        "replies": [
            {
                "comment_id": "c2",
                "author": "bob",
 "content": "Reply here",
                "timestamp": "2026-04-21",
                "replies": [],
            }
        ],
    }

    display_comment_thread([comment])

    assert any(item[0] == "markdown" and "Hello world" in item[1] for item in calls)
    assert any(item[0] == "markdown" and "Reply here" in item[1] for item in calls)


def test_display_trade_summary_renders_metrics(monkeypatch):
    metrics = []
    monkeypatch.setattr(st, "header", lambda *args, **kwargs: metrics.append(("header", args)))
    monkeypatch.setattr(st, "metric", lambda label, value, **kwargs: metrics.append(("metric", label, value)))
    monkeypatch.setattr(st, "table", lambda *args, **kwargs: metrics.append(("table", args)))

    trades = [
        {"contract_name": "A", "quantity": 2, "price": 10},
        {"contract_name": "B", "quantity": 1, "price": 5},
    ]

    display_trade_summary(trades)

    assert any(call[0] == "metric" and call[1] == "Total trades" and call[2] == 2 for call in metrics)
    assert any(call[0] == "metric" and call[1] == "Total volume" and call[2] == 3 for call in metrics)
    assert any(call[0] == "metric" and call[1] == "Total value" and "$25.00" in call[2] for call in metrics)
