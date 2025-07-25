import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class CleanPlayerAnalyzer:
    """Updated player analyzer using properly cleaned data"""
    
    def __init__(self, data_dir: str = "data/clean"):
        self.data_dir = data_dir
        self.standard_data = None
        self.load_clean_data()
    
    def load_clean_data(self):
        """Load the cleaned standard data"""
        try:
            self.standard_data = pd.read_csv(f"{self.data_dir}/player_standard_clean.csv", 
                                           index_col=[0, 1, 2, 3])
            print(f"✅ Loaded clean data: {self.standard_data.shape}")
            print(f"Position distribution: {self.standard_data['position'].value_counts().head()}")
        except Exception as e:
            print(f"❌ Error loading clean data: {e}")
    
    def search_players(self, name_pattern: str, min_minutes: int = 300, position: Optional[str] = None) -> pd.DataFrame:
        """Search for players with clean data"""
        if self.standard_data is None:
            return pd.DataFrame()
        
        df = self.standard_data
        
        # Filter by minimum minutes
        df_filtered = df[df['minutes'] >= min_minutes]
        
        # Search in player names
        matches = df_filtered.index.get_level_values('player').str.contains(name_pattern, case=False, na=False)
        result = df_filtered[matches]
        
        # Filter by position if specified
        if position:
            position_matches = result['position'].str.contains(position, case=False, na=False)
            result = result[position_matches]
        
        # Return key columns
        key_columns = ['nationality', 'position', 'minutes', 'goals', 'assists', 
                      'expected_goals', 'expected_assists', 'goals_per_90', 'assists_per_90']
        
        return result[key_columns]
    
    def get_players_by_position(self, position: str, min_minutes: int = 500) -> pd.DataFrame:
        """Get all players by position"""
        if self.standard_data is None:
            return pd.DataFrame()
        
        df = self.standard_data[self.standard_data['minutes'] >= min_minutes]
        position_matches = df['position'].str.contains(position, case=False, na=False)
        
        return df[position_matches]
    
    def compare_players(self, player_names: List[str]) -> pd.DataFrame:
        """Compare multiple players with clean data"""
        if self.standard_data is None:
            return pd.DataFrame()
        
        comparison_data = []
        
        for player_name in player_names:
            matches = self.standard_data.index.get_level_values('player').str.contains(player_name, case=False, na=False)
            
            if matches.any():
                player_row = self.standard_data[matches].iloc[0]
                
                player_info = {
                    'player': player_name,
                    'team': player_row.name[2],
                    'league': player_row.name[0],
                    'position': player_row['position'],
                    'minutes': player_row['minutes'],
                    'goals': player_row['goals'],
                    'assists': player_row['assists'],
                    'goals_per_90': player_row['goals_per_90'],
                    'assists_per_90': player_row['assists_per_90'],
                    'expected_goals': player_row['expected_goals'],
                    'expected_assists': player_row['expected_assists'],
                    'progressive_carries': player_row['progressive_carries'],
                    'progressive_passes': player_row['progressive_passes']
                }
                
                comparison_data.append(player_info)
        
        return pd.DataFrame(comparison_data)
    
    def find_similar_midfielders(self, target_player: str, league_filter: Optional[str] = None, 
                               top_n: int = 10, min_minutes: int = 500) -> pd.DataFrame:
        """Find similar midfielders with properly working position filtering"""
        if self.standard_data is None:
            return pd.DataFrame()
        
        # Find target player
        target_matches = self.standard_data.index.get_level_values('player').str.contains(target_player, case=False, na=False)
        if not target_matches.any():
            print(f"❌ Player '{target_player}' not found")
            return pd.DataFrame()
        
        target_stats = self.standard_data[target_matches].iloc[0]
        print(f"🎯 Target: {target_player} ({target_stats['position']})")
        
        # Filter for midfielders only
        midfielders = self.standard_data[
            (self.standard_data['position'].str.contains('Midfielder', case=False, na=False)) &
            (self.standard_data['minutes'] >= min_minutes)
        ]
        
        # Filter by league if specified
        if league_filter:
            midfielders = midfielders[
                midfielders.index.get_level_values('league').str.contains(league_filter, case=False, na=False)
            ]
        
        print(f"🔍 Comparing against {len(midfielders)} midfielders...")
        
        # Calculate similarity
        target_metrics = {
            'goals_per_90': target_stats['goals_per_90'],
            'assists_per_90': target_stats['assists_per_90'],
            'progressive_carries': target_stats['progressive_carries'],
            'progressive_passes': target_stats['progressive_passes']
        }
        
        similar_players = []
        
        for idx, player in midfielders.iterrows():
            if idx[3] == target_stats.name[3]:  # Skip same player
                continue
            
            # Calculate comprehensive similarity
            score = 0
            weights = {
                'goals_per_90': 3.0,  # Weight attacking stats more
                'assists_per_90': 3.0,
                'progressive_carries': 0.05,  # Scale down larger numbers
                'progressive_passes': 0.02
            }
            
            for metric, weight in weights.items():
                if pd.notna(target_metrics[metric]) and pd.notna(player[metric]):
                    diff = abs(float(target_metrics[metric]) - float(player[metric]))
                    score += diff * weight
            
            similar_players.append({
                'player': idx[3],
                'team': idx[2],
                'league': idx[0],
                'position': player['position'],
                'similarity_score': score,
                'goals_per_90': player['goals_per_90'],
                'assists_per_90': player['assists_per_90'],
                'progressive_carries': player['progressive_carries'],
                'progressive_passes': player['progressive_passes'],
                'minutes': player['minutes']
            })
        
        # Sort by similarity and return top N
        if similar_players:
            similar_df = pd.DataFrame(similar_players)
            similar_df = similar_df.sort_values('similarity_score')
            return similar_df.head(top_n)
        
        return pd.DataFrame()
    
    def get_position_leaders(self, position: str, stat: str, top_n: int = 10, min_minutes: int = 500) -> pd.DataFrame:
        """Get top performers by position and stat"""
        if self.standard_data is None:
            return pd.DataFrame()
        
        # Filter by position and minutes
        position_players = self.standard_data[
            (self.standard_data['position'].str.contains(position, case=False, na=False)) &
            (self.standard_data['minutes'] >= min_minutes)
        ]
        
        if stat not in position_players.columns:
            print(f"❌ Stat '{stat}' not found in data")
            return pd.DataFrame()
        
        # Sort by stat and return top N
        top_players = position_players.nlargest(top_n, stat)
        
        key_columns = ['position', 'minutes', 'goals', 'assists', 'goals_per_90', 'assists_per_90', stat]
        
        return top_players[key_columns]

if __name__ == "__main__":
    # Test the clean analyzer
    analyzer = CleanPlayerAnalyzer()
    
    print("\n🔍 TESTING CLEAN ANALYZER")
    print("=" * 40)
    
    # Test player search
    print("\n1. Search for Baleba:")
    baleba = analyzer.search_players("Baleba")
    print(baleba)
    
    # Test midfielder search
    print("\n2. Find midfielders similar to Baleba in Ligue 1:")
    similar = analyzer.find_similar_midfielders("Baleba", league_filter="FRA-Ligue 1", top_n=5)
    if not similar.empty:
        print(similar[['player', 'team', 'similarity_score', 'goals_per_90', 'assists_per_90']])
    else:
        print("No similar midfielders found")
    
    # Test position leaders
    print("\n3. Top 5 midfielders by progressive carries:")
    top_progressive = analyzer.get_position_leaders("Midfielder", "progressive_carries", top_n=5)
    print(top_progressive[['position', 'progressive_carries', 'goals_per_90', 'assists_per_90']])