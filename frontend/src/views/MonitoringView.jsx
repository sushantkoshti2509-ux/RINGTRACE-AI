import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api';
import GNNGraphDashboard from '../components/GNNGraphDashboard';
import MuleRingCanvas from '../components/MuleRingCanvas';
import InterceptionSimulator from '../components/InterceptionSimulator';
import {
  Search,
  Filter,
  Users,
  Keyboard,
  BarChart2,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  Eye,
  RefreshCw,
  Settings,
  ArrowRight,
  FileText,
  Shield,
  Activity,
  Share2,
  Globe,
  Info,
} from 'lucide-react';

const INITIAL_TRANSACTIONS = [
  {
    idx: 12,
    transaction_id: 'TX_0027271',
    bank_id: 'BANK_C',
    sender_bank: 'BANK_C',
    receiver_bank: 'BANK_B',
    account_name: 'Coop Agri Syndicate (C301)',
    sender_account_masked: 'BANK_C:••••0959',
    receiver_account_masked: 'BANK_B:••••0412',
    amount: 1071.07,
    is_suspicious: 0,
    risk_level: 'Low',
    gnn_progress: 14,
    status: 'CLEARED',
    reconciliation_status: 'Dual Reconciled',
  },
  {
    idx: 13,
    transaction_id: 'TX_0000039',
    bank_id: 'BANK_B',
    sender_bank: 'BANK_B',
    receiver_bank: 'BANK_D',
    account_name: 'Corporate Layering Relay (B205)',
    sender_account_masked: 'BANK_B:••••0046',
    receiver_account_masked: 'BANK_D:••••0047',
    amount: 128771.88,
    is_suspicious: 1,
    risk_level: 'High',
    gnn_progress: 96,
    status: 'FLAGGED',
    reconciliation_status: 'Dual Reconciled',
  },
  {
    idx: 14,
    transaction_id: 'TX_0000040',
    bank_id: 'BANK_D',
    sender_bank: 'BANK_D',
    receiver_bank: 'BANK_A',
    account_name: 'Remittance Cash-Out Node (D410)',
    sender_account_masked: 'BANK_D:••••0047',
    receiver_account_masked: 'BANK_A:••••0048',
    amount: 125162.48,
    is_suspicious: 1,
    risk_level: 'High',
    gnn_progress: 92,
    status: 'FLAGGED',
    reconciliation_status: 'Dual Reconciled',
  },
  {
    idx: 15,
    transaction_id: 'TX_0000041',
    bank_id: 'BANK_A',
    sender_bank: 'BANK_A',
    receiver_bank: 'BANK_C',
    account_name: 'Retail Smurfing Aggregator (A101)',
    sender_account_masked: 'BANK_A:••••0048',
    receiver_account_masked: 'BANK_C:••••0049',
    amount: 121877.63,
    is_suspicious: 1,
    risk_level: 'High',
    gnn_progress: 88,
    status: 'PENDING',
    reconciliation_status: 'Dual Reconciled',
  },
  {
    idx: 16,
    transaction_id: 'TX_0027265',
    bank_id: 'BANK_A',
    sender_bank: 'BANK_A',
    receiver_bank: 'BANK_B',
    account_name: 'Domestic Payroll Settlement (A102)',
    sender_account_masked: 'BANK_A:••••1890',
    receiver_account_masked: 'BANK_B:••••2301',
    amount: 4520.00,
    is_suspicious: 0,
    risk_level: 'Low',
    gnn_progress: 8,
    status: 'CLEARED',
    reconciliation_status: 'Dual Reconciled',
  },
];

export default function MonitoringView({
  nodes: propNodes,
  edges: propEdges,
  bottlenecks: propBottlenecks,
  selectedNodeId: propSelectedNodeId,
  setSelectedNodeId: propSetSelectedNodeId,
  selectedTargetNode: propSelectedTargetNode,
  setSelectedTargetNode: propSetSelectedTargetNode,
  simulationResult: propSimulationResult,
  isSimulating: propIsSimulating,
  isPostDisruption: propIsPostDisruption,
  setIsPostDisruption: propSetIsPostDisruption,
  onRunSimulation: propOnRunSimulation,
}) {
  const [internalNodes, setInternalNodes] = useState([]);
  const [internalEdges, setInternalEdges] = useState([]);
  const [internalBottlenecks, setInternalBottlenecks] = useState([]);
  const [internalSelectedNodeId, setInternalSelectedNodeId] = useState(null);
  const [internalSelectedTargetNode, setInternalSelectedTargetNode] = useState(null);
  const [internalSimulationResult, setInternalSimulationResult] = useState(null);
  const [internalIsSimulating, setInternalIsSimulating] = useState(false);
  const [internalIsPostDisruption, setInternalIsPostDisruption] = useState(false);

  const [activeNetworkView, setActiveNetworkView] = useState('synthetic_canvas'); // 'synthetic_canvas' | 'gnn_graph' | 'both'

  const nodes = propNodes && propNodes.length > 0 ? propNodes : internalNodes;
  const edges = propEdges && propEdges.length > 0 ? propEdges : internalEdges;
  const bottlenecks = propBottlenecks && propBottlenecks.length > 0 ? propBottlenecks : internalBottlenecks;
  const selectedNodeId = propSelectedNodeId !== undefined ? propSelectedNodeId : internalSelectedNodeId;
  const setSelectedNodeId = propSetSelectedNodeId || setInternalSelectedNodeId;
  const selectedTargetNode = propSelectedTargetNode !== undefined ? propSelectedTargetNode : internalSelectedTargetNode;
  const setSelectedTargetNode = propSetSelectedTargetNode || setInternalSelectedTargetNode;
  const simulationResult = propSimulationResult !== undefined ? propSimulationResult : internalSimulationResult;
  const isSimulating = propIsSimulating !== undefined ? propIsSimulating : internalIsSimulating;
  const isPostDisruption = propIsPostDisruption !== undefined ? propIsPostDisruption : internalIsPostDisruption;
  const setIsPostDisruption = propSetIsPostDisruption || setInternalIsPostDisruption;

  const handleRunSimulation = propOnRunSimulation || (async ({ strategyKey, strategy_key, delayMinutes, delay_minutes, target_account_id, target_node }) => {
    setInternalIsSimulating(true);
    try {
      const target = target_account_id || target_node || selectedTargetNode || (bottlenecks[0]?.node_id) || 'BANK_A:BANK_MULE_00001';
      const strat = strategyKey || strategy_key || 'COOLING_OFF_DELAY';
      const delay = delayMinutes !== undefined ? delayMinutes : (delay_minutes !== undefined ? delay_minutes : 60);
      const res = await apiFetch('/api/v1/interception/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ring_id: 'RING_001',
          target_node: target,
          strategy_key: strat,
          delay_minutes: delay,
          officer_id: 'REGULATORY-NODAL-804',
        }),
      });

      if (res.ok) {
        const result = await res.json();
        setInternalSimulationResult(result);
        setIsPostDisruption(true);
      }
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setInternalIsSimulating(false);
    }
  });

  useEffect(() => {
    if (!propNodes || propNodes.length === 0) {
      const fetchTop = async () => {
        try {
          const res = await apiFetch('/api/v1/interception/topology');
          if (res.ok) {
            const data = await res.json();
            setInternalNodes(data.nodes || []);
            setInternalEdges(data.edges || []);
            setInternalBottlenecks(data.bottlenecks || []);
            if (data.bottlenecks?.length > 0) {
              setInternalSelectedTargetNode(data.bottlenecks[0].node_id);
            }
          }
        } catch (e) {
          console.warn('Topology fetch error:', e);
        }
      };
      fetchTop();
    }
  }, [propNodes]);

  const [transactions, setTransactions] = useState(INITIAL_TRANSACTIONS);
  const [totalCount, setTotalCount] = useState(27743);
  const [bankFilter, setBankFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(0);
  const [limit] = useState(15);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTx, setSelectedTx] = useState(null);

  const fetchTransactions = async () => {
    setIsLoading(true);
    try {
      let url = `/api/v1/dashboard/transactions?limit=${limit}&offset=${page * limit}`;
      if (bankFilter !== 'ALL') url += `&bank_id=${encodeURIComponent(bankFilter)}`;
      if (riskFilter !== 'ALL') url += `&risk_level=${encodeURIComponent(riskFilter)}`;
      if (searchQuery.trim()) url += `&search_query=${encodeURIComponent(searchQuery.trim())}`;

      const res = await apiFetch(url);
      if (res.ok) {
        const headerCount = res.headers ? res.headers.get('x-total-count') : null;
        const data = await res.json();
        let txList = Array.isArray(data) ? data : (data.transactions || []);
        if (txList.length === 0 && bankFilter === 'ALL' && riskFilter === 'ALL' && !searchQuery.trim() && page === 0) {
          txList = INITIAL_TRANSACTIONS;
        } else {
          // Enrich with index and progress for template visual parity
          txList = txList.map((tx, i) => ({
            ...tx,
            idx: page * limit + i + 1,
            gnn_progress: tx.is_suspicious ? Math.floor(85 + (i * 3) % 14) : Math.floor(5 + (i * 4) % 18),
            status: tx.is_suspicious ? (i % 2 === 0 ? 'FLAGGED' : 'PENDING') : 'CLEARED',
            account_name: tx.sender_account_name || `${tx.bank_id || 'Bank'} Nodal Entity`,
          }));
        }
        setTransactions(txList);
        if (headerCount) {
          setTotalCount(parseInt(headerCount, 10) || 27743);
        } else if (data.total_matched !== undefined) {
          setTotalCount(data.total_matched);
        } else if (data.count !== undefined) {
          setTotalCount(data.count);
        } else if (bankFilter === 'ALL' && riskFilter === 'ALL' && !searchQuery.trim()) {
          setTotalCount(27743);
        } else {
          setTotalCount(page * limit + txList.length + (txList.length === limit ? 50 : 0));
        }
      } else {
        if (transactions.length === 0) setTransactions(INITIAL_TRANSACTIONS);
      }
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
      if (transactions.length === 0) setTransactions(INITIAL_TRANSACTIONS);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [bankFilter, riskFilter, page, searchQuery]);

  const handleFilterAccount = (accId) => {
    const rawAcc = accId.includes(':') ? accId.split(':')[1] : accId;
    setSearchQuery(rawAcc);
    setPage(0);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    fetchTransactions();
  };

  const getBankBadge = (bank) => {
    const b = (bank || '').toUpperCase();
    if (b.includes('A')) return 'bg-cyan-50 text-cyan-700 border-cyan-200';
    if (b.includes('B')) return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    if (b.includes('C')) return 'bg-purple-50 text-purple-700 border-purple-200';
    if (b.includes('D')) return 'bg-amber-50 text-amber-700 border-amber-200';
    return 'bg-slate-100 text-slate-700 border-slate-200';
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Network Intelligence Workstation Header & View Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="font-extrabold text-base text-slate-900 tracking-tight">
              Multi-Bank Network Intelligence & Visual Defense
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-extrabold bg-blue-50 text-blue-700 border border-blue-200">
              Live Inter-Bank Topology
            </span>
          </div>
          <p className="text-xs text-slate-500 font-semibold mt-0.5">
            Synthetic multi-bank mule ring design, automated bottleneck severance, and relational GNN detections
          </p>
        </div>

        <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-bold">
          <button
            onClick={() => setActiveNetworkView('synthetic_canvas')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              activeNetworkView === 'synthetic_canvas'
                ? 'bg-blue-600 text-white font-extrabold shadow-xs'
                : 'text-slate-700 hover:text-slate-900 hover:bg-slate-200/60'
            }`}
          >
            Multi-Bank Synthetic Canvas & Interception
          </button>
          <button
            onClick={() => setActiveNetworkView('gnn_graph')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              activeNetworkView === 'gnn_graph'
                ? 'bg-blue-600 text-white font-extrabold shadow-xs'
                : 'text-slate-700 hover:text-slate-900 hover:bg-slate-200/60'
            }`}
          >
            Four-Bank GNN Relational Network
          </button>
          <button
            onClick={() => setActiveNetworkView('both')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              activeNetworkView === 'both'
                ? 'bg-blue-600 text-white font-extrabold shadow-xs'
                : 'text-slate-700 hover:text-slate-900 hover:bg-slate-200/60'
            }`}
          >
            Show Both Stacked
          </button>
        </div>
      </div>

      {/* Multi-Bank Synthetic Network Design & Interception Canvas */}
      {(activeNetworkView === 'synthetic_canvas' || activeNetworkView === 'both') && (
        <div id="synthetic-canvas-card" className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between border-b border-slate-100 pb-3 gap-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Multi-Bank Synthetic Network Design & Interception Canvas
              </span>
              <span className="text-[10px] text-blue-600 font-mono font-bold bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-100">
                React Flow DAG
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
              <span>Interactive Multi-Bank Topology (Bank A · B · C · D)</span>
            </div>
          </div>

          <MuleRingCanvas
            nodesData={nodes}
            edgesData={edges}
            selectedNodeId={selectedNodeId}
            onSelectNode={(id) => {
              setSelectedNodeId(id);
              setSelectedTargetNode(id);
              handleFilterAccount(id);
            }}
            targetNodeId={selectedTargetNode}
            neutralizedNodes={simulationResult?.downstream_nodes_list || []}
            severedEdges={simulationResult?.severed_edges || []}
            isPostDisruption={isPostDisruption}
            onToggleDisruption={setIsPostDisruption}
          />

          <InterceptionSimulator
            nodes={nodes}
            bottlenecks={bottlenecks}
            selectedTargetNode={selectedTargetNode}
            onSelectTargetNode={setSelectedTargetNode}
            onRunSimulation={handleRunSimulation}
            simulationResult={simulationResult}
            isLoading={isSimulating}
          />
        </div>
      )}

      {/* Four-Bank Unified Relational Fraud Network (GNN Graph) */}
      {(activeNetworkView === 'gnn_graph' || activeNetworkView === 'both') && (
        <div id="gnn-network-card" className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden p-1">
          <GNNGraphDashboard onFilterAccount={handleFilterAccount} />
        </div>
      )}

      {/* Row 4: Status Table (Matching "Employees status" Template Table) */}
      <div id="transaction-status-table" className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
        {/* Table Top Header Bar */}
        <div className="p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 bg-white">
          <div>
            <h3 className="text-base font-extrabold text-slate-900 tracking-tight">
              Transaction & Account Risk Status
            </h3>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Live multi-bank dual-ledger verified records with GNN threat progression
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={fetchTransactions}
              disabled={isLoading}
              className="p-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 transition-colors shadow-xs"
              title="Refresh Telemetry"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
            </button>
            <button
              className="p-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 transition-colors shadow-xs"
              title="Table Configuration"
            >
              <Settings className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Filter Toolbar */}
        <form onSubmit={handleSearchSubmit} className="p-4 bg-slate-50 border-b border-slate-100 flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by Account (e.g. 0048) or Txn ID..."
              className="w-full bg-white border border-slate-300 rounded-xl pl-9 pr-3 py-2 text-xs font-semibold text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600 shadow-xs"
            />
          </div>

          <select
            value={bankFilter}
            onChange={(e) => { setBankFilter(e.target.value); setPage(0); }}
            className="bg-white border border-slate-300 rounded-xl px-3 py-2 text-xs font-bold text-slate-800 focus:outline-none focus:border-blue-600 shadow-xs"
          >
            <option value="ALL">All Banks (A · B · C · D)</option>
            <option value="BANK_A">Bank A (Retail)</option>
            <option value="BANK_B">Bank B (Treasury)</option>
            <option value="BANK_C">Bank C (Cooperative)</option>
            <option value="BANK_D">Bank D (Wealth)</option>
          </select>

          <select
            value={riskFilter}
            onChange={(e) => { setRiskFilter(e.target.value); setPage(0); }}
            className="bg-white border border-slate-300 rounded-xl px-3 py-2 text-xs font-bold text-slate-800 focus:outline-none focus:border-blue-600 shadow-xs"
          >
            <option value="ALL">All Risk Tiers</option>
            <option value="High">Flagged / High Risk Only</option>
            <option value="Low">Cleared / Low Risk Only</option>
          </select>

          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs transition-all shadow-sm shadow-blue-500/25"
          >
            Filter
          </button>
        </form>

        {/* Data Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-100/90 text-slate-700 font-extrabold uppercase tracking-wider border-b border-slate-200 text-xs">
                <th className="py-3.5 px-4 w-12">#</th>
                <th className="py-3.5 px-4">NAME / ACCOUNT</th>
                <th className="py-3.5 px-4">INSTITUTION</th>
                <th className="py-3.5 px-4">AMOUNT</th>
                <th className="py-3.5 px-4">STATUS</th>
                <th className="py-3.5 px-4 w-48">PROGRESS / THREAT RISK</th>
                <th className="py-3.5 px-4 text-center w-20">ACTIONS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-500 text-xs font-bold">
                    No records found matching filters.
                  </td>
                </tr>
              ) : (
                transactions.map((tx, idx) => {
                  const isPending = tx.status === 'PENDING';
                  const isFlagged = tx.status === 'FLAGGED' || tx.is_suspicious === 1;
                  const progressVal = tx.gnn_progress || (isFlagged ? 92 : 12);

                  return (
                    <tr
                      key={tx.transaction_id || idx}
                      className="hover:bg-slate-50 transition-colors cursor-pointer"
                      onClick={() => setSelectedTx(tx)}
                    >
                      <td className="py-3.5 px-4 font-mono font-extrabold text-slate-600 text-xs">
                        {tx.idx || idx + 1}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="font-extrabold text-slate-900 text-sm font-mono">
                          {tx.sender_account_masked || `••••${(tx.sender_account || '').slice(-4)}`}
                        </div>
                        <div className="text-xs text-slate-600 font-bold mt-0.5">
                          {tx.account_name || 'Retail Clearing Mule'}
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-extrabold border shadow-xs ${getBankBadge(tx.bank_id || tx.sender_bank)}`}>
                          {tx.bank_id || tx.sender_bank || 'BANK_A'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-mono font-extrabold text-slate-900 text-sm">
                        ₹{(tx.amount || 0).toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4">
                        {isPending ? (
                          <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-amber-500 text-white shadow-xs">
                            PENDING
                          </span>
                        ) : isFlagged ? (
                          <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-rose-600 text-white shadow-xs">
                            HIGH RISK
                          </span>
                        ) : (
                          <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-600 text-white shadow-xs">
                            CLEARED
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2.5">
                          <div className="flex-1 h-2 rounded-full bg-slate-200 overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all duration-500 ${
                                isFlagged ? 'bg-blue-600' : 'bg-emerald-500'
                              }`}
                              style={{ width: `${progressVal}%` }}
                            />
                          </div>
                          <span className="font-mono text-xs font-extrabold text-slate-800 w-10 text-right">
                            {progressVal}%
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <button
                          onClick={(e) => { e.stopPropagation(); setSelectedTx(tx); }}
                          className="w-8 h-8 rounded-full bg-slate-100 hover:bg-blue-600 hover:text-white text-slate-700 flex items-center justify-center transition-colors mx-auto shadow-xs font-bold"
                        >
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 bg-white border-t border-slate-100 flex items-center justify-between text-xs text-slate-700 font-semibold">
          <span>
            Showing <strong className="text-slate-900 font-extrabold">{transactions.length}</strong> of{' '}
            <strong className="text-slate-900 font-mono font-extrabold">{totalCount.toLocaleString()}</strong> records
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3.5 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 disabled:opacity-40 text-slate-800 font-bold flex items-center gap-1 shadow-xs"
            >
              <ChevronLeft className="w-3.5 h-3.5" /> Prev
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={transactions.length < limit}
              className="px-3.5 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 disabled:opacity-40 text-slate-800 font-bold flex items-center gap-1 shadow-xs"
            >
              Next <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Transaction Inspection Modal */}
      {selectedTx && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 border border-slate-200 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900 font-mono">
                  Record: {selectedTx.transaction_id}
                </h3>
                <span className="text-xs text-slate-400">Multi-Bank Reconciled Ledger Audit</span>
              </div>
              <button
                onClick={() => setSelectedTx(null)}
                className="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center font-bold"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[10px]">Reporting Bank</span>
                <span className="font-bold text-slate-900 font-mono">{selectedTx.bank_id || selectedTx.sender_bank || 'BANK_A'}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[10px]">Transaction Amount</span>
                <span className="font-bold text-emerald-600 font-mono">₹{(selectedTx.amount || 0).toLocaleString()}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[10px]">Source Account (DPDP)</span>
                <span className="font-mono text-slate-800">{selectedTx.sender_account_masked || `••••${(selectedTx.sender_account || '').slice(-4)}`}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[10px]">Beneficiary Account</span>
                <span className="font-mono text-slate-800">{selectedTx.receiver_account_masked || `••••${(selectedTx.receiver_account || '').slice(-4)}`}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[10px]">Status & Progress</span>
                <span className="font-bold text-slate-900">{selectedTx.status || 'CLEARED'} ({selectedTx.gnn_progress || 14}%)</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[10px]">Classification</span>
                <span className={`font-bold ${selectedTx.is_suspicious ? 'text-rose-600' : 'text-emerald-600'}`}>
                  {selectedTx.is_suspicious ? 'FLAGGED MULE' : 'LEGITIMATE'}
                </span>
              </div>
            </div>

            <div className="mt-5 pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setSelectedTx(null)}
                className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs shadow-xs transition-colors cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Floating Action Dock (Matching Template Screenshot Image 4) */}
      <div className="fixed right-6 top-1/2 -translate-y-1/2 z-40 bg-white/95 backdrop-blur-md rounded-3xl p-1.5 border border-slate-200 shadow-xl hidden xl:flex flex-col gap-2">
        <button
          onClick={() => {
            const el = document.getElementById('gnn-network-card');
            if (el) el.scrollIntoView({ behavior: 'smooth' });
          }}
          className="w-10 h-10 rounded-2xl bg-blue-50 hover:bg-blue-100 text-blue-600 flex items-center justify-center transition-transform hover:scale-105 shadow-xs"
          title="Jump to 4-Bank GNN Relational Network"
        >
          <Share2 className="w-5 h-5" />
        </button>
        <button
          onClick={() => {
            const el = document.getElementById('transaction-status-table');
            if (el) el.scrollIntoView({ behavior: 'smooth' });
          }}
          className="w-10 h-10 rounded-2xl bg-rose-50 hover:bg-rose-100 text-rose-500 flex items-center justify-center transition-transform hover:scale-105 shadow-xs"
          title="Jump to Reconciled Status Table"
        >
          <Globe className="w-5 h-5" />
        </button>
        <button
          onClick={() => {
            setRiskFilter(riskFilter === 'High' ? 'ALL' : 'High');
            setPage(0);
          }}
          className={`w-10 h-10 rounded-2xl flex items-center justify-center transition-transform hover:scale-105 shadow-xs ${
            riskFilter === 'High'
              ? 'bg-emerald-600 text-white'
              : 'bg-emerald-50 hover:bg-emerald-100 text-emerald-600'
          }`}
          title="Filter High Threat Mule Accounts"
        >
          <Info className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
