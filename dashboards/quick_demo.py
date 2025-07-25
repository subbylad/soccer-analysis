#!/usr/bin/env python3
"""
Quick Soccer Analysis Demo

This script demonstrates the key capabilities of our soccer analysis toolkit
using the clean, refactored analyzer with proper error handling and logging.
"""

import sys
import os
import logging
from pathlib import Path

# Add the parent directory to sys.path to import analysis modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.clean_player_analyzer import CleanPlayerAnalyzer
from analysis.utils import setup_logger
import pandas as pd

# Set up logging for demo
logger = setup_logger(__name__, level=logging.WARNING)  # Suppress info logs for cleaner output


def demo_player_search(analyzer: CleanPlayerAnalyzer) -> None:
    """Demonstrate player search functionality."""
    print("\n1. 🔍 PLAYER SEARCH")
    print("-" * 30)
    
    search_terms = ["Messi", "Ronaldo", "Haaland", "Mbappé"]
    
    for term in search_terms:
        try:
            results = analyzer.search_players(term, min_minutes=200)
            if not results.empty:
                print(f"\n{term} found:")
                player_info = results.iloc[0]
                team = player_info.name[2]
                league = player_info.name[0]
                goals = player_info['goals']
                assists = player_info['assists']
                print(f"  Team: {team} ({league})")
                print(f"  Goals: {goals}, Assists: {assists}")
            else:
                print(f"\n{term}: Not found in current season data")
        except Exception as e:
            print(f"\n{term}: Error during search - {e}")


def demo_top_performers(analyzer: CleanPlayerAnalyzer) -> None:
    """Demonstrate top performers analysis."""
    print("\n\n2. ⚽ TOP GOAL SCORERS")
    print("-" * 30)
    
    try:
        # Get all data and filter for qualified players
        all_players = analyzer.standard_data
        qualified_players = all_players[all_players['minutes'] >= 500]
        
        # Sort by goals
        top_scorers = qualified_players.nlargest(10, 'goals')
        
        print("Top 10 Goal Scorers (500+ minutes):")
        for i, (idx, player) in enumerate(top_scorers.iterrows(), 1):
            player_name = idx[3]
            team = idx[2]
            goals = player['goals']
            minutes = player['minutes']
            goals_per_90 = player['goals_per_90']
            print(f"{i:2d}. {player_name:<20} ({team:<15}) - {goals:2.0f} goals ({goals_per_90:.2f}/90min)")
            
    except Exception as e:
        print(f"Error getting top scorers: {e}")


def demo_top_assisters(analyzer: CleanPlayerAnalyzer) -> None:
    """Demonstrate top assist providers analysis."""
    print("\n\n3. 🎯 TOP ASSIST PROVIDERS")
    print("-" * 30)
    
    try:
        # Get qualified players and sort by assists
        all_players = analyzer.standard_data
        qualified_players = all_players[all_players['minutes'] >= 500]
        top_assists = qualified_players.nlargest(10, 'assists')
        
        print("Top 10 Assist Providers (500+ minutes):")
        for i, (idx, player) in enumerate(top_assists.iterrows(), 1):
            player_name = idx[3]
            team = idx[2]
            assists = player['assists']
            assists_per_90 = player['assists_per_90']
            print(f"{i:2d}. {player_name:<20} ({team:<15}) - {assists:2.0f} assists ({assists_per_90:.2f}/90min)")
            
    except Exception as e:
        print(f"Error getting top assisters: {e}")


def demo_goal_assist_combination(analyzer: CleanPlayerAnalyzer) -> None:
    """Demonstrate combined goals + assists analysis."""
    print("\n\n4. 🏆 BEST GOAL+ASSIST COMBINATION")
    print("-" * 30)
    
    try:
        # Calculate Goals + Assists
        all_players = analyzer.standard_data
        qualified_players = all_players[all_players['minutes'] >= 500].copy()
        qualified_players['total_ga'] = qualified_players['goals'] + qualified_players['assists']
        top_ga = qualified_players.nlargest(10, 'total_ga')
        
        print("Top 10 Goals + Assists (500+ minutes):")
        for i, (idx, player) in enumerate(top_ga.iterrows(), 1):
            player_name = idx[3]
            team = idx[2]
            goals = int(player['goals'])
            assists = int(player['assists'])
            total = int(player['total_ga'])
            print(f"{i:2d}. {player_name:<20} ({team:<15}) - {total:2d} G+A ({goals:2d}G + {assists:2d}A)")
            
    except Exception as e:
        print(f"Error getting goal+assist combinations: {e}")


def demo_player_comparison(analyzer: CleanPlayerAnalyzer) -> None:
    """Demonstrate player comparison functionality."""
    print("\n\n5. 📊 PLAYER COMPARISON EXAMPLE")
    print("-" * 30)
    
    try:
        # Compare some top players
        comparison_players = ["Haaland", "Mbappé", "Kane"]
        comparison = analyzer.compare_players(comparison_players)
        
        if not comparison.empty:
            print("Comparison of top strikers:")
            display_columns = ['player', 'team', 'goals', 'assists', 'goals_per_90', 'assists_per_90']
            available_columns = [col for col in display_columns if col in comparison.columns]
            print(comparison[available_columns].to_string(index=False))
        else:
            print("No players found for comparison")
            
    except Exception as e:
        print(f"Error during player comparison: {e}")


def demo_young_prospects(analyzer: CleanPlayerAnalyzer) -> None:
    """Demonstrate young prospects analysis."""
    print("\n\n6. 🌟 YOUNG PROSPECTS")
    print("-" * 25)
    
    try:
        young_prospects = analyzer.get_young_prospects(max_age=21, min_minutes=1000)
        
        if not young_prospects.empty:
            print("Top 5 Young Prospects (Under 21, 1000+ minutes):")
            for i, (_, prospect) in enumerate(young_prospects.head(5).iterrows(), 1):
                print(f"{i}. {prospect['player']} (Age {prospect['age']}) - {prospect['team']}")
                print(f"   Score: {prospect['potential_score']:.1f} | "
                      f"Output: {prospect['goals_per_90']:.2f}G+{prospect['assists_per_90']:.2f}A/90")
        else:
            print("No young prospects found matching criteria")
            
    except Exception as e:
        print(f"Error getting young prospects: {e}")


def print_usage_tips() -> None:
    """Print usage tips and information."""
    print("\n\n7. 💡 USAGE TIPS")
    print("-" * 20)
    print("✓ Data includes Big 5 European Leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)")
    print("✓ Use analyzer.search_players('name') to find specific players")
    print("✓ Use analyzer.compare_players(['player1', 'player2']) to compare players")
    print("✓ Use analyzer.get_young_prospects() to find promising young players")
    print("✓ All data is automatically validated and cleaned")
    print("✓ Minimum playing time filters ensure statistical relevance")
    
    print("\n🎯 ADVANCED FEATURES:")
    print("✓ Run 'python3 analysis/young_dm_scouting.py' for young DM scouting")
    print("✓ Run 'python3 analysis/dm_attributes_analysis.py' for DM deep dive")
    print("✓ Run 'pytest tests/' to verify functionality")


def main() -> None:
    """Run the comprehensive soccer analysis demo."""
    print("🏈 SOCCER DATA ANALYSIS TOOLKIT DEMO 🏈")
    print("=" * 50)
    
    try:
        # Initialize analyzer
        print("Loading data...")
        analyzer = CleanPlayerAnalyzer()
        
        # Get data summary
        summary = analyzer.data_summary
        print(f"✅ Loaded {summary['total_players']} players from {len(summary['leagues'])} leagues")
        
        # Run all demo sections
        demo_player_search(analyzer)
        demo_top_performers(analyzer)
        demo_top_assisters(analyzer)
        demo_goal_assist_combination(analyzer)
        demo_player_comparison(analyzer)
        demo_young_prospects(analyzer)
        print_usage_tips()
        
        print("\n🎉 Demo complete! Ready for your custom analysis!")
        
    except FileNotFoundError as e:
        print(f"❌ Data files not found: {e}")
        print("Please run 'python3 scripts/data_loader.py' and 'python3 scripts/data_cleaner.py' first.")
        
    except Exception as e:
        print(f"❌ An error occurred during demo: {e}")
        logger.error(f"Demo error: {e}", exc_info=True)


if __name__ == "__main__":
    main()