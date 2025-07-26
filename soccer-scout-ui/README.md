# ⚽ Soccer Scout AI - Frontend

A modern, AI-powered soccer scouting interface built with Next.js 15, React 19, and TypeScript. This frontend provides an intuitive chat-based interface for interacting with the Soccer Scout AI backend, featuring GPT-4 enhanced tactical analysis, player comparisons, and comprehensive scouting insights.

## 🚀 Features

### Chat-First Interface
- **Modern Chat UI**: Clean, responsive chat interface optimized for soccer analytics
- **Real-time Messaging**: Smooth animations and transitions with Framer Motion
- **Smart Suggestions**: Context-aware query suggestions and examples
- **Typing Indicators**: Visual feedback during AI processing

### AI-Powered Analysis
- **GPT-4 Integration**: Advanced tactical analysis and insights
- **Multiple Query Types**: Player comparisons, tactical analysis, scouting reports
- **Rich Visualizations**: Interactive player cards with detailed statistics
- **Tactical Insights**: Formation fit analysis, strengths/weaknesses, compatibility scores

### Player Analytics
- **Comprehensive Stats**: Goals, assists, expected stats (xG, xA), progressive actions
- **Visual Cards**: Color-coded stat cards with icons and progress indicators
- **Defensive Metrics**: Tackles, interceptions, blocks for complete player profiles
- **Performance Indicators**: Tier classification (Elite ⭐, High 🌟, Good 💫, Developing 📈)

### User Experience
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Dark/Light Themes**: Built-in theme support with CSS variables
- **Accessibility**: WCAG-compliant with keyboard navigation and screen reader support
- **Error Handling**: Graceful error states with user-friendly messages

## 🛠️ Tech Stack

### Core Framework
- **Next.js 15**: App Router, Server Components, and latest React features
- **React 19**: Latest React with concurrent features and improved performance
- **TypeScript**: Full type safety with comprehensive interface definitions

### UI & Styling
- **Tailwind CSS 4**: Utility-first styling with custom color palette
- **Framer Motion**: Smooth animations and micro-interactions
- **Lucide React**: Beautiful, consistent icons
- **@headlessui/react**: Accessible, unstyled UI components

### State Management & Data
- **Zustand**: Lightweight, performant state management
- **@tanstack/react-query**: Server state management with caching
- **Custom API Client**: Type-safe API service with error handling

### Chat Interface
- **@chatscope/chat-ui-kit-react**: Professional chat components
- **Custom Message Bubbles**: Tailored for soccer analytics content
- **Real-time Updates**: Optimistic updates and loading states

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (recommended: Node.js 20+)
- npm, yarn, or pnpm package manager
- Soccer Scout AI backend running (default: http://localhost:8000)

### Installation

1. **Navigate to Frontend Directory**
   ```bash
   cd soccer-scout-ui
   ```

2. **Install Dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Environment Setup**
   Create a `.env.local` file in the root directory:
   ```env
   # API Configuration
   NEXT_PUBLIC_API_URL=http://localhost:8000

   # Optional: Enable development features
   NODE_ENV=development
   ```

4. **Start Development Server**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

5. **Open Application**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
soccer-scout-ui/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── globals.css         # Global styles and CSS variables
│   │   ├── layout.tsx          # Root layout with providers
│   │   └── page.tsx            # Home page with chat interface
│   ├── components/
│   │   ├── chat/               # Chat interface components
│   │   │   ├── ChatInterface.tsx    # Main chat container
│   │   │   ├── MessageList.tsx      # Message display area
│   │   │   ├── MessageBubble.tsx    # Individual message rendering
│   │   │   └── QueryInput.tsx       # Message input with suggestions
│   │   ├── layout/             # Layout components
│   │   │   └── Providers.tsx        # React Query and other providers
│   │   ├── player/             # Player-related components
│   │   │   └── PlayerCard.tsx       # Enhanced player stat cards
│   │   └── ui/                 # Reusable UI components
│   │       ├── Button.tsx           # Accessible button component
│   │       └── LoadingSpinner.tsx   # Loading animations
│   ├── hooks/
│   │   └── useChat.ts          # Chat functionality with API integration
│   ├── services/
│   │   └── api.ts              # Type-safe API client with error handling
│   ├── store/
│   │   └── chatStore.ts        # Zustand chat state management
│   ├── types/
│   │   └── index.ts            # Comprehensive TypeScript interfaces
│   └── utils/
│       └── index.ts            # Utility functions and formatters
├── public/                     # Static assets
├── tailwind.config.ts          # Tailwind configuration with custom theme
├── tsconfig.json              # TypeScript configuration
├── next.config.ts             # Next.js configuration
└── package.json               # Dependencies and scripts
```

## 🎨 Design System

### Color Palette
```css
/* Primary Brand Colors */
--primary: #3b82f6 (Blue 500)
--secondary: #22c55e (Green 500)
--accent: #eab308 (Yellow 500)

/* Semantic Colors */
--success: #10b981 (Emerald 500)
--warning: #f59e0b (Amber 500)
--error: #ef4444 (Red 500)
--info: #06b6d4 (Cyan 500)

/* Neutral Palette */
--background: #ffffff
--foreground: #0f172a (Slate 900)
--muted: #f8fafc (Slate 50)
--border: #e2e8f0 (Slate 200)
```

### Typography
- **Font Family**: Inter (Google Fonts)
- **Font Weights**: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)
- **Font Features**: OpenType features enabled for better readability

### Components
- **Border Radius**: Consistent 0.5rem (8px) radius across components
- **Shadows**: Layered shadow system (soft, medium, strong)
- **Animations**: Spring-based animations with Framer Motion

## 🔧 Configuration

### API Configuration
Update the API base URL in your environment:
```env
NEXT_PUBLIC_API_URL=http://your-backend-url:port
```

### Tailwind Customization
Modify colors, fonts, and other design tokens in `tailwind.config.ts`:
```typescript
// Custom color additions
colors: {
  primary: {
    50: '#eff6ff',
    // ... your custom color scale
  }
}
```

## 🚀 Development

### Available Scripts
```bash
npm run dev          # Start development server with Turbopack
npm run build        # Create production build
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Code Quality
- **ESLint**: Configured with Next.js recommended rules
- **TypeScript**: Strict mode enabled with comprehensive type checking
- **Prettier**: Code formatting (configure in your editor)

## 📚 API Integration

### Backend Compatibility
The frontend is designed to work with the Soccer Scout AI Python backend:
- **Expected Endpoint**: `POST /query`
- **Health Check**: `GET /health`
- **Streaming Support**: `POST /query-stream` (optional)

### Query Types Supported
- **Player Comparisons**: "Compare Haaland vs Mbappé"
- **Tactical Analysis**: "Who can play alongside Kobbie Mainoo?"
- **Player Search**: "Find young midfielders under 21"
- **Scouting Reports**: "Scout report for Pedri"

### Response Format
```typescript
interface QueryResponse {
  response_text: string;
  players?: Player[];
  analysis?: TacticalAnalysis;
  comparison?: ComparisonAnalysis;
  scouting_report?: ScoutingReport;
  query_type: 'comparison' | 'search' | 'tactical' | 'scouting' | 'general';
}
```

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Manual Build
```bash
npm run build
npm start
```

## 📄 License

This project is part of the Soccer Scout AI system. Please refer to the main project license.

---

**Built with ❤️ for the football analytics community**
