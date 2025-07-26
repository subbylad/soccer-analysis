"""
AI Data Optimizer for Soccer Scout GPT-4 Integration

This module creates AI-optimized data structures that GPT-4 can directly
consume for tactical analysis and player comparisons.
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class AIDataOptimizer:
    """Create AI-optimized data structures for GPT-4 consumption"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.existing_dir = f"{data_dir}/clean"
        self.comprehensive_dir = f"{data_dir}/comprehensive/processed"
        self.ai_optimized_dir = f"{data_dir}/comprehensive/ai_optimized"
        
        # Ensure AI optimized directory exists
        os.makedirs(self.ai_optimized_dir, exist_ok=True)
    
    def create_rich_player_profiles(self) -> List[Dict[str, Any]]:
        """Create rich player profiles for GPT-4 analysis"""
        print("🧠 Creating rich player profiles for AI analysis...")
        
        # Load all available data
        standard_df = pd.read_csv(f"{self.existing_dir}/player_standard_clean.csv")
        passing_df = pd.read_csv(f"{self.existing_dir}/player_passing_clean.csv")
        defense_df = pd.read_csv(f"{self.existing_dir}/player_defense_clean.csv")
        shooting_df = pd.read_csv(f"{self.existing_dir}/player_shooting_clean.csv")
        
        # Load enhanced data
        possession_df = pd.read_csv(f"{self.comprehensive_dir}/player_possession_clean.csv")
        misc_df = pd.read_csv(f"{self.comprehensive_dir}/player_misc_clean.csv")
        
        # Create player profiles
        player_profiles = []
        
        # Get unique players from standard data
        for idx, player_row in standard_df.iterrows():
            if pd.isna(player_row['player']) or player_row['player'] == '':
                continue
                
            player_id = f"{player_row['player']}_{player_row['team']}".replace(' ', '_').lower()
            
            # Create comprehensive player profile
            profile = {
                "player_id": player_id,
                "basic_info": {
                    "name": player_row['player'],
                    "team": player_row['team'],
                    "league": player_row['league'],
                    "position": player_row.get('position', 'Unknown'),
                    "age": player_row.get('age', 0),
                    "nationality": player_row.get('nationality', 'Unknown')
                },
                "performance_summary": self._generate_performance_summary(player_row),
                "tactical_attributes": self._calculate_tactical_attributes(player_row, idx, standard_df, passing_df, defense_df, shooting_df),
                "enhanced_metrics": self._get_enhanced_metrics(player_row, possession_df, misc_df),
                "ai_insights": self._generate_ai_insights(player_row),
                "comparable_players": [],  # Will be filled later
                "scout_notes": self._generate_scout_notes(player_row)
            }
            
            player_profiles.append(profile)
            
            # Limit to first 50 players for demonstration
            if len(player_profiles) >= 50:
                break
        
        # Save player profiles
        profiles_file = f"{self.ai_optimized_dir}/rich_player_profiles.json"
        with open(profiles_file, 'w') as f:
            json.dump(player_profiles, f, indent=2)
        
        print(f"✅ Created {len(player_profiles)} rich player profiles")
        print(f"💾 Saved to: {profiles_file}")
        
        return player_profiles
    
    def _generate_performance_summary(self, player_row: pd.Series) -> str:
        """Generate AI-friendly performance summary"""
        position = player_row.get('position', 'Player')
        goals = player_row.get('goals', 0)
        assists = player_row.get('assists', 0)
        minutes = player_row.get('minutes', 0)
        
        if position == 'Goalkeeper':
            return f"Goalkeeper with {minutes} minutes played this season."
        elif 'Forward' in str(position):
            return f"Forward with {goals} goals and {assists} assists in {minutes} minutes."
        elif 'Midfielder' in str(position):
            return f"Midfielder contributing {goals} goals and {assists} assists across {minutes} minutes."
        elif 'Defender' in str(position):
            return f"Defender with {goals} goals and {assists} assists, {minutes} minutes played."
        else:
            return f"Player with {goals} goals and {assists} assists in {minutes} minutes."
    
    def _calculate_tactical_attributes(self, player_row: pd.Series, idx: int, 
                                     standard_df: pd.DataFrame, passing_df: pd.DataFrame,
                                     defense_df: pd.DataFrame, shooting_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate normalized tactical attributes for AI analysis"""
        
        # Find matching rows in other datasets
        player_name = player_row['player']
        team_name = player_row['team']
        
        passing_row = passing_df[(passing_df['player'] == player_name) & (passing_df['team'] == team_name)]
        defense_row = defense_df[(defense_df['player'] == player_name) & (defense_df['team'] == team_name)]
        shooting_row = shooting_df[(shooting_df['player'] == player_name) & (shooting_df['team'] == team_name)]
        
        # Calculate normalized attributes (0-10 scale)
        attributes = {
            "attacking_threat": self._normalize_metric(player_row.get('goals_per_90', 0), 0, 1.5, 10),
            "creativity": self._normalize_metric(
                passing_row['assists_per_90'].iloc[0] if not passing_row.empty else 0, 0, 0.8, 10
            ),
            "passing_ability": self._normalize_metric(
                passing_row['pass_completion_pct'].iloc[0] if not passing_row.empty else 0, 70, 95, 10
            ),
            "defensive_work": self._normalize_metric(
                defense_row['tackles_plus_interceptions'].iloc[0] if not defense_row.empty else 0, 0, 8, 10
            ),
            "shooting_accuracy": self._normalize_metric(
                shooting_row['shot_accuracy'].iloc[0] if not shooting_row.empty else 0, 20, 60, 10
            ),
            "work_rate": self._normalize_metric(player_row.get('minutes', 0), 500, 3000, 10),
            "experience": self._normalize_metric(player_row.get('age', 0), 16, 35, 10)
        }
        
        return {k: round(v, 1) for k, v in attributes.items()}
    
    def _normalize_metric(self, value: float, min_val: float, max_val: float, scale: float = 10) -> float:
        """Normalize a metric to 0-scale range"""
        if pd.isna(value) or value == 0:
            return 0.0
        
        normalized = (value - min_val) / (max_val - min_val)
        return max(0, min(scale, normalized * scale))
    
    def _get_enhanced_metrics(self, player_row: pd.Series, 
                            possession_df: pd.DataFrame, misc_df: pd.DataFrame) -> Dict[str, Any]:
        """Get enhanced metrics for the player"""
        player_name = player_row['player']
        team_name = player_row['team']
        
        enhanced = {
            "possession_metrics": {},
            "behavioral_metrics": {},
            "availability": "partial"  # Since not all players have enhanced data
        }
        
        # Try to find possession data
        possession_match = possession_df[
            (possession_df['player'] == player_name) & (possession_df['team'] == team_name)
        ]
        
        if not possession_match.empty:
            pos_row = possession_match.iloc[0]
            enhanced["possession_metrics"] = {
                "touches_per_90": pos_row.get('touches_touches', 0) / max(1, pos_row.get('90s', 1)),
                "dribble_success_rate": pos_row.get('take-ons_succ%', 0),
                "progressive_carries": pos_row.get('carries_prgc', 0)
            }
            enhanced["availability"] = "full"
        
        return enhanced
    
    def _generate_ai_insights(self, player_row: pd.Series) -> List[str]:
        """Generate AI-friendly insights about the player"""
        insights = []
        
        # Performance insights
        goals_per_90 = player_row.get('goals_per_90', 0)
        if goals_per_90 > 0.5:
            insights.append(f"High goal threat with {goals_per_90:.2f} goals per 90 minutes")
        
        assists_per_90 = player_row.get('assists_per_90', 0)
        if assists_per_90 > 0.3:
            insights.append(f"Creative playmaker with {assists_per_90:.2f} assists per 90 minutes")
        
        # Age-based insights
        age = player_row.get('age', 0)
        if age < 21:
            insights.append("Young prospect with development potential")
        elif age > 30:
            insights.append("Experienced player providing leadership and stability")
        
        # Playing time insights
        minutes = player_row.get('minutes', 0)
        if minutes > 2500:
            insights.append("Key player with high playing time")
        elif minutes < 500:
            insights.append("Squad rotation player or recent signing")
        
        return insights
    
    def _generate_scout_notes(self, player_row: pd.Series) -> str:
        """Generate scout-style notes for AI consumption"""
        position = player_row.get('position', 'Player')
        age = player_row.get('age', 0)
        goals = player_row.get('goals', 0)
        assists = player_row.get('assists', 0)
        
        if 'Forward' in str(position):
            return f"{age}-year-old forward with {goals} goals this season. {'Prolific scorer' if goals > 10 else 'Developing striker'} showing {'high' if assists > 5 else 'moderate'} creativity."
        elif 'Midfielder' in str(position):
            return f"{age}-year-old midfielder balancing {goals} goals and {assists} assists. {'Key playmaker' if assists > 8 else 'Box-to-box midfielder'} with {'strong' if goals > 5 else 'moderate'} attacking output."
        elif 'Defender' in str(position):
            return f"{age}-year-old defender contributing {goals + assists} goal involvements. {'Attacking threat' if goals + assists > 3 else 'Solid defender'} from defensive positions."
        else:
            return f"{age}-year-old player with {goals} goals and {assists} assists this season."
    
    def create_gpt4_query_examples(self) -> Dict[str, Any]:
        """Create example queries optimized for GPT-4 analysis"""
        examples = {
            "timestamp": datetime.now().isoformat(),
            "tactical_queries": [
                {
                    "query": "Find midfielders similar to Pedri's playing style",
                    "data_requirements": ["passing_ability", "creativity", "work_rate", "age"],
                    "analysis_type": "similarity_matching",
                    "expected_response": "Young creative midfielders with high pass completion and assist rates"
                },
                {
                    "query": "Who can replace Rodri in Manchester City's system?",
                    "data_requirements": ["defensive_work", "passing_ability", "tactical_attributes"],
                    "analysis_type": "position_specific_replacement",
                    "expected_response": "Defensive midfielders with similar tactical profile and system fit"
                },
                {
                    "query": "Find the best young prospects under 21 for each position",
                    "data_requirements": ["age", "tactical_attributes", "performance_metrics"],
                    "analysis_type": "prospect_identification",
                    "expected_response": "Top young players by position with development potential"
                }
            ],
            "data_structure_info": {
                "rich_profiles": "JSON format with comprehensive player data",
                "tactical_attributes": "CSV matrix with normalized 0-10 tactical scores",
                "enhanced_metrics": "Additional FBref data for detailed analysis"
            },
            "ai_optimization_features": [
                "Normalized tactical attributes (0-10 scale)",
                "Human-readable performance summaries",
                "Scout-style insights and notes",
                "Structured data for consistent AI parsing",
                "Multi-dimensional player profiling"
            ]
        }
        
        # Save GPT-4 examples
        examples_file = f"{self.ai_optimized_dir}/gpt4_query_examples.json"
        with open(examples_file, 'w') as f:
            json.dump(examples, f, indent=2)
        
        print(f"✅ Created GPT-4 query examples")
        print(f"💾 Saved to: {examples_file}")
        
        return examples
    
    def optimize_all_data_for_ai(self) -> Dict[str, str]:
        """Run complete AI optimization process"""
        print("\n" + "="*60)
        print("🧠 AI DATA OPTIMIZATION FOR GPT-4 INTEGRATION")
        print("="*60)
        
        # Create all AI-optimized structures
        profiles = self.create_rich_player_profiles()
        gpt4_examples = self.create_gpt4_query_examples()
        
        # Create optimization summary
        summary = {
            "rich_player_profiles": f"{self.ai_optimized_dir}/rich_player_profiles.json",
            "gpt4_examples": f"{self.ai_optimized_dir}/gpt4_query_examples.json",
            "optimization_complete": True,
            "profiles_created": len(profiles),
            "ai_ready": True
        }
        
        # Save summary
        summary_file = f"{self.ai_optimized_dir}/ai_optimization_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✅ AI OPTIMIZATION COMPLETE!")
        print(f"📁 AI-optimized data saved to: {self.ai_optimized_dir}")
        print(f"🧠 Rich profiles: {len(profiles)} players")
        print(f"🎯 Ready for GPT-4 enhanced tactical analysis!")
        
        return summary


if __name__ == "__main__":
    optimizer = AIDataOptimizer()
    optimization_results = optimizer.optimize_all_data_for_ai()