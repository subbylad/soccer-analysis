#!/usr/bin/env node

/**
 * Test script to validate Vercel deployment functionality
 */

const https = require('https');
const http = require('http');

const TEST_QUERIES = [
  'Compare Haaland vs Mbappé',
  'Who can play alongside Kobbie Mainoo in Ligue 1?',
  'Find young midfielders under 21',
  'Tell me about Pedri',
];

function makeRequest(hostname, path, data = null, isHttps = true) {
  return new Promise((resolve, reject) => {
    const client = isHttps ? https : http;
    
    // Parse hostname and port
    const [host, port] = hostname.split(':');
    
    const options = {
      hostname: host,
      port: port ? parseInt(port) : (isHttps ? 443 : 80),
      path,
      method: data ? 'POST' : 'GET',
      headers: data ? {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      } : {},
      timeout: 10000,
    };

    const req = client.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => {
        body += chunk;
      });
      res.on('end', () => {
        try {
          const response = {
            status: res.statusCode,
            headers: res.headers,
            body: body ? JSON.parse(body) : null,
          };
          resolve(response);
        } catch (error) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            body: body,
            error: 'Failed to parse JSON response',
          });
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    if (data) {
      req.write(data);
    }
    req.end();
  });
}

async function testHealthEndpoint(hostname, isHttps = true) {
  console.log(`🏥 Testing health endpoint: ${hostname}/api/health`);
  
  try {
    const response = await makeRequest(hostname, '/api/health', null, isHttps);
    
    if (response.status === 200) {
      console.log('✅ Health check passed');
      console.log(`   Status: ${response.body?.status || 'unknown'}`);
      console.log(`   Service: ${response.body?.service || 'unknown'}`);
      return true;
    } else {
      console.log(`❌ Health check failed with status: ${response.status}`);
      return false;
    }
  } catch (error) {
    console.log(`❌ Health check error: ${error.message}`);
    return false;
  }
}

async function testQueryEndpoint(hostname, query, isHttps = true) {
  console.log(`🧠 Testing query: "${query}"`);
  
  try {
    const data = JSON.stringify({ query });
    const response = await makeRequest(hostname, '/api/query', data, isHttps);
    
    if (response.status === 200) {
      console.log('✅ Query successful');
      console.log(`   Response length: ${response.body?.response_text?.length || 0} chars`);
      console.log(`   Query type: ${response.body?.query_type || 'unknown'}`);
      return true;
    } else {
      console.log(`❌ Query failed with status: ${response.status}`);
      console.log(`   Error: ${response.body?.error || 'Unknown error'}`);
      return false;
    }
  } catch (error) {
    console.log(`❌ Query error: ${error.message}`);
    return false;
  }
}

async function testDeployment(hostname, isHttps = true) {
  console.log(`🚀 Testing deployment at: ${hostname}`);
  console.log('='.repeat(50));
  
  let totalTests = 0;
  let passedTests = 0;
  
  // Test health endpoint
  totalTests++;
  if (await testHealthEndpoint(hostname, isHttps)) {
    passedTests++;
  }
  
  // Test query endpoints
  for (const query of TEST_QUERIES) {
    totalTests++;
    await new Promise(resolve => setTimeout(resolve, 1000)); // Rate limiting
    if (await testQueryEndpoint(hostname, query, isHttps)) {
      passedTests++;
    }
  }
  
  console.log('='.repeat(50));
  console.log(`📊 Test Results: ${passedTests}/${totalTests} passed`);
  
  if (passedTests === totalTests) {
    console.log('🎉 All tests passed! Deployment is working correctly.');
    return true;
  } else {
    console.log('⚠️ Some tests failed. Check the deployment configuration.');
    return false;
  }
}

// Main execution
async function main() {
  const args = process.argv.slice(2);
  const hostname = args[0];
  
  if (!hostname) {
    console.log('Usage: node test-deployment.js <hostname>');
    console.log('Example: node test-deployment.js soccer-scout-ai.vercel.app');
    console.log('Example: node test-deployment.js localhost:3000');
    process.exit(1);
  }
  
  const isHttps = !hostname.includes('localhost');
  
  try {
    const success = await testDeployment(hostname, isHttps);
    process.exit(success ? 0 : 1);
  } catch (error) {
    console.error('💥 Deployment test failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { testDeployment };