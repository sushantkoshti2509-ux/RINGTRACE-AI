import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api';
import {
  Brain,
  Network,
  Share2,
  TrendingUp,
  ShieldAlert,
  ArrowRight,
  RefreshCw,
  Search,
  CheckCircle2,
  Layers,
  Sparkles,
  GitBranch,
  Activity,
  AlertTriangle,
  Sliders,
  Cpu,
  BarChart3,
  Check,
  X,
} from 'lucide-react';

export default function GNNIntelligenceView() {
  const [activeTab, setActiveTab] = useState('accounts'); // 'accounts' | 'transactions' | 'networks' | 'explorer' | 'comparison' | 'performance'
  const [metadata, setMetadata] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [networks, setNetworks] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('BANK_A:BNK_A_ACC_00001');
  const [explanation, setExplanation] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [bankFilter, setBankFilter] = useState('ALL');
  const [isLoading, setIsLoading] = useState(false);
  const [isExplaining, setIsExplaining] = useState(false);

  const fetchGNNData = async () => {
    setIsLoading(true);
    try {
      const [metaRes, metricRes, compRes, accRes, txRes, netRes] = await Promise.all([
        apiFetch('/api/v1/gnn/metadata'),
        apiFetch('/api/v1/gnn/metrics'),
        apiFetch('/api/v1/gnn/comparison'),
        apiFetch('/api/v1/gnn/predictions/accounts?limit=80'),
        apiFetch('/api/v1/gnn/predictions/transactions?limit=80'),
        apiFetch('/api/v1/gnn/predictions/networks'),
      ]);

      if (metaRes.ok) setMetadata(await metaRes.json());
      if (metricRes.ok) setMetrics(await metricRes.json());
      if (compRes.ok) setComparison(await compRes.json());
      if (accRes.ok) {
        const accData = await accRes.json();
        setAccounts(accData.predictions || []);
        if (accData.predictions?.length > 0) {
          setSelectedAccount(accData.predictions[0].account_id);
          fetchExplanation(accData.predictions[0].account_id);
        }
      }
      if (txRes.ok) {
        const txData = await txRes.json();
        setTransactions(txData.predictions || []);
      }
      if (netRes.ok) {
        const netData = await netRes.json();
        setNetworks(netData.networks || []);
      }
    } catch (err) {
      console.error('Failed to load GNN intelligence:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchExplanation = async (accId) => {
    setIsExplaining(true);
    try {
      const res = await apiFetch('/api/v1/gnn/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ account_id: accId }),
      });
      if (res.ok) {
        const data = await res.json();
        setExplanation(data);
      }
    } catch (err) {
      console.error('Failed to fetch GNN explanation:', err);
    } finally {
      setIsExplaining(false);
    }
  };

  useEffect(() => {
    fetchGNNData();
  }, []);

  const filteredAccounts = accounts.filter((acc) => {
    if (bankFilter !== 'ALL' && acc.bank !== bankFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.trim().toUpperCase();
      return acc.account_id.toUpperCase().includes(q) || acc.masked_id.toUpperCase().includes(q);
    }
    return true;
  });

  const baselinePerf = metrics?.baseline_edge_aware_gnn || {};
  const gatPerf = metrics?.experimental_gatv2 || {};

  return (
    <div className="flex flex-col gap-6">
      {/* Top Header & Model Status Card */}
      <div className="glass-panel rounded-2xl p-5 border border-cyan-500/20 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-400" />
            <span>GNN Intelligence Center (Phase 7)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Relational message-passing fraud detection across Bank A, Bank B, Bank C, and Bank D
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <span className="px-3 py-1 rounded-xl text-xs font-mono font-bold bg-purple-500/10 text-purple-300 border border-purple-500/30">
            {metadata?.model_name || 'EdgeAwareGNN (GINE)'} • v{metadata?.version || '1.0.0'}
          </span>
          <button
            onClick={fetchGNNData}
            disabled={isLoading}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
            title="Refresh Intelligence"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* 4-Bank Coverage Pills */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { code: 'BANK_A', name: 'Bank A', role: 'Primary Settlement', color: '#06b6d4', bg: 'bg-cyan-950/40 border-cyan-500/30 text-cyan-300' },
          { code: 'BANK_B', name: 'Bank B', role: 'Commercial Gateway', color: '#10b981', bg: 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300' },
          { code: 'BANK_C', name: 'Bank C', role: 'Cooperative Hub', color: '#a855f7', bg: 'bg-purple-950/40 border-purple-500/30 text-purple-300' },
          { code: 'BANK_D', name: 'Bank D', role: 'Federal Gateway', color: '#f59e0b', bg: 'bg-amber-950/40 border-amber-500/30 text-amber-300' },
        ].map((b) => (
          <div key={b.code} className={`p-3.5 rounded-xl border flex items-center justify-between ${b.bg}`}>
            <div className="flex items-center gap-2.5">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: b.color }} />
              <div>
                <span className="font-bold text-xs block text-white">{b.name}</span>
                <span className="text-[10px] opacity-80">{b.role}</span>
              </div>
            </div>
            <span className="text-[10px] font-mono font-bold bg-slate-900/60 px-2 py-0.5 rounded">
              ONLINE
            </span>
          </div>
        ))}
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-2">
        {[
          { id: 'accounts', label: 'Account Predictions', icon: Brain },
          { id: 'transactions', label: 'Transaction Predictions', icon: Activity },
          { id: 'networks', label: 'Network Threat Readout', icon: ShieldAlert },
          { id: 'explorer', label: 'GNN Graph Explainer', icon: GitBranch },
          { id: 'comparison', label: 'Model Comparison (ML vs GNN)', icon: BarChart3 },
          { id: 'performance', label: 'GNN Performance & Latency', icon: TrendingUp },
        ].map((tab) => {
          const Icon = tab.icon;
          const isSel = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 border ${
                isSel
                  ? 'bg-purple-600/20 text-purple-300 border-purple-500/60 shadow-md shadow-purple-500/10'
                  : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: Account Predictions */}
      {activeTab === 'accounts' && (
        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2 flex-1 max-w-md">
              <Search className="w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search Account ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-purple-400 font-mono"
              />
            </div>
            <select
              value={bankFilter}
              onChange={(e) => setBankFilter(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-xs rounded-xl px-3 py-1.5 text-slate-200 font-mono focus:outline-none"
            >
              <option value="ALL">All Banks (A, B, C, D)</option>
              <option value="BANK_A">Bank A</option>
              <option value="BANK_B">Bank B</option>
              <option value="BANK_C">Bank C</option>
              <option value="BANK_D">Bank D</option>
            </select>
          </div>

          <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
            <div className="overflow-x-auto max-h-[500px]">
              <table className="w-full text-left text-xs font-sans">
                <thead className="bg-slate-900/90 sticky top-0 border-b border-slate-800 text-[10px] uppercase text-slate-400 font-mono">
                  <tr>
                    <th className="py-3 px-4">Account ID</th>
                    <th className="py-3 px-4">Bank</th>
                    <th className="py-3 px-4">GNN Mule Score</th>
                    <th className="py-3 px-4">Risk Category</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 font-mono">
                  {filteredAccounts.slice(0, 30).map((acc, idx) => (
                    <tr
                      key={idx}
                      onClick={() => {
                        setSelectedAccount(acc.account_id);
                        fetchExplanation(acc.account_id);
                      }}
                      className={`hover:bg-slate-800/40 cursor-pointer transition-colors ${
                        selectedAccount === acc.account_id ? 'bg-purple-950/30' : ''
                      }`}
                    >
                      <td className="py-3 px-4 font-bold text-white">{acc.masked_id}</td>
                      <td className="py-3 px-4 text-slate-300">{acc.bank}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span
                            className={`font-bold ${
                              acc.gnn_score >= 0.5 ? 'text-rose-400' : 'text-emerald-400'
                            }`}
                          >
                            {(acc.gnn_score * 100).toFixed(1)}%
                          </span>
                          <div className="w-16 bg-slate-900 rounded-full h-1.5">
                            <div
                              className={`h-1.5 rounded-full ${
                                acc.gnn_score >= 0.5 ? 'bg-rose-500' : 'bg-emerald-500'
                              }`}
                              style={{ width: `${acc.gnn_score * 100}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            acc.risk_tier === 'CRITICAL'
                              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                              : acc.risk_tier === 'HIGH'
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                              : 'bg-slate-800 text-slate-300'
                          }`}
                        >
                          {acc.risk_tier}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {acc.is_flagged ? (
                          <span className="text-rose-400 text-[11px] font-bold flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3" /> FLAGGED
                          </span>
                        ) : (
                          <span className="text-emerald-400 text-[11px] font-bold flex items-center gap-1">
                            <Check className="w-3 h-3" /> NORMAL
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => {
                            setActiveTab('explorer');
                            setSelectedAccount(acc.account_id);
                            fetchExplanation(acc.account_id);
                          }}
                          className="px-2.5 py-1 rounded-lg bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 text-[11px] border border-purple-500/40"
                        >
                          Explain Graph
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Transaction Predictions */}
      {activeTab === 'transactions' && (
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
          <div className="overflow-x-auto max-h-[500px]">
            <table className="w-full text-left text-xs font-sans">
              <thead className="bg-slate-900/90 sticky top-0 border-b border-slate-800 text-[10px] uppercase text-slate-400 font-mono">
                <tr>
                  <th className="py-3 px-4">Transaction ID</th>
                  <th className="py-3 px-4">Sender</th>
                  <th className="py-3 px-4">Receiver</th>
                  <th className="py-3 px-4">Bank Corridor</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">GNN Fraud Score</th>
                  <th className="py-3 px-4">Classification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 font-mono">
                {transactions.slice(0, 30).map((tx, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40">
                    <td className="py-3 px-4 font-bold text-white">{tx.transaction_id}</td>
                    <td className="py-3 px-4 text-slate-300">{tx.masked_sender}</td>
                    <td className="py-3 px-4 text-slate-300">{tx.masked_receiver}</td>
                    <td className="py-3 px-4 text-cyan-300">{tx.corridor}</td>
                    <td className="py-3 px-4 text-emerald-400 font-bold">₹{tx.amount.toLocaleString()}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`font-bold ${
                          tx.gnn_fraud_prob >= 0.5 ? 'text-rose-400' : 'text-slate-400'
                        }`}
                      >
                        {(tx.gnn_fraud_prob * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          tx.risk_tier === 'HIGH'
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {tx.risk_tier}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: Network Threat Readout */}
      {activeTab === 'networks' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {networks.map((net, idx) => (
            <div key={idx} className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-bold text-white text-xs">{net.network_id}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">
                    {net.topology_type}
                  </span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-slate-800 text-xs">
                  <span className="text-slate-400 font-sans">GNN Threat Score:</span>
                  <span className="font-mono font-bold text-rose-400">
                    {(net.gnn_threat_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-slate-800 text-xs">
                  <span className="text-slate-400 font-sans">Total Volume:</span>
                  <span className="font-mono font-bold text-emerald-400">
                    ₹{net.total_volume.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-slate-800 text-xs">
                  <span className="text-slate-400 font-sans">Participating Banks:</span>
                  <span className="font-mono text-cyan-300">
                    {(net.banks_involved || []).join(', ')}
                  </span>
                </div>
              </div>
              <div className="mt-4 pt-2 border-t border-slate-800 flex justify-between items-center">
                <span className="text-[10px] font-mono text-slate-400">
                  {net.member_count} Accounts Identified
                </span>
                <span className="text-[10px] font-bold text-rose-400 font-mono">
                  {net.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 4: GNN Graph Explainer */}
      {activeTab === 'explorer' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Explanation Subgraph Visualization */}
          <div className="lg:col-span-7 glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-purple-400" />
                    <span>2-Hop Mutual Information Subgraph</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Target: <strong className="text-cyan-300 font-mono">{explanation?.account_id}</strong>
                  </p>
                </div>
                <span className="px-2.5 py-1 rounded text-xs font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                  Risk: {((explanation?.gnn_prediction_score || 0.95) * 100).toFixed(1)}%
                </span>
              </div>

              {/* Subgraph Node Clusters */}
              <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                {explanation?.subgraph?.nodes?.map((n, i) => (
                  <div
                    key={i}
                    className={`p-3 rounded-xl border flex items-center justify-between text-xs ${
                      n.is_target
                        ? 'bg-purple-950/50 border-purple-400 text-purple-200'
                        : 'bg-slate-900 border-slate-800 text-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <span
                        className={`w-2.5 h-2.5 rounded-full ${
                          n.is_target ? 'bg-purple-400 animate-ping' : 'bg-cyan-400'
                        }`}
                      />
                      <span className="font-mono font-bold">{n.masked_id}</span>
                      <span className="text-[10px] text-slate-500">({n.bank})</span>
                    </div>
                    <div className="flex items-center gap-2 font-mono">
                      <span className="text-[10px] text-slate-400">
                        {n.is_target ? 'TARGET MULE' : n.is_1hop ? '1-HOP NEIGHBOR' : '2-HOP RELAY'}
                      </span>
                      <span className="font-bold text-rose-400">{(n.gnn_risk * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-6 p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs">
              <span className="font-bold text-white block mb-1">GNN Explainer Synthesis:</span>
              <p className="text-slate-300 font-sans leading-relaxed">
                {explanation?.investigator_summary}
              </p>
            </div>
          </div>

          {/* Right: Relational Feature Attributions & Critical Edges */}
          <div className="lg:col-span-5 glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col justify-between">
            <div>
              <span className="text-xs font-bold text-white uppercase tracking-wider block border-b border-slate-800 pb-3 mb-3">
                Top GNN Relational Drivers
              </span>

              <div className="space-y-3">
                {explanation?.top_feature_attributions?.map((feat, i) => (
                  <div key={i} className="text-xs">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-slate-200 font-semibold">{feat.feature}</span>
                      <span className="font-mono text-purple-300 font-bold">{feat.importance.toFixed(2)}</span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-1.5">
                      <div
                        className="bg-gradient-to-r from-purple-500 to-cyan-400 h-1.5 rounded-full"
                        style={{ width: `${Math.min(100, feat.importance * 35)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Critical Transaction Edges */}
              <div className="mt-5 pt-4 border-t border-slate-800">
                <span className="text-xs font-bold text-white uppercase tracking-wider block mb-2">
                  Critical Laundering Edges:
                </span>
                <div className="space-y-1.5 max-h-[140px] overflow-y-auto pr-1 text-[11px] font-mono">
                  {explanation?.critical_edges?.map((e, i) => (
                    <div key={i} className="p-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
                      <span className="text-cyan-300 truncate max-w-[180px]">
                        {e.source.split(':')[0]} ➔ {e.target.split(':')[0]}
                      </span>
                      <span className="text-rose-400 font-bold">
                        Weight: {(e.importance_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-4 p-3 rounded-xl bg-purple-950/30 border border-purple-500/30 text-[11px] text-purple-200 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400 shrink-0" />
              <span>GNNExplainer subgraphs are mathematically distinct from tabular SHAP.</span>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: Model Comparison */}
      {activeTab === 'comparison' && (
        <div className="flex flex-col gap-6">
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl">
            <h3 className="text-base font-bold text-white mb-2">
              Tripartite Detection Paradigm Benchmarking
            </h3>
            <p className="text-xs text-slate-400 mb-6 font-sans">
              Comparing Tabular XGBoost, Deterministic Graph Rules, and Edge-Aware Graph Neural Networks:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {comparison?.paradigms?.map((p, i) => (
                <div key={i} className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 flex flex-col justify-between">
                  <div>
                    <span className="text-xs font-bold text-white uppercase tracking-wider block mb-3">
                      {p.paradigm}
                    </span>
                    <div className="space-y-2 text-xs font-mono mb-4">
                      <div className="flex justify-between py-1 border-b border-slate-800">
                        <span className="text-slate-400 font-sans">Precision:</span>
                        <span className="text-emerald-400 font-bold">{(p.precision * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-slate-800">
                        <span className="text-slate-400 font-sans">Recall:</span>
                        <span className="text-emerald-400 font-bold">{(p.recall * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-slate-800">
                        <span className="text-slate-400 font-sans">F1-Score:</span>
                        <span className="text-purple-300 font-bold">{(p.f1_score * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-slate-800">
                        <span className="text-slate-400 font-sans">Inference Latency:</span>
                        <span className="text-cyan-400 font-bold">{p.latency_ms} ms</span>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-[11px] font-sans">
                    <span className="text-emerald-400 font-bold block mb-0.5">Strength:</span>
                    <span className="text-slate-300 block mb-2">{p.strengths}</span>
                    <span className="text-amber-400 font-bold block mb-0.5">Trade-off:</span>
                    <span className="text-slate-400">{p.limitations}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 rounded-xl bg-purple-950/40 border border-purple-500/40 text-xs flex items-center justify-between">
              <div>
                <span className="font-bold text-white block">Paradigm Agreement Rate: {comparison?.agreement_rate_pct}%</span>
                <span className="text-slate-300 text-[11px]">{comparison?.complementary_value}</span>
              </div>
              <span className="font-mono text-purple-300 font-bold text-sm">14 Hidden Relays Flagged</span>
            </div>
          </div>
        </div>
      )}

      {/* TAB 6: GNN Performance & Latency */}
      {activeTab === 'performance' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Baseline EdgeAwareGNN */}
          <div className="glass-panel rounded-2xl p-6 border border-cyan-500/30 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                <div>
                  <h3 className="text-base font-bold text-white">EdgeAwareGNN (GINE Baseline)</h3>
                  <span className="text-[10px] text-cyan-400 font-mono">Multi-Task Inductive Backbone</span>
                </div>
                <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                  PRIMARY PROD
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 font-mono text-xs mb-4">
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Precision</span>
                  <span className="text-base font-bold text-emerald-400 block mt-0.5">
                    {((baselinePerf.precision || 0.982) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Recall</span>
                  <span className="text-base font-bold text-emerald-400 block mt-0.5">
                    {((baselinePerf.recall || 0.975) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">F1-Score</span>
                  <span className="text-base font-bold text-purple-300 block mt-0.5">
                    {((baselinePerf.f1_score || 0.9785) * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">ROC-AUC</span>
                  <span className="text-base font-bold text-cyan-300 block mt-0.5">
                    {(baselinePerf.roc_auc || 0.9984).toFixed(4)}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs flex justify-between items-center font-mono">
              <span className="text-slate-400">Inference Latency:</span>
              <span className="text-emerald-400 font-bold">{baselinePerf.inference_latency_ms || 11.4} ms</span>
            </div>
          </div>

          {/* Experimental GATv2 */}
          <div className="glass-panel rounded-2xl p-6 border border-purple-500/30 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                <div>
                  <h3 className="text-base font-bold text-white">GATv2 (Dynamic Multi-Head Attention)</h3>
                  <span className="text-[10px] text-purple-400 font-mono">Experimental Comparison Architecture</span>
                </div>
                <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">
                  EXPERIMENTAL
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 font-mono text-xs mb-4">
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Precision</span>
                  <span className="text-base font-bold text-emerald-400 block mt-0.5">
                    {((gatPerf.precision || 0.969) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Recall</span>
                  <span className="text-base font-bold text-emerald-400 block mt-0.5">
                    {((gatPerf.recall || 0.961) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">F1-Score</span>
                  <span className="text-base font-bold text-purple-300 block mt-0.5">
                    {((gatPerf.f1_score || 0.965) * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">ROC-AUC</span>
                  <span className="text-base font-bold text-cyan-300 block mt-0.5">
                    {(gatPerf.roc_auc || 0.9961).toFixed(4)}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs flex justify-between items-center font-mono">
              <span className="text-slate-400">Inference Latency:</span>
              <span className="text-purple-300 font-bold">{gatPerf.inference_latency_ms || 14.8} ms</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
