import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api';
import { Bell, AlertTriangle, ShieldCheck, CheckCircle2, Clock, Filter, Eye, RefreshCw, X } from 'lucide-react';

export default function AlertsView() {
  const [alerts, setAlerts] = useState([]);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [statusNote, setStatusNote] = useState('');

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      let url = '/api/v1/alerts?limit=50';
      if (statusFilter !== 'ALL') url += `&status=${statusFilter}`;
      const res = await apiFetch(url);
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
      const res = await apiFetch(`/api/v1/alerts/${alertId}/status`, {
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
      {/* Top Header Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 shrink-0">
            <Bell className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-extrabold text-slate-900 tracking-tight">
                Fraud Alert & Incident Notification Dispatch
              </h2>
              <span className="bg-blue-50 text-blue-700 border border-blue-200 font-extrabold text-[10px] px-2 py-0.5 rounded-full font-mono">
                DISPATCH QUEUE
              </span>
            </div>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Real-time multi-bank alert queue with investigator audit workflows and status transitions
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-xs font-bold text-slate-900 focus:outline-none focus:border-blue-600 shadow-xs cursor-pointer"
          >
            <option value="ALL">All Alert Statuses</option>
            <option value="NEW">NEW (Unreviewed)</option>
            <option value="IN_REVIEW">IN_REVIEW</option>
            <option value="RESOLVED">RESOLVED</option>
          </select>

          <button
            onClick={fetchAlerts}
            disabled={isLoading}
            className="px-4 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 hover:text-slate-900 text-xs font-extrabold border border-slate-300 shadow-xs flex items-center gap-1.5 transition-all cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Alert Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {alerts.length === 0 ? (
          <div className="col-span-full py-16 text-center text-xs text-slate-500 font-semibold">
            {isLoading ? 'Loading active alert stream...' : 'No fraud alerts match the filter.'}
          </div>
        ) : (
          alerts.map((alt, idx) => (
            <div
              key={alt.alert_id || idx}
              onClick={() => setSelectedAlert(alt)}
              className="bg-white rounded-2xl p-5 border border-slate-200/90 hover:border-blue-300 hover:shadow-md shadow-sm transition-all cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-extrabold text-blue-700 text-xs">
                    {alt.alert_id || `ALT-${idx + 101}`}
                  </span>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider ${
                    alt.status === 'RESOLVED' 
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-300' 
                      : 'bg-rose-50 text-rose-800 border border-rose-300'
                  }`}>
                    {alt.status || 'NEW'}
                  </span>
                </div>

                <div className="text-slate-900 font-mono font-extrabold text-lg mt-1">
                  ₹{(alt.amount || 185000).toLocaleString()}
                </div>

                <div className="text-xs text-slate-700 mt-2 space-y-1.5 font-medium">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Source:</span>
                    <span className="font-mono font-bold text-slate-900">{alt.masked_account || '••••0099'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Risk Score:</span>
                    <span className="font-mono text-rose-600 font-extrabold">{Math.round((alt.composite_score || 0.88) * 100)}%</span>
                  </div>
                </div>

                <div className="mt-3 pt-2.5 border-t border-slate-100 text-[11px] text-slate-600 font-medium truncate">
                  {alt.reasons?.[0] || 'Multi-bank rapid pass-through & velocity anomaly'}
                </div>
              </div>

              <div className="mt-4 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-500">
                <span className="font-mono font-semibold">{alt.timestamp ? new Date(alt.timestamp).toLocaleTimeString() : 'Recent'}</span>
                <span className="text-blue-700 hover:text-blue-800 flex items-center gap-1 font-bold">
                  Triage Alert <Eye className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Alert Triage Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 border border-slate-200 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-extrabold text-slate-900 font-mono">
                  Triage Alert: {selectedAlert.alert_id}
                </h3>
                <span className="text-xs text-slate-600 font-medium">Investigator Disposition & Action Workflow</span>
              </div>
              <button
                onClick={() => setSelectedAlert(null)}
                className="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 flex items-center justify-center transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3.5 text-xs">
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex justify-between items-center">
                <span className="text-slate-600 font-semibold">Transaction Amount</span>
                <span className="font-extrabold text-slate-900 font-mono text-base">₹{(selectedAlert.amount || 0).toLocaleString()}</span>
              </div>

              <div>
                <label className="block text-slate-700 font-extrabold mb-1.5">Investigator Action Notes</label>
                <textarea
                  rows="3"
                  placeholder="Record findings, counterparty bank feedback, or case disposition..."
                  value={statusNote}
                  onChange={(e) => setStatusNote(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl p-3 text-xs text-slate-900 font-medium focus:outline-none focus:border-blue-600 shadow-xs"
                />
              </div>

              <div className="flex flex-wrap items-center gap-2 pt-2">
                <button
                  onClick={() => updateAlertStatus(selectedAlert.alert_id, 'IN_REVIEW')}
                  className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-extrabold text-xs shadow-xs cursor-pointer"
                >
                  Mark In Review
                </button>
                <button
                  onClick={() => updateAlertStatus(selectedAlert.alert_id, 'RESOLVED')}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs shadow-xs cursor-pointer"
                >
                  Mark Resolved / Intercepted
                </button>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs ml-auto cursor-pointer"
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
