"""
Unit tests for CleanPlayerAnalyzer.

This module contains comprehensive tests for the CleanPlayerAnalyzer class,
including data loading, player search, comparison, and error handling.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os
import sys

# Add the parent directory to sys.path to import analysis modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from analysis.clean_player_analyzer import CleanPlayerAnalyzer
from analysis.utils import calculate_potential_score, filter_midfielders


class TestCleanPlayerAnalyzer:
    """Test cases for CleanPlayerAnalyzer class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample player data for testing."""
        data = {
            'nationality': ['ENG', 'ESP', 'FRA', 'GER', 'ITA'],
            'position': ['Forward', 'Midfielder', 'Defender', 'Midfielder', 'Forward'],
            'age': [25, 22, 29, 21, 27],
            'minutes': [2500, 1800, 3000, 1200, 2200],
            'goals': [20, 5, 2, 3, 15],
            'assists': [8, 12, 1, 8, 6],
            'expected_goals': [18.5, 4.2, 1.8, 2.9, 14.1],
            'expected_assists': [7.3, 11.8, 0.9, 7.5, 5.2],
            'goals_per_90': [0.72, 0.25, 0.06, 0.22, 0.61],
            'assists_per_90': [0.29, 0.60, 0.03, 0.60, 0.24],
            'progressive_carries': [45, 78, 25, 65, 52],
            'progressive_passes': [120, 180, 95, 145, 110]
        }
        
        # Create MultiIndex for realistic structure
        index = pd.MultiIndex.from_tuples([
            ('ENG-Premier League', '2425', 'Arsenal', 'Test Player 1'),
            ('ESP-La Liga', '2425', 'Barcelona', 'Test Player 2'),
            ('FRA-Ligue 1', '2425', 'PSG', 'Test Player 3'),
            ('GER-Bundesliga', '2425', 'Bayern', 'Test Player 4'),
            ('ITA-Serie A', '2425', 'Juventus', 'Test Player 5')
        ], names=['league', 'season', 'team', 'player'])
        
        return pd.DataFrame(data, index=index)
    
    @pytest.fixture
    def temp_data_dir(self, sample_data):
        """Create temporary directory with sample data file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir)
            sample_data.to_csv(data_path / 'player_standard_clean.csv')
            yield str(data_path)
    
    def test_initialization_success(self, temp_data_dir):
        """Test successful initialization with valid data."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        assert analyzer.standard_data is not None
        assert len(analyzer.standard_data) == 5
        assert analyzer.data_dir == Path(temp_data_dir)
    
    def test_initialization_missing_directory(self):
        """Test initialization with non-existent directory."""
        with pytest.raises(FileNotFoundError, match="Data directory does not exist"):
            CleanPlayerAnalyzer(data_dir="/non/existent/path")
    
    def test_initialization_missing_file(self):
        """Test initialization with missing data file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(FileNotFoundError, match="Standard data file not found"):
                CleanPlayerAnalyzer(data_dir=temp_dir)
    
    def test_search_players_found(self, temp_data_dir):
        """Test searching for players that exist."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        result = analyzer.search_players("Test Player")
        
        assert len(result) == 5  # All test players should match
        assert 'position' in result.columns
        assert 'goals' in result.columns
        assert 'assists' in result.columns
    
    def test_search_players_specific(self, temp_data_dir):
        """Test searching for specific player."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        result = analyzer.search_players("Test Player 1")
        
        assert len(result) == 1
        assert result.iloc[0]['position'] == 'Forward'
        assert result.iloc[0]['goals'] == 20
    
    def test_search_players_not_found(self, temp_data_dir):
        """Test searching for non-existent player."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        result = analyzer.search_players("Non Existent Player")
        
        assert len(result) == 0
    
    def test_search_players_with_position_filter(self, temp_data_dir):
        """Test searching with position filter."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        result = analyzer.search_players("Test Player", position="Midfielder")
        
        assert len(result) == 2  # Only midfielders should match
        assert all(result['position'] == 'Midfielder')
    
    def test_search_players_min_minutes_filter(self, temp_data_dir):
        """Test searching with minimum minutes filter."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        result = analyzer.search_players("Test Player", min_minutes=2000)
        
        assert len(result) == 3  # Only players with 2000+ minutes
        assert all(result['minutes'] >= 2000)
    
    def test_compare_players_success(self, temp_data_dir):
        """Test successful player comparison."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        result = analyzer.compare_players(["Test Player 1", "Test Player 2"])
        
        assert len(result) == 2
        assert 'player' in result.columns
        assert 'team' in result.columns
        assert 'league' in result.columns
        assert 'goals' in result.columns
    
    def test_compare_players_not_found(self, temp_data_dir):
        """Test comparison with non-existent players."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        
        with pytest.raises(ValueError, match="No players found from the provided list"):
            analyzer.compare_players(["Non Existent 1", "Non Existent 2"])
    
    def test_compare_players_partial_found(self, temp_data_dir):
        """Test comparison with mix of found and not found players."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        result = analyzer.compare_players(["Test Player 1", "Non Existent"])
        
        assert len(result) == 1  # Only the found player
        assert result.iloc[0]['player'] == "Test Player 1"
    
    def test_get_players_by_position(self, temp_data_dir):
        """Test getting players by position."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        result = analyzer.get_players_by_position("Midfielder")
        
        assert len(result) == 2
        assert all(result['position'] == 'Midfielder')
    
    def test_get_position_leaders(self, temp_data_dir):
        """Test getting position leaders by statistic."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        result = analyzer.get_position_leaders("Forward", "goals", top_n=2)
        
        assert len(result) == 2
        assert all(result['position'] == 'Forward')
        # Should be sorted by goals (descending)
        assert result.iloc[0]['goals'] >= result.iloc[1]['goals']
    
    def test_get_position_leaders_invalid_stat(self, temp_data_dir):
        """Test getting leaders with invalid statistic."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        
        with pytest.raises(ValueError, match="Stat 'invalid_stat' not found"):
            analyzer.get_position_leaders("Forward", "invalid_stat")
    
    def test_get_young_prospects(self, temp_data_dir):
        """Test getting young prospects."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        result = analyzer.get_young_prospects(max_age=25, min_minutes=1000)
        
        # Should find players under 25 with 1000+ minutes
        assert len(result) >= 1
        assert all(result['age'] < 25)
        assert all(result['minutes'] >= 1000)
        assert 'potential_score' in result.columns
    
    def test_data_summary(self, temp_data_dir):
        """Test data summary property."""
        analyzer = CleanPlayerAnalyzer(data_dir=temp_data_dir)
        summary = analyzer.data_summary
        
        assert summary['total_players'] == 5
        assert len(summary['leagues']) == 5
        assert 'age_range' in summary
        assert 'data_shape' in summary
    
    def test_no_data_loaded_error(self):
        """Test methods when no data is loaded."""
        # Create analyzer without proper initialization
        analyzer = CleanPlayerAnalyzer.__new__(CleanPlayerAnalyzer)
        analyzer.standard_data = None
        
        with pytest.raises(ValueError, match="No data loaded"):
            analyzer.search_players("test")
        
        with pytest.raises(ValueError, match="No data loaded"):
            analyzer.compare_players(["test"])
        
        with pytest.raises(ValueError, match="No data loaded"):
            analyzer.get_players_by_position("Forward")


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    @pytest.fixture
    def sample_player_row(self):
        """Create sample player data for utility function testing."""
        return pd.Series({
            'age': 21,
            'goals_per_90': 0.15,
            'assists_per_90': 0.08,
            'progressive_carries': 45,
            'progressive_passes': 120,
            'expected_goals': 3.2,
            'expected_assists': 2.8,
            'minutes': 2000
        })
    
    def test_calculate_potential_score_success(self, sample_player_row):
        """Test successful potential score calculation."""
        score = calculate_potential_score(sample_player_row)
        
        assert isinstance(score, float)
        assert score > 0
    
    def test_calculate_potential_score_missing_columns(self):
        """Test potential score calculation with missing columns."""
        incomplete_data = pd.Series({'age': 21, 'goals_per_90': 0.15})
        
        with pytest.raises(ValueError, match="Missing required columns"):
            calculate_potential_score(incomplete_data)
    
    def test_filter_midfielders_basic(self):
        """Test basic midfielder filtering."""
        data = pd.DataFrame({
            'position': ['Forward', 'Midfielder', 'Defender', 'Midfielder'],
            'minutes': [2000, 1500, 2500, 800],
            'goals_per_90': [0.5, 0.1, 0.05, 0.15],
            'assists_per_90': [0.2, 0.3, 0.02, 0.12]
        })
        
        result = filter_midfielders(data, min_minutes=1000)
        
        assert len(result) == 1  # Only one midfielder with 1000+ minutes
        assert result.iloc[0]['position'] == 'Midfielder'
        assert result.iloc[0]['minutes'] >= 1000
    
    def test_filter_midfielders_defensive(self):
        """Test filtering for defensive midfielders."""
        data = pd.DataFrame({
            'position': ['Midfielder', 'Midfielder', 'Midfielder'],
            'minutes': [2000, 1500, 2500],
            'goals_per_90': [0.05, 0.25, 0.15],  # First is defensive
            'assists_per_90': [0.08, 0.30, 0.20]  # First is defensive
        })
        
        result = filter_midfielders(data, min_minutes=1000, defensive=True)
        
        assert len(result) == 1
        assert result.iloc[0]['goals_per_90'] <= 0.20
        assert result.iloc[0]['assists_per_90'] <= 0.25
    
    def test_filter_midfielders_attacking(self):
        """Test filtering for attacking midfielders."""
        data = pd.DataFrame({
            'position': ['Midfielder', 'Midfielder', 'Midfielder'],
            'minutes': [2000, 1500, 2500],
            'goals_per_90': [0.05, 0.25, 0.15],
            'assists_per_90': [0.08, 0.30, 0.20]
        })
        
        result = filter_midfielders(data, min_minutes=1000, attacking=True)
        
        assert len(result) == 1  # Second midfielder meets attacking criteria
        assert (result.iloc[0]['goals_per_90'] >= 0.20) or (result.iloc[0]['assists_per_90'] >= 0.25)
    
    def test_filter_midfielders_conflicting_flags(self):
        """Test filtering with conflicting attacking/defensive flags."""
        data = pd.DataFrame({
            'position': ['Midfielder'],
            'minutes': [2000],
            'goals_per_90': [0.15],
            'assists_per_90': [0.12]
        })
        
        with pytest.raises(ValueError, match="Cannot filter for both attacking and defensive"):
            filter_midfielders(data, attacking=True, defensive=True)


if __name__ == "__main__":
    pytest.main([__file__])