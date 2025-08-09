#!/usr/bin/env python3
"""
Simplified Soccer Scout API - Clean Two-Stage AI Architecture

A reliable, simplified backend that:
1. Uses GPT-5-nano to parse queries into simple filters
2. Filters the player database efficiently 
3. Uses GPT-5-mini to generate conversational scout insights

No JSON parsing issues, no over-engineering, just reliable AI-powered scouting.
"""

import os
import time
import logging
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use system env vars

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure CORS for frontend
CORS(app, origins=[
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://soccer-scout-ui.vercel.app",
    "https://soccer-scout-frontend.vercel.app",
    "https://*.vercel.app"
], methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type"])


class SimpleScoutAI:
    """Simplified AI Scout with two-stage architecture"""
    
    def __init__(self, openai_api_key: str):
        """Initialize the scout with OpenAI client and player data"""
        self.client = OpenAI(api_key=openai_api_key)
        self.players_df = None
        self.load_player_data()
        
    def load_player_data(self):
        """Load the comprehensive player database"""
        logger.info("Loading player database...")
        try:
            # Load the unified player data
            data_path = "data/comprehensive/processed/unified_player_data.csv"
            self.players_df = pd.read_csv(data_path)
            
            # Add computed metrics for better analysis
            self._enhance_player_data()
            
            logger.info(f"✅ Loaded {len(self.players_df)} players with {len(self.players_df.columns)} metrics")
        except Exception as e:
            logger.error(f"❌ Failed to load player data: {e}")
            raise
    
    def _enhance_player_data(self):
        """Add computed metrics for AI analysis"""
        # Safe division helper
        def safe_per_90(stat_col, nineties_col):
            return np.where(nineties_col > 0, stat_col / nineties_col, 0)
        
        # Defensive work rate
        self.players_df['defensive_work_rate'] = safe_per_90(
            self.players_df.get('tackles', 0) + self.players_df.get('tackles_won', 0),
            self.players_df.get('nineties', 1)
        )
        
        # Creativity score (simple version)
        self.players_df['creativity_score'] = (
            self.players_df.get('assists_per_90', 0) * 2 +
            self.players_df.get('expected_assists_per_90', 0)
        )
        
        # Overall rating (simple aggregation)
        self.players_df['overall_rating'] = (
            self.players_df.get('goals_per_90', 0) * 3 +
            self.players_df.get('assists_per_90', 0) * 2 +
            self.players_df.get('defensive_work_rate', 0)
        )
    
    def parse_query_to_filters(self, query: str) -> Dict[str, Any]:
        """
        Stage 1: Use GPT-5-nano to parse natural language into simple filters
        Returns a dictionary of filter criteria, not complex JSON
        """
        logger.info(f"🧠 Stage 1: Parsing query with GPT-5-nano")
        
        prompt = f"""Parse this soccer query into simple filter criteria. 
Extract ONLY what's explicitly mentioned. Return simple key-value pairs, no JSON.

Query: "{query}"

Extract these if mentioned:
- position: MUST be one of: "Midfielder", "Forward", "Defender", "Goalkeeper"
  (Map common terms: DM/CDM/CM/CAM → Midfielder, ST/CF/Winger → Forward, CB/LB/RB → Defender, GK → Goalkeeper)
  
- league: MUST be one of: "ENG-Premier League", "ESP-La Liga", "ITA-Serie A", "GER-Bundesliga", "FRA-Ligue 1"
  (Map variations: England/EPL/Prem → ENG-Premier League, Spain → ESP-La Liga, Italy → ITA-Serie A, 
   Germany/Buli → GER-Bundesliga, France/L1 → FRA-Ligue 1)
  
- age_max: (number - for "under X", "U21", "young")
- age_min: (number - for "over X", "veteran")
- min_minutes: (number, default 500 if not specified)
- style: (creative, defensive, fast)
- similar_to: (exact player name if comparing)

Example output:
position: Midfielder
league: FRA-Ligue 1
age_max: 21
style: defensive

Only include fields that are clearly mentioned in the query."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a query parser. Extract filter criteria from soccer queries. Return simple key-value pairs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200,
                timeout=5.0  # Fast timeout for parser
            )
            
            # Parse the simple key-value response
            filters = {}
            response_text = response.choices[0].message.content.strip()
            
            for line in response_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    # Convert numeric values
                    if key in ['age_max', 'age_min', 'min_minutes']:
                        try:
                            filters[key] = int(value)
                        except:
                            pass
                    else:
                        filters[key] = value
            
            # Add default minimum minutes if not specified
            if 'min_minutes' not in filters:
                filters['min_minutes'] = 500
                
            logger.info(f"✅ Parsed filters: {filters}")
            return filters
            
        except Exception as e:
            logger.error(f"❌ OpenAI API call failed (gpt-3.5-turbo): {e}")
            logger.warning(f"⚠️ Using fallback parser instead")
            return self._fallback_parser(query)
    
    def _get_position_mapping(self):
        """Comprehensive position mappings"""
        return {
            # Midfielders
            'midfielder': 'Midfielder',
            'midfield': 'Midfielder',
            'mid': 'Midfielder',
            'cm': 'Midfielder',
            'cdm': 'Midfielder',
            'cam': 'Midfielder',
            'dm': 'Midfielder',
            'defensive midfielder': 'Midfielder',
            'attacking midfielder': 'Midfielder',
            'central midfielder': 'Midfielder',
            'box to box': 'Midfielder',
            'playmaker': 'Midfielder',
            
            # Forwards
            'forward': 'Forward',
            'striker': 'Forward',
            'attacker': 'Forward',
            'cf': 'Forward',
            'st': 'Forward',
            'winger': 'Forward',
            'wing': 'Forward',
            'lw': 'Forward',
            'rw': 'Forward',
            'left winger': 'Forward',
            'right winger': 'Forward',
            
            # Defenders
            'defender': 'Defender',
            'defense': 'Defender',
            'defence': 'Defender',
            'cb': 'Defender',
            'center back': 'Defender',
            'centre back': 'Defender',
            'fullback': 'Defender',
            'full back': 'Defender',
            'lb': 'Defender',
            'rb': 'Defender',
            'left back': 'Defender',
            'right back': 'Defender',
            'wing back': 'Defender',
            'wingback': 'Defender',
            
            # Goalkeeper
            'goalkeeper': 'Goalkeeper',
            'keeper': 'Goalkeeper',
            'gk': 'Goalkeeper',
            'goalie': 'Goalkeeper'
        }
    
    def _get_league_mapping(self):
        """Comprehensive league mappings"""
        return {
            # Premier League variations
            'premier league': 'ENG-Premier League',
            'epl': 'ENG-Premier League',
            'pl': 'ENG-Premier League',
            'england': 'ENG-Premier League',
            'english': 'ENG-Premier League',
            'prem': 'ENG-Premier League',
            
            # La Liga variations
            'la liga': 'ESP-La Liga',
            'laliga': 'ESP-La Liga',
            'spain': 'ESP-La Liga',
            'spanish': 'ESP-La Liga',
            'liga': 'ESP-La Liga',
            
            # Serie A variations
            'serie a': 'ITA-Serie A',
            'seriea': 'ITA-Serie A',
            'italy': 'ITA-Serie A',
            'italian': 'ITA-Serie A',
            'serie': 'ITA-Serie A',
            
            # Bundesliga variations
            'bundesliga': 'GER-Bundesliga',
            'germany': 'GER-Bundesliga',
            'german': 'GER-Bundesliga',
            'buli': 'GER-Bundesliga',
            
            # Ligue 1 variations
            'ligue 1': 'FRA-Ligue 1',
            'ligue1': 'FRA-Ligue 1',
            'france': 'FRA-Ligue 1',
            'french': 'FRA-Ligue 1',
            'ligue': 'FRA-Ligue 1',
            'l1': 'FRA-Ligue 1'
        }
    
    def _fallback_parser(self, query: str) -> Dict[str, Any]:
        """Simple regex-based fallback parser with comprehensive mappings"""
        filters = {'min_minutes': 500}
        query_lower = query.lower()
        
        # Position detection with comprehensive mapping
        positions = self._get_position_mapping()
        for term, position in positions.items():
            if term in query_lower:
                filters['position'] = position
                break
        
        # League detection with comprehensive mapping
        leagues = self._get_league_mapping()
        for term, league in leagues.items():
            if term in query_lower:
                filters['league'] = league
                break
        
        # Age detection - multiple patterns
        age_patterns = [
            (r'under (\d+)', 'age_max'),
            (r'u(\d+)', 'age_max'),
            (r'younger than (\d+)', 'age_max'),
            (r'over (\d+)', 'age_min'),
            (r'older than (\d+)', 'age_min'),
            (r'(\d+) years old', 'age_exact'),
            (r'age (\d+)', 'age_exact')
        ]
        
        for pattern, age_type in age_patterns:
            match = re.search(pattern, query_lower)
            if match:
                age = int(match.group(1))
                if age_type == 'age_exact':
                    filters['age_min'] = age - 1
                    filters['age_max'] = age + 1
                else:
                    filters[age_type] = age
                break
        
        # Style detection
        style_mappings = {
            'creative': 'creative',
            'playmaker': 'creative',
            'technical': 'creative',
            'defensive': 'defensive',
            'destroyer': 'defensive',
            'physical': 'defensive',
            'fast': 'fast',
            'pace': 'fast',
            'quick': 'fast',
            'speedy': 'fast'
        }
        
        for term, style in style_mappings.items():
            if term in query_lower:
                filters['style'] = style
                break
        
        # Young player detection
        if any(word in query_lower for word in ['young', 'prospect', 'talent', 'wonderkid']):
            if 'age_max' not in filters:
                filters['age_max'] = 23
        
        # Similar player detection
        similar_keywords = ['similar to', 'like', 'replacement for', 'alternative to']
        for keyword in similar_keywords:
            if keyword in query_lower:
                # Extract player name after the keyword
                pattern = f"{keyword}\\s+([\\w\\s]+?)(?:\\s+in\\s+|\\s+for\\s+|$)"
                match = re.search(pattern, query_lower)
                if match:
                    player_name = match.group(1).strip()
                    filters['similar_to'] = player_name
                    break
            
        return filters
    
    def filter_players(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Stage 2A: Filter player database using parsed criteria
        """
        logger.info(f"🔍 Stage 2A: Filtering players with criteria: {filters}")
        
        filtered = self.players_df.copy()
        initial_count = len(filtered)
        
        # Apply position filter
        if 'position' in filters:
            filtered = filtered[filtered['position'].str.contains(filters['position'], case=False, na=False)]
            logger.info(f"   Position filter '{filters['position']}': {len(filtered)} players")
        
        # Apply league filter
        if 'league' in filters:
            filtered = filtered[filtered['league'] == filters['league']]
            logger.info(f"   League filter '{filters['league']}': {len(filtered)} players")
        
        # Apply age filters
        if 'age_max' in filters:
            filtered = filtered[filtered['age'] <= filters['age_max']]
            logger.info(f"   Age <= {filters['age_max']}: {len(filtered)} players")
            
        if 'age_min' in filters:
            filtered = filtered[filtered['age'] >= filters['age_min']]
            logger.info(f"   Age >= {filters['age_min']}: {len(filtered)} players")
        
        # Apply minutes filter
        min_minutes = filters.get('min_minutes', 500)
        filtered = filtered[filtered['minutes'] >= min_minutes]
        logger.info(f"   Minutes >= {min_minutes}: {len(filtered)} players")
        
        # Apply style filters
        if 'style' in filters:
            style = filters['style'].lower()
            if style == 'creative':
                # Filter for creative players (high creativity score)
                threshold = filtered['creativity_score'].quantile(0.6)
                filtered = filtered[filtered['creativity_score'] > threshold]
            elif style == 'defensive':
                # Filter for defensive players
                threshold = filtered['defensive_work_rate'].quantile(0.6)
                filtered = filtered[filtered['defensive_work_rate'] > threshold]
            logger.info(f"   Style '{style}': {len(filtered)} players")
        
        # Sort by overall rating
        filtered = filtered.sort_values('overall_rating', ascending=False)
        
        # Limit to top 50 players for AI processing
        if len(filtered) > 50:
            filtered = filtered.head(50)
            logger.info(f"   Limited to top 50 players by rating")
        
        logger.info(f"✅ Filtered from {initial_count} to {len(filtered)} players")
        return filtered
    
    def generate_scout_analysis(self, query: str, players_df: pd.DataFrame, filters: Dict) -> str:
        """
        Stage 2B: Use GPT-5-mini to generate conversational scout analysis
        No JSON parsing - just natural language response
        """
        logger.info(f"🎯 Stage 2B: Generating scout analysis with GPT-5-mini")
        
        # Prepare player summaries for AI
        player_summaries = []
        for _, player in players_df.head(15).iterrows():  # Top 15 players
            summary = (
                f"{player['player']} ({player['team']}, {player['league']}) - "
                f"{player['position']}, Age {int(player['age'])}, "
                f"{int(player['minutes'])} mins, "
                f"{player.get('goals_per_90', 0):.2f} goals/90, "
                f"{player.get('assists_per_90', 0):.2f} assists/90"
            )
            player_summaries.append(summary)
        
        players_text = "\n".join(player_summaries)
        
        prompt = f"""You are an expert soccer scout. Analyze these players for the following query:

Query: "{query}"

Top candidates found:
{players_text}

Provide a conversational response that:
1. Directly answers the user's question
2. Recommends the top 2-3 players with brief reasoning
3. Mentions any standout insights or concerns
4. Keeps it concise and professional

Do not use JSON or structured formats. Write naturally as if talking to a coach."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional soccer scout providing clear, concise analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600,
                timeout=12.0  # Reasonable timeout
            )
            
            analysis = response.choices[0].message.content.strip()
            logger.info("✅ Scout analysis generated successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ OpenAI API call failed (gpt-4o-mini): {e}")
            logger.warning(f"⚠️ Using fallback analysis instead")
            return self._fallback_analysis(query, players_df, filters)
    
    def _fallback_analysis(self, query: str, players_df: pd.DataFrame, filters: Dict) -> str:
        """Simple fallback analysis when AI fails"""
        if len(players_df) == 0:
            return "No players found matching your criteria. Try broadening your search."
        
        top_players = players_df.head(3)
        response = f"Based on your search for {filters.get('position', 'players')}"
        
        if 'league' in filters:
            response += f" in {filters['league']}"
        if 'age_max' in filters:
            response += f" under {filters['age_max']}"
        
        response += f", here are the top {len(top_players)} candidates:\n\n"
        
        for _, player in top_players.iterrows():
            response += (
                f"• {player['player']} ({player['team']}) - "
                f"{player['position']}, {int(player['age'])} years old, "
                f"{player.get('goals_per_90', 0):.2f} goals/90, "
                f"{player.get('assists_per_90', 0):.2f} assists/90\n"
            )
        
        return response
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """Main analysis pipeline"""
        start_time = time.time()
        
        try:
            # Stage 1: Parse query to filters
            filters = self.parse_query_to_filters(query)
            
            # Stage 2A: Filter players
            filtered_players = self.filter_players(filters)
            
            if len(filtered_players) == 0:
                return {
                    "success": False,
                    "response_text": "No players found matching your criteria. Try adjusting your search parameters.",
                    "recommendations": [],
                    "summary": "No matches found",
                    "execution_time": time.time() - start_time
                }
            
            # Stage 2B: Generate analysis
            analysis = self.generate_scout_analysis(query, filtered_players, filters)
            
            # Extract recommendations from the analysis
            recommendations = self._extract_recommendations(analysis, filtered_players)
            
            return {
                "success": True,
                "response_text": analysis,
                "recommendations": recommendations,
                "summary": f"Found {len(filtered_players)} players matching your criteria",
                "metadata": {
                    "filters_applied": filters,
                    "players_found": len(filtered_players),
                    "execution_time": round(time.time() - start_time, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "success": False,
                "response_text": f"Analysis failed: {str(e)}",
                "recommendations": [],
                "summary": "Error occurred",
                "execution_time": time.time() - start_time
            }
    
    def _extract_recommendations(self, analysis: str, players_df: pd.DataFrame) -> List[Dict]:
        """Extract player recommendations from analysis text"""
        recommendations = []
        
        # Simple extraction: look for player names from our filtered list
        for _, player in players_df.head(5).iterrows():
            if player['player'] in analysis:
                recommendations.append({
                    "player": player['player'],
                    "team": player['team'],
                    "league": player['league'],
                    "position": player['position'],
                    "age": int(player['age']),
                    "goals_per_90": round(player.get('goals_per_90', 0), 2),
                    "assists_per_90": round(player.get('assists_per_90', 0), 2),
                    "minutes": int(player['minutes'])
                })
        
        return recommendations[:3]  # Return top 3


# Global scout instance
scout_ai = None

def initialize_scout():
    """Initialize the scout AI"""
    global scout_ai
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_key or openai_key == 'your-openai-api-key-here':
        logger.error("❌ No valid OpenAI API key found in environment variables")
        logger.error("   Please set OPENAI_API_KEY in Railway environment variables")
        return False
    
    try:
        scout_ai = SimpleScoutAI(openai_key)
        logger.info("✅ Scout AI initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize scout: {e}")
        return False


# Initialize on startup
scout_initialized = initialize_scout()


# === ROUTES ===

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy" if scout_initialized else "unhealthy",
        "service": "simple-scout-api",
        "timestamp": datetime.now().isoformat()
    }), 200 if scout_initialized else 503


@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint for the frontend"""
    if not scout_initialized:
        return jsonify({
            "success": False,
            "response_text": "Scout AI not initialized. Please check server configuration.",
            "recommendations": [],
            "summary": "Service unavailable"
        }), 503
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                "success": False,
                "response_text": "Please provide a message",
                "recommendations": [],
                "summary": "Empty message"
            }), 400
        
        # Analyze the query
        result = scout_ai.analyze(message)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({
            "success": False,
            "response_text": "An error occurred processing your request",
            "recommendations": [],
            "summary": "Server error"
        }), 500


@app.route('/api/query', methods=['POST'])
def api_query():
    """Legacy API endpoint for compatibility"""
    if not scout_initialized:
        return jsonify({
            "success": False,
            "response_text": "Scout AI not initialized. Please check server configuration.",
            "recommendations": [],
            "summary": "Service unavailable"
        }), 503
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                "success": False,
                "response_text": "Please provide a query",
                "recommendations": [],
                "summary": "Empty query"
            }), 400
        
        # Analyze the query using the same logic as chat
        result = scout_ai.analyze(query)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API query endpoint error: {e}")
        return jsonify({
            "success": False,
            "response_text": "An error occurred processing your request",
            "recommendations": [],
            "summary": "Server error"
        }), 500


@app.route('/', methods=['GET'])
def index():
    """API information"""
    return jsonify({
        "name": "Simple Scout API",
        "version": "1.0.0",
        "description": "Simplified two-stage AI soccer scout",
        "endpoints": {
            "POST /chat": "Main chat endpoint",
            "POST /api/query": "Legacy query endpoint",
            "GET /health": "Health check",
            "GET /logs": "Recent logs (last 50 lines)"
        },
        "status": "ready" if scout_initialized else "not_initialized"
    })


# Keep recent logs in memory for quick access
from collections import deque
recent_logs = deque(maxlen=50)

# Custom log handler to capture logs
class MemoryHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        recent_logs.append({
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': log_entry
        })

# Add memory handler to logger
memory_handler = MemoryHandler()
memory_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
logger.addHandler(memory_handler)

@app.route('/logs', methods=['GET'])
def get_logs():
    """Get recent logs for debugging"""
    return jsonify({
        "logs": list(recent_logs),
        "count": len(recent_logs),
        "oldest": recent_logs[0]['timestamp'] if recent_logs else None,
        "newest": recent_logs[-1]['timestamp'] if recent_logs else None
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting Simple Scout API on port {port}")
    print(f"📊 Scout initialized: {scout_initialized}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )