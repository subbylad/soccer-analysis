import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clean_player_analyzer import CleanPlayerAnalyzer
import pandas as pd
import numpy as np

def analyze_defensive_midfielder_attributes():
    analyzer = CleanPlayerAnalyzer()
    
    print("🔍 DEFENSIVE MIDFIELDER ATTRIBUTES ANALYSIS")
    print("=" * 60)
    
    # Get all midfielders with sufficient minutes
    all_midfielders = analyzer.get_players_by_position("Midfielder", min_minutes=1000)
    
    print(f"📊 Analyzing {len(all_midfielders)} midfielders with 1000+ minutes")
    
    # Define defensive midfielders (low attacking output)
    defensive_mids = all_midfielders[
        (all_midfielders['goals_per_90'] <= 0.15) & 
        (all_midfielders['assists_per_90'] <= 0.15)
    ]
    
    # Define attacking midfielders (high attacking output)
    attacking_mids = all_midfielders[
        (all_midfielders['goals_per_90'] >= 0.20) | 
        (all_midfielders['assists_per_90'] >= 0.25)
    ]
    
    print(f"🛡️ Defensive Midfielders: {len(defensive_mids)}")
    print(f"⚔️ Attacking Midfielders: {len(attacking_mids)}")
    
    # Analyze key attributes
    print(f"\n📈 KEY ATTRIBUTES COMPARISON:")
    print("-" * 50)
    
    attributes = {
        'Progressive Carries': 'progressive_carries',
        'Progressive Passes': 'progressive_passes', 
        'Progressive Receives': 'progressive_receives',
        'Expected Goals': 'expected_goals',
        'Expected Assists': 'expected_assists',
        'Minutes Played': 'minutes',
        'Goals per 90': 'goals_per_90',
        'Assists per 90': 'assists_per_90'
    }
    
    comparison_data = []
    
    for attr_name, attr_col in attributes.items():
        if attr_col in defensive_mids.columns:
            dm_avg = defensive_mids[attr_col].mean()
            am_avg = attacking_mids[attr_col].mean()
            
            comparison_data.append({
                'Attribute': attr_name,
                'Defensive_Avg': dm_avg,
                'Attacking_Avg': am_avg,
                'Difference': dm_avg - am_avg,
                'DM_Advantage': dm_avg > am_avg
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    print("Attribute Comparison (Defensive vs Attacking Midfielders):")
    print("-" * 70)
    for _, row in comparison_df.iterrows():
        advantage = "✅ DM" if row['DM_Advantage'] else "⚔️ AM"
        print(f"{row['Attribute']:<20}: DM {row['Defensive_Avg']:6.1f} | AM {row['Attacking_Avg']:6.1f} | {advantage}")
    
    # Analyze where DMs excel
    print(f"\n🏆 WHERE DEFENSIVE MIDFIELDERS EXCEL:")
    print("-" * 45)
    
    dm_strengths = comparison_df[comparison_df['DM_Advantage'] == True].sort_values('Difference', ascending=False)
    for _, row in dm_strengths.iterrows():
        diff = row['Difference']
        pct_better = ((row['Defensive_Avg'] - row['Attacking_Avg']) / row['Attacking_Avg'] * 100)
        print(f"• {row['Attribute']}: +{diff:.1f} ({pct_better:+.1f}% better than attacking mids)")
    
    # Top defensive midfielders by key attributes
    print(f"\n🌟 TOP DEFENSIVE MIDFIELDERS BY KEY ATTRIBUTES:")
    print("-" * 55)
    
    key_dm_attributes = ['progressive_carries', 'progressive_passes', 'minutes']
    
    for attr in key_dm_attributes:
        if attr in defensive_mids.columns:
            print(f"\n📊 TOP 10 BY {attr.upper().replace('_', ' ')}:")
            top_dms = defensive_mids.nlargest(10, attr)
            
            for i, (idx, player) in enumerate(top_dms.iterrows(), 1):
                player_name = idx[3]
                team = idx[2]
                league = idx[0]
                value = player[attr]
                
                # Show context stats
                goals_90 = player['goals_per_90']
                assists_90 = player['assists_per_90']
                
                print(f"{i:2d}. {player_name:<20} ({team:<12}) - {value:4.0f} | {goals_90:.2f}G+{assists_90:.2f}A/90")
    
    # Analyze by league
    print(f"\n🌍 DEFENSIVE MIDFIELDERS BY LEAGUE:")
    print("-" * 40)
    
    leagues = ['ENG-Premier League', 'ESP-La Liga', 'ITA-Serie A', 'GER-Bundesliga', 'FRA-Ligue 1']
    
    for league in leagues:
        league_dms = defensive_mids[
            defensive_mids.index.get_level_values('league') == league
        ]
        
        if len(league_dms) > 0:
            avg_prog_carries = league_dms['progressive_carries'].mean()
            avg_prog_passes = league_dms['progressive_passes'].mean()
            
            print(f"{league:<20}: {len(league_dms):2d} DMs | Avg: {avg_prog_carries:4.0f} carries, {avg_prog_passes:4.0f} passes")
    
    # Baleba's ranking among defensive midfielders
    print(f"\n🎯 BALEBA'S RANKING AMONG DEFENSIVE MIDFIELDERS:")
    print("-" * 50)
    
    baleba_data = analyzer.search_players("Carlos Baleba")
    if not baleba_data.empty:
        baleba_row = baleba_data.iloc[0]
        
        # Check if Baleba qualifies as defensive midfielder
        baleba_goals_90 = baleba_row['goals_per_90']
        baleba_assists_90 = baleba_row['assists_per_90']
        
        if baleba_goals_90 <= 0.15 and baleba_assists_90 <= 0.15:
            print("✅ Baleba qualifies as a defensive midfielder")
            
            # Get Baleba's full data
            baleba_full = analyzer.standard_data.loc[baleba_row.name]
            
            # Rank him in key attributes
            for attr in ['progressive_carries', 'progressive_passes']:
                if attr in defensive_mids.columns:
                    baleba_value = baleba_full[attr]
                    rank = (defensive_mids[attr] < baleba_value).sum() + 1
                    percentile = (1 - rank / len(defensive_mids)) * 100
                    
                    print(f"• {attr.replace('_', ' ').title()}: {baleba_value:.0f} (Rank {rank}/{len(defensive_mids)}, {percentile:.0f}th percentile)")
        
        else:
            print("❌ Baleba doesn't qualify as pure defensive midfielder by our criteria")
    
    return defensive_mids, attacking_mids

if __name__ == "__main__":
    dm_data, am_data = analyze_defensive_midfielder_attributes()