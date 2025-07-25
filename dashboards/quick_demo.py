#!/usr/bin/env python3
"""
Quick Soccer Analysis Demo
This script demonstrates the key capabilities of our soccer analysis toolkit.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.player_analyzer import PlayerAnalyzer
import pandas as pd

def main():
    print("🏈 SOCCER DATA ANALYSIS TOOLKIT DEMO 🏈")
    print("=" * 50)
    
    # Initialize analyzer
    print("Loading data...")
    analyzer = PlayerAnalyzer()
    
    print("\n1. 🔍 PLAYER SEARCH")
    print("-" * 30)
    # Search for specific players
    search_terms = ["Messi", "Ronaldo", "Haaland", "Mbappé"]
    
    for term in search_terms:
        results = analyzer.search_players(term, min_minutes=200)
        if not results.empty:
            print(f"\n{term} found:")
            player_info = results.iloc[0]
            team = player_info.name[2]
            league = player_info.name[0]
            goals = player_info[('Performance', 'Gls')]
            assists = player_info[('Performance', 'Ast')]
            print(f"  Team: {team} ({league})")
            print(f"  Goals: {goals}, Assists: {assists}")
        else:
            print(f"\n{term}: Not found in current season data")
    
    print("\n\n2. ⚽ TOP GOAL SCORERS")
    print("-" * 30)
    
    # Get top scorers
    standard_data = analyzer.player_data['standard']
    # Filter players with at least 500 minutes
    qualified_players = standard_data[standard_data[('Playing Time', 'Min')] >= 500]
    
    # Sort by goals
    top_scorers = qualified_players.nlargest(10, ('Performance', 'Gls'))
    
    print("Top 10 Goal Scorers (500+ minutes):")
    for i, (idx, player) in enumerate(top_scorers.iterrows(), 1):
        player_name = idx[3]
        team = idx[2]
        goals = player[('Performance', 'Gls')]
        minutes = player[('Playing Time', 'Min')]
        goals_per_90 = player[('Per 90 Minutes', 'Gls')]
        print(f"{i:2d}. {player_name:<20} ({team:<15}) - {goals:2.0f} goals ({goals_per_90:.2f}/90min)")
    
    print("\n\n3. 🎯 TOP ASSIST PROVIDERS")
    print("-" * 30)
    
    # Sort by assists
    top_assists = qualified_players.nlargest(10, ('Performance', 'Ast'))
    
    print("Top 10 Assist Providers (500+ minutes):")
    for i, (idx, player) in enumerate(top_assists.iterrows(), 1):
        player_name = idx[3]
        team = idx[2]
        assists = player[('Performance', 'Ast')]
        assists_per_90 = player[('Per 90 Minutes', 'Ast')]
        print(f"{i:2d}. {player_name:<20} ({team:<15}) - {assists:2.0f} assists ({assists_per_90:.2f}/90min)")
    
    print("\n\n4. 🏆 BEST GOAL+ASSIST COMBINATION")
    print("-" * 30)
    
    # Calculate Goals + Assists
    qualified_players_copy = qualified_players.copy()
    qualified_players_copy['total_ga'] = qualified_players_copy[('Performance', 'Gls')] + qualified_players_copy[('Performance', 'Ast')]
    top_ga = qualified_players_copy.nlargest(10, 'total_ga')
    
    print("Top 10 Goals + Assists (500+ minutes):")
    for i, (idx, player) in enumerate(top_ga.iterrows(), 1):
        player_name = idx[3]
        team = idx[2]
        goals = float(player[('Performance', 'Gls')])
        assists = float(player[('Performance', 'Ast')])
        total = float(player['total_ga'])
        print(f"{i:2d}. {player_name:<20} ({team:<15}) - {total:2.0f} G+A ({goals:2.0f}G + {assists:2.0f}A)")
    
    print("\n\n5. 📊 PLAYER COMPARISON EXAMPLE")
    print("-" * 30)
    
    # Compare some top players
    comparison_players = ["Haaland", "Mbappé", "Kane"]
    comparison = analyzer.compare_players(comparison_players)
    
    if not comparison.empty:
        print("Comparison of top strikers:")
        print(comparison[['player', 'team', 'Performance_Gls', 'Performance_Ast', 'Per 90 Minutes_Gls', 'Per 90 Minutes_Ast']].to_string(index=False))
    
    print("\n\n6. 💡 USAGE TIPS")
    print("-" * 30)
    print("✓ Data includes Big 5 European Leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)")
    print("✓ Use analyzer.search_players('name') to find specific players")
    print("✓ Use analyzer.compare_players(['player1', 'player2']) to compare players")
    print("✓ All data is cached in the 'data/' directory")
    print("✓ Minimum 300 minutes played filter is applied by default")
    
    print("\n🎉 Demo complete! Ready for your custom analysis!")

if __name__ == "__main__":
    main()