#!/usr/bin/env python3
"""
Tactical Query Examples and Expected Responses

This module demonstrates the advanced GPT-4 enhanced tactical analysis capabilities
of the Soccer Analytics API with real-world examples and expected response formats.
"""

import os
import sys
from typing import Dict, Any, List
from dataclasses import dataclass

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.main_api import SoccerAnalyticsAPI, APIConfig


@dataclass
class TacticalQueryExample:
    """Example tactical query with expected response structure."""
    category: str
    query: str
    description: str
    expected_gpt_analysis: Dict[str, Any]
    expected_results_summary: str
    tactical_reasoning: str


def get_tactical_query_examples() -> List[TacticalQueryExample]:
    """Get comprehensive examples of tactical queries and expected responses."""
    
    return [
        # 1. Tactical Partnership Analysis
        TacticalQueryExample(
            category="Tactical Partnership",
            query="Who can play alongside Kobbie Mainoo in Ligue 1?",
            description="Find midfield partners who complement Mainoo's playing style",
            expected_gpt_analysis={
                "query_type": "tactical_analysis",
                "players_mentioned": ["Kobbie Mainoo"],
                "position": "Midfielder",
                "league": "FRA-Ligue 1",
                "tactical_context": "Finding midfield partners who complement Mainoo's progressive passing and energy",
                "priority_stats": ["progressive_passes", "tackles", "interceptions", "pass_completion"],
                "reasoning": "Mainoo excels at progressive passing and box-to-box play. Need partners who can provide defensive stability and allow him creative freedom.",
                "age_constraints": {"min": 18, "max": 30}
            },
            expected_results_summary="Found 8-12 midfield candidates in Ligue 1 who could partner with Mainoo",
            tactical_reasoning="Look for players with high defensive actions (tackles, interceptions) and good passing accuracy to complement Mainoo's creative abilities. Prefer players who can cover defensively while Mainoo makes forward runs."
        ),
        
        # 2. Player Replacement Analysis
        TacticalQueryExample(
            category="Player Replacement",
            query="Find an alternative to Rodri for Manchester City",
            description="Identify defensive midfielders who can replicate Rodri's role",
            expected_gpt_analysis={
                "query_type": "tactical_analysis",
                "players_mentioned": ["Rodri"],
                "position": "Midfielder",
                "league": None,
                "tactical_context": "Finding a defensive midfielder who can replicate Rodri's passing range and positional discipline",
                "priority_stats": ["progressive_passes", "pass_completion", "tackles", "interceptions", "aerial_duels"],
                "reasoning": "Rodri is crucial to City's possession system with elite passing, defensive coverage, and tactical intelligence. Need similar profile with passing range and defensive solidity.",
                "age_constraints": {"min": 20, "max": 32}
            },
            expected_results_summary="Found 5-8 defensive midfielders worldwide who could replace Rodri's tactical role",
            tactical_reasoning="Prioritize players with exceptional passing accuracy (85%+), high progressive pass volume, strong defensive metrics, and aerial ability. Must be comfortable as sole pivot in possession system."
        ),
        
        # 3. Style-Based Player Matching
        TacticalQueryExample(
            category="Style Matching",
            query="Show me players similar to Pedri's style",
            description="Find creative midfielders with similar technical attributes",
            expected_gpt_analysis={
                "query_type": "tactical_analysis", 
                "players_mentioned": ["Pedri"],
                "position": "Midfielder",
                "league": None,
                "tactical_context": "Finding creative midfielders with excellent close control, press resistance, and vision",
                "priority_stats": ["progressive_passes", "pass_completion", "dribbles_completed", "key_passes", "shot_creating_actions"],
                "reasoning": "Pedri's style combines technical excellence, press resistance, tempo control, and creative vision. Look for players with similar passing accuracy, dribbling success, and chance creation.",
                "age_constraints": {"min": 18, "max": 28}
            },
            expected_results_summary="Found 6-10 technically gifted playmakers with Pedri-like characteristics",
            tactical_reasoning="Focus on players with high pass completion in tight spaces, successful dribbles under pressure, and ability to create chances. Prefer players who can dictate tempo and resist high pressing."
        ),
        
        # 4. Formation-Specific Analysis
        TacticalQueryExample(
            category="Formation Complement",
            query="Who would complement Bellingham in Real Madrid's midfield?",
            description="Find midfield partners for Bellingham's box-to-box role",
            expected_gpt_analysis={
                "query_type": "tactical_analysis",
                "players_mentioned": ["Bellingham"],
                "position": "Midfielder",
                "league": None,
                "tactical_context": "Finding midfield partners who can provide balance alongside Bellingham's box-to-box style",
                "priority_stats": ["defensive_actions", "progressive_passes", "aerial_duels", "pass_completion"],
                "reasoning": "Bellingham provides goal threat and forward runs. Need partners who can cover defensively during his attacking phases while maintaining passing quality and aerial presence.",
                "age_constraints": {"min": 20, "max": 33}
            },
            expected_results_summary="Found 7-11 midfielders who could balance Bellingham's attacking tendencies",
            tactical_reasoning="Seek players with strong defensive positioning to cover when Bellingham advances, plus passing ability to maintain Real Madrid's possession standards. Aerial ability important for balance."
        ),
        
        # 5. Age-Constrained Replacement
        TacticalQueryExample(
            category="Young Replacement",
            query="Find young defensive midfielders under 25 who can replace Casemiro",
            description="Identify young DMs with Casemiro's physical and tactical profile",
            expected_gpt_analysis={
                "query_type": "tactical_analysis",
                "players_mentioned": ["Casemiro"],
                "position": "Midfielder", 
                "league": None,
                "tactical_context": "Finding young defensive midfielders with physicality and positional awareness",
                "priority_stats": ["tackles", "interceptions", "aerial_duels", "fouls", "clearances"],
                "reasoning": "Casemiro's game is built on physicality, tactical fouling, aerial dominance, and breaking up play. Need young players with similar defensive instincts and physical presence.",
                "age_constraints": {"min": 18, "max": 25}
            },
            expected_results_summary="Found 4-8 young defensive midfielders with Casemiro-like physicality",
            tactical_reasoning="Prioritize young players with high tackle and interception rates, strong aerial duel success, and willingness to make tactical fouls. Physical presence and defensive leadership potential crucial."
        ),
        
        # 6. System-Specific Analysis
        TacticalQueryExample(
            category="System Fit",
            query="Find a creative midfielder who fits Pep's system",
            description="Identify playmakers suitable for Guardiola's possession system",
            expected_gpt_analysis={
                "query_type": "tactical_analysis",
                "players_mentioned": [],
                "position": "Midfielder",
                "league": None,
                "tactical_context": "Finding creative midfielders who can operate in Guardiola's possession-based system",
                "priority_stats": ["pass_completion", "progressive_passes", "key_passes", "press_resistance", "positioning"],
                "reasoning": "Pep's system requires midfielders with exceptional passing accuracy, press resistance, tactical intelligence, and ability to create from deep positions. Must maintain possession under pressure.",
                "age_constraints": {"min": 20, "max": 30}
            },
            expected_results_summary="Found 8-12 creative midfielders suited to Pep's possession system",
            tactical_reasoning="Focus on players with 90%+ pass completion, high progressive pass volume, excellent press resistance, and positional intelligence. Must excel in tight spaces and quick combination play."
        ),
        
        # 7. League-Specific Tactical Analysis
        TacticalQueryExample(
            category="League-Specific",
            query="Find a box-to-box midfielder who can handle Premier League intensity",
            description="Identify midfielders with physicality for English game",
            expected_gpt_analysis={
                "query_type": "tactical_analysis",
                "players_mentioned": [],
                "position": "Midfielder",
                "league": None,
                "tactical_context": "Finding box-to-box midfielders with the physicality and pace for Premier League football",
                "priority_stats": ["distance_covered", "sprints", "duels_won", "progressive_carries", "stamina"],
                "reasoning": "Premier League demands exceptional physical output, pace, and ability to cover ground. Need midfielders who can contribute in both boxes while maintaining high work rate throughout matches.",
                "age_constraints": {"min": 20, "max": 29}
            },
            expected_results_summary="Found 6-10 box-to-box midfielders with Premier League physicality",
            tactical_reasoning="Prioritize players with high distance covered, successful duels, and ability to make progressive carries. Must have pace, stamina, and physical presence to thrive in English football."
        ),
        
        # 8. Tactical Role Specialization
        TacticalQueryExample(
            category="Role Specialization", 
            query="Find a deep-lying playmaker like Pirlo for a 3-5-2 formation",
            description="Identify regista-type players for specific tactical setup",
            expected_gpt_analysis={
                "query_type": "tactical_analysis",
                "players_mentioned": ["Pirlo"],
                "position": "Midfielder",
                "league": None,
                "tactical_context": "Finding deep-lying playmakers with exceptional passing range and vision for 3-5-2 system",
                "priority_stats": ["long_passes", "pass_completion", "progressive_passes", "key_passes", "switches"],
                "reasoning": "Pirlo-style regista anchors play from deep with exceptional passing range, vision, and ability to switch play. Critical for 3-5-2 where central midfielder must distribute to wing-backs and forwards.",
                "age_constraints": {"min": 22, "max": 35}
            },
            expected_results_summary="Found 3-6 deep-lying playmakers with regista characteristics",
            tactical_reasoning="Focus on players with exceptional long passing accuracy, ability to switch play, and vision to find wing-backs in wide areas. Must have composure under pressure and game management skills."
        )
    ]


def demonstrate_tactical_query_capabilities():
    """Demonstrate the tactical query system with real examples."""
    
    print("🧠 TACTICAL QUERY CAPABILITIES DEMONSTRATION")
    print("=" * 80)
    print("Advanced Soccer Scout AI with GPT-4 Enhanced Analysis")
    print()
    
    examples = get_tactical_query_examples()
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example.category.upper()}")
        print(f"   Query: \"{example.query}\"")
        print(f"   Description: {example.description}")
        print()
        print(f"   🎯 Expected GPT-4 Analysis:")
        print(f"      • Target Player: {example.expected_gpt_analysis.get('players_mentioned', ['None'])[0] if example.expected_gpt_analysis.get('players_mentioned') else 'None'}")
        print(f"      • Position Focus: {example.expected_gpt_analysis.get('position', 'Any')}")
        print(f"      • League: {example.expected_gpt_analysis.get('league', 'Any')}")
        print(f"      • Priority Stats: {', '.join(example.expected_gpt_analysis.get('priority_stats', [])[:3])}...")
        print()
        print(f"   📊 Expected Results: {example.expected_results_summary}")
        print()
        print(f"   🔍 Tactical Reasoning:")
        print(f"      {example.tactical_reasoning}")
        print()
        print("-" * 80)


def test_tactical_queries_with_api():
    """Test tactical queries with the actual API (requires OpenAI key for full functionality)."""
    
    print("\n🚀 TESTING TACTICAL QUERIES WITH API")
    print("=" * 80)
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  No OPENAI_API_KEY found. Testing with mock responses only.")
        print("   Set API key: export OPENAI_API_KEY='your-key-here'")
        print()
    
    # Initialize API
    config = APIConfig(openai_api_key=api_key)
    
    try:
        api = SoccerAnalyticsAPI(config)
        print("✅ Soccer Analytics API initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize API: {e}")
        return
    
    # Test a few key examples
    test_queries = [
        "Who can play alongside Kobbie Mainoo in Ligue 1?",
        "Find an alternative to Rodri for Manchester City", 
        "Show me players similar to Pedri's style"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 50)
        
        try:
            result = api.query(query)
            
            print(f"✅ Success: {result.get('success', False)}")
            print(f"📊 Type: {result.get('type', 'unknown')}")
            print(f"🎯 Confidence: {result.get('query_confidence', 0):.2f}")
            
            # Show chat preview
            chat_text = result.get('chat_text', '')
            if chat_text:
                preview = chat_text.replace('\n', ' ')[:200]
                print(f"💬 Response: {preview}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()


if __name__ == "__main__":
    # Demonstrate capabilities
    demonstrate_tactical_query_capabilities()
    
    # Test with API
    test_tactical_queries_with_api()
    
    print("\n💡 PRODUCTION USAGE GUIDE:")
    print("=" * 50)
    print("1. Install dependencies: pip install openai")
    print("2. Set API key: export OPENAI_API_KEY='your-openai-key'")
    print("3. Import and use:")
    print("   from api.main_api import SoccerAnalyticsAPI, APIConfig")
    print("   config = APIConfig(openai_api_key='your-key')")
    print("   api = SoccerAnalyticsAPI(config)")
    print("   result = api.query('Who can play alongside Pedri?')")
    print("4. Access results: result['chat_text'] for formatted response")
    print("5. Check success: result['success'] for operation status")