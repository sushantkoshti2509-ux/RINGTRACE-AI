import React, { useState, useEffect } from 'react';
import { apiFetch, API_BASE } from '../api';
import { Briefcase, FileText, Download, CheckSquare, Square, Shield, UserCheck, RefreshCw } from 'lucide-react';

export default function CaseManagerView() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchCases = async () => {
    setIsLoading(true);
    try {
      const res = await apiFetch('/api/v1/platform/cases');
      if (res.ok) {
        const data = await res.json();
        setCases(data.cases || []);
        if (data.cases?.length > 0) {
          setSelectedCase(data.cases[0]);
        }
      }
    } catch (err) {
      console.error('Failed to fetch cases:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleDownloadPdf = (caseId) => {
    window.open(`${API_BASE}/api/v1/platform/cases/${caseId}/pdf`, '_blank');
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Title Card */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-cyan-400" />
            <span>Fraud Investigation Assistant & Case Management</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Automated case assembly, evidence checklists, and official ReportLab PDF dossier export
          </p>
        </div>
        <button
          onClick={fetchCases}
          disabled={isLoading}
          className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center gap-2 transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
          <span>Sync Cases</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Cases List */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col gap-3">
          <span className="text-xs font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
            Active Multi-Bank Case Files ({cases.length})
          </span>

          <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
            {cases.length === 0 ? (
              <div className="text-center py-12 text-xs text-slate-400">
                {isLoading ? 'Syncing case records...' : 'No active investigation cases.'}
              </div>
            ) : (
              cases.map((c) => (
                <div
                  key={c.case_id}
                  onClick={() => setSelectedCase(c)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    selectedCase?.case_id === c.case_id
                      ? 'bg-cyan-950/40 border-cyan-500/60 shadow-lg'
                      : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-mono font-bold text-white">{c.case_id}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                      Risk: {c.risk_score || 92}%
                    </span>
                  </div>

                  <div className="text-xs text-slate-300 font-medium">
                    {c.topology_type || 'RAPID_DISPERSION_RING'}
                  </div>

                  <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                    <span>Vol: ₹{(c.total_volume || 750000).toLocaleString()}</span>
                    <span>Status: {c.status || 'UNDER_INVESTIGATION'}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Case Details & Evidence Checklist */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl flex flex-col justify-between">
          {selectedCase ? (
            <div className="flex flex-col gap-4">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
                <div>
                  <h3 className="text-base font-bold text-white font-mono">{selectedCase.case_id}</h3>
                  <span className="text-xs text-slate-400">Topology: {selectedCase.topology_type || 'RAPID_DISPERSION_RING'}</span>
                </div>

                {/* PDF Export Button */}
                <button
                  onClick={() => handleDownloadPdf(selectedCase.case_id)}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-cyan-600/25 transition-all"
                >
                  <Download className="w-4 h-4" />
                  <span>Export PDF Dossier</span>
                </button>
              </div>

              {/* AI Summary */}
              <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800">
                <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider block mb-1">
                  AI Evidence Summary
                </span>
                <p className="text-xs text-slate-300 leading-relaxed font-sans">
                  {selectedCase.ai_summary || 'Coordinated multi-bank fund routing detected across synthetic banking institutions with near-zero resting balance and rapid pass-through velocity.'}
                </p>
              </div>

              {/* Investigator Checklist */}
              <div>
                <span className="text-xs font-bold text-white uppercase tracking-wider block mb-2">
                  Investigator Evidence Checklist:
                </span>
                <div className="space-y-2 text-xs text-slate-300 font-sans">
                  <div className="flex items-center gap-2.5 p-2 rounded-lg bg-slate-900 border border-slate-800">
                    <CheckSquare className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>Verify transaction turnaround velocity & pass-through ratios (&lt; 90s)</span>
                  </div>
                  <div className="flex items-center gap-2.5 p-2 rounded-lg bg-slate-900 border border-slate-800">
                    <CheckSquare className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>Cross-reference counterparty accounts across all participating banks</span>
                  </div>
                  <div className="flex items-center gap-2.5 p-2 rounded-lg bg-slate-900 border border-slate-800">
                    <CheckSquare className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>Check for circular transaction loops (layering evidence detected)</span>
                  </div>
                  <div className="flex items-center gap-2.5 p-2 rounded-lg bg-slate-900 border border-slate-800">
                    <Square className="w-4 h-4 text-slate-500 shrink-0" />
                    <span>Dispatch coordinated multi-bank nodal notification</span>
                  </div>
                </div>
              </div>

              {/* Participating Banks */}
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs">
                <span className="text-slate-400">Participating Banks:</span>
                <span className="font-mono text-cyan-300 font-bold">{selectedCase.banks_involved || 'BANK_A, BANK_B, BANK_C, BANK_D, BANK_E, BANK_F'}</span>
              </div>
            </div>
          ) : (
            <div className="text-center py-20 text-xs text-slate-400">
              Select a case from the left to view evidence checklist and download official PDF.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
