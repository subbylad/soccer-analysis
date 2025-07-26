import { NextResponse } from 'next/server';

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
        'Cache-Control': 'no-cache',
      }
    }
  );
}