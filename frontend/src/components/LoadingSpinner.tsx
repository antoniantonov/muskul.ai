import React from 'react';

export function LoadingSpinner(): React.ReactElement {
  return (
    <div className="flex min-h-[400px] items-center justify-center" role="status">
      <div className="spinner" aria-label="Loading" />
      <span className="sr-only">Loading...</span>
    </div>
  );
}
