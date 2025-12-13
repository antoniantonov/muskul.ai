import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFound(): React.ReactElement {
  return (
    <div className="flex min-h-[400px] items-center justify-center">
      <div className="card max-w-md text-center">
        <h1 className="mb-4 text-4xl font-bold text-neutral-900">404</h1>
        <p className="mb-6 text-xl text-neutral-700">Page not found</p>
        <Link to="/" className="btn-primary">
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
