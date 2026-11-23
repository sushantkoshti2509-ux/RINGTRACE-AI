import React from 'react';
import { AlertCircle, Clock, CheckCircle2, Shield, ArrowUpRight } from 'lucide-react';

export default function LiveAlertTicker({ alerts = [], onSelectAlert = () => {} }) {
  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-2xl flex flex-col h-[460px]">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-3">
        <div className="flex items-center gap-2.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
          <h4 className="text-xs uppercase font-bold tracking-wider text-slate-200">
            Real-Time Fraud Alert Feed
          </h4>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/30">
          Sub-15ms Scoring Active
        </span>
      </div>

      {/* Alert List */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
        {alerts.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-400 text-xs">
            <Shield className="w-8 h-8 text-slate-600 mb-2 animate-pulse" />
            <span>Streaming multi-bank transaction telemetry...</span>
          </div>
        ) : (
          alerts.map((alert, idx) => (
            <div
              key={alert.alert_id || idx}
              onClick={() => onSelectAlert(alert)}
              className="p-3 rounded-xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-cyan-500/40 transition-all cursor-pointer group shadow-sm"
            >
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-mono font-bold text-white text-[11px] group-hover:text-cyan-300 transition-colors">
                  {alert.alert_id || `ALT-${idx + 101}`}
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950/80 text-rose-300 border border-rose-700/50">
                  Risk: {Math.round((alert.composite_score || 0.88) * 100)}%
                </span>
              </div>

              <div className="text-xs text-slate-300 flex items-center justify-between">
                <div>
                  <span className="text-slate-400">Account: </span>
                  <span className="font-mono text-cyan-200">{alert.masked_account || '••••0099'}</span>
                </div>
                <div className="font-mono font-bold text-white">
                  ₹{(alert.amount || 185000).toLocaleString()}
                </div>
              </div>

              <div className="mt-2 pt-1.5 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400">
                <span className="truncate max-w-[180px]">
                  {alert.reasons?.[0] || 'Rapid cross-bank dispersion & velocity spike'}
                </span>
                <span className="font-mono text-slate-400 shrink-0">
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
