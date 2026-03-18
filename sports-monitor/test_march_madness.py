#!/usr/bin/env python3
"""
Test March Madness integration with EPG matching
"""

def test_match_game_to_channel():
    """Test matching upset alert games to EPG channels"""
    from march_madness_integration import match_games_to_channels
    
    # Mock EPG data
    epg_programs = [
        {'channel': 811, 'title': 'NC State vs Virginia ᴸᶦᵛᵉ'},
        {'channel': 812, 'title': 'SEC Inside - Auburn'},
        {'channel': 809, 'title': 'SportsCenter'}
    ]
    
    # Mock upset alerts
    upset_alerts = [
        {'Matchup': 'NC State vs Virginia', 'Upset_Score': 6},
        {'Matchup': 'Duke vs New Mexico', 'Upset_Score': 7}
    ]
    
    result = match_games_to_channels(upset_alerts, epg_programs)
    
    # Should match NC State game to channel 811
    assert len(result) == 2
    assert result[0]['channel'] == 811
    assert result[0]['live'] == True
    assert result[1]['channel'] is None  # Duke game not found
    assert result[1]['live'] == False
    
    print("✅ test_match_game_to_channel passed")

def test_fuzzy_match():
    """Test fuzzy matching for team names"""
    from march_madness_integration import fuzzy_match_teams
    
    # Should match despite formatting differences
    assert fuzzy_match_teams("NC State vs Virginia", "NC State vs Virginia ᴸᶦᵛᵉ")
    assert fuzzy_match_teams("Duke vs New Mexico", "Duke Blue Devils vs New Mexico")
    assert not fuzzy_match_teams("Duke vs Virginia", "NC State vs Virginia")
    
    print("✅ test_fuzzy_match passed")

if __name__ == '__main__':
    test_fuzzy_match()
    test_match_game_to_channel()
    print("\n✅ All tests passed!")
