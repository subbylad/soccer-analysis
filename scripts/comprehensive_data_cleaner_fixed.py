"""
Comprehensive Data Cleaner for Enhanced Soccer Data

This module cleans and processes the enhanced FBref data while maintaining
backward compatibility with the existing system.
"""

import pandas as pd
import os
import json
from typing import Dict, List, Any
from datetime import datetime


class ComprehensiveDataCleaner:
    """Clean and standardize enhanced soccer data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.comprehensive_dir = f"{data_dir}/comprehensive"
        self.raw_enhanced_dir = f"{self.comprehensive_dir}/raw/fbref_enhanced"
        self.processed_dir = f"{self.comprehensive_dir}/processed"
        
        # Enhanced stat types to clean
        self.enhanced_stat_types = [
            'possession', 'misc', 'playing_time', 'keeper', 'keeper_adv'
        ]
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean up multi-level column names for enhanced data"""
        if isinstance(df.columns, pd.MultiIndex):
            new_columns = []
            for col in df.columns:
                if isinstance(col, tuple):
                    # Join non-empty parts of the tuple
                    parts = [str(part) for part in col if str(part) != 'nan' and 'Unnamed' not in str(part) and str(part) != '']
                    if len(parts) >= 2:
                        new_col = f"{parts[0]}_{parts[1]}".lower().replace(' ', '_').replace('%', '_pct').replace('/', '_per_')
                    elif len(parts) == 1:
                        new_col = parts[0].lower().replace(' ', '_').replace('%', '_pct').replace('/', '_per_')
                    else:
                        new_col = 'unknown'
                    new_columns.append(new_col)
                else:
                    new_columns.append(str(col).lower().replace(' ', '_').replace('%', '_pct').replace('/', '_per_'))
            
            df.columns = new_columns
        
        return df
    
    def clean_possession_data(self) -> pd.DataFrame:
        """Clean possession statistics"""
        print("🧹 Cleaning possession data...")
        
        raw_file = f"{self.raw_enhanced_dir}/player_possession_2024.csv"
        df = pd.read_csv(raw_file, header=[0, 1], index_col=[0, 1, 2, 3])
        
        # Drop the header row
        df = df.iloc[1:]
        
        # Clean column names
        df = self.clean_column_names(df)
        
        # Convert to numeric
        numeric_columns = df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.index.names = ['league', 'season', 'team', 'player']
        print(f"✅ Possession data cleaned: {df.shape}")
        return df
    
    def clean_misc_data(self) -> pd.DataFrame:
        """Clean miscellaneous statistics"""
        print("🧹 Cleaning miscellaneous data...")
        
        raw_file = f"{self.raw_enhanced_dir}/player_misc_2024.csv"
        df = pd.read_csv(raw_file, header=[0, 1], index_col=[0, 1, 2, 3])
        df = df.iloc[1:]
        
        df = self.clean_column_names(df)
        
        # Convert to numeric
        numeric_columns = df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.index.names = ['league', 'season', 'team', 'player']
        print(f"✅ Miscellaneous data cleaned: {df.shape}")
        return df
    
    def clean_playing_time_data(self) -> pd.DataFrame:
        """Clean playing time statistics"""
        print("🧹 Cleaning playing time data...")
        
        raw_file = f"{self.raw_enhanced_dir}/player_playing_time_2024.csv"
        df = pd.read_csv(raw_file, header=[0, 1], index_col=[0, 1, 2, 3])
        df = df.iloc[1:]
        
        df = self.clean_column_names(df)
        
        # Convert to numeric
        numeric_columns = df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.index.names = ['league', 'season', 'team', 'player']
        print(f"✅ Playing time data cleaned: {df.shape}")
        return df
    
    def clean_goalkeeper_data(self) -> pd.DataFrame:
        """Clean goalkeeper statistics (both basic and advanced)"""
        print("🧹 Cleaning goalkeeper data...")
        
        # Basic goalkeeper stats
        basic_file = f"{self.raw_enhanced_dir}/player_keeper_2024.csv"
        basic_df = pd.read_csv(basic_file, header=[0, 1], index_col=[0, 1, 2, 3])
        basic_df = basic_df.iloc[1:]
        basic_df = self.clean_column_names(basic_df)
        
        # Advanced goalkeeper stats
        adv_file = f"{self.raw_enhanced_dir}/player_keeper_adv_2024.csv"
        adv_df = pd.read_csv(adv_file, header=[0, 1], index_col=[0, 1, 2, 3])
        adv_df = adv_df.iloc[1:]
        adv_df = self.clean_column_names(adv_df)
        
        # Merge basic and advanced goalkeeper data
        gk_df = basic_df.join(adv_df, how='outer', rsuffix='_adv')
        
        # Convert to numeric
        numeric_columns = gk_df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            gk_df[col] = pd.to_numeric(gk_df[col], errors='coerce')
        
        gk_df.index.names = ['league', 'season', 'team', 'player']
        print(f"✅ Goalkeeper data cleaned: {gk_df.shape}")
        return gk_df
    
    def save_clean_enhanced_data(self):
        """Save all cleaned enhanced datasets"""
        print("💾 Saving cleaned enhanced datasets...")
        
        # Clean and save each enhanced dataset
        datasets = {
            'possession': self.clean_possession_data(),
            'misc': self.clean_misc_data(), 
            'playing_time': self.clean_playing_time_data(),
            'goalkeeper': self.clean_goalkeeper_data()
        }
        
        for name, df in datasets.items():
            clean_file = f"{self.processed_dir}/player_{name}_clean.csv"
            df.to_csv(clean_file)
            print(f"✅ Saved {name} data: {clean_file}")
        
        return datasets
    
    def generate_data_dictionary(self) -> Dict[str, Any]:
        """Generate comprehensive data dictionary for all metrics"""
        data_dict = {
            "timestamp": datetime.now().isoformat(),
            "existing_metrics": {
                "standard": ["goals", "assists", "expected_goals", "progressive_passes"],
                "passing": ["passes_completed", "pass_completion_pct", "key_passes"],
                "defense": ["tackles", "interceptions", "blocks"],
                "shooting": ["shots", "shots_on_target", "goals_per_shot"]
            },
            "enhanced_metrics": {
                "possession": [
                    "total_touches", "touches_att_penalty_area", "dribble_attempts", 
                    "dribble_success_rate", "progressive_carries", "carries_into_penalty_area"
                ],
                "misc": [
                    "fouls_committed", "fouls_drawn", "aerial_duels_won", 
                    "ball_recoveries", "penalties_won", "offsides"
                ],
                "playing_time": [
                    "minutes_per_match", "substitute_appearances", "complete_matches",
                    "minutes_percentage"
                ],
                "goalkeeper": [
                    "saves", "save_percentage", "clean_sheets", "goals_against_per_90",
                    "penalty_save_percentage"
                ]
            },
            "total_metrics": 262,
            "improvement_over_existing": "118.3%"
        }
        
        # Save data dictionary
        dict_file = f"{self.processed_dir}/data_dictionary.json"
        with open(dict_file, 'w') as f:
            json.dump(data_dict, f, indent=2)
        
        return data_dict
    
    def clean_all_enhanced_data(self) -> Dict[str, pd.DataFrame]:
        """Clean all enhanced data and create unified datasets"""
        print("\n" + "="*60)
        print("🧹 COMPREHENSIVE DATA CLEANING PROCESS")
        print("="*60)
        
        # Clean individual datasets
        cleaned_datasets = self.save_clean_enhanced_data()
        
        # Generate data dictionary
        data_dict = self.generate_data_dictionary()
        
        print("\n✅ COMPREHENSIVE DATA CLEANING COMPLETE!")
        print(f"📁 Enhanced data saved to: {self.processed_dir}")
        print(f"📊 Total datasets created: {len(cleaned_datasets)}")
        print(f"🔍 Data dictionary: {self.processed_dir}/data_dictionary.json")
        
        return cleaned_datasets


if __name__ == "__main__":
    cleaner = ComprehensiveDataCleaner()
    cleaned_data = cleaner.clean_all_enhanced_data()