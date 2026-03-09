'use client';

import { usePaymentStore } from '@/src/store/paymentStore';
import Link from 'next/link';

export function Sidebar() {
  const sentinelHealth = usePaymentStore((state) => state.sentinelHealth);
  const transactions = usePaymentStore((state) => state.transactions);

  const healthColor = {
    healthy: 'bg-green-500',
    healing: 'bg-amber-500',
    offline: 'bg-red-500',
  };

  const healthLabel = {
    healthy: 'Healthy',
    healing: 'Self-Healing',
    offline: 'Offline',
  };

  return (
    <aside className="w-64 bg-white text-gray-900 h-screen flex flex-col border-r border-gray-200 shadow-sm">
      {/* Header with Guard SVG */}
      <div className="p-6 border-b border-gray-200">
        <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-all group">
          <div className="w-10 h-10 bg-black rounded-xl flex items-center justify-center shadow-lg shadow-blue-200 group-hover:scale-105 transition-transform">
            <svg 
              className="w-6 h-6 text-white" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24" 
              xmlns="http://www.w3.org/2000/svg"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" 
              />
            </svg>
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-lg leading-tight">Sentinel</span>
            <span className="text-[10px] text-blue-600 font-bold uppercase tracking-widest">ACS Platform</span>
          </div>
        </Link>
      </div>

      {/* Health Status */}
      <div className="p-6 border-b border-gray-200">
        <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">
          System Health
        </div>
        <div className="flex items-center gap-3 bg-gray-50 p-3 rounded-xl border border-gray-100">
          <div className={`w-2.5 h-2.5 rounded-full animate-pulse ${healthColor[sentinelHealth]}`} />
          <span className="text-sm font-bold text-gray-700">{healthLabel[sentinelHealth]}</span>
        </div>
        {sentinelHealth === 'healing' && (
          <p className="text-[10px] text-amber-600 mt-2 font-bold animate-bounce text-center">
            AI PATROL ACTIVE
          </p>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        <Link
          href="/"
          className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-blue-50 hover:text-blue-600 transition-all text-sm font-semibold text-gray-600"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <span>Payment Hub</span>
        </Link>
        <Link
          href="/dashboard"
          className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-blue-50 hover:text-blue-600 transition-all text-sm font-semibold text-gray-600"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span>Analytics</span>
        </Link>
      </nav>

      {/* Transaction Count */}
      <div className="p-6 border-t border-gray-100 bg-gray-50/50">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1">
            Live Records
          </div>
          <div className="text-2xl font-black text-gray-900">
            {transactions.length.toString().padStart(2, '0')}
          </div>
        </div>
      </div>
    </aside>
  );
}