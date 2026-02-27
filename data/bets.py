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
    {
        "bet_id": "eth-5k",
        "bet_name": "Will Ethereum reach $5,000 in 2025?",
        "bet_image_link": None,
        "yes_value": 0.45,
        "no_value": 0.55,
        "yes_percent": 45,
        "no_percent": 55,
        "rules": "Resolves YES if ETH trades at or above $5,000 on any major exchange before Jan 1 2026.",
        "category": "Crypto",
    },
    {
        "bet_id": "sol-top5",
        "bet_name": "Will Solana be top 5 by market cap by end of 2025?",
        "bet_image_link": None,
        "yes_value": 0.62,
        "no_value": 0.38,
        "yes_percent": 62,
        "no_percent": 38,
        "rules": "Resolves YES if Solana ranks in top 5 by total market cap on CoinGecko as of Dec 31 2025.",
        "category": "Crypto",
    },
    {
        "bet_id": "president-2028",
        "bet_name": "Will the incumbent win the 2028 US presidential election?",
        "bet_image_link": None,
        "yes_value": 0.35,
        "no_value": 0.65,
        "yes_percent": 35,
        "no_percent": 65,
        "rules": "Resolves YES if the sitting US president wins the popular vote in the 2028 general election.",
        "category": "Politics",
    },
    {
        "bet_id": "senate-majority",
        "bet_name": "Will Democrats hold Senate majority after 2026 midterms?",
        "bet_image_link": None,
        "yes_value": 0.52,
        "no_value": 0.48,
        "yes_percent": 52,
        "no_percent": 48,
        "rules": "Resolves YES if Democrats control 51+ Senate seats after the 2026 midterm elections.",
        "category": "Politics",
    },
    {
        "bet_id": "nba-champ-2025",
        "bet_name": "Will a Western Conference team win NBA Finals 2025?",
        "bet_image_link": None,
        "yes_value": 0.58,
        "no_value": 0.42,
        "yes_percent": 58,
        "no_percent": 42,
        "rules": "Resolves YES if the 2025 NBA champion is from the Western Conference.",
        "category": "Sports",
    },
    {
        "bet_id": "worldcup-2026",
        "bet_name": "Will USA reach semifinals of FIFA World Cup 2026?",
        "bet_image_link": None,
        "yes_value": 0.28,
        "no_value": 0.72,
        "yes_percent": 28,
        "no_percent": 72,
        "rules": "Resolves YES if the USA men's national team reaches the semifinals of the 2026 World Cup.",
        "category": "Sports",
    },
    {
        "bet_id": "ai-agi-2027",
        "bet_name": "Will an AI system pass the AGI benchmark by 2027?",
        "bet_image_link": None,
        "yes_value": 0.22,
        "no_value": 0.78,
        "yes_percent": 22,
        "no_percent": 78,
        "rules": "Resolves YES if a system is certified as passing the designated AGI benchmark before Jan 1 2028.",
        "category": "Other",
    },
]


def get_available_bets():
    """Return list of available bet dicts (for dashboard). Each has bet_id, bet_name, bet_image_link, yes_value, no_value, yes_percent, no_percent, rules, category."""
    return list(AVAILABLE_BETS)


def get_bet_categories():
    """Return ordered list of category names for filters/sections."""
    return list(BET_CATEGORIES)
