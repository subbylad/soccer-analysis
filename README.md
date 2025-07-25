# Soccer Data Analysis Toolkit 🏈

A comprehensive Python toolkit for soccer data analysis, player comparison, and discovery using data from the Big 5 European leagues.

## Features

✅ **Data Collection**: Automated download of player and team statistics from FBref  
✅ **Player Search**: Find players by name with comprehensive stats  
✅ **Player Comparison**: Compare multiple players across key metrics  
✅ **Similar Player Discovery**: Find players with similar playing styles  
✅ **Top Performers**: Identify league leaders in goals, assists, and other metrics  
✅ **Dashboard**: Ready-to-use analysis dashboard  

## Project Structure

```
socceranalysis/
├── data/                   # Cached soccer data (CSV files)
├── scripts/               # Data loading utilities
│   └── data_loader.py     # Main data downloader
├── analysis/              # Analysis modules
│   └── player_analyzer.py # Core player analysis class
├── dashboards/            # Dashboard and demo scripts
│   └── quick_demo.py      # Comprehensive demo
└── notebooks/             # Jupyter notebooks (for future use)
```

## Quick Start

### 1. Run the Demo
```bash
python3 dashboards/quick_demo.py
```

This will show:
- Top goal scorers and assist providers
- Player search examples
- Player comparisons
- Goals + assists leaderboard

### 2. Basic Usage Examples

#### Search for a Player
```python
from analysis.player_analyzer import PlayerAnalyzer

analyzer = PlayerAnalyzer()

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

#### Find Similar Players
```python
# Find players similar to Haaland
similar = analyzer.find_similar_players("Haaland", position="FW")
print(similar)
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

## Next Steps for Development

1. **Interactive Dashboards**: Create web-based dashboards with Plotly/Streamlit
2. **Advanced Analytics**: Player performance trends, injury prediction
3. **Scouting Reports**: Automated player scouting and recommendation system
4. **Multi-Season Analysis**: Historical data comparison and player development tracking
5. **Market Value Integration**: Combine with transfer market data

## Dependencies

- `soccerdata`: Soccer data scraping and API
- `pandas`: Data manipulation and analysis  
- `matplotlib`: Basic plotting
- `seaborn`: Statistical visualizations
- `numpy`: Numerical computations

## Installation

```bash
pip install soccerdata pandas matplotlib seaborn numpy
```

---

**Ready to discover the next soccer superstar!** 🌟