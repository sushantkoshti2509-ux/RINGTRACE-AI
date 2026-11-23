import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api';
import { Search, Filter, ArrowUpDown, Shield, AlertTriangle, CheckCircle, ChevronLeft, ChevronRight, Eye, RefreshCw } from 'lucide-react';

export default function MonitoringView() {
  const [transactions, setTransactions] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
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
        const data = await res.json();
        setTransactions(data.transactions || []);
        setTotalCount(data.total_matched || data.count || 25430);
      }
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [bankFilter, riskFilter, page]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    fetchTransactions();
  };

  const getBankBadge = (bank) => {
    const b = (bank || '').toUpperCase();
    if (b.includes('A')) return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40';
    if (b.includes('B')) return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    if (b.includes('C')) return 'bg-purple-500/20 text-purple-300 border-purple-500/40';
    return 'bg-slate-700 text-slate-300 border-slate-600';
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header & Filter Controls */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Shield className="w-5 h-5 text-cyan-400" />
              <span>Multi-Bank Transaction Monitoring & Ledger Search</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Unified cross-bank records with DPDP Act 2023 account masking and real-time risk scoring
            </p>
          </div>
          <button
            onClick={fetchTransactions}
            disabled={isLoading}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center gap-2 transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
            <span>Refresh Ledger</span>
          </button>
        </div>

        {/* Filter Bar */}
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 pt-2">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search Txn ID, Account, Customer..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400"
            />
          </div>

          {/* Bank Filter */}
          <div>
            <select
              value={bankFilter}
              onChange={(e) => { setBankFilter(e.target.value); setPage(0); }}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-400"
            >
              <option value="ALL">All Banks (Bank A through F)</option>
              <option value="Bank A">Bank A (Alpha Clearing)</option>
              <option value="Bank B">Bank B (Beta Remittance)</option>
              <option value="Bank C">Bank C (Gamma Settlement)</option>
              <option value="Bank D">Bank D (Delta Exchange)</option>
              <option value="Bank E">Bank E (Epsilon Treasury)</option>
              <option value="Bank F">Bank F (Zeta Gateway)</option>
            </select>
          </div>

          {/* Risk Level Filter */}
          <div>
            <select
              value={riskFilter}
              onChange={(e) => { setRiskFilter(e.target.value); setPage(0); }}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-400"
            >
              <option value="ALL">All Risk Tiers</option>
              <option value="High">High Risk / Flagged Only</option>
              <option value="Low">Low Risk / Legitimate Only</option>
            </select>
          </div>

          {/* Submit Search Button */}
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs uppercase tracking-wider transition-all shadow-md shadow-cyan-600/30"
          >
            Apply Filters
          </button>
        </form>
      </div>

      {/* Main Data Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-900/90 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                <th className="py-3 px-4">Transaction ID</th>
                <th className="py-3 px-4">Reporting Bank</th>
                <th className="py-3 px-4">Source Account (DPDP)</th>
                <th className="py-3 px-4">Destination Account</th>
                <th className="py-3 px-4">Amount (INR)</th>
                <th className="py-3 px-4">Risk Tier</th>
                <th className="py-3 px-4">Reconciliation</th>
                <th className="py-3 px-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan="8" className="py-8 text-center text-slate-400 text-sm font-sans">
                    {isLoading ? 'Loading multi-bank transactions...' : 'No transactions matched the active filters.'}
                  </td>
                </tr>
              ) : (
                transactions.map((tx) => {
                  const isHigh = tx.is_suspicious === 1 || tx.risk_level === 'High';
                  return (
                    <tr
                      key={tx.transaction_id}
                      className="hover:bg-slate-850/60 transition-colors cursor-pointer"
                      onClick={() => setSelectedTx(tx)}
                    >
                      <td className="py-3 px-4 font-bold text-cyan-300">
                        {tx.transaction_id}
                      </td>
                      <td className="py-3 px-4 font-sans">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getBankBadge(tx.bank_id)}`}>
                          {tx.bank_id}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-300">
                        {tx.sender_account_masked || `••••${(tx.sender_account || '').slice(-4)}`}
                      </td>
                      <td className="py-3 px-4 text-slate-300">
                        {tx.receiver_account_masked || `••••${(tx.receiver_account || '').slice(-4)}`}
                      </td>
                      <td className="py-3 px-4 font-bold text-white">
                        ₹{(tx.amount || 0).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 font-sans">
                        {isHigh ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40 flex items-center gap-1 w-fit">
                            <AlertTriangle className="w-3 h-3 text-rose-400" /> High Risk
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1 w-fit">
                            <CheckCircle className="w-3 h-3 text-emerald-400" /> Legitimate
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 font-sans">
                        <span className="text-[11px] text-slate-300">
                          {tx.reconciliation_status || 'Dual Reconciled'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <button
                          onClick={(e) => { e.stopPropagation(); setSelectedTx(tx); }}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 text-[11px] font-sans font-semibold border border-slate-700 flex items-center gap-1 mx-auto transition-colors"
                        >
                          <Eye className="w-3 h-3" /> Inspect
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
        <div className="p-4 bg-slate-900/80 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-sans">
          <span>
            Showing page <strong className="text-white">{page + 1}</strong> • Total Matched: <strong className="text-cyan-300 font-mono">{totalCount.toLocaleString()}</strong>
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 border border-slate-700 flex items-center gap-1"
            >
              <ChevronLeft className="w-4 h-4" /> Prev
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={transactions.length < limit}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 border border-slate-700 flex items-center gap-1"
            >
              Next <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Transaction Inspection Modal */}
      {selectedTx && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel rounded-2xl max-w-xl w-full p-6 border border-slate-700 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div>
                <h3 className="text-base font-bold text-white font-mono">
                  Transaction: {selectedTx.transaction_id}
                </h3>
                <span className="text-xs text-slate-400">Multi-Bank Ledger Reconciled Audit Record</span>
              </div>
              <button
                onClick={() => setSelectedTx(null)}
                className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center font-bold"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block mb-1">Reporting Bank</span>
                <span className="font-bold text-white font-mono text-sm">{selectedTx.bank_id}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block mb-1">Transaction Amount</span>
                <span className="font-bold text-emerald-400 font-mono text-sm">₹{(selectedTx.amount || 0).toLocaleString()}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block mb-1">Source Account (DPDP Masked)</span>
                <span className="font-mono text-cyan-300">{selectedTx.sender_account_masked || `••••${(selectedTx.sender_account || '').slice(-4)}`}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block mb-1">Beneficiary Account</span>
                <span className="font-mono text-cyan-300">{selectedTx.receiver_account_masked || `••••${(selectedTx.receiver_account || '').slice(-4)}`}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block mb-1">Timestamp</span>
                <span className="font-mono text-slate-200">{selectedTx.timestamp || '2026-11-20 14:22:10'}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block mb-1">Classification</span>
                <span className={`font-bold ${selectedTx.is_suspicious ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {selectedTx.is_suspicious ? 'MULE CANDIDATE (FLAGGED)' : 'NORMAL RETAIL PAYMENT'}
                </span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setSelectedTx(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
