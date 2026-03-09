'use client';

import { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { usePaymentStore } from '@/src/store/paymentStore';
import { apiClient } from '@/src/lib/api';
import { toast } from 'sonner';

export function PaymentForm() {
  const [amount, setAmount] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  
  const addTransaction = usePaymentStore((state) => state.addTransaction);
  const updateTransactionState = usePaymentStore((state) => state.updateTransactionState);
  
  const pollingIntervals = useRef<{ [key: string]: NodeJS.Timeout }>({});

  useEffect(() => {
    return () => {
      Object.values(pollingIntervals.current).forEach(clearInterval);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!amount || parseFloat(amount) <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    setIsSubmitting(true);
    const idempotencyKey = uuidv4();

    try {

      const response = await apiClient.startPayment({
        amount: parseFloat(amount),
        idempotencyKey,
      });

      addTransaction(response.id, idempotencyKey, parseFloat(amount));
      toast.success(`Payment initiated: ${response.id}`);
      setAmount('');

      const intervalId = setInterval(async () => {
        try {
          const status = await apiClient.getPaymentStatus(response.id);
          
          if (status.sql_validated && status.status === 'validated') {
            updateTransactionState(response.id, 'validated', 'Passed Risk Guard');
          }
          
          if (status.blockchain_mined && status.status === 'finalized') {
            updateTransactionState(response.id, 'finalized', 'Mined on Blockchain');
            clearInterval(pollingIntervals.current[response.id]);
          }

          // If the backend returns an error field
          if (status.error) {
            updateTransactionState(response.id, 'failed', status.error);
            clearInterval(pollingIntervals.current[response.id]);
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 2000);

      pollingIntervals.current[response.id] = intervalId;

    } catch (err) {
      const message = err instanceof Error ? err.message : 'Payment failed';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Process Payment</h2>
        <p className="text-sm text-gray-500 mt-1">
          Secure payment with idempotency protection
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
            Amount (INR)
          </label>
          <div className="relative">
            <span className="absolute left-4 top-3.5 text-gray-400 font-medium">₹</span>
            <input
              type="number"
              id="amount"
              placeholder="0.00"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              disabled={isSubmitting}
              className="w-full pl-8 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all disabled:bg-gray-50"
            />
          </div>
        </div>

        <div className="bg-blue-50/50 rounded-xl p-4 border border-blue-100">
          <p className="text-xs font-semibold text-blue-600 uppercase tracking-wider mb-2">Core Features</p>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-center gap-2">
              <div className="w-1 h-1 bg-blue-500 rounded-full" /> Idempotency Protection
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1 h-1 bg-blue-500 rounded-full" /> Real-time status tracking
            </li>
          </ul>
        </div>

        <button
          type="submit"
          disabled={isSubmitting || !amount}
          className="w-full py-4 bg-black hover:bg-gray-800 text-white rounded-xl font-bold transition-all shadow-md active:scale-[0.98] disabled:bg-gray-200 disabled:text-gray-400 disabled:shadow-none"
        >
          {isSubmitting ? (
            <div className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Verifying...
            </div>
          ) : (
            'Complete Transaction'
          )}
        </button>
      </form>
    </div>
  );
}