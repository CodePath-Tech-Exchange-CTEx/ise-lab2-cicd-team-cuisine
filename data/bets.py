"""
Hardcoded bet data for the available-bets dashboard.
Replace with Kalshi/Polymarket API later.
"""

BET_CATEGORIES = ["Crypto", "Politics", "Sports", "Other"]

AVAILABLE_BETS = [
    {
        "bet_id": "btc-100k",
        "bet_name": "Will Bitcoin hit $100k?",
        "bet_image_link": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/240px-Bitcoin.svg.png",
        "yes_value": 0.72,
        "no_value": 0.28,
        "yes_percent": 72,
        "no_percent": 28,
        "rules": "Resolves YES if Bitcoin closes above $100,000 USD on any major exchange before Dec 31 2026.",
        "category": "Crypto",
    },
    # Add more hardcoded bets here; keep category in BET_CATEGORIES.
]


def get_available_bets():
    """Return list of available bet dicts (for dashboard). Each has bet_id, bet_name, bet_image_link, yes_value, no_value, yes_percent, no_percent, rules, category."""
    return list(AVAILABLE_BETS)


def get_bet_categories():
    """Return ordered list of category names for filters/sections."""
    return list(BET_CATEGORIES)
