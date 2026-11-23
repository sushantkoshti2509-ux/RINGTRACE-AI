import React, { useState, useEffect } from 'react';
import { Bell, AlertTriangle, ShieldCheck, CheckCircle2, Clock, Filter, Eye, RefreshCw } from 'lucide-react';

export default function AlertsView() {
  const [alerts, setAlerts] = useState([]);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [statusNote, setStatusNote] = useState('');

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      let url = '/api/v1/alerts/?limit=50';
      if (statusFilter !== 'ALL') url += `&status=${statusFilter}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setAlerts(data.alerts || data || []);
      }
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter]);

  const updateAlertStatus = async (alertId, newStatus) => {
    try {
      const res = await fetch(`/api/v1/alerts/${alertId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          notes: statusNote || `Investigator marked status as ${newStatus}`,
        }),
      });
      if (res.ok) {
        fetchAlerts();
        setSelectedAlert(null);
        setStatusNote('');
      }
    } catch (err) {
      console.error('Failed to update alert:', err);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Title & Filter Bar */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Bell className="w-5 h-5 text-rose-500 animate-pulse" />
            <span>Fraud Alert & Incident Notification Dispatch</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time multi-bank alert queue with investigator audit workflows and status transitions
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-400"
          >
            <option value="ALL">All Alert Statuses</option>
            <option value="NEW">NEW (Unreviewed)</option>
            <option value="IN_REVIEW">IN_REVIEW</option>
            <option value="RESOLVED">RESOLVED</option>
          </select>

          <button
            onClick={fetchAlerts}
            disabled={isLoading}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Alert Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {alerts.length === 0 ? (
          <div className="col-span-full py-16 text-center text-xs text-slate-400">
            {isLoading ? 'Loading active alert stream...' : 'No fraud alerts match the filter.'}
          </div>
        ) : (
          alerts.map((alt, idx) => (
            <div
              key={alt.alert_id || idx}
              onClick={() => setSelectedAlert(alt)}
              className="glass-panel rounded-2xl p-4 border border-slate-800 hover:border-cyan-500/50 shadow-xl transition-all cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-bold text-cyan-300 text-xs">
                    {alt.alert_id || `ALT-${idx + 101}`}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                    alt.status === 'RESOLVED' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                  }`}>
                    {alt.status || 'NEW'}
                  </span>
                </div>

                <div className="text-white font-mono font-bold text-base mt-1">
                  ₹{(alt.amount || 185000).toLocaleString()}
                </div>

                <div className="text-xs text-slate-300 mt-2 space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Source:</span>
                    <span className="font-mono text-cyan-200">{alt.masked_account || '••••0099'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Risk Score:</span>
                    <span className="font-mono text-rose-400 font-bold">{Math.round((alt.composite_score || 0.88) * 100)}%</span>
                  </div>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-800 text-[11px] text-slate-400 truncate">
                  {alt.reasons?.[0] || 'Multi-bank rapid pass-through & velocity anomaly'}
                </div>
              </div>

              <div className="mt-4 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500">
                <span className="font-mono">{alt.timestamp ? new Date(alt.timestamp).toLocaleTimeString() : 'Recent'}</span>
                <span className="text-cyan-400 hover:underline flex items-center gap-1 font-semibold">
                  Triage Alert <Eye className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Alert Triage Drawer / Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel rounded-2xl max-w-lg w-full p-6 border border-slate-700 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white font-mono">
                  Triage Alert: {selectedAlert.alert_id}
                </h3>
                <span className="text-xs text-slate-400">Investigator Disposition & Action Workflow</span>
              </div>
              <button
                onClick={() => setSelectedAlert(null)}
                className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex justify-between">
                <span className="text-slate-400">Transaction Amount</span>
                <span className="font-bold text-white font-mono">₹{(selectedAlert.amount || 0).toLocaleString()}</span>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Investigator Action Notes</label>
                <textarea
                  rows="3"
                  placeholder="Record findings, counterparty bank feedback, or case disposition..."
                  value={statusNote}
                  onChange={(e) => setStatusNote(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-cyan-400"
                />
              </div>

              <div className="flex flex-wrap items-center gap-2 pt-2">
                <button
                  onClick={() => updateAlertStatus(selectedAlert.alert_id, 'IN_REVIEW')}
                  className="px-3 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs"
                >
                  Mark In Review
                </button>
                <button
                  onClick={() => updateAlertStatus(selectedAlert.alert_id, 'RESOLVED')}
                  className="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs"
                >
                  Mark Resolved / Intercepted
                </button>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="px-3 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs ml-auto"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
