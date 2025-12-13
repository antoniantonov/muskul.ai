import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps): React.ReactElement {
  return (
    <div className="min-h-screen bg-neutral-50">
      <a href="#main-content" className="skip-to-main">
        Skip to main content
      </a>
      <header className="bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-neutral-900">Muskul.ai</h1>
        </div>
      </header>
      <main id="main-content" className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
