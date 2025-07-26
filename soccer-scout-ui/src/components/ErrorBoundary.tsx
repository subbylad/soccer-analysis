'use client';

import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error?: Error; resetError: () => void }>;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by boundary:', error, errorInfo);
    }
    
    // In production, you could send error to monitoring service here
    // Example: errorReportingService.captureException(error, errorInfo);
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback;
        return <FallbackComponent error={this.state.error} resetError={this.resetError} />;
      }

      // Default fallback UI with world.org styling
      return (
        <div className="world-card mx-auto mt-8 max-w-md text-center">
          <div className="text-4xl mb-4">⚠️</div>
          <h2 className="world-text-body font-semibold mb-2">Something went wrong</h2>
          <p className="world-text-meta mb-4">
            An unexpected error occurred. Please try refreshing the page.
          </p>
          <div className="space-y-2">
            <button 
              onClick={this.resetError}
              className="world-button mr-2"
            >
              Try Again
            </button>
            <button 
              onClick={() => window.location.reload()}
              className="world-button bg-world-bg-muted text-world-text-primary hover:opacity-70"
            >
              Refresh Page
            </button>
          </div>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details className="mt-4 text-left">
              <summary className="world-text-meta cursor-pointer">Error Details</summary>
              <pre className="world-text-meta text-xs mt-2 p-2 bg-world-bg-muted rounded overflow-auto">
                {this.state.error.stack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;