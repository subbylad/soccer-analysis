import soccerdata as sd
import pandas as pd
import os
from typing import Optional, List, Dict

class SoccerDataLoader:
    """Class to handle loading and caching soccer data from various sources"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def load_fbref_player_stats(self, seasons: Optional[List[int]] = None, stat_types: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """Load player statistics from FBref for Big 5 European leagues"""
        if seasons is None:
            seasons = [2024]  # Current season
        if stat_types is None:
            stat_types = ['standard', 'shooting', 'passing', 'defense']
            
        all_data = {}
        
        for season in seasons:
            fbref = sd.FBref(leagues='Big 5 European Leagues Combined', seasons=season)
            
            for stat_type in stat_types:
                try:
                    data = fbref.read_player_season_stats(stat_type=stat_type)
                    cache_file = f"{self.data_dir}/fbref_player_{stat_type}_{season}.csv"
                    data.to_csv(cache_file)
                    all_data[f"{stat_type}_{season}"] = data
                    print(f"Loaded {stat_type} stats for {season}: {data.shape}")
                except Exception as e:
                    print(f"Error loading {stat_type} for {season}: {e}")
        
        return all_data
    
    def load_team_stats(self, seasons: Optional[List[int]] = None) -> Dict[str, pd.DataFrame]:
        """Load team statistics from FBref"""
        if seasons is None:
            seasons = [2024]
            
        all_data = {}
        
        for season in seasons:
            fbref = sd.FBref(leagues='Big 5 European Leagues Combined', seasons=season)
            
            try:
                data = fbref.read_team_season_stats()
                cache_file = f"{self.data_dir}/fbref_team_stats_{season}.csv"
                data.to_csv(cache_file)
                all_data[f"team_{season}"] = data
                print(f"Loaded team stats for {season}: {data.shape}")
            except Exception as e:
                print(f"Error loading team stats for {season}: {e}")
                
        return all_data
    
    def load_cached_data(self, filename: str) -> Optional[pd.DataFrame]:
        """Load previously cached data"""
        filepath = f"{self.data_dir}/{filename}"
        if os.path.exists(filepath):
            return pd.read_csv(filepath, index_col=0)
        return None
    
    def get_available_cache_files(self) -> List[str]:
        """Get list of available cached files"""
        if os.path.exists(self.data_dir):
            return [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        return []

if __name__ == "__main__":
    loader = SoccerDataLoader()
    
    print("Loading player statistics...")
    player_data = loader.load_fbref_player_stats(seasons=[2024])
    
    print("\nLoading team statistics...")
    team_data = loader.load_team_stats(seasons=[2024])
    
    print(f"\nData saved to {loader.data_dir}/ directory")
    print("Available cache files:", loader.get_available_cache_files())