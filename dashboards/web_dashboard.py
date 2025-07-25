#!/usr/bin/env python3
"""
Soccer Data Analysis Web Dashboard

An interactive Streamlit dashboard for exploring soccer player data,
comparing players, and analyzing team performance across European leagues.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path
import logging
from typing import List, Optional, Dict, Any

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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .player-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #fafafa;
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

def create_performance_chart(players_df: pd.DataFrame, x_col: str, y_col: str, 
                           color_col: str = None, title: str = "Player Performance") -> go.Figure:
    """Create an interactive performance scatter plot."""
    fig = px.scatter(
        players_df,
        x=x_col,
        y=y_col,
        color=color_col if color_col else 'league',
        hover_data=['player', 'team', 'age', 'minutes'],
        title=title,
        labels={
            'goals_per_90': 'Goals per 90 min',
            'assists_per_90': 'Assists per 90 min',
            'minutes': 'Minutes Played',
            'age': 'Age'
        }
    )
    
    fig.update_layout(
        height=500,
        hovermode='closest'
    )
    
    return fig

def create_top_performers_chart(data: pd.DataFrame, stat: str, top_n: int = 10) -> go.Figure:
    """Create a horizontal bar chart for top performers."""
    top_players = data.nlargest(top_n, stat)
    
    fig = go.Figure(data=[
        go.Bar(
            y=[f"{row['player']} ({row['team']})" for _, row in top_players.iterrows()],
            x=top_players[stat],
            orientation='h',
            marker=dict(color='#1f77b4', opacity=0.8),
            text=top_players[stat].round(2),
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title=f"Top {top_n} Players - {stat.replace('_', ' ').title()}",
        xaxis_title=stat.replace('_', ' ').title(),
        yaxis_title="Player (Team)",
        height=400,
        yaxis=dict(autorange="reversed")
    )
    
    return fig

def create_league_comparison_chart(data: pd.DataFrame) -> go.Figure:
    """Create league comparison charts."""
    league_stats = data.groupby('league').agg({
        'goals_per_90': 'mean',
        'assists_per_90': 'mean',
        'age': 'mean',
        'player': 'count'
    }).round(3)
    
    league_stats.columns = ['Avg Goals/90', 'Avg Assists/90', 'Avg Age', 'Total Players']
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Average Goals per 90min', 'Average Assists per 90min', 
                       'Average Age', 'Total Players'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    leagues = league_stats.index
    colors = px.colors.qualitative.Set1[:len(leagues)]
    
    # Add traces
    fig.add_trace(go.Bar(x=leagues, y=league_stats['Avg Goals/90'], 
                        name='Goals/90', marker_color=colors), row=1, col=1)
    fig.add_trace(go.Bar(x=leagues, y=league_stats['Avg Assists/90'], 
                        name='Assists/90', marker_color=colors), row=1, col=2)
    fig.add_trace(go.Bar(x=leagues, y=league_stats['Avg Age'], 
                        name='Age', marker_color=colors), row=2, col=1)
    fig.add_trace(go.Bar(x=leagues, y=league_stats['Total Players'], 
                        name='Players', marker_color=colors), row=2, col=2)
    
    fig.update_layout(height=600, showlegend=False, title_text="League Statistics Comparison")
    
    return fig

def player_search_section(analyzer: CleanPlayerAnalyzer):
    """Player search and comparison section."""
    st.header("🔍 Player Search & Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("Search for players:", placeholder="e.g., Messi, Haaland, Mbappé")
        
    with col2:
        min_minutes = st.selectbox("Minimum playing time:", [0, 500, 1000, 1500, 2000], index=1)
    
    # Add position filter
    col3, col4 = st.columns([1, 1])
    with col3:
        position_filter = st.selectbox("Position (optional):", 
                                     ["All Positions", "Forward", "Midfielder", "Defender", "Goalkeeper"])
    with col4:
        max_results = st.selectbox("Max results:", [5, 10, 20, 50], index=1)
    
    if search_term:
        try:
            # Apply position filter if specified
            position = None if position_filter == "All Positions" else position_filter
            results = analyzer.search_players(search_term, min_minutes=min_minutes, position=position)
            
            # Limit results
            if not results.empty and len(results) > max_results:
                results = results.head(max_results)
                st.info(f"Showing top {max_results} results. {len(analyzer.search_players(search_term, min_minutes=min_minutes, position=position)) - max_results} more players match your search.")
            
            if not results.empty:
                st.success(f"Found {len(results)} player(s) matching '{search_term}'")
                
                # Display results in a nice format
                for idx, (player_idx, player) in enumerate(results.iterrows()):
                    player_name = player_idx[3]  # player name
                    team_name = player_idx[2]    # team name  
                    league_name = player_idx[0]  # league name
                    
                    with st.container():
                        # Calculate additional stats
                        total_ga = player.get('goals', 0) + player.get('assists', 0)
                        xg = player.get('expected_goals', 0)
                        xa = player.get('expected_assists', 0)
                        
                        st.markdown(f"""
                        <div class="player-card">
                            <h4>⚽ {player_name} - {team_name} ({league_name})</h4>
                            <p><strong>Position:</strong> {player.get('position', 'N/A')} | <strong>Age:</strong> {player.get('age', 'N/A')} | <strong>Nationality:</strong> {player.get('nationality', 'N/A')}</p>
                            <p><strong>Minutes:</strong> {player.get('minutes', 0):,} | <strong>Goals:</strong> {player.get('goals', 0)} ({player.get('goals_per_90', 0):.2f}/90) | <strong>Assists:</strong> {player.get('assists', 0)} ({player.get('assists_per_90', 0):.2f}/90)</p>
                            <p><strong>G+A:</strong> {total_ga} | <strong>xG:</strong> {xg:.1f} | <strong>xA:</strong> {xa:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show comparison if multiple players found
                if len(results) > 1:
                    st.subheader("📊 Player Comparison")
                    
                    comparison_metrics = ['goals', 'assists', 'goals_per_90', 'assists_per_90', 'minutes']
                    available_metrics = [col for col in comparison_metrics if col in results.columns]
                    
                    if available_metrics:
                        # Create comparison DataFrame
                        comparison_data = []
                        for player_idx, player in results.iterrows():
                            row_data = {
                                'Player': f"{player_idx[3]} ({player_idx[2]})",  # Player (Team)
                                'League': player_idx[0],
                                'Position': player.get('position', 'N/A'),
                                'Age': player.get('age', 'N/A'),
                            }
                            # Add available metrics
                            for metric in available_metrics:
                                row_data[metric.replace('_', ' ').title()] = player.get(metric, 0)
                            comparison_data.append(row_data)
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.dataframe(comparison_df, use_container_width=True)
                        
                        # Create comparison chart
                        if len(results) <= 10:  # Only create chart for reasonable number of players
                            fig = create_performance_chart(
                                results.reset_index(),
                                'goals_per_90', 'assists_per_90',
                                title=f"Performance Comparison: {search_term}"
                            )
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No players found matching '{search_term}' with {min_minutes}+ minutes")
                
        except Exception as e:
            st.error(f"Error searching for players: {e}")
    
    else:
        # Show browse functionality when no search term
        st.info("💡 Enter a player name above to search, or browse by filters below")
        
        if st.button("🎲 Show Random Sample"):
            try:
                # Get random sample of players
                all_players = analyzer.standard_data[analyzer.standard_data['minutes'] >= min_minutes]
                if position_filter != "All Positions":
                    all_players = all_players[all_players['position'].str.contains(position_filter, case=False, na=False)]
                
                if not all_players.empty:
                    sample_size = min(5, len(all_players))
                    sample_players = all_players.sample(n=sample_size)
                    
                    st.success(f"Random sample of {sample_size} players:")
                    
                    for idx, (player_idx, player) in enumerate(sample_players.iterrows()):
                        player_name = player_idx[3]
                        team_name = player_idx[2]
                        league_name = player_idx[0]
                        
                        total_ga = player.get('goals', 0) + player.get('assists', 0)
                        xg = player.get('expected_goals', 0)
                        xa = player.get('expected_assists', 0)
                        
                        st.markdown(f"""
                        <div class="player-card">
                            <h4>⚽ {player_name} - {team_name} ({league_name})</h4>
                            <p><strong>Position:</strong> {player.get('position', 'N/A')} | <strong>Age:</strong> {player.get('age', 'N/A')} | <strong>Nationality:</strong> {player.get('nationality', 'N/A')}</p>
                            <p><strong>Minutes:</strong> {player.get('minutes', 0):,} | <strong>Goals:</strong> {player.get('goals', 0)} ({player.get('goals_per_90', 0):.2f}/90) | <strong>Assists:</strong> {player.get('assists', 0)} ({player.get('assists_per_90', 0):.2f}/90)</p>
                            <p><strong>G+A:</strong> {total_ga} | <strong>xG:</strong> {xg:.1f} | <strong>xA:</strong> {xa:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No players found with current filters")
            except Exception as e:
                st.error(f"Error browsing players: {e}")

def top_performers_section(analyzer: CleanPlayerAnalyzer):
    """Top performers analysis section."""
    st.header("🏆 Top Performers")
    
    # Get qualified players
    qualified_players = analyzer.standard_data[analyzer.standard_data['minutes'] >= 500].copy()
    
    # Add derived metrics
    qualified_players['total_ga'] = qualified_players['goals'] + qualified_players['assists']
    qualified_players['player'] = qualified_players.index.get_level_values('player')
    qualified_players['team'] = qualified_players.index.get_level_values('team')
    qualified_players['league'] = qualified_players.index.get_level_values('league')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚽ Top Goal Scorers")
        top_scorers = qualified_players.nlargest(10, 'goals')
        
        for i, (_, player) in enumerate(top_scorers.iterrows(), 1):
            st.write(f"{i}. **{player['player']}** ({player['team']}) - {player['goals']} goals")
        
        # Create chart
        fig_goals = create_top_performers_chart(top_scorers, 'goals', 10)
        st.plotly_chart(fig_goals, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Top Assist Providers")
        top_assisters = qualified_players.nlargest(10, 'assists')
        
        for i, (_, player) in enumerate(top_assisters.iterrows(), 1):
            st.write(f"{i}. **{player['player']}** ({player['team']}) - {player['assists']} assists")
        
        # Create chart
        fig_assists = create_top_performers_chart(top_assisters, 'assists', 10)
        st.plotly_chart(fig_assists, use_container_width=True)
    
    # Goals + Assists combination
    st.subheader("🏅 Best Goal + Assist Combination")
    top_ga = qualified_players.nlargest(10, 'total_ga')
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        for i, (_, player) in enumerate(top_ga.iterrows(), 1):
            st.write(f"{i}. **{player['player']}** ({player['team']}) - {int(player['total_ga'])} G+A")
    
    with col2:
        fig_ga = create_top_performers_chart(top_ga, 'total_ga', 10)
        st.plotly_chart(fig_ga, use_container_width=True)

def young_prospects_section(analyzer: CleanPlayerAnalyzer):
    """Young prospects analysis section."""
    st.header("🌟 Young Prospects")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        max_age = st.selectbox("Maximum age:", [19, 20, 21, 22, 23], index=2)
    with col2:
        min_minutes = st.selectbox("Minimum minutes:", [500, 1000, 1500, 2000], index=1)
    with col3:
        top_n = st.selectbox("Show top:", [5, 10, 15, 20], index=1)
    
    try:
        prospects = analyzer.get_young_prospects(max_age=max_age, min_minutes=min_minutes)
        
        if not prospects.empty:
            st.success(f"Found {len(prospects)} young prospects (age ≤ {max_age}, {min_minutes}+ minutes)")
            
            # Show top prospects
            top_prospects = prospects.head(top_n)
            
            # Create metrics display
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Prospects", len(prospects))
            with col2:
                st.metric("Average Age", f"{prospects['age'].mean():.1f}")
            with col3:
                st.metric("Avg Potential Score", f"{prospects['potential_score'].mean():.1f}")
            with col4:
                st.metric("Top Score", f"{prospects['potential_score'].max():.1f}")
            
            # Display prospects table
            st.subheader(f"Top {top_n} Young Prospects")
            
            display_df = top_prospects[['player', 'team', 'league', 'age', 'potential_score', 
                                     'goals_per_90', 'assists_per_90']].copy()
            display_df.columns = ['Player', 'Team', 'League', 'Age', 'Potential Score', 
                                'Goals/90', 'Assists/90']
            
            st.dataframe(display_df, use_container_width=True)
            
            # Create scatter plot of prospects
            fig = create_performance_chart(
                top_prospects,
                'age', 'potential_score',
                'league',
                f"Young Prospects: Age vs Potential Score (Top {top_n})"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning(f"No young prospects found with age ≤ {max_age} and {min_minutes}+ minutes")
            
    except Exception as e:
        st.error(f"Error analyzing young prospects: {e}")

def league_analysis_section(analyzer: CleanPlayerAnalyzer):
    """League analysis and comparison section."""
    st.header("🌍 League Analysis")
    
    # Get qualified players for analysis
    qualified_players = analyzer.standard_data[analyzer.standard_data['minutes'] >= 500].copy()
    qualified_players['player'] = qualified_players.index.get_level_values('player')
    qualified_players['team'] = qualified_players.index.get_level_values('team')
    qualified_players['league'] = qualified_players.index.get_level_values('league')
    
    # League overview
    league_summary = qualified_players.groupby('league').agg({
        'player': 'count',
        'age': 'mean',
        'goals_per_90': 'mean',
        'assists_per_90': 'mean',
        'minutes': 'mean'
    }).round(2)
    
    league_summary.columns = ['Players', 'Avg Age', 'Avg Goals/90', 'Avg Assists/90', 'Avg Minutes']
    
    st.subheader("📊 League Overview")
    st.dataframe(league_summary, use_container_width=True)
    
    # League comparison charts
    st.subheader("📈 League Comparisons")
    fig_leagues = create_league_comparison_chart(qualified_players)
    st.plotly_chart(fig_leagues, use_container_width=True)
    
    # Interactive league filter
    st.subheader("🔍 League Deep Dive")
    selected_leagues = st.multiselect(
        "Select leagues to compare:",
        options=qualified_players['league'].unique(),
        default=qualified_players['league'].unique()[:3]
    )
    
    if selected_leagues:
        filtered_data = qualified_players[qualified_players['league'].isin(selected_leagues)]
        
        # Performance distribution by league
        fig = px.box(
            filtered_data,
            x='league',
            y='goals_per_90',
            title="Goals per 90 minutes distribution by league"
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        fig2 = px.box(
            filtered_data,
            x='league',
            y='assists_per_90',
            title="Assists per 90 minutes distribution by league"
        )
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)

def main():
    """Main dashboard function."""
    # Header
    st.markdown('<h1 class="main-header">⚽ Soccer Data Analysis Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading soccer data..."):
        analyzer = load_data()
    
    if analyzer is None:
        st.error("Failed to load data. Please check if data files exist.")
        st.stop()
    
    # Data summary
    summary = analyzer.data_summary
    
    st.markdown("---")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", f"{summary['total_players']:,}")
    with col2:
        st.metric("Leagues", len(summary['leagues']))
    with col3:
        age_range = summary['age_range']
        st.metric("Age Range", f"{age_range[0]}-{age_range[1]}")
    with col4:
        st.metric("Data Shape", f"{summary['data_shape'][0]} × {summary['data_shape'][1]}")
    
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Analysis:",
        ["🔍 Player Search", "🏆 Top Performers", "🌟 Young Prospects", "🌍 League Analysis"]
    )
    
    # Page routing
    if page == "🔍 Player Search":
        player_search_section(analyzer)
    elif page == "🏆 Top Performers":
        top_performers_section(analyzer)
    elif page == "🌟 Young Prospects":
        young_prospects_section(analyzer)
    elif page == "🌍 League Analysis":
        league_analysis_section(analyzer)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Soccer Data Analysis Dashboard | Data from FBref via soccerdata package</p>
        <p>🔧 Built with Streamlit & Plotly | 📊 Analyzing Big 5 European Leagues</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()