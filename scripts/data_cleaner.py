import pandas as pd
import os
from typing import Dict, List

class SoccerDataCleaner:
    """Clean and standardize soccer data from FBref"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.raw_dir = f"{data_dir}/raw"
        self.clean_dir = f"{data_dir}/clean"
        
        # Create directories
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.clean_dir, exist_ok=True)
    
    def move_raw_files(self):
        """Move current messy files to raw directory"""
        files_to_move = [
            'fbref_player_standard_2024.csv',
            'fbref_player_shooting_2024.csv', 
            'fbref_player_passing_2024.csv',
            'fbref_player_defense_2024.csv',
            'fbref_team_stats_2024.csv'
        ]
        
        for filename in files_to_move:
            old_path = f"{self.data_dir}/{filename}"
            new_path = f"{self.raw_dir}/{filename}"
            
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                print(f"Moved {filename} to raw/")
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean up the messy multi-level column names"""
        if isinstance(df.columns, pd.MultiIndex):
            # Flatten multi-level columns
            new_columns = []
            for col in df.columns:
                if isinstance(col, tuple):
                    # Join non-empty parts of the tuple
                    parts = [str(part) for part in col if str(part) != 'nan' and 'Unnamed' not in str(part)]
                    if len(parts) == 2:
                        new_col = f"{parts[0]}_{parts[1]}"
                    elif len(parts) == 1:
                        new_col = parts[0]
                    else:
                        new_col = "_".join(parts)
                    new_columns.append(new_col)
                else:
                    new_columns.append(str(col))
            
            df.columns = new_columns
        
        # Clean up specific problematic column names
        column_mappings = {
            'nation': 'nationality',
            'pos': 'position', 
            'age': 'age',
            'born': 'birth_year',
            'Playing Time_MP': 'matches_played',
            'Playing Time_Starts': 'starts',
            'Playing Time_Min': 'minutes',
            'Playing Time_90s': 'nineties',
            'Performance_Gls': 'goals',
            'Performance_Ast': 'assists',
            'Performance_G+A': 'goals_assists',
            'Performance_G-PK': 'goals_non_penalty',
            'Performance_PK': 'penalties_made',
            'Performance_PKatt': 'penalties_attempted',
            'Performance_CrdY': 'yellow_cards',
            'Performance_CrdR': 'red_cards',
            'Expected_xG': 'expected_goals',
            'Expected_npxG': 'expected_goals_non_penalty',
            'Expected_xAG': 'expected_assists',
            'Expected_npxG+xAG': 'expected_goals_assists_non_penalty',
            'Progression_PrgC': 'progressive_carries',
            'Progression_PrgP': 'progressive_passes',
            'Progression_PrgR': 'progressive_receives',
            'Per 90 Minutes_Gls': 'goals_per_90',
            'Per 90 Minutes_Ast': 'assists_per_90',
            'Per 90 Minutes_G+A': 'goals_assists_per_90',
            'Per 90 Minutes_G-PK': 'goals_non_penalty_per_90',
            'Per 90 Minutes_G+A-PK': 'goals_assists_non_penalty_per_90',
            'Per 90 Minutes_xG': 'expected_goals_per_90',
            'Per 90 Minutes_xAG': 'expected_assists_per_90',
            'Per 90 Minutes_xG+xAG': 'expected_goals_assists_per_90',
            'Per 90 Minutes_npxG': 'expected_goals_non_penalty_per_90',
            'Per 90 Minutes_npxG+xAG': 'expected_goals_assists_non_penalty_per_90'
        }
        
        # Rename columns
        df = df.rename(columns=column_mappings)
        
        return df
    
    def clean_standard_data(self) -> pd.DataFrame:
        """Clean the standard player statistics"""
        print("🧹 Cleaning standard player data...")
        
        # Load raw data
        raw_file = f"{self.raw_dir}/fbref_player_standard_2024.csv"
        df = pd.read_csv(raw_file, header=[0, 1], index_col=[0, 1, 2, 3])
        
        # Drop the first row (contains sub-headers)
        df = df.iloc[1:]
        
        # Clean column names
        df = self.clean_column_names(df)
        
        # Convert numeric columns
        numeric_columns = df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean index names
        df.index.names = ['league', 'season', 'team', 'player']
        
        # Clean position data
        if 'position' in df.columns:
            df['position'] = df['position'].fillna('Unknown')
            # Standardize position names
            position_mappings = {
                'DF': 'Defender',
                'MF': 'Midfielder', 
                'FW': 'Forward',
                'GK': 'Goalkeeper',
                'DF,MF': 'Defender/Midfielder',
                'MF,FW': 'Midfielder/Forward',
                'MF,DF': 'Midfielder/Defender',
                'FW,MF': 'Forward/Midfielder'
            }
            df['position'] = df['position'].replace(position_mappings)
        
        print(f"✅ Standard data cleaned: {df.shape}")
        return df
    
    def clean_defense_data(self) -> pd.DataFrame:
        """Clean the defensive statistics"""
        print("🧹 Cleaning defensive data...")
        
        raw_file = f"{self.raw_dir}/fbref_player_defense_2024.csv"
        df = pd.read_csv(raw_file, header=[0, 1], index_col=[0, 1, 2, 3])
        df = df.iloc[1:]
        
        # Clean column names for defense
        defense_mappings = {
            'Tackles_Tkl': 'tackles',
            'Tackles_TklW': 'tackles_won',
            'Tackles_Def 3rd': 'tackles_def_third',
            'Tackles_Mid 3rd': 'tackles_mid_third', 
            'Tackles_Att 3rd': 'tackles_att_third',
            'Challenges_Tkl': 'challenge_tackles',
            'Challenges_Att': 'challenges_attempted',
            'Challenges_Tkl%': 'tackle_success_rate',
            'Challenges_Lost': 'challenges_lost',
            'Blocks_Blocks': 'blocks',
            'Blocks_Sh': 'shots_blocked',
            'Blocks_Pass': 'passes_blocked',
            'Int': 'interceptions',
            'Tkl+Int': 'tackles_plus_interceptions',
            'Clr': 'clearances',
            'Err': 'errors'
        }
        
        df = self.clean_column_names(df)
        df = df.rename(columns=defense_mappings)
        df.index.names = ['league', 'season', 'team', 'player']
        
        # Convert to numeric
        numeric_columns = df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"✅ Defense data cleaned: {df.shape}")
        return df
    
    def clean_passing_data(self) -> pd.DataFrame:
        """Clean the passing statistics"""
        print("🧹 Cleaning passing data...")
        
        raw_file = f"{self.raw_dir}/fbref_player_passing_2024.csv"
        df = pd.read_csv(raw_file, header=[0, 1], index_col=[0, 1, 2, 3])
        df = df.iloc[1:]
        
        # Clean column names for passing
        passing_mappings = {
            'Total_Cmp': 'passes_completed',
            'Total_Att': 'passes_attempted',
            'Total_Cmp%': 'pass_completion_pct',
            'Total_TotDist': 'total_pass_distance',
            'Total_PrgDist': 'progressive_pass_distance',
            'Short_Cmp': 'short_passes_completed',
            'Short_Att': 'short_passes_attempted',
            'Short_Cmp%': 'short_pass_completion_pct',
            'Medium_Cmp': 'medium_passes_completed',
            'Medium_Att': 'medium_passes_attempted', 
            'Medium_Cmp%': 'medium_pass_completion_pct',
            'Long_Cmp': 'long_passes_completed',
            'Long_Att': 'long_passes_attempted',
            'Long_Cmp%': 'long_pass_completion_pct',
            'Ast': 'assists',
            'xAG': 'expected_assists',
            'Expected_xA': 'expected_assists_fbref',
            'Expected_A-xAG': 'assists_minus_expected',
            'KP': 'key_passes',
            '1/3': 'passes_into_final_third',
            'PPA': 'passes_into_penalty_area',
            'CrsPA': 'crosses_into_penalty_area',
            'PrgP': 'progressive_passes'
        }
        
        df = self.clean_column_names(df)
        df = df.rename(columns=passing_mappings)
        df.index.names = ['league', 'season', 'team', 'player']
        
        # Convert to numeric
        numeric_columns = df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"✅ Passing data cleaned: {df.shape}")
        return df
    
    def clean_shooting_data(self) -> pd.DataFrame:
        """Clean the shooting statistics"""
        print("🧹 Cleaning shooting data...")
        
        raw_file = f"{self.raw_dir}/fbref_player_shooting_2024.csv"
        df = pd.read_csv(raw_file, header=[0, 1], index_col=[0, 1, 2, 3])
        df = df.iloc[1:]
        
        shooting_mappings = {
            'Standard_Gls': 'goals',
            'Standard_Sh': 'shots',
            'Standard_SoT': 'shots_on_target',
            'Standard_SoT%': 'shot_accuracy',
            'Standard_Sh/90': 'shots_per_90',
            'Standard_SoT/90': 'shots_on_target_per_90',
            'Standard_G/Sh': 'goals_per_shot',
            'Standard_G/SoT': 'goals_per_shot_on_target',
            'Standard_Dist': 'average_shot_distance',
            'Standard_FK': 'free_kick_shots',
            'Standard_PK': 'penalty_kicks_made',
            'Standard_PKatt': 'penalty_kicks_attempted',
            'Expected_xG': 'expected_goals',
            'Expected_npxG': 'expected_goals_non_penalty',
            'Expected_npxG/Sh': 'expected_goals_per_shot_non_penalty',
            'Expected_G-xG': 'goals_minus_expected',
            'Expected_np:G-xG': 'non_penalty_goals_minus_expected'
        }
        
        df = self.clean_column_names(df)
        df = df.rename(columns=shooting_mappings)
        df.index.names = ['league', 'season', 'team', 'player']
        
        # Convert to numeric
        numeric_columns = df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"✅ Shooting data cleaned: {df.shape}")
        return df
    
    def save_clean_data(self, df: pd.DataFrame, filename: str):
        """Save cleaned data"""
        clean_path = f"{self.clean_dir}/{filename}"
        df.to_csv(clean_path)
        print(f"💾 Saved clean data: {filename}")
    
    def clean_all_data(self):
        """Clean all player data files"""
        print("🧹 STARTING DATA CLEANING PROCESS")
        print("=" * 50)
        
        # Move raw files
        self.move_raw_files()
        
        # Clean each dataset
        standard_clean = self.clean_standard_data()
        defense_clean = self.clean_defense_data()
        passing_clean = self.clean_passing_data()
        shooting_clean = self.clean_shooting_data()
        
        # Save clean data
        self.save_clean_data(standard_clean, 'player_standard_clean.csv')
        self.save_clean_data(defense_clean, 'player_defense_clean.csv')
        self.save_clean_data(passing_clean, 'player_passing_clean.csv')
        self.save_clean_data(shooting_clean, 'player_shooting_clean.csv')
        
        print("\n✅ DATA CLEANING COMPLETE!")
        print(f"📁 Raw data moved to: {self.raw_dir}/")
        print(f"📁 Clean data saved to: {self.clean_dir}/")
        
        return {
            'standard': standard_clean,
            'defense': defense_clean,
            'passing': passing_clean,
            'shooting': shooting_clean
        }
    
    def show_clean_data_summary(self, clean_data: Dict[str, pd.DataFrame]):
        """Show summary of cleaned data"""
        print("\n📊 CLEAN DATA SUMMARY")
        print("=" * 40)
        
        for data_type, df in clean_data.items():
            print(f"\n{data_type.upper()} DATA:")
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)[:10]}...")  # Show first 10
            
            if 'position' in df.columns:
                print(f"Positions: {df['position'].value_counts().head()}")

if __name__ == "__main__":
    cleaner = SoccerDataCleaner()
    clean_data = cleaner.clean_all_data()
    cleaner.show_clean_data_summary(clean_data)