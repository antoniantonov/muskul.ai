/**
 * Application configuration
 * 
 * Centralized configuration for the application.
 * Values are loaded from environment variables.
 */

export const config = {
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
    timeout: 30000,
  },
  app: {
    name: 'Muskul.ai',
    version: '0.1.0',
  },
  features: {
    // Feature flags can be added here
    enableAnalytics: false,
    enableDarkMode: false,
  },
} as const;
