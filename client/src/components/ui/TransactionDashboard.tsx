'use client';

import { usePaymentStore, TransactionState, Transaction } from '@/src/store/paymentStore';
import { HealthPulse } from './HealthPulse';
import { useEffect, useState } from 'react';
import { apiClient, SentinelHealth } from '@/src/lib/api';

export function TransactionDashboard() {
  // Store state and actions
  const transactions = usePaymentStore((state) => state.transactions);
  const setTransactions = usePaymentStore((state) => state.setTransactions);
  const updateTransactionState = usePaymentStore((state) => state.updateTransactionState);
  const setSentinelHealth = usePaymentStore((state) => state.setSentinelHealth);
  
  const [health, setHealth] = useState<SentinelHealth | null>(null);
  const [loadingHistory, setLoadingHistory] = useState(true);

  // 1. Initial History Loader - Matches Backend snake_case
  useEffect(() => {
    const initHistory = async () => {
      try {
        const data = await apiClient.getPayments(1);
        const mappedData: Transaction[] = data.map(tx => ({
          id: tx.id,
          idempotencyKey: tx.id, 
          amount: tx.amount ?? 0,
          // Use backend timestamp if available, else current time
          timestamp: tx.created_at || new Date().toISOString(), 
          state: (tx.status as TransactionState) || 'pending',
          status: tx.status === 'finalized' ? 'Success: Mined' : 
                  tx.status === 'validated' ? 'SQL Verified' : 'Processing'
        }));
        setTransactions(mappedData);
      } catch (err) {
        console.error("Failed to load history", err);
      } finally {
        setLoadingHistory(false);
      }
    };
    initHistory();
  }, [setTransactions]);

  // 2. Adaptive Polling Logic - Handles 404s gracefully during DB propagation
  useEffect(() => {
  const pollActiveTransactions = async () => {
  const activeTxs = transactions.filter(tx => tx.state === 'pending' || tx.state === 'validated');
  
  for (const tx of activeTxs) {
    try {
      const latest = await apiClient.getPaymentStatus(tx.id);
      updateTransactionState(
        tx.id, 
        latest.status as TransactionState, 
        latest.status === 'finalized' ? 'Success: Mined' : 'Processing...'
      );
    } catch (err: any) {
      // Defensive: Ignore 404s while DB propagates
      if (err.message?.includes('404')) {
        console.log(`Still propagating ${tx.id}...`);
      } else {
        console.error("Critical connection failure", err);
      }
    }
  }
};

    const interval = setInterval(pollActiveTransactions, 3000); // Poll every 3 seconds
    return () => clearInterval(interval);
  }, [transactions, updateTransactionState]);

  // 3. Health Monitoring
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await apiClient.getSentinelHealth();
        setHealth(data);
        setSentinelHealth(data?.status || 'offline');
      } catch (err) {
        setSentinelHealth('offline');
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, [setSentinelHealth]);

  const stateConfig: Record<TransactionState, { color: string; bgColor: string; label: string }> = {
    pending: { color: 'text-blue-700', bgColor: 'bg-blue-100', label: 'Pending' },
    validated: { color: 'text-amber-700', bgColor: 'bg-amber-100', label: 'Validated' },
    finalized: { color: 'text-green-700', bgColor: 'bg-green-100', label: 'Finalized' },
    failed: { color: 'text-red-700', bgColor: 'bg-red-100', label: 'Failed' },
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="space-y-6">
      <HealthPulse />

      {/* Health Stats Grid */}
      {health && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard 
            label="CPU Usage" 
            value={`${(health.cpu ?? 0).toFixed(1)}%`} 
            progress={health.cpu ?? 0} 
            color="bg-gray-600" 
          />
          <StatCard 
            label="RAM Usage" 
            value={`${(health.ram ?? 0).toFixed(1)}%`} 
            progress={health.ram ?? 0} 
            color="bg-purple-600" 
          />
          <StatCard 
            label="Anomaly Score" 
            value={(health.anomalyScore ?? 0).toFixed(2)} 
            progress={(health.anomalyScore ?? 0) * 100} 
            color={(health.anomalyScore ?? 0) > 0.7 ? 'bg-red-600' : (health.anomalyScore ?? 0) > 0.4 ? 'bg-yellow-500' : 'bg-green-500'} 
          />
        </div>
      )}

      {/* Transactions Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100 flex justify-between items-center">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Live Transaction Feed</h2>
            <p className="text-xs text-gray-500">Real-time lifecycle monitoring</p>
          </div>
        </div>

        {transactions.length === 0 ? (
          <div className="px-6 py-20 text-center text-gray-500 text-sm">
            Waiting for new transactions...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50/50 text-gray-600 font-semibold border-b border-gray-100">
                <tr>
                  <th className="px-6 py-4 text-left">Timestamp</th>
                  <th className="px-6 py-4 text-left">Amount</th>
                  <th className="px-6 py-4 text-left">Lifecycle State</th>
                  <th className="px-6 py-4 text-left">Detailed Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {transactions.map((tx) => {
                  const config = stateConfig[tx.state] || stateConfig.pending;
                  return (
                    <tr key={tx.id} className="hover:bg-blue-50/30 transition-colors">
                      <td className="px-6 py-4 text-gray-500 font-mono text-xs">{formatDate(tx.timestamp)}</td>
                      <td className="px-6 py-4 font-bold text-gray-900">₹{(tx.amount ?? 0).toFixed(2)}</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${config.bgColor} ${config.color}`}>
                          {config.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-600 italic text-xs">{tx.status}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, progress, color }: { label: string, value: string, progress: number, color: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <p className="text-[10px] uppercase tracking-widest text-gray-400 font-bold mb-1">{label}</p>
      <p className="text-2xl font-black text-gray-900 mb-3">{value}</p>
      <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
        <div className={`${color} h-full transition-all duration-1000`} style={{ width: `${Math.min(progress, 100)}%` }} />
      </div>
    </div>
  );
}