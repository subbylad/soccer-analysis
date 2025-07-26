'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { apiTester, TestResult, TestSuite } from '@/utils/api-tester';
import { TEST_QUERIES, getTestQueriesByCategory } from '@/utils/test-queries';

export default function TestPage() {
  const [isRunning, setIsRunning] = useState(false);
  const [testSuite, setTestSuite] = useState<TestSuite | null>(null);
  const [healthStatus, setHealthStatus] = useState<boolean | null>(null);

  const runHealthCheck = async () => {
    setHealthStatus(null);
    const result = await apiTester.runHealthCheck();
    setHealthStatus(result);
  };

  const runFullSuite = async () => {
    setIsRunning(true);
    setTestSuite(null);
    
    try {
      const results = await apiTester.runFullTestSuite();
      setTestSuite(results);
    } catch (error) {
      console.error('Test suite failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const runCategoryTest = async (category: string) => {
    setIsRunning(true);
    
    try {
      const results = await apiTester.runCategoryTests(category as any);
      setTestSuite(results);
    } catch (error) {
      console.error('Category test failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      comparison: 'bg-blue-100 text-blue-800',
      tactical: 'bg-green-100 text-green-800', 
      prospect: 'bg-purple-100 text-purple-800',
      search: 'bg-orange-100 text-orange-800',
      demo: 'bg-gray-100 text-gray-800'
    };
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Soccer Scout AI - Testing Suite
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Comprehensive testing infrastructure for validating API functionality,
            response quality, and system performance.
          </p>
        </motion.div>

        {/* Health Check */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-lg p-6 mb-8"
        >
          <h2 className="text-2xl font-semibold mb-4">Health Check</h2>
          <div className="flex items-center gap-4">
            <button
              onClick={runHealthCheck}
              disabled={isRunning}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Run Health Check
            </button>
            {healthStatus !== null && (
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                healthStatus 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {healthStatus ? '✅ Healthy' : '❌ Unhealthy'}
              </div>
            )}
          </div>
        </motion.div>

        {/* Test Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-lg p-6 mb-8"
        >
          <h2 className="text-2xl font-semibold mb-4">Test Controls</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <button
              onClick={runFullSuite}
              disabled={isRunning}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {isRunning ? 'Running...' : 'Run All Tests'}
            </button>
            
            {['comparison', 'tactical', 'prospect', 'search', 'demo'].map(category => (
              <button
                key={category}
                onClick={() => runCategoryTest(category)}
                disabled={isRunning}
                className={`px-4 py-2 rounded-lg text-sm font-medium capitalize ${getCategoryColor(category)} hover:opacity-80 disabled:opacity-50`}
              >
                {category}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Test Queries Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-lg shadow-lg p-6 mb-8"
        >
          <h2 className="text-2xl font-semibold mb-4">Available Test Queries</h2>
          <div className="grid gap-4">
            {TEST_QUERIES.map((query, index) => (
              <div
                key={query.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(query.category)}`}>
                        {query.category}
                      </span>
                      <span className="text-sm text-gray-500">
                        Expected: {query.expectedType}
                      </span>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-1">
                      "{query.query}"
                    </h3>
                    <p className="text-gray-600 text-sm">
                      {query.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Test Results */}
        {testSuite && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-lg p-6"
          >
            <h2 className="text-2xl font-semibold mb-4">Test Results</h2>
            
            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {testSuite.totalTests}
                </div>
                <div className="text-sm text-blue-800">Total Tests</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-600">
                  {testSuite.passed}
                </div>
                <div className="text-sm text-green-800">Passed</div>
              </div>
              <div className="bg-red-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-600">
                  {testSuite.failed}
                </div>
                <div className="text-sm text-red-800">Failed</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {testSuite.averageResponseTime.toFixed(0)}ms
                </div>
                <div className="text-sm text-purple-800">Avg Response</div>
              </div>
            </div>

            {/* Individual Results */}
            <div className="space-y-4">
              {testSuite.results.map((result, index) => (
                <div
                  key={result.query.id}
                  className={`border rounded-lg p-4 ${
                    result.success 
                      ? 'border-green-200 bg-green-50' 
                      : 'border-red-200 bg-red-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={result.success ? '✅' : '❌'}>
                        {result.success ? '✅' : '❌'}
                      </span>
                      <span className="font-semibold">
                        {result.query.description}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs ${getCategoryColor(result.query.category)}`}>
                        {result.query.category}
                      </span>
                    </div>
                    <span className="text-sm text-gray-500">
                      {result.duration.toFixed(0)}ms
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">
                    Query: "{result.query.query}"
                  </div>
                  {result.error && (
                    <div className="text-sm text-red-600 bg-red-100 rounded p-2">
                      Error: {result.error}
                    </div>
                  )}
                  {result.response && (
                    <details className="text-sm">
                      <summary className="cursor-pointer text-gray-700 hover:text-gray-900">
                        View Response
                      </summary>
                      <pre className="mt-2 bg-gray-100 rounded p-2 overflow-auto text-xs">
                        {JSON.stringify(result.response, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}