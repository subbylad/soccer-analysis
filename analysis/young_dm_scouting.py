"""
Young defensive midfielder scouting and potential analysis.

This module provides comprehensive scouting tools for identifying young defensive
midfielders with high growth potential using standardized metrics and scoring algorithms.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple

from .clean_player_analyzer import CleanPlayerAnalyzer
from .utils import (
    POTENTIAL_SCORING_WEIGHTS, MIN_MINUTES_THRESHOLDS,
    calculate_potential_score, filter_midfielders, filter_by_position,
    setup_logger, get_tier_description
)

logger = setup_logger(__name__)


class YoungDMScout:
    """
    Scout for young defensive midfielders with high potential.
    
    This class provides specialized analysis for identifying and evaluating
    young defensive midfielders across various criteria and metrics.
    """
    
    def __init__(self, data_dir: str = "data/clean"):
        """
        Initialize the young DM scout.
        
        Args:
            data_dir: Directory containing clean data files
        """
        self.analyzer = CleanPlayerAnalyzer(data_dir=data_dir)
        logger.info("Young DM Scout initialized")
    
    def scout_young_defensive_midfielders(self, 
                                        max_age: int = 23,
                                        min_minutes: int = MIN_MINUTES_THRESHOLDS['scouting']) -> pd.DataFrame:
        """
        Comprehensive scouting of young defensive midfielders.
        
        Args:
            max_age: Maximum age for prospect consideration
            min_minutes: Minimum playing time threshold
            
        Returns:
            DataFrame with top young DM prospects and analysis
        """
        logger.info(f"Scouting young DMs under {max_age} with {min_minutes}+ minutes")
        
        # Get young players
        young_players = self.analyzer.standard_data[
            (self.analyzer.standard_data['age'] < max_age) & 
            (self.analyzer.standard_data['minutes'] >= min_minutes)
        ]
        
        logger.info(f"Found {len(young_players)} young players with sufficient minutes")
        
        # Filter for midfielders
        young_midfielders = young_players[
            young_players['position'].str.contains('Midfielder', case=False, na=False)
        ]
        
        logger.info(f"Young midfielders: {len(young_midfielders)}")
        
        # Define defensive midfielders (low attacking output)
        young_dms = filter_midfielders(
            young_midfielders, 
            min_minutes=0,  # Already filtered above
            defensive=True
        )
        
        logger.info(f"Young defensive midfielders: {len(young_dms)}")
        
        if young_dms.empty:
            logger.warning("No young defensive midfielders found matching criteria")
            return pd.DataFrame()
        
        # Calculate potential scores
        prospects = []
        for idx, player in young_dms.iterrows():
            try:
                potential_score = calculate_potential_score(player, max_age=max_age)
                tier_emoji, tier_desc = get_tier_description(potential_score)
                
                prospect_data = {
                    'player': idx[3],
                    'team': idx[2],
                    'league': idx[0],
                    'age': int(player['age']),
                    'position': player['position'],
                    'potential_score': potential_score,
                    'tier': tier_desc,
                    'tier_emoji': tier_emoji,
                    'minutes': int(player['minutes']),
                    'goals_per_90': player['goals_per_90'],
                    'assists_per_90': player['assists_per_90'],
                    'progressive_carries': player.get('progressive_carries', 0),
                    'progressive_passes': player.get('progressive_passes', 0)
                }
                
                prospects.append(prospect_data)
                
            except (ValueError, KeyError) as e:
                logger.debug(f"Skipping player {idx[3]} due to missing data: {e}")
                continue
        
        if not prospects:
            logger.warning("No prospects generated due to data issues")
            return pd.DataFrame()
        
        prospects_df = pd.DataFrame(prospects)
        prospects_df = prospects_df.sort_values('potential_score', ascending=False)
        
        logger.info(f"Generated analysis for {len(prospects_df)} young DM prospects")
        return prospects_df
    
    def analyze_by_age_groups(self, prospects_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Analyze prospects by age groups.
        
        Args:
            prospects_df: DataFrame with prospect data
            
        Returns:
            Dictionary with age group analyses
        """
        age_groups = {
            'Teenagers (19 and under)': prospects_df[prospects_df['age'] <= 19],
            'Early Twenties (20-22)': prospects_df[
                (prospects_df['age'] >= 20) & (prospects_df['age'] <= 22)
            ]
        }
        
        results = {}
        for group_name, group_data in age_groups.items():
            if not group_data.empty:
                top_in_group = group_data.nlargest(5, 'potential_score')
                results[group_name] = top_in_group
                logger.info(f"{group_name}: {len(group_data)} prospects")
        
        return results
    
    def analyze_by_playing_time(self, 
                               prospects_df: pd.DataFrame,
                               high_usage_threshold: int = MIN_MINUTES_THRESHOLDS['high_usage']) -> pd.DataFrame:
        """
        Analyze prospects by playing time (coach trust indicator).
        
        Args:
            prospects_df: DataFrame with prospect data
            high_usage_threshold: Minimum minutes for high usage classification
            
        Returns:
            DataFrame with high-usage prospects
        """
        high_usage = prospects_df[prospects_df['minutes'] >= high_usage_threshold]
        high_usage = high_usage.sort_values('minutes', ascending=False)
        
        logger.info(f"Found {len(high_usage)} high-usage prospects ({high_usage_threshold}+ minutes)")
        return high_usage
    
    def analyze_by_league(self, prospects_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze prospect distribution by league.
        
        Args:
            prospects_df: DataFrame with prospect data
            
        Returns:
            DataFrame with league-wise analysis
        """
        league_analysis = []
        
        leagues = ['ENG-Premier League', 'ESP-La Liga', 'ITA-Serie A', 
                  'GER-Bundesliga', 'FRA-Ligue 1']
        
        for league in leagues:
            league_prospects = prospects_df[prospects_df['league'] == league]
            
            if not league_prospects.empty:
                best_prospect = league_prospects.iloc[0]  # Already sorted by potential
                
                league_analysis.append({
                    'league': league,
                    'total_prospects': len(league_prospects),
                    'best_prospect': best_prospect['player'],
                    'best_prospect_age': best_prospect['age'],
                    'best_prospect_score': best_prospect['potential_score'],
                    'avg_potential': league_prospects['potential_score'].mean()
                })
        
        league_df = pd.DataFrame(league_analysis)
        if not league_df.empty:
            league_df = league_df.sort_values('total_prospects', ascending=False)
        
        return league_df
    
    def get_top_recommendations(self, 
                               prospects_df: pd.DataFrame, 
                               top_n: int = 5) -> List[Dict]:
        """
        Get detailed recommendations for top prospects.
        
        Args:
            prospects_df: DataFrame with prospect data
            top_n: Number of recommendations to generate
            
        Returns:
            List of detailed prospect analyses
        """
        top_prospects = prospects_df.head(top_n)
        recommendations = []
        
        for idx, prospect in top_prospects.iterrows():
            # Generate reasoning
            reasons = []
            
            if prospect['minutes'] >= MIN_MINUTES_THRESHOLDS['high_usage']:
                reasons.append("high playing time shows coach trust")
            
            if prospect['age'] <= 20:
                reasons.append("very young with years to develop")
            
            prog_total = prospect['progressive_carries'] + prospect['progressive_passes']
            if prog_total >= 100:
                reasons.append("already showing good progressive ability")
            
            if prospect['potential_score'] >= 140:
                reasons.append("elite-tier potential score")
            
            xg_xa_total = 0  # Would need to calculate from original data
            if xg_xa_total >= 2:
                reasons.append("some attacking contribution")
            
            recommendation = {
                'rank': len(recommendations) + 1,
                'player': prospect['player'],
                'age': prospect['age'],
                'team': prospect['team'],
                'league': prospect['league'],
                'tier': prospect['tier'],
                'potential_score': prospect['potential_score'],
                'minutes': prospect['minutes'],
                'goals_per_90': prospect['goals_per_90'],
                'assists_per_90': prospect['assists_per_90'],
                'progressive_total': prog_total,
                'reasoning': reasons
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def generate_report(self, max_age: int = 23, min_minutes: int = 500) -> str:
        """
        Generate comprehensive scouting report.
        
        Args:
            max_age: Maximum age for prospects
            min_minutes: Minimum playing time threshold
            
        Returns:
            Formatted report string
        """
        logger.info("Generating comprehensive young DM scouting report")
        
        # Get prospects
        prospects_df = self.scout_young_defensive_midfielders(max_age, min_minutes)
        
        if prospects_df.empty:
            return "No young defensive midfielder prospects found matching criteria."
        
        report_lines = [
            f"🔍 YOUNG DEFENSIVE MIDFIELDER SCOUTING REPORT",
            f"=" * 60,
            f"📊 Analysis Parameters:",
            f"   • Maximum Age: {max_age}",
            f"   • Minimum Minutes: {min_minutes:,}",
            f"   • Total Prospects Found: {len(prospects_df)}",
            ""
        ]
        
        # Top prospects
        top_prospects = prospects_df.head(10)
        report_lines.extend([
            f"🌟 TOP 10 PROSPECTS BY POTENTIAL SCORE:",
            f"-" * 60
        ])
        
        for i, (_, prospect) in enumerate(top_prospects.iterrows(), 1):
            report_lines.append(
                f"{i:2d}. {prospect['player']:<20} (Age {prospect['age']}) - {prospect['team']}"
            )
            report_lines.append(
                f"    League: {prospect['league']}"
            )
            report_lines.append(
                f"    Stats: {prospect['minutes']:,} mins | "
                f"{prospect['goals_per_90']:.3f}G+{prospect['assists_per_90']:.3f}A/90"
            )
            report_lines.append(
                f"    {prospect['tier_emoji']} {prospect['tier']} (Score: {prospect['potential_score']:.1f})"
            )
            report_lines.append("")
        
        # Age group analysis
        age_groups = self.analyze_by_age_groups(prospects_df)
        report_lines.extend([
            f"📊 ANALYSIS BY AGE GROUPS:",
            f"-" * 40
        ])
        
        for group_name, group_data in age_groups.items():
            if not group_data.empty:
                best = group_data.iloc[0]
                report_lines.append(
                    f"{group_name} ({len(group_data)} prospects):"
                )
                report_lines.append(
                    f"   Best: {best['player']} ({best['team']}) - Score: {best['potential_score']:.1f}"
                )
                report_lines.append("")
        
        # League analysis
        league_analysis = self.analyze_by_league(prospects_df)
        if not league_analysis.empty:
            report_lines.extend([
                f"🌍 PROSPECTS BY LEAGUE:",
                f"-" * 30
            ])
            
            for _, league in league_analysis.iterrows():
                report_lines.append(
                    f"{league['league']:<20}: {league['total_prospects']:2d} prospects | "
                    f"Best: {league['best_prospect']} (Age {league['best_prospect_age']}, "
                    f"Score: {league['best_prospect_score']:.1f})"
                )
        
        return "\n".join(report_lines)


def main():
    """Run young DM scouting analysis."""
    scout = YoungDMScout()
    
    # Generate and print report
    report = scout.generate_report()
    print(report)
    
    # Get top recommendations
    prospects = scout.scout_young_defensive_midfielders()
    if not prospects.empty:
        recommendations = scout.get_top_recommendations(prospects, top_n=5)
        
        print(f"\n🏆 TOP 5 DETAILED RECOMMENDATIONS:")
        print("-" * 40)
        
        for rec in recommendations:
            print(f"\n{rec['rank']}. {rec['player']} (Age {rec['age']}) - {rec['team']} ({rec['league']})")
            print(f"   {rec['tier']} (Score: {rec['potential_score']:.1f})")
            print(f"   Playing Time: {rec['minutes']:,} minutes")
            print(f"   Output: {rec['goals_per_90']:.3f}G+{rec['assists_per_90']:.3f}A/90")
            print(f"   Progressive: {rec['progressive_total']:.0f} total actions")
            
            if rec['reasoning']:
                print(f"   💡 Why: {', '.join(rec['reasoning'])}")


if __name__ == "__main__":
    main()