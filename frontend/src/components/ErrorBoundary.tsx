import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-neutral-50 px-4">
          <div className="card max-w-md text-center">
            <h1 className="mb-4 text-2xl font-bold text-error-600">Something went wrong</h1>
            <p className="mb-6 text-neutral-700">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <button
              className="btn-primary"
              onClick={() => window.location.reload()}
              type="button"
            >
              Reload page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
