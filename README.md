# Soccer Data Analysis Toolkit ⚽

A comprehensive Python toolkit for soccer data analysis, player comparison, and scouting using data from the Big 5 European leagues.

## Features

✅ **Data Collection**: Automated download and cleaning of player statistics from FBref  
✅ **Player Search**: Find players by name with comprehensive stats  
✅ **Player Comparison**: Compare multiple players across key metrics  
✅ **Scouting Tools**: Young player discovery and potential analysis  
✅ **Position Analysis**: Deep dive into defensive midfielder attributes  
✅ **Clean Data Pipeline**: Properly processed and standardized datasets  
✅ **Interactive Web Dashboard**: Modern web interface with charts and visualizations  

## Project Structure

```
socceranalysis/
├── data/
│   ├── raw/               # Original downloaded data
│   └── clean/             # Processed, analysis-ready data
├── scripts/               # Data pipeline utilities
│   ├── data_loader.py     # Downloads fresh data from FBref
│   └── data_cleaner.py    # Cleans and standardizes data
├── analysis/              # Core analysis modules
│   ├── clean_player_analyzer.py    # Main analysis class
│   ├── young_dm_scouting.py        # Young player scouting
│   ├── dm_attributes_analysis.py   # Defensive midfielder analysis
│   └── check_ugochukwu_agoume.py   # Specific player analysis
├── dashboards/
│   ├── quick_demo.py         # Command-line demo
│   ├── web_dashboard.py      # Interactive web dashboard (Streamlit)
│   └── improved_dashboard.py # Enhanced player search interface
└── notebooks/             # Reserved for Jupyter analysis
```

## Quick Start

### 1. 🌐 Web Dashboard (Recommended)
```bash
# Easy launcher
python3 run_dashboard.py

# Or directly with Streamlit
python3 -m streamlit run dashboards/web_dashboard.py
```

**Features:**
- 🔍 **Player Search**: Interactive search with filters
- 🏆 **Top Performers**: Visual charts of best players
- 🌟 **Young Prospects**: Scouting analysis with scoring
- 🌍 **League Analysis**: Compare leagues and distributions
- 📊 **Interactive Charts**: Hover, zoom, filter data

**Dashboard will open in your browser at:** `http://localhost:8501`

### 2. Command-Line Demo
```bash
python3 dashboards/quick_demo.py
```

This will show:
- Top goal scorers and assist providers
- Player search examples
- Player comparisons
- Goals + assists leaderboard

### 3. Basic Usage Examples

#### Search for a Player
```python
from analysis.clean_player_analyzer import CleanPlayerAnalyzer

analyzer = CleanPlayerAnalyzer()

# Search for players
haaland_stats = analyzer.search_players("Haaland")
print(haaland_stats)
```

#### Compare Players
```python
# Compare top strikers
comparison = analyzer.compare_players(["Haaland", "Mbappé", "Kane"])
print(comparison)
```

#### Scout Young Defensive Midfielders
```python
# Run young DM scouting analysis
python3 analysis/young_dm_scouting.py
```

#### Analyze Defensive Midfielder Attributes
```python
# Deep dive into what makes DMs effective
python3 analysis/dm_attributes_analysis.py
```

## Data Sources

- **FBref**: Player and team statistics from Big 5 European leagues
  - English Premier League
  - Spanish La Liga  
  - Italian Serie A
  - German Bundesliga
  - French Ligue 1

## Key Metrics Available

**Standard Stats**: Goals, Assists, Minutes Played, Cards, etc.  
**Shooting**: Shots, Shot Accuracy, Expected Goals (xG)  
**Passing**: Pass Completion, Progressive Passes, Expected Assists (xAG)  
**Defense**: Tackles, Interceptions, Clearances  

## Current Season Data

The toolkit currently loads **2024/25 season data** with:
- **2,853 players** across all positions
- **96 teams** from the Big 5 leagues
- Minimum 300 minutes played filter (adjustable)

## Sample Output

```
🏈 SOCCER DATA ANALYSIS TOOLKIT DEMO 🏈

Top 10 Goal Scorers (500+ minutes):
 1. Kylian Mbappé        (Real Madrid    ) - 31 goals (0.96/90min)
 2. Mohamed Salah        (Liverpool      ) - 29 goals (0.77/90min)
 3. Robert Lewandowski   (Barcelona      ) - 27 goals (0.91/90min)
 4. Harry Kane           (Bayern Munich  ) - 26 goals (0.98/90min)
 5. Mateo Retegui        (Atalanta       ) - 25 goals (0.94/90min)
```

## Advanced Features

### 🔍 **Scouting Analysis**
- Young player discovery (under 23)
- Potential scoring algorithm
- Position-specific analysis
- League-by-league breakdown

### 📊 **Defensive Midfielder Deep Dive**
- Progressive passing vs carrying analysis
- Comparison of DM vs attacking midfielders
- Individual player rankings and percentiles
- League style differences

### 🧹 **Clean Data Pipeline**
- Automated data cleaning and standardization
- Proper column naming and data types
- Position normalization
- Raw data preservation

## Recent Analysis Examples

- **Baleba vs Ligue 1**: Found Florian Sotoca (Lens) as closest statistical match
- **Young DM Prospects**: Identified Pedri, Diego Moreira, and Warren Zaïre-Emery as top prospects
- **DM Attributes**: Discovered DMs excel in durability and progressive passing, not carrying

## Dependencies

- `soccerdata`: Soccer data scraping and API
- `pandas`: Data manipulation and analysis  
- `matplotlib`: Basic plotting
- `seaborn`: Statistical visualizations
- `numpy`: Numerical computations

## Installation

```bash
# Install required dependencies
pip install soccerdata pandas matplotlib seaborn numpy

# For web dashboard
pip install streamlit plotly

# For development and testing
pip install pytest pytest-cov
```

## Testing

The project includes a comprehensive test suite to ensure reliability:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=analysis tests/

# Run specific test file
pytest tests/test_clean_player_analyzer.py -v
```

## Development

### Project Architecture

- **CleanPlayerAnalyzer**: Main analysis class with robust error handling
- **Utility Functions**: Shared configuration and helper functions in `analysis/utils.py`
- **Specialized Modules**: Young player scouting, DM analysis, specific player evaluation
- **Logging**: Structured logging throughout with configurable levels
- **Type Hints**: Full type annotation support for better development experience

### Configuration

Key parameters can be customized via `analysis/utils.py`:

```python
# Potential scoring weights
POTENTIAL_SCORING_WEIGHTS = {
    'goals_per_90': 3.0,
    'assists_per_90': 3.0, 
    'progressive_carries': 0.05,
    'progressive_passes': 0.02
}

# Playing time thresholds
MIN_MINUTES_THRESHOLDS = {
    'basic_analysis': 300,
    'comparison': 500,
    'scouting': 500,
    'high_usage': 2000
}
```

---

**Ready to discover the next soccer superstar!** 🌟