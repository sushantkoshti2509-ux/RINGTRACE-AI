import React, { useState, useEffect } from 'react';
import { apiFetch, API_BASE } from '../api';
import {
  FolderSearch,
  FileText,
  Download,
  CheckSquare,
  Square,
  Shield,
  UserCheck,
  RefreshCw,
  Save,
  MessageSquare,
  ShieldAlert,
  Building2,
  Check,
} from 'lucide-react';

const getCaseTopology = (c) => {
  if (!c) return 'RAPID_DISPERSION_RING';
  if (c.topology_type) return c.topology_type;
  if (Array.isArray(c.detected_patterns) && c.detected_patterns.length > 0) return c.detected_patterns[0];
  if (typeof c.detected_patterns === 'string') {
    try {
      const parsed = JSON.parse(c.detected_patterns);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed[0];
    } catch {
      return c.detected_patterns;
    }
  }
  if (c.title && c.title.includes(' - ')) {
    return c.title.split(' - ').pop().trim();
  }
  return 'RAPID_DISPERSION_RING';
};

const parseBanks = (banks) => {
  if (!banks) return ['BANK_A', 'BANK_B', 'BANK_C'];
  if (Array.isArray(banks)) return banks;
  if (typeof banks === 'string') {
    try {
      const parsed = JSON.parse(banks);
      if (Array.isArray(parsed)) return parsed;
    } catch {
      // not json
    }
    return banks.split(',').map((b) => b.trim()).filter(Boolean);
  }
  return ['BANK_A', 'BANK_B', 'BANK_C'];
};

const BANK_STYLES = {
  BANK_A: 'bg-blue-50 text-blue-800 border-blue-200',
  BANK_B: 'bg-emerald-50 text-emerald-800 border-emerald-200',
  BANK_C: 'bg-purple-50 text-purple-800 border-purple-200',
  BANK_D: 'bg-amber-50 text-amber-800 border-amber-200',
};

export default function CaseManagerView() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [disposition, setDisposition] = useState('UNDER_INVESTIGATION');
  const [investigatorNote, setInvestigatorNote] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [checklist, setChecklist] = useState({
    velocity: true,
    counterparties: true,
    circular: true,
    notification: false,
  });

  const fetchCases = async () => {
    setIsLoading(true);
    try {
      const res = await apiFetch('/api/v1/platform/cases');
      if (res.ok) {
        const data = await res.json();
        const caseList = data.cases || [];
        setCases(caseList);
        if (caseList.length > 0) {
          const current = selectedCase ? caseList.find((c) => c.case_id === selectedCase.case_id) || caseList[0] : caseList[0];
          setSelectedCase(current);
          setDisposition(current.status || 'UNDER_INVESTIGATION');
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

  const handleUpdateDisposition = async () => {
    if (!selectedCase) return;
    setIsUpdating(true);
    try {
      const res = await apiFetch(`/api/v1/platform/cases/${selectedCase.case_id}/disposition`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          disposition: disposition,
          notes: investigatorNote || 'Investigator reviewed multi-bank topological evidence.',
        }),
      });
      if (res.ok) {
        setInvestigatorNote('');
        setSavedSuccess(true);
        setTimeout(() => setSavedSuccess(false), 2500);
        fetchCases();
      }
    } catch (err) {
      console.error('Failed to update disposition:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  const selectedBanks = parseBanks(selectedCase?.banks_involved);
  const selectedTopology = getCaseTopology(selectedCase);

  return (
    <div className="flex flex-col gap-6">
      {/* Title Card */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 shrink-0">
            <FolderSearch className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
              <span>Case Management & Evidence Dossiers</span>
            </h2>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Review synchronized case files, verify investigator checklists, and export regulatory filings
            </p>
          </div>
        </div>

        <button
          onClick={fetchCases}
          disabled={isLoading}
          className="px-4 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 hover:text-slate-900 text-xs font-bold border border-slate-300 shadow-xs flex items-center gap-2 transition-all cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
          <span>Sync Cases</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Cases List */}
        <div className="lg:col-span-5 bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col gap-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider">
              Active Multi-Bank Case Files ({cases.length})
            </span>
            <span className="text-[10px] font-mono font-extrabold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
              DPDP 2023
            </span>
          </div>

          <div className="space-y-2.5 max-h-[580px] overflow-y-auto pr-1">
            {cases.length === 0 ? (
              <div className="text-center py-16 text-xs text-slate-500 font-semibold">
                {isLoading ? 'Syncing case records from cross-bank graph...' : 'No active investigation cases.'}
              </div>
            ) : (
              cases.map((c) => {
                const topo = getCaseTopology(c);
                const isSelected = selectedCase?.case_id === c.case_id;
                return (
                  <div
                    key={c.case_id}
                    onClick={() => {
                      setSelectedCase(c);
                      setDisposition(c.status || 'UNDER_INVESTIGATION');
                    }}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-blue-50/80 border-blue-400 shadow-sm'
                        : 'bg-slate-50/60 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="font-mono font-extrabold text-slate-900 text-sm">{c.case_id}</span>
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold font-mono bg-rose-50 text-rose-700 border border-rose-200">
                        Risk: {c.risk_score || 94.8}%
                      </span>
                    </div>

                    <div className="text-xs text-blue-800 font-bold mb-2">
                      {topo}
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-slate-600 font-mono font-medium pt-1.5 border-t border-slate-200/60">
                      <span>Vol: ₹{(c.total_volume || 750000).toLocaleString('en-IN')}</span>
                      <span className="font-bold text-slate-800">{c.status || 'UNDER_INVESTIGATION'}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Case Details & Evidence Checklist */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between">
          {selectedCase ? (
            <div className="flex flex-col gap-5">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-extrabold text-slate-900 font-mono">{selectedCase.case_id}</h3>
                    <span className="text-xs font-extrabold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded-md">
                      {selectedTopology}
                    </span>
                  </div>
                  <span className="text-xs text-slate-500 font-medium mt-0.5 block">
                    Exposure: ₹{(selectedCase.total_volume || 0).toLocaleString('en-IN')} • {selectedCase.transactions_count || 15} transactions
                  </span>
                </div>

                {/* PDF Export Button */}
                <button
                  onClick={() => handleDownloadPdf(selectedCase.case_id)}
                  className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 shadow-md shadow-blue-500/20 transition-all cursor-pointer"
                >
                  <Download className="w-4 h-4" />
                  <span>Export Official PDF Dossier</span>
                </button>
              </div>

              {/* AI Summary */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-xs font-extrabold text-blue-900 uppercase tracking-wider block mb-1.5 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-blue-600" />
                  AI Evidence Summary
                </span>
                <p className="text-xs text-slate-700 leading-relaxed font-medium">
                  {selectedCase.ai_summary ||
                    'Coordinated multi-bank fund routing detected across synthetic banking institutions with near-zero resting balance and rapid pass-through velocity.'}
                </p>
              </div>

              {/* Investigator Checklist */}
              <div>
                <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider block mb-2.5">
                  Investigator Evidence Verification:
                </span>
                <div className="space-y-2 text-xs text-slate-800">
                  <div
                    onClick={() => setChecklist((prev) => ({ ...prev, velocity: !prev.velocity }))}
                    className="flex items-center gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-200 cursor-pointer hover:bg-blue-50/50 hover:border-blue-200 transition-all"
                  >
                    {checklist.velocity ? (
                      <CheckSquare className="w-4 h-4 text-emerald-600 shrink-0" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-400 shrink-0" />
                    )}
                    <span className="font-semibold text-slate-800">
                      Verify transaction turnaround velocity & pass-through ratios (&lt; 90s)
                    </span>
                  </div>
                  <div
                    onClick={() => setChecklist((prev) => ({ ...prev, counterparties: !prev.counterparties }))}
                    className="flex items-center gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-200 cursor-pointer hover:bg-blue-50/50 hover:border-blue-200 transition-all"
                  >
                    {checklist.counterparties ? (
                      <CheckSquare className="w-4 h-4 text-emerald-600 shrink-0" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-400 shrink-0" />
                    )}
                    <span className="font-semibold text-slate-800">
                      Cross-reference counterparty accounts across all participating banks
                    </span>
                  </div>
                  <div
                    onClick={() => setChecklist((prev) => ({ ...prev, circular: !prev.circular }))}
                    className="flex items-center gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-200 cursor-pointer hover:bg-blue-50/50 hover:border-blue-200 transition-all"
                  >
                    {checklist.circular ? (
                      <CheckSquare className="w-4 h-4 text-emerald-600 shrink-0" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-400 shrink-0" />
                    )}
                    <span className="font-semibold text-slate-800">
                      Check for circular transaction loops (layering evidence detected)
                    </span>
                  </div>
                  <div
                    onClick={() => setChecklist((prev) => ({ ...prev, notification: !prev.notification }))}
                    className="flex items-center gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-200 cursor-pointer hover:bg-blue-50/50 hover:border-blue-200 transition-all"
                  >
                    {checklist.notification ? (
                      <CheckSquare className="w-4 h-4 text-emerald-600 shrink-0" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-400 shrink-0" />
                    )}
                    <span className="font-semibold text-slate-800">
                      Dispatch coordinated multi-bank nodal notification
                    </span>
                  </div>
                </div>
              </div>

              {/* Status & Disposition Update Form */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <UserCheck className="w-4 h-4 text-blue-600" />
                    <span>Update Case Disposition & Investigator Notes</span>
                  </span>
                  {savedSuccess && (
                    <span className="text-xs font-extrabold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded flex items-center gap-1">
                      <Check className="w-3 h-3" />
                      Saved
                    </span>
                  )}
                </div>

                <div className="flex flex-col md:flex-row gap-3">
                  <select
                    value={disposition}
                    onChange={(e) => setDisposition(e.target.value)}
                    className="bg-white border border-slate-300 text-xs font-bold text-slate-900 rounded-xl px-3 py-2.5 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 font-mono shadow-xs cursor-pointer"
                  >
                    <option value="UNDER_INVESTIGATION">UNDER_INVESTIGATION</option>
                    <option value="ESCALATED_REGULATORY">ESCALATED_REGULATORY</option>
                    <option value="ACCOUNT_FREEZE_ORDERED">ACCOUNT_FREEZE_ORDERED</option>
                    <option value="SAR_FILED">SAR_FILED</option>
                    <option value="CLOSED_CLEARED">CLOSED_CLEARED</option>
                  </select>

                  <input
                    type="text"
                    value={investigatorNote}
                    onChange={(e) => setInvestigatorNote(e.target.value)}
                    placeholder="Add investigator findings or evidence notes..."
                    className="flex-1 bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 shadow-xs"
                  />

                  <button
                    onClick={handleUpdateDisposition}
                    disabled={isUpdating}
                    className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-blue-500/20 shrink-0 cursor-pointer disabled:opacity-50"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>{isUpdating ? 'Saving...' : 'Save Update'}</span>
                  </button>
                </div>
              </div>

              {/* Participating Banks */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-2 text-xs">
                <span className="text-slate-600 font-bold uppercase text-[11px]">Participating Banks:</span>
                <div className="flex flex-wrap gap-1.5">
                  {selectedBanks.map((b, i) => {
                    const badge = BANK_STYLES[b] || 'bg-slate-100 text-slate-800 border-slate-200';
                    return (
                      <span key={i} className={`font-mono text-xs font-extrabold px-2 py-0.5 rounded border ${badge}`}>
                        {b}
                      </span>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-20 text-xs text-slate-500 font-semibold">
              Select a case from the left to view evidence checklist and download official PDF.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
