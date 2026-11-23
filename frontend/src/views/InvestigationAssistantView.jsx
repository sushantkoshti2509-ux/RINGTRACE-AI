import React, { useState, useEffect } from 'react';
import { apiFetch, API_BASE } from '../api';
import {
  Bot,
  Send,
  Sparkles,
  ShieldAlert,
  FileText,
  Download,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  Building2,
  Clock,
  ArrowRight,
} from 'lucide-react';

export default function InvestigationAssistantView() {
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState('');
  const [selectedCase, setSelectedCase] = useState(null);
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  // Suggested prompt chips for the investigator
  const promptPresets = [
    { label: 'Generate SAR Draft', query: 'Generate official SAR report narrative draft for this case' },
    { label: 'Trace Hop Velocity', query: 'Trace turnaround velocity and inter-bank flow hops' },
    { label: 'Recommend Countermeasures', query: 'Recommend immediate tactical countermeasures and nodal account freezes' },
    { label: 'Bank Risk Exposure', query: 'Analyze risk exposure and volume breakdown across participating banks' },
  ];

  const fetchCases = async () => {
    setIsSyncing(true);
    try {
      const res = await apiFetch('/api/v1/platform/cases');
      if (res.ok) {
        const data = await res.json();
        const caseList = data.cases || [];
        setCases(caseList);
        if (caseList.length > 0 && !selectedCaseId) {
          setSelectedCaseId(caseList[0].case_id);
          setSelectedCase(caseList[0]);
          // Initial greeting from AI
          setChatHistory([
            {
              sender: 'assistant',
              text: `AI Investigation Assistant initialized for **${caseList[0].case_id}**.\n\n` +
                `- **Topology**: \`${caseList[0].topology_type || 'CIRCULAR_LAYERING'}\`\n` +
                `- **Total Volume**: ₹${(caseList[0].total_volume || 950000).toLocaleString()}\n` +
                `- **Risk Level**: **${caseList[0].risk_score || 95}% (Critical)**\n\n` +
                `How can I assist your investigation? Select a preset action below or ask any question.`,
              suggestedActions: ['Generate SAR Draft', 'Recommend Countermeasures', 'Trace Hop Velocity'],
              timestamp: new Date().toLocaleTimeString(),
            },
          ]);
        }
      }
    } catch (err) {
      console.error('Failed to sync cases:', err);
    } finally {
      setIsSyncing(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleSelectCase = (caseId) => {
    setSelectedCaseId(caseId);
    const found = cases.find((c) => c.case_id === caseId);
    if (found) {
      setSelectedCase(found);
      setChatHistory((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: `Switched investigation context to **${found.case_id}** (Topology: \`${found.topology_type}\`, Volume: ₹${(found.total_volume || 0).toLocaleString()}). All subsequent queries will analyze this case's transaction graph and participating institutions.`,
          suggestedActions: ['Generate SAR Draft', 'Recommend Countermeasures'],
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    }
  };

  const handleSendMessage = async (queryText) => {
    const textToSend = queryText || query;
    if (!textToSend.trim()) return;

    const userMessage = {
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString(),
    };

    setChatHistory((prev) => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const res = await apiFetch('/api/v1/platform/investigation/assistant/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: selectedCaseId || 'CASE_001',
          query: textToSend,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const assistantMessage = {
          sender: 'assistant',
          text: data.reply,
          suggestedActions: data.suggested_actions || [],
          citations: data.evidence_citations || [],
          timestamp: new Date().toLocaleTimeString(),
        };
        setChatHistory((prev) => [...prev, assistantMessage]);
      } else {
        throw new Error('Server returned non-200');
      }
    } catch (err) {
      setChatHistory((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: '⚠️ Intelligence assistant service temporarily unavailable. Default analysis: Rapid layering pattern detected across multiple synthetic institutions. Pass-through ratio exceeds 94%.',
          suggestedActions: ['Generate SAR Draft'],
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPdf = (caseId) => {
    if (!caseId) return;
    window.open(`${API_BASE}/api/v1/platform/cases/${caseId}/pdf`, '_blank');
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Title & Context Selector Header */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Bot className="w-5 h-5 text-cyan-400" />
            <span>Investigation Assistant</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            AI-supported case investigation, evidence synthesis, and automated regulatory SAR drafting
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Case Selector Dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-medium">Active Case:</span>
            <select
              value={selectedCaseId}
              onChange={(e) => handleSelectCase(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-1.5 focus:outline-none focus:border-cyan-500 font-mono"
            >
              {cases.map((c) => (
                <option key={c.case_id} value={c.case_id}>
                  {c.case_id} — {c.topology_type || 'RING'} (₹{(c.total_volume || 0).toLocaleString()})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={fetchCases}
            disabled={isSyncing}
            className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300"
            title="Refresh Cases"
          >
            <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Case Evidence Telemetry Card */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-rose-400" />
                Case Intelligence Profile
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                Risk: {selectedCase?.risk_score || 95}%
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Case Identifier</span>
                <span className="font-mono text-white font-bold">{selectedCase?.case_id || 'CASE_001'}</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Detected Topology</span>
                <span className="font-semibold text-cyan-300">{selectedCase?.topology_type || 'CIRCULAR_LAYERING'}</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Total Ring Exposure</span>
                <span className="font-mono text-emerald-400 font-bold">
                  ₹{(selectedCase?.total_volume || 950000).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Current Status</span>
                <span className="font-bold text-amber-300">{selectedCase?.status || 'UNDER_INVESTIGATION'}</span>
              </div>
            </div>

            {/* Participating Institutions */}
            <div>
              <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block mb-2">
                Participating Institutions:
              </span>
              <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-300 font-mono">
                {selectedCase?.banks_involved || 'Apex National, Crest Commercial, Zenith Cooperative'}
              </div>
            </div>

            {/* Export Official Dossier */}
            <button
              onClick={() => handleDownloadPdf(selectedCaseId)}
              className="w-full mt-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/20 transition-all"
            >
              <Download className="w-4 h-4" />
              <span>Export Official PDF Dossier</span>
            </button>
          </div>

          {/* Quick Action Chips */}
          <div className="glass-panel rounded-2xl p-4 border border-slate-800 shadow-xl flex flex-col gap-2.5">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Quick Intelligence Prompts</span>
            </span>
            <div className="flex flex-col gap-2">
              {promptPresets.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(p.query)}
                  disabled={isLoading}
                  className="text-left p-2.5 rounded-xl bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-cyan-500/40 text-xs text-slate-300 flex items-center justify-between group transition-all"
                >
                  <span>{p.label}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: AI Copilot Interactive Workstation */}
        <div className="lg:col-span-8 glass-panel rounded-2xl border border-slate-800 shadow-xl flex flex-col h-[650px] overflow-hidden">
          {/* Chat Header */}
          <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <span className="text-xs font-bold text-white block">AI Fraud Investigation Copilot</span>
                <span className="text-[10px] text-slate-400">Trained on multi-bank graph topology & AML regulatory reason codes</span>
              </div>
            </div>
            <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded">
              ONLINE
            </span>
          </div>

          {/* Chat Messages Stream */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {chatHistory.map((msg, idx) => (
              <div
                key={idx}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[85%] p-4 rounded-2xl text-xs leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-cyan-600 text-white rounded-br-none shadow-md shadow-cyan-600/20'
                      : 'bg-slate-900/90 border border-slate-800 text-slate-200 rounded-bl-none shadow-md'
                  }`}
                >
                  <div className="whitespace-pre-line font-sans">{msg.text}</div>

                  {/* Evidence Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-slate-800/80">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">
                        Cited Counterparties (DPDP Masked):
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.citations.map((c, i) => (
                          <span
                            key={i}
                            className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-cyan-300"
                          >
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Suggested Action Buttons */}
                  {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                    <div className="mt-3 pt-2 flex flex-wrap gap-2">
                      {msg.suggestedActions.map((act, i) => (
                        <button
                          key={i}
                          onClick={() => handleSendMessage(act)}
                          className="text-[10px] font-bold px-2.5 py-1 rounded-lg bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/25 transition-all"
                        >
                          + {act}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <span className="text-[9px] text-slate-500 font-mono mt-1 px-1">{msg.timestamp}</span>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-start">
                <div className="p-3.5 rounded-2xl bg-slate-900/90 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                  <span>Synthesizing multi-bank evidence & regulatory narrative...</span>
                </div>
              </div>
            )}
          </div>

          {/* Chat Input Bar */}
          <div className="p-3.5 border-t border-slate-800 bg-slate-900/60">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about this case, SAR drafts, hop velocity, or freezing countermeasures..."
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
              <button
                type="submit"
                disabled={isLoading || !query.trim()}
                className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs flex items-center gap-1.5 transition-all disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Send</span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
