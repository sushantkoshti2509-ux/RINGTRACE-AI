import React from 'react';
import { BarChart3, Lightbulb, Zap, ShieldCheck, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function KPIMetricsBar({ summary = {} }) {
  const cards = [
    {
      label: 'NEW ACCOUNTS / RECONCILED',
      value: (summary.total_transactions || 46380).toLocaleString(),
      badgeIcon: BarChart3,
      badgeColor: 'text-emerald-600',
      trend: '↑ 15.4% increase this month',
      trendColor: 'text-emerald-400',
      bgClass: 'bg-gradient-to-br from-[#1e3a8a] to-[#1e40af] text-white',
      labelColor: 'text-blue-100 font-extrabold',
    },
    {
      label: 'FLAGGED HIGH-RISK MULES',
      value: (summary.high_risk_count || 128).toLocaleString(),
      badgeIcon: Lightbulb,
      badgeColor: 'text-blue-600',
      trend: '↑ 7.4% same as before',
      trendColor: 'text-blue-200',
      bgClass: 'bg-gradient-to-r from-[#1e2d42] to-[#14233a] text-white',
      labelColor: 'text-slate-200 font-extrabold',
    },
    {
      label: 'INTERCEPTION LATENCY',
      value: '11.4 ms',
      badgeIcon: Zap,
      badgeColor: 'text-indigo-600',
      trend: '↓ 15.4% less latency',
      trendColor: 'text-indigo-100',
      bgClass: 'bg-gradient-to-r from-[#4f46e5] to-[#6366f1] text-white',
      labelColor: 'text-indigo-100 font-extrabold',
    },
    {
      label: 'FINANCIAL CAPITAL SHIELDED',
      value: '₹3.42 Cr',
      badgeIcon: ShieldCheck,
      badgeColor: 'text-teal-600',
      trend: '↑ 24.1% prevented loss',
      trendColor: 'text-teal-100',
      bgClass: 'bg-gradient-to-r from-[#0d9488] to-[#059669] text-white',
      labelColor: 'text-teal-100 font-extrabold',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((c, idx) => {
        const Icon = c.badgeIcon;
        return (
          <div
            key={idx}
            className={`rounded-2xl p-5 shadow-sm transition-all hover:shadow-md flex flex-col justify-between ${c.bgClass}`}
          >
            <div className="flex items-start justify-between">
              <div>
                <span className={`text-xs font-extrabold tracking-wider uppercase block ${c.labelColor}`}>
                  {c.label}
                </span>
                <div className="text-3xl md:text-4xl font-extrabold font-mono mt-2 tracking-tight">
                  {c.value}
                </div>
              </div>
              <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center shadow-sm shrink-0">
                <Icon className={`w-5 h-5 ${c.badgeColor}`} />
              </div>
            </div>

            <div className={`text-xs font-bold mt-4 flex items-center gap-1 ${c.trendColor}`}>
              <span>{c.trend}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
