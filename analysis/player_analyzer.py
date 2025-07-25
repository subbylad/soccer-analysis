import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import os

class PlayerAnalyzer:
    """Advanced player analysis and comparison tool"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.player_data = {}
        self.load_all_data()
    
    def load_all_data(self):
        """Load all available player data"""
        files = {
            'standard': 'fbref_player_standard_2024.csv',
            'shooting': 'fbref_player_shooting_2024.csv',
            'passing': 'fbref_player_passing_2024.csv',
            'defense': 'fbref_player_defense_2024.csv'
        }
        
        for stat_type, filename in files.items():
            filepath = f"{self.data_dir}/{filename}"
            if os.path.exists(filepath):
                # Read with multi-level header
                df = pd.read_csv(filepath, header=[0, 1], index_col=[0, 1, 2, 3])
                # Drop the first row which contains sub-headers
                df = df.iloc[1:]
                # Convert numeric columns
                numeric_columns = df.select_dtypes(include=['object']).columns
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                self.player_data[stat_type] = df
                print(f"Loaded {stat_type} data: {df.shape}")
    
    def search_players(self, name_pattern: str, min_minutes: int = 300) -> pd.DataFrame:
        """Search for players by name pattern"""
        if 'standard' not in self.player_data:
            return pd.DataFrame()
        
        df = self.player_data['standard']
        # Filter by minimum minutes
        df_filtered = df[df[('Playing Time', 'Min')] >= min_minutes]
        
        # Search in player names (index level 3)
        matches = df_filtered.index.get_level_values(3).str.contains(name_pattern, case=False, na=False)
        result = df_filtered[matches]
        
        return result[[('nation', 'Unnamed: 4_level_1'), ('pos', 'Unnamed: 5_level_1'), 
                      ('Playing Time', 'Min'), ('Performance', 'Gls'), 
                      ('Performance', 'Ast'), ('Expected', 'xG'), ('Expected', 'xAG')]]
    
    def get_player_profile(self, player_name: str) -> Dict:
        """Get comprehensive player profile across all stat types"""
        profile = {}
        
        for stat_type, df in self.player_data.items():
            # Find exact player match
            player_matches = df.index.get_level_values(3).str.contains(player_name, case=False, na=False)
            if player_matches.any():
                player_data = df[player_matches].iloc[0]  # Take first match
                profile[stat_type] = player_data.to_dict()
        
        return profile
    
    def compare_players(self, player_names: List[str], metrics: Optional[List[str]] = None) -> pd.DataFrame:
        """Compare multiple players across key metrics"""
        if metrics is None:
            metrics = [
                ('Performance', 'Gls'),
                ('Performance', 'Ast'),
                ('Expected', 'xG'),
                ('Expected', 'xAG'),
                ('Per 90 Minutes', 'Gls'),
                ('Per 90 Minutes', 'Ast')
            ]
        
        comparison_data = []
        
        for player_name in player_names:
            if 'standard' in self.player_data:
                df = self.player_data['standard']
                player_matches = df.index.get_level_values(3).str.contains(player_name, case=False, na=False)
                
                if player_matches.any():
                    player_row = df[player_matches].iloc[0]
                    player_info = {
                        'player': player_name,
                        'team': player_row.name[2],
                        'league': player_row.name[0],
                        'position': player_row[('pos', 'Unnamed: 5_level_1')],
                        'minutes': player_row[('Playing Time', 'Min')]
                    }
                    
                    for metric in metrics:
                        if metric in df.columns:
                            player_info[f"{metric[0]}_{metric[1]}"] = player_row[metric]
                    
                    comparison_data.append(player_info)
        
        return pd.DataFrame(comparison_data)
    
    def find_similar_players(self, target_player: str, position: Optional[str] = None, 
                           top_n: int = 10, min_minutes: int = 500) -> pd.DataFrame:
        """Find players similar to target player based on key metrics"""
        if 'standard' not in self.player_data:
            return pd.DataFrame()
        
        df = self.player_data['standard']
        
        # Get target player stats
        target_matches = df.index.get_level_values(3).str.contains(target_player, case=False, na=False)
        if not target_matches.any():
            print(f"Player '{target_player}' not found")
            return pd.DataFrame()
        
        target_stats = df[target_matches].iloc[0]
        target_position = position or target_stats[('pos', 'Unnamed: 5_level_1')]
        
        # Filter by position and minutes
        # Convert position column to string and handle NaN values
        pos_series = df[('pos', 'Unnamed: 5_level_1')].astype(str)
        similar_df = df[
            (pos_series.str.contains(target_position, case=False, na=False)) &
            (df[('Playing Time', 'Min')] >= min_minutes)
        ]
        
        # Key metrics for similarity
        key_metrics = [
            ('Per 90 Minutes', 'Gls'),
            ('Per 90 Minutes', 'Ast'),
            ('Per 90 Minutes', 'xG'),
            ('Per 90 Minutes', 'xAG')
        ]
        
        # Calculate similarity scores
        similarity_scores = []
        for idx, row in similar_df.iterrows():
            if idx[3] == target_stats.name[3]:  # Skip same player
                continue
            
            score = 0
            valid_metrics = 0
            
            for metric in key_metrics:
                if metric in df.columns:
                    target_val = target_stats[metric]
                    player_val = row[metric]
                    
                    if pd.notna(target_val) and pd.notna(player_val):
                        # Normalized difference (lower is more similar)
                        diff = abs(target_val - player_val) / (target_val + 0.001)
                        score += diff
                        valid_metrics += 1
            
            if valid_metrics > 0:
                avg_score = score / valid_metrics
                similarity_scores.append((idx, avg_score))
        
        # Sort by similarity and get top N
        similarity_scores.sort(key=lambda x: x[1])
        top_similar = similarity_scores[:top_n]
        
        # Create result DataFrame
        result_data = []
        for idx, score in top_similar:
            player_data = similar_df.loc[idx]
            result_data.append({
                'player': idx[3],
                'team': idx[2],
                'league': idx[0],
                'similarity_score': score,
                'goals_per_90': player_data[('Per 90 Minutes', 'Gls')],
                'assists_per_90': player_data[('Per 90 Minutes', 'Ast')],
                'xG_per_90': player_data[('Per 90 Minutes', 'xG')],
                'xAG_per_90': player_data[('Per 90 Minutes', 'xAG')],
                'minutes': player_data[('Playing Time', 'Min')]
            })
        
        return pd.DataFrame(result_data)
    
    def plot_player_comparison(self, player_names: List[str], save_path: Optional[str] = None):
        """Create visualization comparing players"""
        comparison_df = self.compare_players(player_names)
        
        if comparison_df.empty:
            print("No players found for comparison")
            return
        
        # Set up the plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Player Comparison Dashboard', fontsize=16)
        
        # Goals per 90
        axes[0, 0].bar(comparison_df['player'], comparison_df['Performance_Gls'])
        axes[0, 0].set_title('Total Goals')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Assists per 90
        axes[0, 1].bar(comparison_df['player'], comparison_df['Performance_Ast'])
        axes[0, 1].set_title('Total Assists')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # xG vs Actual Goals
        axes[1, 0].scatter(comparison_df['Expected_xG'], comparison_df['Performance_Gls'])
        for i, player in enumerate(comparison_df['player']):
            axes[1, 0].annotate(player, 
                              (comparison_df['Expected_xG'].iloc[i], comparison_df['Performance_Gls'].iloc[i]))
        axes[1, 0].plot([0, comparison_df['Expected_xG'].max()], [0, comparison_df['Expected_xG'].max()], 'r--')
        axes[1, 0].set_xlabel('Expected Goals (xG)')
        axes[1, 0].set_ylabel('Actual Goals')
        axes[1, 0].set_title('Goals vs Expected Goals')
        
        # Goals + Assists per 90
        goals_assists_90 = comparison_df['Per 90 Minutes_Gls'] + comparison_df['Per 90 Minutes_Ast']
        axes[1, 1].bar(comparison_df['player'], goals_assists_90)
        axes[1, 1].set_title('Goals + Assists per 90 minutes')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()

if __name__ == "__main__":
    analyzer = PlayerAnalyzer()
    
    print("=== PLAYER SEARCH DEMO ===")
    # Search for players named "Haaland"
    haaland_results = analyzer.search_players("Haaland")
    print("\nHaaland search results:")
    print(haaland_results)
    
    print("\n=== PLAYER COMPARISON DEMO ===")
    # Compare top strikers
    top_strikers = ["Haaland", "Mbappé", "Kane"]
    comparison = analyzer.compare_players(top_strikers)
    print("\nTop strikers comparison:")
    print(comparison)
    
    print("\n=== SIMILAR PLAYERS DEMO ===")
    # Find players similar to Haaland
    similar_to_haaland = analyzer.find_similar_players("Haaland", position="FW")
    print("\nPlayers similar to Haaland:")
    print(similar_to_haaland)