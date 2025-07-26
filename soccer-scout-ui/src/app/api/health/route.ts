import { NextResponse } from 'next/server';

// Add CORS headers for Vercel deployment
function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };
}

// Handle OPTIONS requests for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: corsHeaders(),
  });
}

/**
 * Health check endpoint for Soccer Scout AI
 */
export async function GET() {
  return NextResponse.json(
    {
      status: 'healthy',
      service: 'Soccer Scout AI',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development',
      features: [
        'Player comparison analysis',
        'Tactical scouting insights',
        'Young prospect identification',
        'GPT-4 enhanced responses'
      ]
    },
    { 
      status: 200,
      headers: {
        ...corsHeaders(),
        'Cache-Control': 'no-cache',
      }
    }
  );
}