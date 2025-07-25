#!/usr/bin/env python3
"""
Soccer Analysis Chat Interface

A conversational Streamlit interface for natural language soccer queries.
Built on top of the Soccer Analytics API for seamless query processing.
"""

import streamlit as st
import sys
import os
from pathlib import Path
import time
from typing import List, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    from api.main_api import SoccerAnalyticsAPI, APIConfig
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info(f"Looking for modules in: {parent_dir}")
    st.stop()

# Configure Streamlit page
st.set_page_config(
    page_title="Soccer Chat ⚽💬",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for chat interface
st.markdown("""
<style>
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px auto;
        max-width: 70%;
        word-wrap: break-word;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px auto 8px 0;
        max-width: 70%;
        word-wrap: break-word;
    }
    
    .system-message {
        background: #e9ecef;
        color: #495057;
        padding: 8px 12px;
        border-radius: 12px;
        margin: 4px auto;
        text-align: center;
        font-size: 0.9rem;
        max-width: 50%;
    }
    
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e9ecef;
        padding: 12px 20px;
    }
    
    .suggestion-pill {
        background: #e7f3ff;
        color: #0066cc;
        padding: 6px 12px;
        border-radius: 20px;
        border: 1px solid #b3daff;
        margin: 2px;
        cursor: pointer;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    .main-header {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea, #764ba2);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
if 'api' not in st.session_state:
    with st.spinner("Initializing Soccer Analytics..."):
        try:
            st.session_state.api = SoccerAnalyticsAPI()
            st.session_state.api_ready = True
        except Exception as e:
            st.session_state.api_ready = False
            st.session_state.api_error = str(e)

def add_message(role: str, content: str, metadata: Dict[str, Any] = None):
    """Add a message to the chat history."""
    st.session_state.messages.append({
        'role': role,
        'content': content,
        'timestamp': time.time(),
        'metadata': metadata or {}
    })

def display_chat_history():
    """Display all chat messages in a styled container."""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        if message['role'] == 'user':
            st.markdown(
                f'<div class="user-message">{message["content"]}</div>',
                unsafe_allow_html=True
            )
        elif message['role'] == 'assistant':
            st.markdown(
                f'<div class="assistant-message">{message["content"]}</div>',
                unsafe_allow_html=True
            )
        elif message['role'] == 'system':
            st.markdown(
                f'<div class="system-message">{message["content"]}</div>',
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_data_if_available(response: Dict[str, Any]):
    """Display charts and data tables if available in the response."""
    if response.get('display_data'):
        data = response['display_data']
        if isinstance(data, pd.DataFrame) and not data.empty:
            st.subheader("📊 Analysis Results")
            st.dataframe(data, use_container_width=True)
            
            # Auto-generate simple visualizations
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'Player' in data.columns or 'player' in data.columns:
                        player_col = 'Player' if 'Player' in data.columns else 'player'
                        fig = px.bar(
                            data.head(10), 
                            x=player_col, 
                            y=numeric_cols[0],
                            title=f"Top 10 by {numeric_cols[0]}"
                        )
                        fig.update_xaxis(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if len(numeric_cols) >= 2:
                        fig = px.scatter(
                            data.head(20),
                            x=numeric_cols[0],
                            y=numeric_cols[1],
                            title=f"{numeric_cols[0]} vs {numeric_cols[1]}"
                        )
                        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main chat interface."""
    
    # Header
    st.markdown('<h1 class="main-header">⚽ Soccer Analysis Chat</h1>', unsafe_allow_html=True)
    
    # Check API status
    if not st.session_state.get('api_ready', False):
        st.error(f"❌ API initialization failed: {st.session_state.get('api_error', 'Unknown error')}")
        st.info("Please check your data files and dependencies.")
        return
    
    # Sidebar with information and suggestions
    with st.sidebar:
        st.header("💡 Query Examples")
        
        suggestions = st.session_state.api.get_suggestions()
        st.write("Click any suggestion to try it:")
        
        for suggestion in suggestions:
            if st.button(suggestion, key=f"suggestion_{suggestion}", use_container_width=True):
                # Add the suggestion as a user message and process it
                add_message('user', suggestion)
                process_query(suggestion)
                st.rerun()
        
        st.divider()
        
        # API Status
        health = st.session_state.api.health_check()
        st.header("🔧 System Status")
        if health['status'] == 'healthy':
            st.success(f"✅ All systems operational")
        else:
            st.warning(f"⚠️ Status: {health['status']}")
        
        # Data Summary
        data_summary = st.session_state.api.get_data_summary()
        st.write(f"**Players:** {data_summary.get('total_players', 'N/A')}")
        st.write(f"**Leagues:** {len(data_summary.get('leagues', []))}")
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # Welcome message for new chats
    if not st.session_state.messages:
        add_message('system', 'Welcome! Ask me anything about soccer players and stats.')
    
    # Display chat history
    display_chat_history()
    
    # Chat input
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Ask about players, comparisons, stats...",
                placeholder="e.g., 'Who are the best young midfielders?' or 'Compare Haaland vs Mbappé'",
                key="chat_input",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.button("Send ➤", type="primary", use_container_width=True)
    
    # Process input
    if (send_button or user_input) and user_input.strip():
        add_message('user', user_input)
        process_query(user_input)
        
        # Clear input and rerun
        st.session_state.chat_input = ""
        st.rerun()

def process_query(query: str):
    """Process a user query and add the response to chat."""
    
    with st.spinner("Analyzing..."):
        try:
            # Get API response
            response = st.session_state.api.query(query)
            
            # Format for chat
            chat_response = st.session_state.api.format_for_chat(response)
            
            # Add assistant response
            add_message('assistant', chat_response, metadata=response)
            
            # Store the full response for potential data display
            if response.get('display_data') is not None:
                st.session_state.last_response = response
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            add_message('assistant', error_msg)

# Display data from last response if available
if hasattr(st.session_state, 'last_response'):
    display_data_if_available(st.session_state.last_response)
    # Clear after displaying to avoid repeated displays
    del st.session_state.last_response

if __name__ == "__main__":
    main()