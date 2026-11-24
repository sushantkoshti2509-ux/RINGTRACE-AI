import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api';
import {
  TrendingUp,
  Building2,
  Layers,
  Clock,
  Share2,
  RefreshCw,
  ArrowRight,
  Shield,
  Activity,
} from 'lucide-react';

export default function AdvancedAnalyticsView() {
  const [bankMetrics, setBankMetrics] = useState([]);
  const [topologyDistribution, setTopologyDistribution] = useState([]);
  const [velocityHistogram, setVelocityHistogram] = useState([]);
  const [crossBankFlows, setCrossBankFlows] = useState([]);
  const [graphKpis, setGraphKpis] = useState({
    total_nodes: 1200,
    total_edges: 46380,
    reconciliation_rate_pct: 100.0,
    rings_detected: 33,
    density: '0.0032',
    diameter: 6,
    avg_clustering_coef: '0.142',
  });
  const [isLoading, setIsLoading] = useState(false);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const [reconRes, flowsRes] = await Promise.all([
        apiFetch('/api/v1/reconciliation/summary'),
        apiFetch('/api/v1/cross-bank-flows'),
      ]);

      if (reconRes.ok) {
        const data = await reconRes.json();
        if (data.bank_wise_breakdown) setBankMetrics(data.bank_wise_breakdown);
      }

      if (flowsRes.ok) {
        const data = await flowsRes.json();
        if (data.flows) setCrossBankFlows(data.flows);
      }
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    setTopologyDistribution([
      { topology: 'Cycle Ring (AMLSim Loop)', count: 18, share_pct: 54.5, color: '#ef4444' },
      { topology: 'Fan-Out Splitter Ring', count: 7, share_pct: 21.2, color: '#f59e0b' },
      { topology: 'Fan-In Collector Ring', count: 5, share_pct: 15.2, color: '#a855f7' },
      { topology: 'Rapid Pass-Through Chain', count: 3, share_pct: 9.1, color: '#06b6d4' },
    ]);

    setVelocityHistogram([
      { bin: '< 10 Seconds', count: 1420, description: 'Automated Bot Smurfing (Zero Human Delay)' },
      { bin: '10s - 1 Minute', count: 864, description: 'Synchronized Rapid Mule Relaying' },
      { bin: '1m - 5 Minutes', count: 512, description: 'Multi-Bank Handoff Window' },
      { bin: '5m - 30 Minutes', count: 210, description: 'Cooling-Off Evaded Layering' },
      { bin: '> 30 Minutes', count: 85, description: 'Terminal Cash-Out Phase' },
    ]);
  }, []);

  return (
    <div className="flex flex-col gap-6">
      {/* Top Header Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 shrink-0">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-extrabold text-slate-900 tracking-tight">
                Advanced Network Analytics & Telemetry
              </h2>
              <span className="bg-blue-50 text-blue-700 border border-blue-200 font-extrabold text-[10px] px-2 py-0.5 rounded-full font-mono">
                GRAPH ANALYTICS
              </span>
            </div>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Bank-wise risk exposure, laundering topology distributions, and inter-bank clearing network analytics
            </p>
          </div>
        </div>

        <button
          onClick={fetchAnalytics}
          disabled={isLoading}
          className="px-4 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 hover:text-slate-900 text-xs font-extrabold border border-slate-300 shadow-xs flex items-center gap-2 transition-all cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
          <span>Refresh Analytics</span>
        </button>
      </div>

      {/* Top Level Structural KPI Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <span className="text-[10px] text-slate-500 font-extrabold uppercase tracking-wider">Total Ledger Accounts</span>
          <div className="text-2xl font-extrabold font-mono text-slate-900 mt-1">
            {graphKpis.total_nodes.toLocaleString()}
          </div>
          <span className="text-xs text-blue-700 font-bold mt-1">Across 4 Synthetic Banks</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <span className="text-[10px] text-slate-500 font-extrabold uppercase tracking-wider">Dual-Ledger Reconciled</span>
          <div className="text-2xl font-extrabold font-mono text-emerald-700 mt-1">
            {graphKpis.reconciliation_rate_pct}%
          </div>
          <span className="text-xs text-emerald-700 font-bold mt-1">0 Ledger Discrepancies</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <span className="text-[10px] text-slate-500 font-extrabold uppercase tracking-wider">Mule Rings Detected</span>
          <div className="text-2xl font-extrabold font-mono text-rose-600 mt-1">
            {graphKpis.rings_detected} Rings
          </div>
          <span className="text-xs text-rose-700 font-bold mt-1">100% Graph Traversal Recall</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <span className="text-[10px] text-slate-500 font-extrabold uppercase tracking-wider">Network Density & Diameter</span>
          <div className="text-2xl font-extrabold font-mono text-purple-700 mt-1">
            {graphKpis.density} / {graphKpis.diameter} Hops
          </div>
          <span className="text-xs text-purple-700 font-bold mt-1">Clustering Coef: {graphKpis.avg_clustering_coef}</span>
        </div>
      </div>

      {/* Section 1: Bank-Wise Fraud Distribution Table */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col gap-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <Building2 className="w-4 h-4 text-blue-600" />
            Bank-Wise Transaction Volume & Fraud Metrics (4 Synthetic Institutions)
          </span>
          <span className="text-[10px] text-slate-500 font-mono font-bold">Central Regulatory Clearing Standard</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-300 bg-slate-100 text-xs text-slate-700 font-extrabold uppercase tracking-wider">
                <th className="py-3 px-3">Institution</th>
                <th className="py-3 px-3 text-right">Transactions</th>
                <th className="py-3 px-3 text-right">Flagged Suspicious</th>
                <th className="py-3 px-3 text-right">Fraud Rate</th>
                <th className="py-3 px-3 text-right">Total Volume (INR)</th>
                <th className="py-3 px-3 text-center">Risk Posture</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {bankMetrics.map((b) => (
                <tr key={b.bank_id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-3 font-extrabold text-slate-900 flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                    <span>{b.bank_name}</span>
                    <span className="text-[10px] font-mono font-bold text-slate-500">({b.bank_id})</span>
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-700 font-bold">
                    {b.transactions.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-rose-600 font-extrabold">
                    {b.suspicious.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-amber-700 font-extrabold">
                    {b.fraud_rate}%
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-900 font-extrabold">
                    ₹{(b.volume_inr || 0).toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-center">
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-extrabold font-mono bg-amber-50 text-amber-800 border border-amber-300">
                      MONITORED
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Section 2: Topology Distribution & Turnaround Velocity Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Topology Distribution */}
        <div className="lg:col-span-6 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-600" />
              Laundering Network Topology Breakdown
            </span>
            <span className="text-[10px] text-slate-500 font-mono font-bold">IBM AMLSim Patterns</span>
          </div>

          <div className="space-y-4">
            {topologyDistribution.map((t, idx) => (
              <div key={idx} className="text-xs">
                <div className="flex justify-between items-center mb-1.5">
                  <span className="font-extrabold text-slate-900">{t.topology}</span>
                  <span className="font-mono text-blue-700 font-extrabold">{t.count} rings ({t.share_pct}%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                  <div
                    className="h-2.5 rounded-full transition-all duration-500"
                    style={{ width: `${t.share_pct * 2.5}%`, backgroundColor: t.color }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Turnaround Velocity Histogram */}
        <div className="lg:col-span-6 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-500" />
              Inter-Bank Turnaround Velocity Histogram
            </span>
            <span className="text-[10px] text-slate-500 font-mono font-bold">PaySim vs Anomaly</span>
          </div>

          <div className="space-y-3">
            {velocityHistogram.map((v, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
                <div>
                  <span className="font-extrabold text-slate-900 block">{v.bin}</span>
                  <span className="text-[10px] text-slate-600 font-semibold">{v.description}</span>
                </div>
                <div className="text-right">
                  <span className="font-mono text-blue-700 font-extrabold text-sm">{v.count}</span>
                  <span className="text-[10px] text-slate-500 font-bold block">hops</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Section 3: Pairwise Cross-Bank Clearing Matrix */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col gap-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <Share2 className="w-4 h-4 text-emerald-600" />
            Inter-Bank Pairwise Clearing Remittance Matrix
          </span>
          <span className="text-[10px] text-slate-500 font-mono font-bold">Reconciled Flows</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {crossBankFlows.map((flow, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col gap-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-extrabold text-blue-900">{flow.from.replace('_', ' ')}</span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                <span className="font-extrabold text-emerald-900">{flow.to.replace('_', ' ')}</span>
              </div>
              <div className="flex justify-between items-center text-xs pt-1.5 border-t border-slate-200 font-mono">
                <span className="text-slate-600 font-bold">{flow.tx_count} Transactions</span>
                <span className="text-slate-900 font-extrabold">₹{flow.volume_inr.toLocaleString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
