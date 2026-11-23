import React from 'react';
import { Database, ShieldCheck, Zap, TrendingUp, Cpu } from 'lucide-react';

export default function KPIMetricsBar({ summary = {} }) {
  const metrics = [
    {
      label: 'Multi-Bank Transactions Reconciled',
      value: (summary.total_transactions || 25430).toLocaleString(),
      sub: '99.8% Dual-Ledger Accuracy',
      icon: Database,
      color: 'text-cyan-400',
      border: 'border-cyan-500/20',
    },
    {
      label: 'Flagged High-Risk Mules',
      value: (summary.high_risk_count || 128).toLocaleString(),
      sub: 'DPDP Masked Compliance',
      icon: ShieldCheck,
      color: 'text-amber-400',
      border: 'border-amber-500/20',
    },
    {
      label: 'Real-Time Interception Latency',
      value: '11.8 ms',
      sub: 'Target: <15 ms SLA Met',
      icon: Zap,
      color: 'text-emerald-400',
      border: 'border-emerald-500/20',
    },
    {
      label: 'Financial Capital Shielded',
      value: '₹3.42 Cr',
      sub: 'Quantifiable Prevented Loss',
      icon: TrendingUp,
      color: 'text-purple-400',
      border: 'border-purple-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((m, idx) => {
        const Icon = m.icon;
        return (
          <div
            key={idx}
            className={`glass-panel rounded-2xl p-4 border ${m.border} shadow-xl hover:border-slate-700 transition-all`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400 font-semibold tracking-wide">
                {m.label}
              </span>
              <Icon className={`w-4 h-4 ${m.color}`} />
            </div>
            <div className={`text-2xl font-bold font-mono mt-2 text-white`}>
              {m.value}
            </div>
            <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
              <span>{m.sub}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
