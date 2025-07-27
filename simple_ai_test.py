"""
Simple AI System Test

Direct test of the AI analysis engine without complex imports.
"""

import sys
import os
sys.path.append('.')

def test_ai_engine():
    """Test the AI analysis engine directly."""
    print("🔬 Testing AI Analysis Engine...")
    
    try:
        from analysis.ai_analysis_engine import AIAnalysisEngine
        
        # Test without OpenAI first
        print("📋 Testing without OpenAI API key...")
        engine = AIAnalysisEngine(
            comprehensive_data_dir="data/comprehensive",
            enable_ai_enhancement=False
        )
        
        # Get summary
        summary = engine.get_database_summary()
        print(f"✅ Players loaded: {summary.get('total_players', 0)}")
        print(f"✅ Total metrics: {summary.get('total_metrics', 0)}")
        print(f"✅ AI enabled: {summary.get('ai_enabled', False)}")
        
        # Test basic query
        print("\n📋 Testing basic query analysis...")
        result = engine.analyze_query("Find young midfielders under 21")
        print(f"✅ Query success: {result.get('success', False)}")
        print(f"✅ Query type: {result.get('type', 'unknown')}")
        
        # Test player search
        print("\n📋 Testing player profile access...")
        if engine.player_profiles:
            sample_player = list(engine.player_profiles.values())[0]
            print(f"✅ Sample player: {sample_player.name}")
            print(f"✅ Position: {sample_player.position}")
            print(f"✅ AI rating: {sample_player.ai_scout_rating}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Engine test failed: {e}")
        return False

def test_ai_query_processor():
    """Test the AI query processor."""
    print("\n🔬 Testing AI Query Processor...")
    
    try:
        from api.ai_query_processor import AIQueryProcessor
        
        # Test without OpenAI
        processor = AIQueryProcessor(enable_ai=False)
        
        # Test basic processing
        print("📋 Testing basic query processing...")
        request = processor.process_query("Find young midfielders under 21")
        print(f"✅ Request type: {request.query_type.value}")
        print(f"✅ Confidence: {request.confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Query Processor test failed: {e}")
        return False

def test_ai_router():
    """Test the AI analysis router."""
    print("\n🔬 Testing AI Analysis Router...")
    
    try:
        from api.ai_analysis_router import AIAnalysisRouter
        from api.types import QueryType, PlayerSearchRequest
        
        # Test without OpenAI
        router = AIAnalysisRouter(
            data_dir="data/clean",
            comprehensive_data_dir="data/comprehensive",
            enable_ai_engine=False
        )
        
        # Test basic request
        print("📋 Testing basic analysis routing...")
        request = PlayerSearchRequest(
            query_type=QueryType.PLAYER_SEARCH,
            position="Midfielder",
            min_minutes=500,
            confidence=0.8
        )
        
        response = router.execute_analysis(request)
        print(f"✅ Response success: {response.success}")
        print(f"✅ Total found: {response.total_found}")
        
        # Test engine status
        print("\n📋 Testing engine status...")
        status = router.get_engine_status()
        print(f"✅ AI engine available: {status.get('ai_engine_available', False)}")
        print(f"✅ Traditional available: {status.get('traditional_analyzer_available', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Router test failed: {e}")
        return False

def test_main_api():
    """Test the main API with AI integration."""
    print("\n🔬 Testing Main API with AI Integration...")
    
    try:
        from api.main_api import SoccerAnalyticsAPI, APIConfig
        
        # Test traditional mode
        print("📋 Testing traditional mode...")
        config = APIConfig(
            enable_ai_engine=False,
            ai_first=False
        )
        
        api = SoccerAnalyticsAPI(config)
        print(f"✅ AI native: {api.ai_native}")
        
        # Test basic query
        result = api.query("Find young midfielders")
        print(f"✅ Query success: {result.get('success', False)}")
        
        # Test with AI engine enabled (but no OpenAI key)
        print("\n📋 Testing AI engine mode (without OpenAI)...")
        config_ai = APIConfig(
            enable_ai_engine=True,
            ai_first=True,
            comprehensive_data_dir="data/comprehensive"
        )
        
        api_ai = SoccerAnalyticsAPI(config_ai)
        print(f"✅ AI native: {api_ai.ai_native}")
        
        # Test capabilities
        capabilities = api_ai.get_system_capabilities()
        print(f"✅ System version: {capabilities.get('system_version', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Main API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Simple AI System Tests")
    print("=" * 40)
    
    tests = [
        test_ai_engine,
        test_ai_query_processor, 
        test_ai_router,
        test_main_api
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI system is working.")
    else:
        print("⚠️  Some tests failed. Check logs above.")
    
    print("\n💡 To test full AI capabilities, set OPENAI_API_KEY environment variable")