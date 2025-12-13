import React from 'react';

export default function Dashboard(): React.ReactElement {
  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold">Dashboard</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="card">
          <h2 className="mb-2 text-xl font-semibold">Welcome to Muskul.ai</h2>
          <p className="text-neutral-600">Your fitness analytics dashboard</p>
        </div>
      </div>
    </div>
  );
}
