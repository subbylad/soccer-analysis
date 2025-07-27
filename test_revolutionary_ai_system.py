"""
Test Revolutionary AI-Native Soccer Analysis System

Comprehensive testing of the new AI-powered analysis engine and
comparison with traditional methods to demonstrate the transformation.
"""

import os
import time
import json
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ai_system():
    """Main test function for the revolutionary AI system."""
    print("=" * 80)
    print("🚀 TESTING REVOLUTIONARY AI-NATIVE SOCCER ANALYSIS SYSTEM")
    print("=" * 80)
    
    # Test without OpenAI key first (fallback mode)
    print("\n📋 Phase 1: Testing System Without OpenAI API Key (Fallback Mode)")
    test_fallback_system()
    
    # Test with OpenAI key if available
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print("\n🧠 Phase 2: Testing AI-Native System with GPT-4")
        test_ai_native_system(openai_key)
    else:
        print("\n⚠️  Phase 2 Skipped: No OpenAI API key found")
        print("   Set OPENAI_API_KEY environment variable to test AI capabilities")
    
    # Performance comparison
    print("\n📊 Phase 3: Performance Comparison")
    compare_system_performance()
    
    print("\n✅ Testing Complete!")

def test_fallback_system():
    """Test the system in fallback mode (no AI)."""
    try:
        import sys
        sys.path.append('.')
        from api.main_api import SoccerAnalyticsAPI, APIConfig
        
        # Configure for fallback mode
        config = APIConfig(
            enable_ai_engine=False,
            ai_first=False
        )
        
        api = SoccerAnalyticsAPI(config)
        
        print(f"   System Type: {api.ai_native and 'AI-Native' or 'Traditional'}")
        
        # Test basic queries
        test_queries = [
            "Find young midfielders under 21",
            "Compare Haaland vs Mbappé",
            "Best defensive midfielders"
        ]
        
        for query in test_queries:
            print(f"\n   Testing: '{query}'")
            start_time = time.time()
            result = api.query(query)
            execution_time = time.time() - start_time
            
            print(f"   ✓ Success: {result.get('success', False)}")
            print(f"   ⏱️ Time: {execution_time:.2f}s")
            print(f"   📊 Results: {result.get('total_found', 0)} players")
            
        # Test system status
        print("\n   📋 System Status:")
        health = api.health_check()
        print(f"   Health: {health.get('status', 'unknown')}")
        
        data_summary = api.get_data_summary()
        print(f"   Players: {data_summary.get('total_players', 0)}")
        print(f"   System: {data_summary.get('system_type', 'unknown')}")
        
        print("   ✅ Fallback system test completed")
        
    except Exception as e:
        print(f"   ❌ Fallback system test failed: {e}")
        logger.error(f"Fallback test error: {e}")

def test_ai_native_system(openai_key: str):
    """Test the AI-native system with full capabilities."""
    try:
        import sys
        sys.path.append('.')
        from api.main_api import SoccerAnalyticsAPI, APIConfig
        
        # Configure for AI-native mode
        config = APIConfig(
            openai_api_key=openai_key,
            enable_ai_engine=True,
            ai_first=True,
            comprehensive_data_dir="data/comprehensive"
        )
        
        api = SoccerAnalyticsAPI(config)
        
        print(f"   System Type: {api.ai_native and 'AI-Native' or 'Traditional'}")
        
        # Test sophisticated AI queries
        ai_test_queries = [
            "Find a creative midfielder like Pedri but with better defensive work rate",
            "Who can play alongside Kobbie Mainoo in Ligue 1's tactical system?",
            "Alternative to Rodri for Manchester City's possession-based system",
            "Young wingers under 21 with pace and creativity for counter-attacking football",
            "Left-backs who can play inverted role in Pep's system"
        ]
        
        print("\n   🧠 Testing AI-Enhanced Queries:")
        for query in ai_test_queries:
            print(f"\n   Testing: '{query}'")
            start_time = time.time()
            
            try:
                result = api.query(query)
                execution_time = time.time() - start_time
                
                print(f"   ✓ Success: {result.get('success', False)}")
                print(f"   ⏱️ Time: {execution_time:.2f}s")
                print(f"   📊 Results: {result.get('total_found', 0)} players")
                print(f"   🤖 AI Confidence: {result.get('query_confidence', 0):.2f}")
                
                # Show AI insights if available
                if 'ai_insights' in result:
                    insights = result['ai_insights'][:100] + "..." if len(result.get('ai_insights', '')) > 100 else result.get('ai_insights', '')
                    print(f"   💡 AI Insights: {insights}")
                
            except Exception as e:
                print(f"   ❌ Query failed: {e}")
        
        # Test AI status and capabilities
        print("\n   🎯 AI System Status:")
        ai_status = api.get_ai_status()
        print(f"   AI Native: {ai_status.get('ai_native', False)}")
        print(f"   System: {ai_status.get('system_type', 'unknown')}")
        
        capabilities = api.get_system_capabilities()
        print(f"   Version: {capabilities.get('system_version', 'unknown')}")
        
        # Show AI capabilities
        if 'intelligence_features' in capabilities:
            print("   🧠 AI Features:")
            for feature in capabilities['intelligence_features'][:3]:
                print(f"     • {feature}")
        
        # Test data summary
        print("\n   📊 Data Summary:")
        data_summary = api.get_data_summary()
        print(f"   Players: {data_summary.get('total_players', 0)}")
        print(f"   Metrics: {data_summary.get('total_metrics', 0)}")
        print(f"   AI Enabled: {data_summary.get('ai_enabled', False)}")
        
        print("   ✅ AI-native system test completed")
        
    except Exception as e:
        print(f"   ❌ AI-native system test failed: {e}")
        logger.error(f"AI system test error: {e}")

def compare_system_performance():
    """Compare performance between traditional and AI systems."""
    print("\n   📈 Performance Comparison:")
    
    try:
        import sys
        sys.path.append('.')
        from api.main_api import SoccerAnalyticsAPI, APIConfig
        
        test_query = "Find young midfielders under 21"
        
        # Test traditional system
        print("   🔄 Testing Traditional System...")
        config_traditional = APIConfig(enable_ai_engine=False, ai_first=False)
        
        try:
            api_traditional = SoccerAnalyticsAPI(config_traditional)
            start_time = time.time()
            result_traditional = api_traditional.query(test_query)
            traditional_time = time.time() - start_time
            
            print(f"   Traditional: {traditional_time:.2f}s, {result_traditional.get('total_found', 0)} results")
        except Exception as e:
            print(f"   Traditional system error: {e}")
            traditional_time = None
        
        # Test AI system if OpenAI key available
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            print("   🧠 Testing AI System...")
            config_ai = APIConfig(
                openai_api_key=openai_key,
                enable_ai_engine=True,
                ai_first=True
            )
            
            try:
                api_ai = SoccerAnalyticsAPI(config_ai)
                start_time = time.time()
                result_ai = api_ai.query(test_query)
                ai_time = time.time() - start_time
                
                print(f"   AI System: {ai_time:.2f}s, {result_ai.get('total_found', 0)} results")
                
                # Compare quality metrics
                if traditional_time and ai_time:
                    speed_comparison = "AI faster" if ai_time < traditional_time else "Traditional faster"
                    time_diff = abs(ai_time - traditional_time)
                    print(f"   ⚡ Speed: {speed_comparison} by {time_diff:.2f}s")
                    
                    ai_confidence = result_ai.get('query_confidence', 0)
                    print(f"   🎯 AI Confidence: {ai_confidence:.2f}")
                
            except Exception as e:
                print(f"   AI system error: {e}")
        else:
            print("   ⚠️  AI system test skipped (no OpenAI key)")
        
    except Exception as e:
        print(f"   ❌ Performance comparison failed: {e}")

def demonstrate_ai_capabilities():
    """Demonstrate advanced AI capabilities."""
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("Skipping AI demonstration - no OpenAI key found")
        return
    
    print("\n🎯 AI CAPABILITIES DEMONSTRATION")
    print("=" * 50)
    
    try:
        import sys
        sys.path.append('.')
        from api.main_api import SoccerAnalyticsAPI, APIConfig
        
        config = APIConfig(
            openai_api_key=openai_key,
            enable_ai_engine=True,
            ai_first=True
        )
        
        api = SoccerAnalyticsAPI(config)
        
        # Demonstrate sophisticated queries
        demo_queries = [
            {
                "query": "Find players like Pedri but with better defensive work rate",
                "description": "Multi-dimensional analysis with tactical reasoning"
            },
            {
                "query": "Who would complement Bellingham in Real Madrid's midfield?",
                "description": "Team chemistry and tactical partnership analysis"
            },
            {
                "query": "Find a striker for a 4-3-3 formation that plays high press",
                "description": "Formation-specific tactical requirements"
            }
        ]
        
        for demo in demo_queries:
            print(f"\n📝 Query: {demo['query']}")
            print(f"🎯 Focus: {demo['description']}")
            
            start_time = time.time()
            result = api.query(demo['query'])
            execution_time = time.time() - start_time
            
            if result.get('success'):
                print(f"✅ Execution: {execution_time:.2f}s")
                print(f"📊 Results: {result.get('total_found', 0)} players")
                print(f"🤖 Confidence: {result.get('query_confidence', 0):.2f}")
                
                # Show sample results
                if result.get('display_data'):
                    sample_player = result['display_data'][0]
                    print(f"🏆 Top Result: {sample_player.get('name', 'Unknown')}")
            else:
                print(f"❌ Failed: {result.get('error_message', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ AI demonstration failed: {e}")

def validate_data_integration():
    """Validate that comprehensive data is properly integrated."""
    print("\n🔍 DATA INTEGRATION VALIDATION")
    print("=" * 40)
    
    try:
        # Check if comprehensive data exists
        import os
        from pathlib import Path
        
        data_paths = {
            "Clean Data": "data/clean",
            "Comprehensive Data": "data/comprehensive", 
            "Processed Data": "data/comprehensive/processed",
            "AI Optimized": "data/comprehensive/ai_optimized"
        }
        
        for name, path in data_paths.items():
            if Path(path).exists():
                file_count = len(list(Path(path).glob("*.csv"))) + len(list(Path(path).glob("*.json")))
                print(f"✅ {name}: {file_count} files")
            else:
                print(f"❌ {name}: Not found")
        
        # Test data loading
        try:
            from analysis.ai_analysis_engine import AIAnalysisEngine
            
            print("\n🔄 Testing AI Engine Data Loading...")
            engine = AIAnalysisEngine(
                comprehensive_data_dir="data/comprehensive",
                enable_ai_enhancement=False  # Test without OpenAI first
            )
            
            summary = engine.get_database_summary()
            print(f"✅ Players Loaded: {summary.get('total_players', 0)}")
            print(f"✅ Total Metrics: {summary.get('total_metrics', 0)}")
            print(f"✅ Leagues: {len(summary.get('leagues', []))}")
            
        except Exception as e:
            print(f"❌ AI Engine loading failed: {e}")
    
    except Exception as e:
        print(f"❌ Data validation failed: {e}")

if __name__ == "__main__":
    print("🔬 Starting Revolutionary AI System Tests...")
    
    # Run main tests
    test_ai_system()
    
    # Additional demonstrations
    print("\n" + "=" * 80)
    demonstrate_ai_capabilities()
    
    print("\n" + "=" * 80)
    validate_data_integration()
    
    print("\n🎉 All tests completed!")
    print("\n💡 To test AI capabilities fully, set: export OPENAI_API_KEY='your-key-here'")