'use client';

import { PaymentForm } from '@/src/components/ui/PaymentForm';
import { TransactionDashboard } from '@/src/components/ui/TransactionDashboard';

export default function Home() {
  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Payment Portal</h1>
          <p className="text-gray-600 mt-2">
            Secure payment processing powered by AI-driven chaos resilience
          </p>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <PaymentForm />
          </div>

          {/* Transaction Dashboard - 3/4 */}
          <div className="lg:col-span-3">
            <TransactionDashboard />
          </div>
        </div>
      </div>
    </div>
  );
}
