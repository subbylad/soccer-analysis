#!/usr/bin/env python3
"""
Simple Soccer Analysis Chat Interface
"""

import streamlit as st
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from api.main_api import SoccerAnalyticsAPI

st.set_page_config(
    page_title="Soccer Chat ⚽",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Soccer Analysis Chat")

# Initialize API
@st.cache_resource
def init_api():
    return SoccerAnalyticsAPI()

try:
    api = init_api()
    st.success("✅ Soccer Analytics API loaded successfully!")
    
    # Input
    user_query = st.text_input("Ask about soccer players:", placeholder="e.g., 'Who are the best young midfielders?'")
    
    if st.button("Ask") and user_query:
        with st.spinner("Analyzing..."):
            try:
                response = api.query(user_query)
                
                if response.get('success'):
                    st.success("Analysis completed!")
                    
                    # Show summary
                    st.write(f"**{response.get('summary', 'Results')}**")
                    
                    # Show chat text
                    chat_text = response.get('chat_text', '')
                    if chat_text:
                        st.markdown(chat_text)
                    
                    # Show data if available
                    if response.get('display_data'):
                        st.subheader("📊 Player Data")
                        st.dataframe(response['display_data'])
                        
                else:
                    st.error(f"Error: {response.get('error_message', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"Error processing query: {e}")
    
    # Show suggestions
    st.subheader("💡 Try these queries:")
    suggestions = [
        "Who are the best young midfielders?",
        "Compare Haaland vs Mbappé", 
        "Top scorers in Premier League",
        "Find young prospects under 21"
    ]
    
    for suggestion in suggestions:
        if st.button(suggestion, key=f"suggestion_{suggestion}"):
            st.rerun()
            
except Exception as e:
    st.error(f"Failed to initialize API: {e}")
    st.info("Please check that your data files are in the correct location.")