"""
Clean player analyzer using properly processed soccer data.

This module provides the main analysis interface for soccer player data
that has been cleaned and standardized. It offers search, comparison,
and filtering capabilities across player statistics.
"""

import pandas as pd
import numpy as np
import logging
import os
from typing import Dict, List, Optional, Union
from pathlib import Path

from .utils import (
    DEFAULT_CLEAN_FILES, MIN_MINUTES_THRESHOLDS,
    filter_midfielders, filter_by_position, setup_logger,
    validate_dataframe_columns, calculate_potential_score
)

logger = setup_logger(__name__)


class CleanPlayerAnalyzer:
    """
    Analyzer for cleaned and standardized soccer player data.
    
    This class provides methods to search, compare, and analyze soccer players
    using preprocessed data with standardized column names and data types.
    
    Attributes:
        data_dir (str): Directory containing clean data files
        standard_data (pd.DataFrame): Main player statistics data
        file_config (Dict[str, str]): Configuration of data file names
    """
    
    def __init__(self, 
                 data_dir: str = "data/clean",
                 file_config: Optional[Dict[str, str]] = None):
        """
        Initialize the analyzer with clean data.
        
        Args:
            data_dir: Directory path containing clean CSV files
            file_config: Custom file names, uses defaults if None
            
        Raises:
            FileNotFoundError: If data directory doesn't exist
            ValueError: If required data files are missing
        """
        self.data_dir = Path(data_dir)
        self.file_config = file_config or DEFAULT_CLEAN_FILES.copy()
        self.standard_data: Optional[pd.DataFrame] = None
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory does not exist: {self.data_dir}")
        
        self._load_clean_data()
    
    def _load_clean_data(self) -> None:
        """
        Load the cleaned standard player data.
        
        Raises:
            FileNotFoundError: If standard data file is missing
            ValueError: If data file is corrupted or has wrong format
        """
        standard_file = self.data_dir / self.file_config['standard']
        
        if not standard_file.exists():
            raise FileNotFoundError(f"Standard data file not found: {standard_file}")
        
        try:
            self.standard_data = pd.read_csv(standard_file, index_col=[0, 1, 2, 3])
            
            # Validate required columns exist
            required_columns = ['position', 'minutes', 'goals', 'assists', 'age']
            validate_dataframe_columns(self.standard_data, required_columns, "Standard data")
            
            logger.info(f"Loaded clean data: {self.standard_data.shape}")
            logger.debug(f"Position distribution: {self.standard_data['position'].value_counts().head()}")
            
        except Exception as e:
            raise ValueError(f"Error loading clean data from {standard_file}: {e}")
    
    def search_players(self, 
                      name_pattern: str, 
                      min_minutes: int = MIN_MINUTES_THRESHOLDS['basic_analysis'],
                      position: Optional[str] = None) -> pd.DataFrame:
        """
        Search for players by name pattern.
        
        Args:
            name_pattern: Player name search pattern (case-insensitive)
            min_minutes: Minimum playing time threshold
            position: Position filter (optional, case-insensitive)
            
        Returns:
            DataFrame with matching players and key statistics
            
        Raises:
            ValueError: If no data is loaded
        """
        if self.standard_data is None:
            raise ValueError("No data loaded. Check data files and initialization.")
        
        df = self.standard_data
        
        # Filter by minimum minutes
        df_filtered = df[df['minutes'] >= min_minutes]
        
        # Search in player names (index level 3)
        matches = df_filtered.index.get_level_values('player').str.contains(
            name_pattern, case=False, na=False
        )
        result = df_filtered[matches]
        
        # Filter by position if specified
        if position:
            position_matches = result['position'].str.contains(position, case=False, na=False)
            result = result[position_matches]
        
        # Return key columns
        key_columns = [
            'nationality', 'position', 'minutes', 'goals', 'assists', 
            'expected_goals', 'expected_assists', 'goals_per_90', 'assists_per_90'
        ]
        
        # Only include columns that exist in the data
        available_columns = [col for col in key_columns if col in result.columns]
        
        logger.info(f"Found {len(result)} players matching '{name_pattern}'")
        return result[available_columns]
    
    def get_players_by_position(self, 
                              position: str, 
                              min_minutes: int = MIN_MINUTES_THRESHOLDS['comparison']) -> pd.DataFrame:
        """
        Get all players by position.
        
        Args:
            position: Position name to filter by
            min_minutes: Minimum playing time threshold
            
        Returns:
            DataFrame with players in specified position
            
        Raises:
            ValueError: If no data is loaded
        """
        if self.standard_data is None:
            raise ValueError("No data loaded. Check data files and initialization.")
        
        df = self.standard_data[self.standard_data['minutes'] >= min_minutes]
        position_matches = df['position'].str.contains(position, case=False, na=False)
        
        result = df[position_matches]
        logger.info(f"Found {len(result)} {position} players with {min_minutes}+ minutes")
        
        return result
    
    def compare_players(self, player_names: List[str]) -> pd.DataFrame:
        """
        Compare multiple players across key metrics.
        
        Args:
            player_names: List of player names to compare
            
        Returns:
            DataFrame with comparison data for all found players
            
        Raises:
            ValueError: If no data is loaded or no players found
        """
        if self.standard_data is None:
            raise ValueError("No data loaded. Check data files and initialization.")
        
        comparison_data = []
        found_players = []
        
        for player_name in player_names:
            matches = self.standard_data.index.get_level_values('player').str.contains(
                player_name, case=False, na=False
            )
            
            if matches.any():
                player_row = self.standard_data[matches].iloc[0]
                found_players.append(player_name)
                
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
                }
                
                # Add progressive stats if available
                if 'progressive_carries' in player_row.index:
                    player_info['progressive_carries'] = player_row['progressive_carries']
                if 'progressive_passes' in player_row.index:
                    player_info['progressive_passes'] = player_row['progressive_passes']
                
                comparison_data.append(player_info)
            else:
                logger.warning(f"Player '{player_name}' not found in data")
        
        if not comparison_data:
            raise ValueError(f"No players found from the provided list: {player_names}")
        
        logger.info(f"Successfully compared {len(found_players)} players: {found_players}")
        return pd.DataFrame(comparison_data)
    
    def find_similar_midfielders(self, 
                                target_player: str, 
                                league_filter: Optional[str] = None,
                                top_n: int = 10, 
                                min_minutes: int = MIN_MINUTES_THRESHOLDS['comparison'],
                                attacking: bool = False,
                                defensive: bool = False) -> pd.DataFrame:
        """
        Find midfielders similar to target player.
        
        Args:
            target_player: Name of player to find similar players for
            league_filter: League to filter results (optional)
            top_n: Number of similar players to return
            min_minutes: Minimum playing time threshold
            attacking: If True, only consider attacking midfielders
            defensive: If True, only consider defensive midfielders
            
        Returns:
            DataFrame with most similar players
            
        Raises:
            ValueError: If target player not found or no data loaded
        """
        if self.standard_data is None:
            raise ValueError("No data loaded. Check data files and initialization.")
        
        # Find target player
        target_matches = self.standard_data.index.get_level_values('player').str.contains(
            target_player, case=False, na=False
        )
        
        if not target_matches.any():
            raise ValueError(f"Target player '{target_player}' not found in data")
        
        target_stats = self.standard_data[target_matches].iloc[0]
        logger.info(f"Target: {target_player} ({target_stats['position']})")
        
        # Filter for midfielders
        midfielders = filter_midfielders(
            self.standard_data, 
            min_minutes=min_minutes,
            attacking=attacking,
            defensive=defensive
        )
        
        # Filter by league if specified
        if league_filter:
            league_matches = midfielders.index.get_level_values('league').str.contains(
                league_filter, case=False, na=False
            )
            midfielders = midfielders[league_matches]
        
        logger.info(f"Comparing against {len(midfielders)} midfielders")
        
        # Calculate similarity using utils function
        similar_players = []
        
        for idx, player in midfielders.iterrows():
            if idx[3] == target_stats.name[3]:  # Skip same player
                continue
            
            # Calculate similarity score based on key metrics
            score = self._calculate_similarity_score(target_stats, player)
            
            similar_players.append({
                'player': idx[3],
                'team': idx[2],
                'league': idx[0],
                'position': player['position'],
                'similarity_score': score,
                'goals_per_90': player['goals_per_90'],
                'assists_per_90': player['assists_per_90'],
                'progressive_carries': player.get('progressive_carries', 0),
                'progressive_passes': player.get('progressive_passes', 0),
                'minutes': player['minutes']
            })
        
        # Sort by similarity and return top N
        if similar_players:
            similar_df = pd.DataFrame(similar_players)
            similar_df = similar_df.sort_values('similarity_score')
            return similar_df.head(top_n)
        
        return pd.DataFrame()
    
    def _calculate_similarity_score(self, target_stats: pd.Series, player_stats: pd.Series) -> float:
        """
        Calculate similarity score between two players.
        
        Args:
            target_stats: Target player statistics
            player_stats: Comparison player statistics
            
        Returns:
            Similarity score (lower = more similar)
        """
        weights = {
            'goals_per_90': 3.0,
            'assists_per_90': 3.0,
            'progressive_carries': 0.05,
            'progressive_passes': 0.02
        }
        
        score = 0
        for metric, weight in weights.items():
            if metric in target_stats.index and metric in player_stats.index:
                target_val = target_stats[metric]
                player_val = player_stats[metric]
                
                if pd.notna(target_val) and pd.notna(player_val):
                    diff = abs(float(target_val) - float(player_val))
                    score += diff * weight
        
        return score
    
    def get_position_leaders(self, 
                           position: str, 
                           stat: str, 
                           top_n: int = 10,
                           min_minutes: int = MIN_MINUTES_THRESHOLDS['comparison']) -> pd.DataFrame:
        """
        Get top performers by position and statistic.
        
        Args:
            position: Position name to filter by
            stat: Statistic column name to sort by
            top_n: Number of top players to return
            min_minutes: Minimum playing time threshold
            
        Returns:
            DataFrame with top performers
            
        Raises:
            ValueError: If position has no players or stat column doesn't exist
        """
        position_players = self.get_players_by_position(position, min_minutes)
        
        if position_players.empty:
            raise ValueError(f"No {position} players found with {min_minutes}+ minutes")
        
        if stat not in position_players.columns:
            available_stats = list(position_players.columns)
            raise ValueError(f"Stat '{stat}' not found. Available stats: {available_stats}")
        
        # Sort by stat and return top N
        top_players = position_players.nlargest(top_n, stat)
        
        key_columns = ['position', 'minutes', 'goals', 'assists', 'goals_per_90', 'assists_per_90', stat]
        available_columns = [col for col in key_columns if col in top_players.columns]
        
        logger.info(f"Found top {len(top_players)} {position} players by {stat}")
        return top_players[available_columns]
    
    def get_young_prospects(self, 
                          max_age: int = 23,
                          min_minutes: int = MIN_MINUTES_THRESHOLDS['scouting']) -> pd.DataFrame:
        """
        Get young players with high potential.
        
        Args:
            max_age: Maximum age for prospect consideration
            min_minutes: Minimum playing time threshold
            
        Returns:
            DataFrame with young prospects and potential scores
            
        Raises:
            ValueError: If no data loaded
        """
        if self.standard_data is None:
            raise ValueError("No data loaded. Check data files and initialization.")
        
        young_players = self.standard_data[
            (self.standard_data['age'] < max_age) & 
            (self.standard_data['minutes'] >= min_minutes)
        ]
        
        if young_players.empty:
            logger.warning(f"No players found under age {max_age} with {min_minutes}+ minutes")
            return pd.DataFrame()
        
        # Calculate potential scores
        prospects = []
        for idx, player in young_players.iterrows():
            try:
                potential_score = calculate_potential_score(player, max_age=max_age)
                prospects.append({
                    'player': idx[3],
                    'team': idx[2],
                    'league': idx[0],
                    'age': int(player['age']),
                    'position': player['position'],
                    'potential_score': potential_score,
                    'minutes': int(player['minutes']),
                    'goals_per_90': player['goals_per_90'],
                    'assists_per_90': player['assists_per_90']
                })
            except (ValueError, KeyError) as e:
                logger.debug(f"Skipping player {idx[3]} due to missing data: {e}")
                continue
        
        if prospects:
            prospects_df = pd.DataFrame(prospects)
            prospects_df = prospects_df.sort_values('potential_score', ascending=False)
            logger.info(f"Found {len(prospects_df)} young prospects")
            return prospects_df
        
        return pd.DataFrame()
    
    @property
    def data_summary(self) -> Dict[str, Union[int, str]]:
        """
        Get summary information about loaded data.
        
        Returns:
            Dictionary with data summary statistics
        """
        if self.standard_data is None:
            return {"status": "No data loaded"}
        
        return {
            "total_players": len(self.standard_data),
            "leagues": list(self.standard_data.index.get_level_values('league').unique()),
            "positions": list(self.standard_data['position'].value_counts().index[:5]),
            "age_range": f"{self.standard_data['age'].min():.0f}-{self.standard_data['age'].max():.0f}",
            "data_shape": str(self.standard_data.shape)
        }