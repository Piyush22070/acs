'use client';

import { usePaymentStore } from '@/src/store/paymentStore';

export function HealthPulse() {
  const sentinelHealth = usePaymentStore((state) => state.sentinelHealth);

  const healthConfig = {
    healthy: {
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-800',
      dotColor: 'bg-green-500',
      label: 'Sentinel Active',
      description: 'All systems operational',
    },
    healing: {
      bgColor: 'bg-amber-50',
      borderColor: 'border-amber-200',
      textColor: 'text-amber-800',
      dotColor: 'bg-amber-500',
      label: 'System Self-Healing',
      description: 'Repairing cluster automatically',
    },
    offline: {
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-800',
      dotColor: 'bg-red-500',
      label: 'Sentinel Offline',
      description: 'Connection lost',
    },
  };

  const config = healthConfig[sentinelHealth];

  return (
    <div className={`${config.bgColor} border ${config.borderColor} rounded-lg p-4`}>
      <div className="flex items-start gap-3">
        <div className={`relative w-4 h-4 ${config.dotColor} rounded-full mt-0.5 shrink-0`}>
          {sentinelHealth !== 'offline' && (
            <div
              className={`absolute inset-0 ${config.dotColor} rounded-full animate-ping opacity-75`}
            />
          )}
        </div>
        <div className="flex-1">
          <p className={`text-sm font-semibold ${config.textColor}`}>
            {config.label}
          </p>
          <p className={`text-xs ${config.textColor} opacity-75 mt-0.5`}>
            {config.description}
          </p>
        </div>
      </div>
    </div>
  );
}
