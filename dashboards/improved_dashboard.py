#!/usr/bin/env python3
"""
Improved Soccer Analysis Dashboard

A much better, more visual Streamlit dashboard with proper UI elements
and clear player display functionality.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from pathlib import Path
import logging

# Add the parent directory to sys.path to import analysis modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.clean_player_analyzer import CleanPlayerAnalyzer
from analysis.utils import setup_logger

# Set up logging
logger = setup_logger(__name__, level=logging.WARNING)

# Configure Streamlit page
st.set_page_config(
    page_title="Soccer Analysis Dashboard ⚽",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .player-card {
        border: 2px solid #1f77b4;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: linear-gradient(135deg, #f8f9fa, #e3f2fd);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .player-name {
        font-size: 1.4rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 5px;
    }
    .player-info {
        font-size: 1rem;
        margin: 5px 0;
        color: #333;
    }
    .stat-highlight {
        background-color: #fff3cd;
        padding: 3px 6px;
        border-radius: 4px;
        font-weight: bold;
    }
    .search-results {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the soccer data."""
    try:
        analyzer = CleanPlayerAnalyzer()
        return analyzer
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def display_player_card(player_idx, player_data):
    """Display a nice player card with all information."""
    player_name = player_idx[3]
    team_name = player_idx[2]
    league_name = player_idx[0]
    
    # Calculate stats
    goals = player_data.get('goals', 0)
    assists = player_data.get('assists', 0)
    total_ga = goals + assists
    minutes = player_data.get('minutes', 0)
    goals_per_90 = player_data.get('goals_per_90', 0)
    assists_per_90 = player_data.get('assists_per_90', 0)
    xg = player_data.get('expected_goals', 0)
    xa = player_data.get('expected_assists', 0)
    position = player_data.get('position', 'N/A')
    age = player_data.get('age', 'N/A')
    nationality = player_data.get('nationality', 'N/A')
    
    # Create the card HTML
    card_html = f"""
    <div class="player-card">
        <div class="player-name">⚽ {player_name}</div>
        <div class="player-info"><strong>Team:</strong> {team_name} ({league_name})</div>
        <div class="player-info"><strong>Position:</strong> {position} | <strong>Age:</strong> {age} | <strong>Nationality:</strong> {nationality}</div>
        <div class="player-info">
            <strong>Playing Time:</strong> <span class="stat-highlight">{minutes:,} minutes</span>
        </div>
        <div class="player-info">
            <strong>Goals:</strong> <span class="stat-highlight">{goals}</span> ({goals_per_90:.2f}/90) | 
            <strong>Assists:</strong> <span class="stat-highlight">{assists}</span> ({assists_per_90:.2f}/90) | 
            <strong>G+A:</strong> <span class="stat-highlight">{total_ga}</span>
        </div>
        <div class="player-info">
            <strong>Expected Goals:</strong> {xg:.1f} | <strong>Expected Assists:</strong> {xa:.1f}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def player_search_page():
    """Enhanced player search page."""
    st.header("🔍 Player Search & Analysis")
    
    # Load data
    analyzer = load_data()
    if analyzer is None:
        st.error("Failed to load data!")
        return
    
    # Search interface
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "🔎 Search for players:", 
            placeholder="Try: Watkins, Haaland, Messi, Silva, etc.",
            help="Enter any part of a player's name"
        )
    
    with col2:
        min_minutes = st.selectbox(
            "Min. Minutes:", 
            [0, 300, 500, 1000, 1500, 2000], 
            index=1,
            help="Minimum playing time filter"
        )
    
    with col3:
        max_results = st.selectbox(
            "Max Results:", 
            [5, 10, 20, 50], 
            index=2,
            help="Maximum number of results to show"
        )
    
    # Position and league filters
    col4, col5 = st.columns(2)
    with col4:
        position_filter = st.selectbox(
            "Position Filter:", 
            ["All Positions", "Forward", "Midfielder", "Defender", "Goalkeeper"]
        )
    
    with col5:
        league_filter = st.selectbox(
            "League Filter:",
            ["All Leagues", "ENG-Premier League", "ESP-La Liga", "ITA-Serie A", "GER-Bundesliga", "FRA-Ligue 1"]
        )
    
    # Search execution
    if search_term:
        with st.spinner("Searching players..."):
            try:
                # Apply filters
                position = None if position_filter == "All Positions" else position_filter
                results = analyzer.search_players(search_term, min_minutes=min_minutes, position=position)
                
                # Apply league filter
                if league_filter != "All Leagues":
                    league_mask = [idx[0] == league_filter for idx in results.index]
                    results = results[league_mask]
                
                # Limit results
                if len(results) > max_results:
                    results = results.head(max_results)
                    st.info(f"Showing top {max_results} results. Use filters to narrow your search.")
                
                if not results.empty:
                    # Success message
                    st.markdown(f"""
                    <div class="search-results">
                        <strong>✅ Found {len(results)} player(s) matching '{search_term}'</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display each player
                    for idx, (player_idx, player_data) in enumerate(results.iterrows()):
                        st.markdown(f"### Result #{idx + 1}")
                        display_player_card(player_idx, player_data)
                    
                    # Comparison table if multiple players
                    if len(results) > 1:
                        st.markdown("---")
                        st.subheader("📊 Quick Comparison Table")
                        
                        # Create comparison DataFrame
                        comparison_data = []
                        for player_idx, player in results.iterrows():
                            comparison_data.append({
                                'Player': player_idx[3],
                                'Team': player_idx[2],
                                'League': player_idx[0],
                                'Position': player.get('position', 'N/A'),
                                'Age': player.get('age', 'N/A'),
                                'Minutes': player.get('minutes', 0),
                                'Goals': player.get('goals', 0),
                                'Assists': player.get('assists', 0),
                                'Goals/90': f"{player.get('goals_per_90', 0):.2f}",
                                'Assists/90': f"{player.get('assists_per_90', 0):.2f}",
                            })
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.dataframe(comparison_df, use_container_width=True)
                        
                        # Performance chart
                        if len(results) <= 10:
                            st.subheader("📈 Performance Comparison")
                            
                            chart_data = []
                            for player_idx, player in results.iterrows():
                                chart_data.append({
                                    'Player': player_idx[3],
                                    'Goals per 90': player.get('goals_per_90', 0),
                                    'Assists per 90': player.get('assists_per_90', 0),
                                    'Team': player_idx[2],
                                    'League': player_idx[0]
                                })
                            
                            chart_df = pd.DataFrame(chart_data)
                            
                            fig = px.scatter(
                                chart_df,
                                x='Goals per 90',
                                y='Assists per 90',
                                color='League',
                                size=[15] * len(chart_df),  # Fixed size
                                hover_data=['Player', 'Team'],
                                title=f"Performance Comparison: {search_term}",
                                width=800,
                                height=500
                            )
                            
                            # Add player name annotations
                            for i, row in chart_df.iterrows():
                                fig.add_annotation(
                                    x=row['Goals per 90'],
                                    y=row['Assists per 90'],
                                    text=row['Player'].split()[-1],  # Show last name
                                    showarrow=True,
                                    arrowhead=2,
                                    yshift=10
                                )
                            
                            st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.warning(f"❌ No players found matching '{search_term}' with your current filters.")
                    st.info("💡 Try:")
                    st.info("• Reducing the minimum minutes filter")
                    st.info("• Changing position or league filters")
                    st.info("• Using a shorter search term (e.g., 'Silva' instead of 'Bernardo Silva')")
                    
            except Exception as e:
                st.error(f"❌ Error during search: {e}")
                
    else:
        # Show helpful information when no search term
        st.info("👆 Enter a player name above to start searching!")
        
        # Quick search suggestions
        st.markdown("### 🔥 Popular Searches")
        
        col1, col2, col3, col4 = st.columns(4)
        
        suggestions = [
            "Haaland", "Messi", "Mbappé", "Kane",
            "Salah", "Watkins", "Silva", "Ronaldo",
            "Pedri", "Bellingham", "Vinicius", "Lewandowski"
        ]
        
        for i, suggestion in enumerate(suggestions):
            col = [col1, col2, col3, col4][i % 4]
            with col:
                if st.button(f"🔍 {suggestion}", key=f"search_{suggestion}"):
                    st.experimental_rerun()

def main():
    """Main dashboard function."""
    # Header
    st.markdown('<h1 class="main-header">⚽ Soccer Player Search</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("**Search and analyze players from the Big 5 European Leagues** 🏆")
    
    # Load data summary
    analyzer = load_data()
    if analyzer:
        summary = analyzer.data_summary
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Players", f"{summary['total_players']:,}")
        with col2:
            st.metric("Leagues", len(summary['leagues']))
        with col3:
            age_range = summary['age_range']
            st.metric("Age Range", f"{age_range[0]}-{age_range[1]}")
        with col4:
            st.metric("Season", "2024/25")
    
    st.markdown("---")
    
    # Main search functionality
    player_search_page()

if __name__ == "__main__":
    main()