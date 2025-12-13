import React, { Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

import { Layout } from './components/Layout';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorBoundary } from './components/ErrorBoundary';

// Lazy load pages for code splitting
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Activities = React.lazy(() => import('./pages/Activities'));
const Providers = React.lazy(() => import('./pages/Providers'));
const Import = React.lazy(() => import('./pages/Import'));
const NotFound = React.lazy(() => import('./pages/NotFound'));

function App(): React.ReactElement {
  return (
    <ErrorBoundary>
      <Layout>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/activities" element={<Activities />} />
            <Route path="/providers" element={<Providers />} />
            <Route path="/import" element={<Import />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </Layout>
    </ErrorBoundary>
  );
}

export default App;
