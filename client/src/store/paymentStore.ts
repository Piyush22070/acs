import { create } from 'zustand';

export type TransactionState = 'pending' | 'validated' | 'finalized' | 'failed';

export interface Transaction {
  id: string; 
  idempotencyKey: string;
  amount: number;
  timestamp: string;
  state: TransactionState;
  status: string;
}

interface PaymentStore {
  transactions: Transaction[];
  sentinelHealth: 'healthy' | 'healing' | 'offline';
  isProcessing: boolean;
  error: string | null;
  
  // Actions
  addTransaction: (id: string, idempotencyKey: string, amount: number) => void;
  setTransactions: (transactions: Transaction[], append?: boolean) => void;
  updateTransactionState: (id: string, state: TransactionState, status: string) => void;
  setSentinelHealth: (health: 'healthy' | 'healing' | 'offline') => void;
  setProcessing: (processing: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  getTransaction: (id: string) => Transaction | undefined;
}

export const usePaymentStore = create<PaymentStore>((set, get) => ({
  transactions: [],
  sentinelHealth: 'healthy',
  isProcessing: false,
  error: null,

  addTransaction: (id, idempotencyKey, amount) => {
    if (get().transactions.some(tx => tx.id === id)) return;

    const transaction: Transaction = {
      id,
      idempotencyKey,
      amount,
      timestamp: new Date().toISOString(),
      state: 'pending',
      status: 'Relay Started',
    };

    set((state) => ({
      transactions: [transaction, ...state.transactions],
    }));
  },

  setTransactions: (newTransactions, append = false) => {
    set((state) => ({
      transactions: append 
        ? [...state.transactions, ...newTransactions] 
        : newTransactions,
    }));
  },

  updateTransactionState: (id, state, status) => {
  set((prevState) => ({
    transactions: prevState.transactions.map((tx) =>
      tx.id === id ? { ...tx, state, status } : tx
    ),
  }));
},

  setSentinelHealth: (health) => set({ sentinelHealth: health }),
  setProcessing: (processing) => set({ isProcessing: processing }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
  getTransaction: (id) => get().transactions.find((tx) => tx.id === id),
}));