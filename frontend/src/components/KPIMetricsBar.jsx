import React from 'react';
import { BarChart3, AlertOctagon, Zap, ShieldCheck } from 'lucide-react';

export default function KPIMetricsBar({ summary = {} }) {
  const cards = [
    {
      label: 'NEW ACCOUNTS / RECONCILED',
      value: (summary.total_transactions || 46380).toLocaleString(),
      badgeIcon: BarChart3,
      iconColor: 'text-blue-600',
      iconBg: 'bg-blue-50 border border-blue-200',
      trend: '↑ 15.4% increase this month',
      trendColor: 'text-emerald-700 font-bold',
    },
    {
      label: 'FLAGGED HIGH-RISK MULES',
      value: (summary.high_risk_count || 128).toLocaleString(),
      badgeIcon: AlertOctagon,
      iconColor: 'text-rose-600',
      iconBg: 'bg-rose-50 border border-rose-200',
      trend: '↑ 7.4% same as before',
      trendColor: 'text-rose-700 font-bold',
    },
    {
      label: 'INTERCEPTION LATENCY',
      value: '11.4 ms',
      badgeIcon: Zap,
      iconColor: 'text-indigo-600',
      iconBg: 'bg-indigo-50 border border-indigo-200',
      trend: '↓ 15.4% less latency',
      trendColor: 'text-indigo-700 font-bold',
    },
    {
      label: 'FINANCIAL CAPITAL SHIELDED',
      value: '₹3.42 Cr',
      badgeIcon: ShieldCheck,
      iconColor: 'text-emerald-600',
      iconBg: 'bg-emerald-50 border border-emerald-200',
      trend: '↑ 24.1% prevented loss',
      trendColor: 'text-emerald-700 font-bold',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((c, idx) => {
        const Icon = c.badgeIcon;
        return (
          <div
            key={idx}
            className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm transition-all hover:shadow-md flex flex-col justify-between"
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-extrabold tracking-wider uppercase block text-slate-500">
                  {c.label}
                </span>
                <div className="text-3xl md:text-4xl font-extrabold font-mono text-slate-900 mt-2 tracking-tight">
                  {c.value}
                </div>
              </div>
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-xs shrink-0 ${c.iconBg}`}>
                <Icon className={`w-5 h-5 ${c.iconColor}`} />
              </div>
            </div>

            <div className={`text-xs mt-4 flex items-center gap-1 ${c.trendColor}`}>
              <span>{c.trend}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
