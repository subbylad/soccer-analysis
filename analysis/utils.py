"""
Utility functions and configuration for soccer data analysis.

This module contains shared constants, helper functions, and utilities
used across different analysis modules.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple

# Configuration for potential scoring algorithm
POTENTIAL_SCORING_WEIGHTS = {
    'goals_per_90': 3.0,
    'assists_per_90': 3.0, 
    'progressive_carries': 0.05,
    'progressive_passes': 0.02,
    'expected_goals': 5.0,
    'expected_assists': 5.0,
    'minutes': 0.002,
    'age_factor': 10.0  # Multiplied by (23 - age) for young players
}

# Position filters for different analyses
POSITION_FILTERS = {
    'defensive_midfielder': {
        # Tighter thresholds to identify primarily defensive players
        'goals_per_90_max': 0.10,
        'assists_per_90_max': 0.15,
        'position_contains': 'Midfielder'
    },
    'attacking_midfielder': {
        'goals_per_90_min': 0.20,
        'assists_per_90_min': 0.25,
        'position_contains': 'Midfielder'
    },
    'midfielder': {
        'position_contains': 'Midfielder'
    },
    'forward': {
        'position_contains': 'Forward'
    },
    'defender': {
        'position_contains': 'Defender'
    }
}

# Default file names for raw and clean data
DEFAULT_RAW_FILES = {
    'standard': 'fbref_player_standard_2024.csv',
    'shooting': 'fbref_player_shooting_2024.csv',
    'passing': 'fbref_player_passing_2024.csv',
    'defense': 'fbref_player_defense_2024.csv',
    'team': 'fbref_team_stats_2024.csv'
}

DEFAULT_CLEAN_FILES = {
    'standard': 'player_standard_clean.csv',
    'shooting': 'player_shooting_clean.csv',
    'passing': 'player_passing_clean.csv',
    'defense': 'player_defense_clean.csv'
}

# Minimum playing time thresholds
MIN_MINUTES_THRESHOLDS = {
    'basic_analysis': 300,
    'comparison': 500,
    'scouting': 500,
    'high_usage': 2000
}


def calculate_potential_score(player_row: pd.Series, 
                            weights: Optional[Dict[str, float]] = None,
                            max_age: int = 23) -> float:
    """
    Calculate potential score for a young player.
    
    Args:
        player_row: Player data as pandas Series
        weights: Custom weights dict, uses default if None
        max_age: Maximum age for age factor calculation
        
    Returns:
        Potential score as float
        
    Raises:
        ValueError: If required columns are missing
    """
    if weights is None:
        weights = POTENTIAL_SCORING_WEIGHTS
    
    required_cols = ['age', 'goals_per_90', 'assists_per_90', 'progressive_carries', 
                    'progressive_passes', 'expected_goals', 'expected_assists', 'minutes']
    
    missing_cols = [col for col in required_cols if col not in player_row.index]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    age = player_row['age']
    if age >= max_age:
        age_factor = 0
    else:
        age_factor = (max_age - age) * weights['age_factor']
    
    # Calculate progressive total
    prog_total = player_row['progressive_carries'] + player_row['progressive_passes']
    
    score = (
        prog_total * weights['progressive_carries'] +
        player_row['minutes'] * weights['minutes'] +
        age_factor +
        player_row['expected_goals'] * weights['expected_goals'] +
        player_row['expected_assists'] * weights['expected_assists']
    )
    
    return score


def filter_midfielders(df: pd.DataFrame, 
                      min_minutes: int = 500,
                      attacking: bool = False,
                      defensive: bool = False) -> pd.DataFrame:
    """
    Filter dataframe for midfielders based on criteria.
    
    Args:
        df: Input dataframe with player data
        min_minutes: Minimum minutes threshold
        attacking: If True, filter for attacking midfielders
        defensive: If True, filter for defensive midfielders
        
    Returns:
        Filtered dataframe
        
    Raises:
        ValueError: If both attacking and defensive are True
    """
    if attacking and defensive:
        raise ValueError("Cannot filter for both attacking and defensive simultaneously")
    
    # Base filter for midfielders with minimum minutes
    filtered_df = df[
        (df['position'].str.contains('Midfielder', case=False, na=False)) &
        (df['minutes'] >= min_minutes)
    ]
    
    if attacking:
        filters = POSITION_FILTERS['attacking_midfielder']
        filtered_df = filtered_df[
            (filtered_df['goals_per_90'] >= filters['goals_per_90_min']) |
            (filtered_df['assists_per_90'] >= filters['assists_per_90_min'])
        ]
    elif defensive:
        filters = POSITION_FILTERS['defensive_midfielder']
        filtered_df = filtered_df[
            (filtered_df['goals_per_90'] <= filters['goals_per_90_max']) &
            (filtered_df['assists_per_90'] <= filters['assists_per_90_max'])
        ]
    
    return filtered_df


def filter_by_position(df: pd.DataFrame, 
                      position_type: str,
                      min_minutes: int = 500) -> pd.DataFrame:
    """
    Filter dataframe by position type using predefined filters.
    
    Args:
        df: Input dataframe
        position_type: Type from POSITION_FILTERS keys
        min_minutes: Minimum minutes threshold
        
    Returns:
        Filtered dataframe
        
    Raises:
        ValueError: If position_type not in POSITION_FILTERS
    """
    if position_type not in POSITION_FILTERS:
        valid_types = list(POSITION_FILTERS.keys())
        raise ValueError(f"Invalid position_type '{position_type}'. Valid types: {valid_types}")
    
    filters = POSITION_FILTERS[position_type]
    
    # Base filter
    filtered_df = df[
        (df['position'].str.contains(filters['position_contains'], case=False, na=False)) &
        (df['minutes'] >= min_minutes)
    ]
    
    # Apply additional filters if they exist
    if 'goals_per_90_max' in filters:
        filtered_df = filtered_df[filtered_df['goals_per_90'] <= filters['goals_per_90_max']]
    if 'goals_per_90_min' in filters:
        filtered_df = filtered_df[filtered_df['goals_per_90'] >= filters['goals_per_90_min']]
    if 'assists_per_90_max' in filters:
        filtered_df = filtered_df[filtered_df['assists_per_90'] <= filters['assists_per_90_max']]
    if 'assists_per_90_min' in filters:
        filtered_df = filtered_df[filtered_df['assists_per_90'] >= filters['assists_per_90_min']]
    
    return filtered_df


def flatten_multiindex_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten multi-level column index into single-level column names.
    
    Args:
        df: DataFrame with multi-level columns
        
    Returns:
        DataFrame with flattened column names
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() for col in df.columns]
    return df


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:  # Avoid adding handlers multiple times
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger


def validate_dataframe_columns(df: pd.DataFrame, 
                              required_columns: List[str],
                              df_name: str = "DataFrame") -> None:
    """
    Validate that a DataFrame contains required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        df_name: Name for error messages
        
    Raises:
        ValueError: If required columns are missing
    """
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"{df_name} missing required columns: {missing_cols}")


def get_tier_description(potential_score: float) -> Tuple[str, str]:
    """
    Get tier classification for a potential score.
    
    Args:
        potential_score: Calculated potential score
        
    Returns:
        Tuple of (tier_emoji, tier_description)
    """
    if potential_score >= 140:
        return "⭐", "ELITE (Top 5 level)"
    elif potential_score >= 120:
        return "🌟", "HIGH (Top 10 level)"
    elif potential_score >= 100:
        return "💫", "GOOD (Top 20 level)"
    else:
        return "📈", "DEVELOPING"