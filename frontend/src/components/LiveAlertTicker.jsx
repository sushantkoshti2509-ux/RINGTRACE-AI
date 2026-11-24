import React from 'react';
import { AlertCircle, Clock, CheckCircle2, Shield, ArrowUpRight } from 'lucide-react';

export default function LiveAlertTicker({ alerts = [], onSelectAlert = () => {} }) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col h-[460px]">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3">
        <div className="flex items-center gap-2.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
          <h4 className="text-xs uppercase font-extrabold tracking-wider text-slate-900">
            Real-Time Fraud Alert Feed
          </h4>
        </div>
        <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-800 border border-rose-300 font-bold">
          Sub-15ms Scoring Active
        </span>
      </div>

      {/* Alert List */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
        {alerts.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-400 text-xs">
            <Shield className="w-8 h-8 text-blue-500 mb-2 animate-pulse" />
            <span className="font-semibold text-slate-500">Streaming multi-bank transaction telemetry...</span>
          </div>
        ) : (
          alerts.map((alert, idx) => (
            <div
              key={alert.alert_id || idx}
              onClick={() => onSelectAlert(alert)}
              className="p-3.5 rounded-xl bg-slate-50 hover:bg-blue-50/60 border border-slate-200 hover:border-blue-300 transition-all cursor-pointer group shadow-xs"
            >
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-mono font-extrabold text-blue-700 text-xs group-hover:text-blue-900 transition-colors">
                  {alert.alert_id || `ALT-${idx + 101}`}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-rose-50 text-rose-800 border border-rose-300">
                  Risk: {Math.round((alert.composite_score || 0.88) * 100)}%
                </span>
              </div>

              <div className="text-xs text-slate-700 flex items-center justify-between font-medium">
                <div>
                  <span className="text-slate-500">Account: </span>
                  <span className="font-mono font-bold text-slate-900">{alert.masked_account || '••••0099'}</span>
                </div>
                <div className="font-mono font-extrabold text-slate-900 text-sm">
                  ₹{(alert.amount || 185000).toLocaleString()}
                </div>
              </div>

              <div className="mt-2 pt-2 border-t border-slate-200/80 flex items-center justify-between text-[10px] text-slate-500">
                <span className="truncate max-w-[180px] font-medium text-slate-600">
                  {alert.reasons?.[0] || 'Rapid cross-bank dispersion & velocity spike'}
                </span>
                <span className="font-mono font-semibold text-slate-500 shrink-0">
                  {alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : 'Just now'}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
