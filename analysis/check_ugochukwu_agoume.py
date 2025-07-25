import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clean_player_analyzer import CleanPlayerAnalyzer
import pandas as pd

def analyze_ugochukwu_agoume():
    analyzer = CleanPlayerAnalyzer()
    
    print("🔍 LESLEY UGOCHUKWU & LUCIEN AGOUMÉ ANALYSIS")
    print("=" * 50)
    
    # Search for both players
    players_found = []
    
    # Search for Ugochukwu
    ugochukwu_results = analyzer.search_players("Ugochukwu", min_minutes=50)
    if not ugochukwu_results.empty:
        players_found.append(("Ugochukwu", ugochukwu_results.iloc[0]))
    
    # Search for Agoumé  
    agoume_results = analyzer.search_players("Agoumé", min_minutes=50)
    if not agoume_results.empty:
        players_found.append(("Agoumé", agoume_results.iloc[0]))
    
    # Also try alternative spellings
    agoume_alt = analyzer.search_players("Lucien", min_minutes=50)
    for idx, player in agoume_alt.iterrows():
        player_name = idx[3]
        if "Agoum" in player_name or "Lucien" in player_name:
            if player_name not in [p[0] for p in players_found]:
                players_found.append((player_name, player))
    
    if not players_found:
        print("❌ Neither player found in our dataset")
        return
    
    print(f"✅ Found {len(players_found)} players:")
    
    for player_name, player_data in players_found:
        idx = player_data.name
        team = idx[2]
        league = idx[0]
        
        print(f"\n📊 {player_name}")
        print("-" * 30)
        print(f"Team: {team} ({league})")
        print(f"Position: {player_data['position']}")
        print(f"Minutes: {player_data['minutes']:,}")
        print(f"Goals: {player_data['goals']} ({player_data['goals_per_90']:.3f}/90)")
        print(f"Assists: {player_data['assists']} ({player_data['assists_per_90']:.3f}/90)")
        print(f"Expected: {player_data['expected_goals']:.1f}xG, {player_data['expected_assists']:.1f}xA")
        
        # Get full data for more stats
        full_player = analyzer.standard_data.loc[idx]
        age = full_player['age']
        prog_carries = full_player['progressive_carries']
        prog_passes = full_player['progressive_passes']
        prog_total = prog_carries + prog_passes
        
        print(f"Age: {age}")
        print(f"Progressive: {prog_carries:.0f} carries + {prog_passes:.0f} passes = {prog_total:.0f} total")
        
        # Analyze their profile
        goals_90 = player_data['goals_per_90']
        assists_90 = player_data['assists_per_90']
        
        # Check if they qualify as defensive midfielder
        if goals_90 <= 0.20 and assists_90 <= 0.25:
            print("✅ Profile: Defensive Midfielder")
        elif goals_90 > 0.20 or assists_90 > 0.25:
            print("⚔️ Profile: More attacking-minded midfielder")
        
        # Calculate potential score if under 23
        if age < 23:
            potential_score = (
                prog_total * 0.3 +
                player_data['minutes'] * 0.002 +
                (23 - age) * 10 +
                player_data['expected_goals'] * 5 +
                player_data['expected_assists'] * 5
            )
            print(f"Potential Score: {potential_score:.1f}")
            
            # Compare to our rankings
            if potential_score >= 140:
                rank_tier = "⭐ ELITE (Top 5 level)"
            elif potential_score >= 120:
                rank_tier = "🌟 HIGH (Top 10 level)"
            elif potential_score >= 100:
                rank_tier = "💫 GOOD (Top 20 level)"
            else:
                rank_tier = "📈 DEVELOPING"
            
            print(f"Tier: {rank_tier}")
            
            # Context vs our top prospects
            print(f"\n🎯 vs Our Top Prospects:")
            print(f"   Pedri (Barcelona): 209.4")
            print(f"   Diego Moreira (Strasbourg): 147.4") 
            print(f"   Alberto Moleiro (Las Palmas): 143.8")
            print(f"   → {player_name}: {potential_score:.1f}")
            
        else:
            print("⚠️ Over 23 - not in young prospect category")
        
        # Minutes analysis
        minutes = player_data['minutes']
        if minutes >= 2000:
            usage = "🔥 High usage - coach trusts them"
        elif minutes >= 1000:
            usage = "📈 Regular rotation player"
        elif minutes >= 500:
            usage = "⏱️ Limited opportunities"
        else:
            usage = "🚨 Very low playing time"
        
        print(f"Usage: {usage}")
        
        # League context
        if league == "ENG-Premier League":
            league_context = "Premier League - top competition level"
        elif league == "FRA-Ligue 1":
            league_context = "Ligue 1 - good development league"
        elif league == "ESP-La Liga":
            league_context = "La Liga - excellent technical development"
        else:
            league_context = f"{league} - various development opportunities"
        
        print(f"Context: {league_context}")
    
    # Overall assessment
    print(f"\n🏆 OVERALL ASSESSMENT:")
    print("-" * 25)
    
    for player_name, player_data in players_found:
        idx = player_data.name
        full_player = analyzer.standard_data.loc[idx]
        age = full_player['age']
        minutes = player_data['minutes']
        prog_total = full_player['progressive_carries'] + full_player['progressive_passes']
        
        print(f"\n{player_name}:")
        
        # Strengths
        strengths = []
        if minutes >= 1000:
            strengths.append("getting regular playing time")
        if age < 22:
            strengths.append("young with development runway")
        if prog_total >= 100:
            strengths.append("good progressive ability")
        if idx[0] == "ENG-Premier League":
            strengths.append("Premier League experience")
        
        if strengths:
            print(f"  ✅ Strengths: {', '.join(strengths)}")
        
        # Areas for growth
        concerns = []
        if minutes < 1000:
            concerns.append("needs more playing time")
        if prog_total < 100:
            concerns.append("could improve progressive play")
        if player_data['goals_per_90'] + player_data['assists_per_90'] < 0.1:
            concerns.append("very low attacking output")
        
        if concerns:
            print(f"  📈 Growth areas: {', '.join(concerns)}")
        
        # Final verdict
        if age < 21 and minutes >= 1000:
            verdict = "🌟 Strong prospect with good trajectory"
        elif age < 23 and prog_total >= 100:
            verdict = "💫 Solid potential, needs more opportunities"
        elif minutes < 500:
            verdict = "⏳ Hard to assess without more playing time"
        else:
            verdict = "📊 Decent profile but not standout level"
        
        print(f"  🎯 Verdict: {verdict}")

if __name__ == "__main__":
    analyze_ugochukwu_agoume()