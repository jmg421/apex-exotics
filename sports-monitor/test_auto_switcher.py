#!/usr/bin/env python3
"""
Test auto-switching logic for March Madness
"""

def test_should_auto_switch():
    """Test auto-switch trigger conditions"""
    from auto_switcher import should_auto_switch
    
    # High upset score (≥7) should trigger
    game1 = {'Upset_Score': 7, 'live': True}
    assert should_auto_switch(game1) == (True, "High upset potential (score: 7)")
    
    # Low upset score should not trigger
    game2 = {'Upset_Score': 5, 'live': True}
    assert should_auto_switch(game2) == (False, None)
    
    # Not live should not trigger
    game3 = {'Upset_Score': 8, 'live': False}
    assert should_auto_switch(game3) == (False, None)
    
    print("✅ test_should_auto_switch passed")

def test_get_top_upset_game():
    """Test finding highest priority game"""
    from auto_switcher import get_top_upset_game
    
    games = [
        {'Matchup': 'Game A', 'Upset_Score': 6, 'channel': 811, 'live': True},
        {'Matchup': 'Game B', 'Upset_Score': 8, 'channel': 809, 'live': True},
        {'Matchup': 'Game C', 'Upset_Score': 7, 'channel': 812, 'live': False}
    ]
    
    top = get_top_upset_game(games, min_score=7)
    assert top['channel'] == 809  # Highest score + live
    assert top['Upset_Score'] == 8
    
    print("✅ test_get_top_upset_game passed")

if __name__ == '__main__':
    test_should_auto_switch()
    test_get_top_upset_game()
    print("\n✅ All auto-switcher tests passed!")
