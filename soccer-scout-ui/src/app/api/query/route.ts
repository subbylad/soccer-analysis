import { NextRequest, NextResponse } from 'next/server';

// CORS headers for Vercel deployment
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
 * Next.js API Route for handling soccer analytics queries
 * This proxies requests to the Railway Flask backend
 */

// Backend URL configuration - Railway production URL
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://soccer-scout-api-production.up.railway.app';

export async function POST(request: NextRequest) {
  try {
    // Parse request body
    const body = await request.json();
    const { query } = body;

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { 
          response_text: 'Query parameter is required and must be a string',
          query_type: 'error',
          error: 'Missing or invalid query parameter'
        },
        { 
          status: 400,
          headers: corsHeaders(),
        }
      );
    }

    if (query.trim().length === 0) {
      return NextResponse.json(
        {
          response_text: 'Query cannot be empty',
          query_type: 'error', 
          error: 'Empty query'
        },
        { 
          status: 400,
          headers: corsHeaders(),
        }
      );
    }

    // Connect to Railway backend
    console.log(`Connecting to backend: ${BACKEND_URL}`);
    
    const backendResponse = await fetch(`${BACKEND_URL}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ query: query.trim() }),
      signal: AbortSignal.timeout(30000), // 30 second timeout
    });

    if (backendResponse.ok) {
      const data = await backendResponse.json();
      console.log('Backend response received successfully');
      
      return NextResponse.json(data, {
        headers: corsHeaders(),
      });
    } else {
      console.error(`Backend responded with status: ${backendResponse.status}`);
      
      // Return error response
      return NextResponse.json(
        {
          response_text: `❌ Backend API error (Status: ${backendResponse.status})
          
**Your query:** "${query}"

The Soccer Scout AI backend encountered an error. Please try again in a moment.

**If this persists, the backend may be temporarily unavailable.**`,
          query_type: 'error',
          error: `Backend error: ${backendResponse.status}`,
          backend_url: BACKEND_URL
        },
        { 
          status: 503,
          headers: corsHeaders(),
        }
      );
    }
      
  } catch (backendError) {
    console.error('Backend connection failed:', backendError);
    
    // Return connection error
    return NextResponse.json(
      {
        response_text: `❌ Unable to connect to Soccer Scout AI backend

**Your query:** "${request.json ? (await request.json().catch(() => ({})))?.query || 'Unknown' : 'Unknown'}"

**Connection Error:** The backend API is temporarily unavailable.

**Backend URL:** ${BACKEND_URL}

**Please try again in a moment.** If the issue persists, the backend service may be down for maintenance.`,
        query_type: 'error',
        error: 'Backend connection failed',
        backend_url: BACKEND_URL,
        error_details: backendError instanceof Error ? backendError.message : 'Unknown error'
      },
      { 
        status: 503,
        headers: corsHeaders(),
      }
    );
  }
}

export async function GET() {
  return NextResponse.json(
    {
      message: 'Soccer Scout AI Query API',
      version: '1.0.0',
      methods: ['POST'],
      description: 'Send POST requests with a "query" parameter to analyze soccer data',
      backend_url: BACKEND_URL
    },
    { 
      status: 200,
      headers: corsHeaders(),
    }
  );
}