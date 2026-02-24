# Data layer: hardcoded / static data (bets, etc.). Replace with API later.
from data.bets import get_available_bets, get_bet_categories

__all__ = ["get_available_bets", "get_bet_categories"]
