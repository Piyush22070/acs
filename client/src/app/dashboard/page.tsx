'use client';

import { TransactionDashboard } from '@/src/components/ui/TransactionDashboard';

export default function Dashboard() {
  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Monitor transactions and test system resilience
          </p>
        </div>
        {/* Dashboard Content */}
        <TransactionDashboard />
      </div>
    </div>
  );
}
