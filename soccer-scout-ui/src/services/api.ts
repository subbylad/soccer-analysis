import { QueryResponse, APIConfig } from '@/types';

// Custom error types for better error handling
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class NetworkError extends Error {
  constructor(message: string = 'Network connection failed') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class TimeoutError extends Error {
  constructor(message: string = 'Request timeout') {
    super(message);
    this.name = 'TimeoutError';
  }
}

class SoccerScoutAPI {
  private config: APIConfig;

  constructor(config: APIConfig = { 
    baseUrl: typeof window !== 'undefined' ? '/api' : 'http://localhost:5001', 
    timeout: 30000 
  }) {
    this.config = config;
  }

  private async handleResponse(response: Response): Promise<QueryResponse> {
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If response isn't JSON, use the status text
      }

      throw new APIError(errorMessage, response.status);
    }

    try {
      const responseData = await response.json();
      
      // Handle the nested response structure from our API
      const data = responseData.data || responseData;
      
      // Validate the response structure
      if (!data.response_text) {
        throw new APIError('Invalid API response: missing response_text');
      }

      return data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError('Failed to parse API response');
    }
  }

  async query(query: string): Promise<QueryResponse> {
    if (!query.trim()) {
      throw new APIError('Query cannot be empty');
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

      const response = await fetch(`${this.config.baseUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ query: query.trim() }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return await this.handleResponse(response);

    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new TimeoutError(`Request timeout after ${this.config.timeout}ms`);
      }
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new NetworkError('Failed to connect to the API server');
      }

      if (error instanceof APIError || error instanceof NetworkError || error instanceof TimeoutError) {
        throw error;
      }

      console.error('API query failed:', error);
      throw new APIError('An unexpected error occurred while processing your request');
    }
  }

  async queryWithStreaming(
    query: string,
    onPartialResponse?: (partial: string) => void
  ): Promise<QueryResponse> {
    if (!query.trim()) {
      throw new APIError('Query cannot be empty');
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

      const response = await fetch(`${this.config.baseUrl}/query-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ query: query.trim() }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new APIError(
          `HTTP ${response.status}: ${response.statusText}`,
          response.status
        );
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new APIError('No response body available for streaming');
      }

      const decoder = new TextDecoder();
      let result = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          result += chunk;
          onPartialResponse?.(chunk);
        }
      } finally {
        reader.releaseLock();
      }

      if (!result.trim()) {
        throw new APIError('Empty response from streaming endpoint');
      }

      try {
        return JSON.parse(result);
      } catch (parseError) {
        throw new APIError('Failed to parse streaming response as JSON');
      }

    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new TimeoutError(`Streaming request timeout after ${this.config.timeout}ms`);
      }
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new NetworkError('Failed to connect to the streaming API');
      }

      if (error instanceof APIError || error instanceof NetworkError || error instanceof TimeoutError) {
        throw error;
      }

      console.error('Streaming query failed:', error);
      throw new APIError('An unexpected error occurred during streaming');
    }
  }

  // Health check method
  async healthCheck(): Promise<{ status: string; version?: string }> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout for health check

      const response = await fetch(`${this.config.baseUrl}/health`, {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new APIError(`Health check failed: ${response.status}`, response.status);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new TimeoutError('Health check timeout');
      }
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new NetworkError('Cannot reach API server');
      }

      throw error;
    }
  }
}

export const api = new SoccerScoutAPI();