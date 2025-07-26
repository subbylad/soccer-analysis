import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        // World.org inspired neutral palette
        world: {
          'bg-primary': '#1a1a1a',
          'bg-secondary': '#f8f8f8', 
          'bg-card': '#ffffff',
          'bg-muted': '#f5f5f5',
          'text-primary': '#000000',
          'text-secondary': '#666666', 
          'text-muted': '#888888',
          'text-light': '#cccccc',
          'border': '#e5e5e5',
          'border-muted': '#f0f0f0',
          'accent': '#000000',
          'accent-muted': '#333333',
        },
        // Minimal color accents for data visualization
        data: {
          'positive': '#22c55e',
          'negative': '#ef4444',
          'neutral': '#6b7280',
          'warning': '#f59e0b',
        },
      fontFamily: {
        display: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif',
        ],
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif',
        ],
        mono: [
          'SF Mono',
          'Monaco',
          'Inconsolata',
          'Roboto Mono',
          'monospace',
        ],
      },
      fontSize: {
        'chat-title': ['1.875rem', { lineHeight: '2.25rem', letterSpacing: '-0.025em' }],
        'chat-subtitle': ['1rem', { lineHeight: '1.5rem', letterSpacing: '0' }],
        'chat-message': ['1rem', { lineHeight: '1.6rem', letterSpacing: '0' }],
        'chat-meta': ['0.875rem', { lineHeight: '1.25rem', letterSpacing: '0' }],
        'chat-input': ['1.125rem', { lineHeight: '1.75rem', letterSpacing: '0' }],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'world-hover': 'worldHover 0.3s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        worldHover: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0.6' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'world-subtle': '0 1px 3px rgba(0, 0, 0, 0.05)',
        'world-medium': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'world-strong': '0 4px 16px rgba(0, 0, 0, 0.12)',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
    },
  },
  plugins: [],
};

export default config;