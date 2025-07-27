"""
Create Unified Data for AI Analysis Engine

This script merges all available data sources into a unified format
that the AI analysis engine can use effectively.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def create_unified_data():
    """Create unified data from all available sources."""
    print("🔄 Creating unified data for AI analysis engine...")
    
    # Define data paths
    clean_dir = Path("data/clean")
    comprehensive_dir = Path("data/comprehensive") 
    processed_dir = comprehensive_dir / "processed"
    
    # Ensure output directory exists
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Copy clean data to comprehensive/processed with proper naming
    clean_files = {
        "player_standard_clean.csv": "player_standard_clean.csv",
        "player_passing_clean.csv": "player_passing_clean.csv", 
        "player_defense_clean.csv": "player_defense_clean.csv",
        "player_shooting_clean.csv": "player_shooting_clean.csv"
    }
    
    print("📋 Step 1: Copying clean data...")
    for clean_file, processed_file in clean_files.items():
        clean_path = clean_dir / clean_file
        processed_path = processed_dir / processed_file
        
        if clean_path.exists():
            # Read and save to ensure consistent format
            df = pd.read_csv(clean_path, index_col=[0, 1, 2, 3])
            df.to_csv(processed_path)
            print(f"   ✅ {clean_file} -> {processed_file} ({df.shape})")
        else:
            print(f"   ❌ {clean_file} not found")
    
    # Step 2: Verify comprehensive data exists
    print("\n📋 Step 2: Verifying comprehensive data...")
    comprehensive_files = [
        "player_possession_clean.csv",
        "player_misc_clean.csv", 
        "player_playing_time_clean.csv",
        "player_goalkeeper_clean.csv"
    ]
    
    for comp_file in comprehensive_files:
        comp_path = processed_dir / comp_file
        if comp_path.exists():
            df = pd.read_csv(comp_path, index_col=[0, 1, 2, 3])
            print(f"   ✅ {comp_file} exists ({df.shape})")
        else:
            print(f"   ⚠️  {comp_file} not found")
    
    # Step 3: Create a sample unified file for testing
    print("\n📋 Step 3: Creating sample unified dataset...")
    try:
        # Load main data
        standard_path = processed_dir / "player_standard_clean.csv"
        if standard_path.exists():
            standard_df = pd.read_csv(standard_path, index_col=[0, 1, 2, 3])
            
            # Try to merge with additional data
            unified_df = standard_df.copy()
            
            # Add possession data if available
            possession_path = processed_dir / "player_possession_clean.csv"
            if possession_path.exists():
                try:
                    possession_df = pd.read_csv(possession_path, index_col=[0, 1, 2, 3])
                    # Select key possession metrics
                    key_possession_cols = [col for col in possession_df.columns 
                                         if any(keyword in col.lower() for keyword in 
                                               ['touches', 'dribble', 'carries', 'progressive'])][:10]
                    if key_possession_cols:
                        possession_subset = possession_df[key_possession_cols]
                        unified_df = unified_df.join(possession_subset, how='left', rsuffix='_poss')
                        print(f"   ✅ Added {len(key_possession_cols)} possession metrics")
                except Exception as e:
                    print(f"   ⚠️  Could not merge possession data: {e}")
            
            # Add defensive data if available  
            defense_path = processed_dir / "player_defense_clean.csv"
            if defense_path.exists():
                try:
                    defense_df = pd.read_csv(defense_path, index_col=[0, 1, 2, 3])
                    key_defense_cols = [col for col in defense_df.columns 
                                      if any(keyword in col.lower() for keyword in 
                                            ['tackles', 'interceptions', 'blocks'])][:5]
                    if key_defense_cols:
                        defense_subset = defense_df[key_defense_cols]
                        unified_df = unified_df.join(defense_subset, how='left', rsuffix='_def')
                        print(f"   ✅ Added {len(key_defense_cols)} defensive metrics")
                except Exception as e:
                    print(f"   ⚠️  Could not merge defense data: {e}")
            
            # Save unified data
            unified_path = processed_dir / "unified_player_data.csv" 
            unified_df.to_csv(unified_path)
            print(f"   ✅ Unified dataset created: {unified_df.shape}")
            print(f"   📁 Saved to: {unified_path}")
            
        else:
            print("   ❌ Standard data not found - cannot create unified dataset")
            
    except Exception as e:
        print(f"   ❌ Failed to create unified dataset: {e}")
    
    print("\n✅ Unified data creation completed!")

if __name__ == "__main__":
    create_unified_data()