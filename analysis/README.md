# Analysis Tools

This directory contains the core analysis modules for soccer data analysis.

## Core Modules

### `clean_player_analyzer.py`
Main analysis class that uses properly cleaned data. Provides:
- Player search functionality
- Player comparison across metrics
- Position-based filtering
- Similar player discovery

### `player_analyzer.py` 
Legacy analyzer (kept for compatibility) - uses raw data with column issues.

## Specialized Analysis

### `dm_attributes_analysis.py`
Deep analysis of defensive midfielder attributes:
- Compares defensive vs attacking midfielders
- Identifies key DM skills (progressive passing, durability)
- League-by-league breakdown
- Individual player rankings

### `young_dm_scouting.py`
Comprehensive young player scouting tool:
- Finds prospects under 23
- Calculates potential scores
- Age group analysis
- Playing time and coach trust metrics

### `check_ugochukwu_agoume.py`
Specific analysis for Ugochukwu and Agoumé:
- Detailed prospect evaluation
- Comparison to top young DMs
- Strengths and development areas

## Usage

```python
from analysis.clean_player_analyzer import CleanPlayerAnalyzer

analyzer = CleanPlayerAnalyzer()
results = analyzer.search_players("Haaland")
```

## Data Requirements

All analysis tools expect clean data in `data/clean/` directory.