/**
 * Comprehensive API testing utilities for Soccer Scout AI
 * Provides automated testing and validation of API responses
 */

import { api } from '@/services/api';
import { TEST_QUERIES, TestQuery } from './test-queries';
import { QueryResponse } from '@/types';

export interface TestResult {
  query: TestQuery;
  success: boolean;
  response?: QueryResponse;
  error?: string;
  duration: number;
  timestamp: Date;
}

export interface TestSuite {
  totalTests: number;
  passed: number;
  failed: number; 
  results: TestResult[];
  averageResponseTime: number;
  startTime: Date;
  endTime?: Date;
}

export class APITester {
  private results: TestResult[] = [];

  /**
   * Run a single test query
   */
  async runSingleTest(testQuery: TestQuery): Promise<TestResult> {
    const startTime = performance.now();
    const timestamp = new Date();

    try {
      console.log(`🧪 Testing: ${testQuery.description}`);
      
      const response = await api.query(testQuery.query);
      const duration = performance.now() - startTime;

      // Validate response structure
      const isValid = this.validateResponse(response, testQuery);
      
      const result: TestResult = {
        query: testQuery,
        success: isValid,
        response,
        duration,
        timestamp,
        error: isValid ? undefined : 'Response validation failed'
      };

      console.log(`${isValid ? '✅' : '❌'} ${testQuery.description} (${duration.toFixed(0)}ms)`);
      
      return result;

    } catch (error) {
      const duration = performance.now() - startTime;
      const result: TestResult = {
        query: testQuery,
        success: false,
        duration,
        timestamp,
        error: error instanceof Error ? error.message : String(error)
      };

      console.log(`❌ ${testQuery.description} - Error: ${result.error}`);
      
      return result;
    }
  }

  /**
   * Run all test queries
   */
  async runFullTestSuite(): Promise<TestSuite> {
    console.log('🚀 Starting comprehensive API test suite...');
    
    const startTime = new Date();
    const results: TestResult[] = [];

    for (const testQuery of TEST_QUERIES) {
      const result = await this.runSingleTest(testQuery);
      results.push(result);
      
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    const endTime = new Date();
    const passed = results.filter(r => r.success).length;
    const failed = results.length - passed;
    const averageResponseTime = results.reduce((sum, r) => sum + r.duration, 0) / results.length;

    const testSuite: TestSuite = {
      totalTests: results.length,
      passed,
      failed,
      results,
      averageResponseTime,
      startTime,
      endTime
    };

    this.results = results;
    this.printTestSummary(testSuite);
    
    return testSuite;
  }

  /**
   * Run tests for a specific category
   */
  async runCategoryTests(category: TestQuery['category']): Promise<TestSuite> {
    const categoryQueries = TEST_QUERIES.filter(q => q.category === category);
    console.log(`🧪 Testing ${category} queries (${categoryQueries.length} tests)...`);
    
    const startTime = new Date();
    const results: TestResult[] = [];

    for (const testQuery of categoryQueries) {
      const result = await this.runSingleTest(testQuery);
      results.push(result);
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    const endTime = new Date();
    const passed = results.filter(r => r.success).length;
    const failed = results.length - passed;
    const averageResponseTime = results.reduce((sum, r) => sum + r.duration, 0) / results.length;

    return {
      totalTests: results.length,
      passed,
      failed,
      results,
      averageResponseTime,
      startTime,
      endTime
    };
  }

  /**
   * Validate API response structure and content
   */
  private validateResponse(response: QueryResponse, testQuery: TestQuery): boolean {
    // Basic structure validation
    if (!response.response_text || typeof response.response_text !== 'string') {
      return false;
    }

    if (!response.query_type || typeof response.query_type !== 'string') {
      return false;
    }

    // Category-specific validation
    switch (testQuery.category) {
      case 'comparison':
        return response.query_type === 'comparison' && 
               response.comparison !== undefined &&
               Array.isArray(response.players);

      case 'tactical':
        return response.query_type === 'tactical_analysis' &&
               response.response_text.includes('Tactical') &&
               response.response_text.length > 100;

      case 'prospect':
        return response.query_type === 'prospect_search' &&
               Array.isArray(response.players) &&
               response.response_text.includes('Prospects');

      case 'search':
        return response.query_type === 'search' ||
               response.query_type === 'demo';

      case 'demo':
        return response.query_type === 'demo' &&
               response.response_text.length > 50;

      default:
        return true;
    }
  }

  /**
   * Print comprehensive test summary
   */
  private printTestSummary(testSuite: TestSuite): void {
    console.log('\n📊 Test Suite Summary:');
    console.log('========================');
    console.log(`Total Tests: ${testSuite.totalTests}`);
    console.log(`✅ Passed: ${testSuite.passed}`);
    console.log(`❌ Failed: ${testSuite.failed}`);
    console.log(`🎯 Success Rate: ${((testSuite.passed / testSuite.totalTests) * 100).toFixed(1)}%`);
    console.log(`⚡ Average Response Time: ${testSuite.averageResponseTime.toFixed(0)}ms`);
    console.log(`⏱️ Total Duration: ${testSuite.endTime ? (testSuite.endTime.getTime() - testSuite.startTime.getTime()) : 0}ms`);
    
    // Category breakdown
    const categoryStats = this.getCategoryStats(testSuite.results);
    console.log('\n📋 Category Breakdown:');
    Object.entries(categoryStats).forEach(([category, stats]) => {
      console.log(`  ${category}: ${stats.passed}/${stats.total} (${((stats.passed/stats.total)*100).toFixed(0)}%)`);
    });

    // Failed tests details
    const failedTests = testSuite.results.filter(r => !r.success);
    if (failedTests.length > 0) {
      console.log('\n❌ Failed Tests:');
      failedTests.forEach(test => {
        console.log(`  - ${test.query.description}: ${test.error}`);
      });
    }
  }

  /**
   * Get statistics by category
   */
  private getCategoryStats(results: TestResult[]) {
    const stats: Record<string, { total: number; passed: number }> = {};
    
    results.forEach(result => {
      const category = result.query.category;
      if (!stats[category]) {
        stats[category] = { total: 0, passed: 0 };
      }
      stats[category].total++;
      if (result.success) {
        stats[category].passed++;
      }
    });

    return stats;
  }

  /**
   * Get latest test results
   */
  getResults(): TestResult[] {
    return this.results;
  }

  /**
   * Health check test
   */
  async runHealthCheck(): Promise<boolean> {
    try {
      console.log('🏥 Running health check...');
      const health = await api.healthCheck();
      console.log('✅ Health check passed:', health);
      return true;
    } catch (error) {
      console.log('❌ Health check failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const apiTester = new APITester();