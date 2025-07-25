import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clean_player_analyzer import CleanPlayerAnalyzer
import pandas as pd
import numpy as np

def scout_young_defensive_midfielders():
    analyzer = CleanPlayerAnalyzer()
    
    print("🔍 SCOUTING YOUNG DEFENSIVE MIDFIELDERS (UNDER 23)")
    print("=" * 60)
    
    # Get all players data
    all_players = analyzer.standard_data
    
    # Filter for young players (under 23)
    young_players = all_players[
        (all_players['age'] < 23) & 
        (all_players['minutes'] >= 500)  # Reasonable playing time
    ]
    
    print(f"📊 Found {len(young_players)} players under 23 with 500+ minutes")
    
    # Filter for midfielders
    young_midfielders = young_players[
        young_players['position'].str.contains('Midfielder', case=False, na=False)
    ]
    
    print(f"⚽ Young midfielders: {len(young_midfielders)}")
    
    # Define defensive midfielders (low attacking output but good fundamentals)
    young_dms = young_midfielders[
        (young_midfielders['goals_per_90'] <= 0.20) &  # Not primarily attackers
        (young_midfielders['assists_per_90'] <= 0.25)   # Not primarily creators
    ]
    
    print(f"🛡️ Young defensive midfielders: {len(young_dms)}")
    
    # Calculate potential indicators
    young_dms_copy = young_dms.copy()
    
    # Growth potential metrics
    young_dms_copy['minutes_per_game'] = young_dms_copy['minutes'] / young_dms_copy['matches_played']
    young_dms_copy['progressive_total'] = young_dms_copy['progressive_carries'] + young_dms_copy['progressive_passes']
    young_dms_copy['experience_factor'] = young_dms_copy['minutes'] / 1000  # More minutes = more experience
    
    # Potential score (combination of current performance and room for growth)
    young_dms_copy['potential_score'] = (
        young_dms_copy['progressive_total'] * 0.3 +  # Current progressive ability
        young_dms_copy['minutes'] * 0.002 +  # Playing time (trust from coaches)
        (23 - young_dms_copy['age']) * 10 +  # Age factor (younger = more potential)
        young_dms_copy['expected_goals'] * 5 +  # Some attacking threat
        young_dms_copy['expected_assists'] * 5   # Some creative ability
    )
    
    # Sort by potential
    top_prospects = young_dms_copy.sort_values('potential_score', ascending=False)
    
    print(f"\n🌟 TOP 15 YOUNG DM PROSPECTS BY POTENTIAL:")
    print("-" * 70)
    
    for i, (idx, player) in enumerate(top_prospects.head(15).iterrows(), 1):
        player_name = idx[3]
        team = idx[2]
        league = idx[0]
        age = int(player['age'])
        
        # Key stats
        minutes = int(player['minutes'])
        prog_total = int(player['progressive_total'])
        goals_90 = player['goals_per_90']
        assists_90 = player['assists_per_90']
        potential = player['potential_score']
        
        print(f"{i:2d}. {player_name:<22} (Age {age}) - {team}")
        print(f"    League: {league}")
        print(f"    Stats: {minutes:,} mins | {prog_total} prog total | {goals_90:.2f}G+{assists_90:.2f}A/90")
        print(f"    Potential Score: {potential:.1f}")
        print()
    
    # Analyze by specific criteria
    print(f"\n📊 ANALYSIS BY KEY CRITERIA:")
    print("-" * 40)
    
    # Most promising by age groups
    age_groups = {
        'Teenagers (19 and under)': young_dms_copy[young_dms_copy['age'] <= 19],
        'Early Twenties (20-22)': young_dms_copy[(young_dms_copy['age'] >= 20) & (young_dms_copy['age'] <= 22)]
    }
    
    for group_name, group_data in age_groups.items():
        if len(group_data) > 0:
            top_in_group = group_data.nlargest(3, 'potential_score')
            print(f"\n🎯 {group_name} ({len(group_data)} players):")
            
            for j, (idx, player) in enumerate(top_in_group.iterrows(), 1):
                name = idx[3]
                team = idx[2]
                age = int(player['age'])
                potential = player['potential_score']
                print(f"   {j}. {name} ({team}) - Age {age}, Potential: {potential:.1f}")
    
    # High playing time young DMs (coach trust indicator)
    print(f"\n⭐ MOST TRUSTED BY COACHES (2000+ minutes):")
    print("-" * 50)
    
    high_minutes = young_dms_copy[young_dms_copy['minutes'] >= 2000].sort_values('minutes', ascending=False)
    
    for i, (idx, player) in enumerate(high_minutes.head(10).iterrows(), 1):
        name = idx[3]
        team = idx[2]
        age = int(player['age'])
        minutes = int(player['minutes'])
        starts = int(player['starts'])
        matches = int(player['matches_played'])
        
        print(f"{i:2d}. {name:<22} (Age {age}) - {team}")
        print(f"    {minutes:,} minutes, {starts}/{matches} starts")
        print()
    
    # Progressive standouts
    print(f"\n📈 BEST PROGRESSIVE PLAYERS:")
    print("-" * 35)
    
    prog_leaders = young_dms_copy.sort_values('progressive_total', ascending=False).head(8)
    
    for i, (idx, player) in enumerate(prog_leaders.iterrows(), 1):
        name = idx[3]
        team = idx[2]
        age = int(player['age'])
        prog_carries = int(player['progressive_carries'])
        prog_passes = int(player['progressive_passes'])
        total = int(player['progressive_total'])
        
        print(f"{i}. {name} (Age {age}) - {team}: {total} total ({prog_carries} carries + {prog_passes} passes)")
    
    # League breakdown
    print(f"\n🌍 PROSPECTS BY LEAGUE:")
    print("-" * 30)
    
    leagues = ['ENG-Premier League', 'ESP-La Liga', 'ITA-Serie A', 'GER-Bundesliga', 'FRA-Ligue 1']
    
    for league in leagues:
        league_prospects = young_dms_copy[
            young_dms_copy.index.get_level_values('league') == league
        ].sort_values('potential_score', ascending=False)
        
        if len(league_prospects) > 0:
            top_prospect = league_prospects.iloc[0]
            name = top_prospect.name[3]
            age = int(top_prospect['age'])
            potential = top_prospect['potential_score']
            
            print(f"{league:<20}: {len(league_prospects):2d} prospects | Best: {name} (Age {age}, {potential:.1f})")
    
    # Specific recommendations
    print(f"\n🏆 CLAUDE'S TOP 5 RECOMMENDATIONS:")
    print("-" * 40)
    
    # Get top 5 with detailed analysis
    top_5 = top_prospects.head(5)
    
    for i, (idx, player) in enumerate(top_5.iterrows(), 1):
        name = idx[3]
        team = idx[2]
        league = idx[0]
        age = int(player['age'])
        
        print(f"\n{i}. {name} (Age {age}) - {team} ({league})")
        
        # Detailed breakdown
        minutes = int(player['minutes'])
        starts = int(player['starts'])
        matches = int(player['matches_played'])
        
        goals = int(player['goals'])
        assists = int(player['assists'])
        xg = player['expected_goals']
        xa = player['expected_assists']
        
        prog_c = int(player['progressive_carries'])
        prog_p = int(player['progressive_passes'])
        
        print(f"   📊 Playing Time: {minutes:,} mins ({starts}/{matches} starts)")
        print(f"   ⚽ Output: {goals}G+{assists}A (xG: {xg:.1f}, xA: {xa:.1f})")
        print(f"   📈 Progressive: {prog_c} carries, {prog_p} passes")
        print(f"   💡 Why: ", end="")
        
        # Reasoning
        reasons = []
        if minutes >= 2000:
            reasons.append("high playing time shows coach trust")
        if age <= 20:
            reasons.append("very young with years to develop")
        if prog_c + prog_p >= 100:
            reasons.append("already showing good progressive ability")
        if xg + xa >= 2:
            reasons.append("some attacking contribution")
        
        print(", ".join(reasons))
    
    return top_prospects

if __name__ == "__main__":
    prospects = scout_young_defensive_midfielders()