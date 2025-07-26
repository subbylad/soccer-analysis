#!/usr/bin/env node

/**
 * Test script to validate Vercel deployment and API routes
 */

const https = require('https');

function testEndpoint(hostname, path) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname,
      path,
      method: 'GET',
      timeout: 10000,
    };

    console.log(`🧪 Testing: https://${hostname}${path}`);

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        console.log(`✅ Status: ${res.statusCode}`);
        if (res.statusCode === 200) {
          try {
            const parsed = JSON.parse(data);
            console.log(`📊 Response: ${JSON.stringify(parsed, null, 2).substring(0, 200)}...`);
            resolve(true);
          } catch (e) {
            console.log(`📝 HTML Response received (likely working)`);
            resolve(true);
          }
        } else {
          console.log(`❌ Error: ${data}`);
          resolve(false);
        }
      });
    });

    req.on('error', (error) => {
      console.log(`❌ Request failed: ${error.message}`);
      resolve(false);
    });

    req.on('timeout', () => {
      console.log(`⏰ Request timeout`);
      req.destroy();
      resolve(false);
    });

    req.end();
  });
}

async function main() {
  const hostname = process.argv[2];
  
  if (!hostname) {
    console.log('Usage: node test-vercel-deployment.js <vercel-domain>');
    console.log('Example: node test-vercel-deployment.js soccer-scout-ai.vercel.app');
    process.exit(1);
  }

  console.log(`🚀 Testing Vercel deployment: ${hostname}`);
  console.log('=' * 50);

  const tests = [
    { path: '/', name: 'Homepage' },
    { path: '/api/health', name: 'Health API Route' },
    { path: '/api/query', name: 'Query API Route (should fail without POST)' },
  ];

  let passed = 0;
  let total = tests.length;

  for (const test of tests) {
    console.log(`\n${test.name}:`);
    const success = await testEndpoint(hostname, test.path);
    if (success) passed++;
    await new Promise(resolve => setTimeout(resolve, 1000)); // Rate limiting
  }

  console.log('\n' + '=' * 50);
  console.log(`📊 Results: ${passed}/${total} tests passed`);
  
  if (passed === total) {
    console.log('🎉 All tests passed! Vercel deployment is working.');
  } else {
    console.log('⚠️  Some tests failed. Check the deployment configuration.');
  }

  process.exit(passed === total ? 0 : 1);
}

if (require.main === module) {
  main();
}