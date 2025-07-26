import { NextRequest, NextResponse } from 'next/server';
import { QueryResponse } from '@/types';

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
 * Next.js API Route for handling soccer analytics queries
 * This proxies requests to the Railway Flask backend
 */

// Backend URL configuration
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || 'http://localhost:5001';
const MOCK_PLAYERS = [
  {
    name: "Erling Haaland",
    team: "Manchester City",
    league: "Premier League",
    position: "CF",
    age: 24,
    goals: 27,
    assists: 5,
    xg: 25.2,
    xa: 4.8
  },
  {
    name: "Kylian Mbappé",
    team: "Paris Saint-Germain", 
    league: "Ligue 1",
    position: "LW/CF",
    age: 25,
    goals: 29,
    assists: 7,
    xg: 26.8,
    xa: 6.2
  }
];

function generateMockResponse(query: string): QueryResponse {
  const lowerQuery = query.toLowerCase();
  
  // Handle comparison queries
  if (lowerQuery.includes('compare') && (lowerQuery.includes('haaland') || lowerQuery.includes('mbappé'))) {
    return {
      response_text: `## Player Comparison: Haaland vs Mbappé

**Erling Haaland (Manchester City)**
- Position: Centre Forward
- Age: 24 | Goals: 27 | Assists: 5
- Expected Goals: 25.2 | Expected Assists: 4.8

**Kylian Mbappé (Paris Saint-Germain)**
- Position: Left Wing/Centre Forward  
- Age: 25 | Goals: 29 | Assists: 7
- Expected Goals: 26.8 | Expected Assists: 6.2

### Analysis
Both players are elite finishers with Mbappé showing slightly better creativity (more assists). Haaland is more specialized as a pure striker, while Mbappé offers versatility across the front line.`,
      query_type: 'comparison',
      players: MOCK_PLAYERS,
      comparison: {
        player1: MOCK_PLAYERS[0],
        player2: MOCK_PLAYERS[1],
        winner: 'mbappé',
        analysis: 'Close comparison with Mbappé edging on versatility'
      }
    };
  }
  
  // Handle tactical queries
  if (lowerQuery.includes('alongside') || lowerQuery.includes('mainoo')) {
    return {
      response_text: `## Tactical Analysis: Partners for Kobbie Mainoo

**Recommended Midfield Partners in Ligue 1:**

1. **Aurélien Tchouaméni** (Monaco → Real Madrid)
   - Perfect defensive shield for Mainoo's creative freedom
   - Elite ball-winning and progressive passing

2. **Warren Zaïre-Emery** (PSG)
   - Similar age profile, excellent technical ability
   - Box-to-box style complements Mainoo's deep-lying role

3. **Khéphren Thuram** (Nice)
   - Physical presence and driving runs
   - Would allow Mainoo to orchestrate from deeper positions

### Tactical Reasoning
Mainoo excels as a deep-lying playmaker who needs defensive security behind him and runners ahead. These partners provide the perfect balance of protection and forward momentum.`,
      query_type: 'tactical_analysis',
      players: [
        {
          name: "Aurélien Tchouaméni",
          team: "Real Madrid",
          league: "La Liga",
          position: "CDM",
          age: 24,
          tackles: 3.2,
          interceptions: 2.1,
          progressive_passes: 8.5
        }
      ],
      scouting_report: {
        summary: 'Elite partners identified for Mainoo in Ligue 1',
        recommendations: ['Tchouaméni', 'Zaïre-Emery', 'Thuram'],
        tactical_fit: 9.2
      }
    };
  }
  
  // Handle prospect queries
  if (lowerQuery.includes('young') && lowerQuery.includes('midfielder')) {
    return {
      response_text: `## Young Midfield Prospects Under 21

**Elite Prospects:**

1. **Warren Zaïre-Emery** (PSG) - Age 19
   - 🌟 Technical ability: 9/10
   - Box-to-box midfielder with exceptional passing range
   - Already established in PSG first team

2. **Pedri** (Barcelona) - Age 21
   - ⭐ Creativity: 10/10  
   - Deep-lying playmaker with world-class vision
   - Key player for club and country

3. **Eduardo Camavinga** (Real Madrid) - Age 21
   - 💫 Physicality: 9/10
   - Defensive midfielder with pace and power
   - Champions League proven

### Scouting Summary
All three offer different profiles - Zaïre-Emery for balance, Pedri for creativity, Camavinga for physicality. Investment in any would yield long-term dividends.`,
      query_type: 'prospect_search',
      players: [
        {
          name: "Warren Zaïre-Emery",
          team: "Paris Saint-Germain",
          league: "Ligue 1", 
          position: "CM",
          age: 19,
          potential_score: 9.2
        },
        {
          name: "Pedri",
          team: "Barcelona",
          league: "La Liga",
          position: "CAM",
          age: 21,
          potential_score: 9.8
        }
      ]
    };
  }

  // Default response for unrecognized queries
  return {
    response_text: `Thank you for your query: "${query}"

I'm a demonstration API endpoint showing how the Soccer Scout AI system would work with real data integration.

**Sample queries I can handle:**
- "Compare Haaland vs Mbappé" - Player comparisons with detailed analysis
- "Who can play alongside Kobbie Mainoo in Ligue 1?" - Tactical partner analysis  
- "Find young midfielders under 21" - Prospect identification and scouting

**In full deployment, I would:**
- Access 2,853+ players from Big 5 European leagues
- Use GPT-4 enhanced tactical analysis
- Provide real-time statistical comparisons
- Generate professional scouting reports

To see the complete system with live data, run both the Flask backend and frontend locally.`,
    query_type: 'demo',
    players: []
  };
}

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

    // Try to connect to Railway backend first
    try {
      console.log(`Attempting to connect to backend: ${BACKEND_URL}`);
      
      const backendResponse = await fetch(`${BACKEND_URL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ query: query.trim() }),
        signal: AbortSignal.timeout(25000), // 25 second timeout
      });

      if (backendResponse.ok) {
        const data = await backendResponse.json();
        console.log('Backend response received successfully');
        
        return NextResponse.json(data, {
          headers: corsHeaders(),
        });
      } else {
        console.log(`Backend responded with status: ${backendResponse.status}`);
        throw new Error(`Backend error: ${backendResponse.status}`);
      }
      
    } catch (backendError) {
      console.log('Backend connection failed, falling back to mock data:', backendError);
      
      // Fallback to mock response if backend is unavailable
      const mockResponse = generateMockResponse(query);
      
      // Add metadata indicating this is a fallback response
      const enrichedResponse = {
        ...mockResponse,
        request_id: `req_${Date.now()}`,
        timestamp: new Date().toISOString(),
        processing_time: Math.random() * 1000 + 500,
        fallback_mode: true,
        backend_status: 'unavailable'
      };

      return NextResponse.json(enrichedResponse, {
        headers: corsHeaders(),
      });
    }

  } catch (error) {
    console.error('API route error:', error);
    
    return NextResponse.json(
      {
        response_text: 'An internal server error occurred while processing your request',
        query_type: 'error',
        error: 'Internal server error'
      },
      { 
        status: 500,
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
      description: 'Send POST requests with a "query" parameter to analyze soccer data'
    },
    { 
      status: 200,
      headers: corsHeaders(),
    }
  );
}