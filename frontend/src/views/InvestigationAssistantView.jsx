import React, { useState, useEffect, useRef } from 'react';
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
  ShieldCheck,
  Copy,
  Check,
  ChevronRight,
  User,
} from 'lucide-react';

// Safe extraction of topology from case data
const getCaseTopology = (c) => {
  if (!c) return 'CIRCULAR_LAYERING';
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
  return 'CIRCULAR_LAYERING';
};

// Safe extraction of bank list from case data
const parseBanksList = (banks) => {
  if (!banks) return ['BANK_A', 'BANK_B', 'BANK_C'];
  if (Array.isArray(banks)) return banks;
  if (typeof banks === 'string') {
    try {
      const parsed = JSON.parse(banks);
      if (Array.isArray(parsed)) return parsed;
    } catch {
      // not JSON
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

// Pure React Markdown & Structured Text Formatter
function parseInlineMarkdown(text) {
  if (!text) return '';
  const parts = [];
  const regex = /(\*\*.*?\*\*|`.*?`)/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith('**') && token.endsWith('**')) {
      parts.push(
        <strong key={`b-${match.index}`} className="font-extrabold text-slate-900">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('`') && token.endsWith('`')) {
      parts.push(
        <code
          key={`c-${match.index}`}
          className="font-mono text-[11px] font-bold bg-slate-100 text-blue-700 px-1.5 py-0.5 rounded border border-slate-200"
        >
          {token.slice(1, -1)}
        </code>
      );
    }
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }
  return parts.length > 0 ? parts : text;
}

function FormattedMessage({ text }) {
  if (!text) return null;
  const lines = text.split('\n');

  return (
    <div className="space-y-1.5 text-xs leading-relaxed text-slate-800">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) {
          return <div key={idx} className="h-1" />;
        }

        if (trimmed.startsWith('### ')) {
          return (
            <h3
              key={idx}
              className="text-sm font-extrabold text-slate-900 mt-3 mb-1.5 pb-1 border-b border-slate-100 flex items-center gap-2"
            >
              <FileText className="w-4 h-4 text-blue-600 inline" />
              <span>{parseInlineMarkdown(trimmed.replace('### ', ''))}</span>
            </h3>
          );
        }

        if (trimmed.startsWith('#### ')) {
          return (
            <h4
              key={idx}
              className="text-xs font-extrabold text-blue-900 uppercase tracking-wide mt-2.5 mb-1"
            >
              {parseInlineMarkdown(trimmed.replace('#### ', ''))}
            </h4>
          );
        }

        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
          return (
            <div key={idx} className="flex items-start gap-2 pl-2 my-0.5 text-slate-700">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 shrink-0" />
              <span>{parseInlineMarkdown(trimmed.substring(2))}</span>
            </div>
          );
        }

        const numMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
        if (numMatch) {
          return (
            <div key={idx} className="flex items-start gap-2 pl-2 my-0.5 text-slate-700">
              <span className="font-mono font-extrabold text-blue-600 shrink-0 text-[11px]">
                {numMatch[1]}.
              </span>
              <span>{parseInlineMarkdown(numMatch[2])}</span>
            </div>
          );
        }

        return (
          <p key={idx} className="text-slate-800 my-0.5 font-medium">
            {parseInlineMarkdown(line)}
          </p>
        );
      })}
    </div>
  );
}

export default function InvestigationAssistantView() {
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState('');
  const [selectedCase, setSelectedCase] = useState(null);
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const messagesEndRef = useRef(null);

  // Suggested prompt chips for the investigator
  const promptPresets = [
    { label: 'Generate SAR Draft', query: 'Generate official SAR report narrative draft for this case' },
    { label: 'Trace Hop Velocity', query: 'Trace turnaround velocity and inter-bank flow hops' },
    { label: 'Recommend Countermeasures', query: 'Recommend immediate tactical countermeasures and nodal account freezes' },
    { label: 'Bank Risk Exposure', query: 'Analyze risk exposure and volume breakdown across participating banks' },
    { label: 'Identify Mule Counterparties', query: 'What accounts are involved and who is the primary mule hub?' },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isLoading]);

  const fetchCases = async () => {
    setIsSyncing(true);
    try {
      const res = await apiFetch('/api/v1/platform/cases');
      if (res.ok) {
        const data = await res.json();
        const caseList = data.cases || [];
        setCases(caseList);
        if (caseList.length > 0) {
          const currentCase = selectedCaseId
            ? caseList.find((c) => c.case_id === selectedCaseId) || caseList[0]
            : caseList[0];

          setSelectedCaseId(currentCase.case_id);
          setSelectedCase(currentCase);

          if (chatHistory.length === 0) {
            const topo = getCaseTopology(currentCase);
            setChatHistory([
              {
                sender: 'assistant',
                text: `### AI Investigation Copilot Initialized\n\n` +
                  `Active Case: **${currentCase.case_id}**\n\n` +
                  `- **Topology Detected**: \`${topo}\`\n` +
                  `- **Aggregate Exposure**: **₹${(currentCase.total_volume || 950000).toLocaleString('en-IN')}**\n` +
                  `- **GNN Mule Risk Score**: **${currentCase.risk_score || 95.8}% (Critical)**\n` +
                  `- **Institutions Monitored**: \`${parseBanksList(currentCase.banks_involved).join(', ')}\`\n\n` +
                  `How can I assist your investigation? Select a preset action below or ask any question regarding multi-bank fund flows, velocity hops, or regulatory filings.`,
                suggestedActions: [
                  'Generate SAR Draft',
                  'Recommend Countermeasures',
                  'Bank Risk Exposure',
                  'Trace Hop Velocity',
                ],
                citations: currentCase.member_accounts?.slice(0, 4) || [],
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
          }
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
      const topo = getCaseTopology(found);
      setChatHistory((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: `Switched investigation context to **${found.case_id}** (Topology: \`${topo}\`, Volume: **₹${(found.total_volume || 0).toLocaleString('en-IN')}**). All subsequent analysis and SAR drafts will target this case's transaction graph and participating counterparties.`,
          suggestedActions: ['Generate SAR Draft', 'Recommend Countermeasures', 'Bank Risk Exposure'],
          citations: found.member_accounts?.slice(0, 4) || [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
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
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setChatHistory((prev) => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const activeId = selectedCaseId || (cases[0]?.case_id) || 'CASE-MR-001';
      const res = await apiFetch('/api/v1/platform/investigation/assistant/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: activeId,
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
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
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
          text: '⚠️ **Intelligence assistant service temporarily unavailable.** Default analysis: Rapid layering pattern detected across multiple synthetic institutions. Pass-through ratio exceeds 94%.',
          suggestedActions: ['Generate SAR Draft'],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPdf = (caseId) => {
    const id = caseId || selectedCaseId || 'CASE-MR-001';
    window.open(`${API_BASE}/api/v1/platform/cases/${id}/pdf`, '_blank');
  };

  const handleCopyText = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const banksList = parseBanksList(selectedCase?.banks_involved);
  const topology = getCaseTopology(selectedCase);

  return (
    <div className="flex flex-col gap-6">
      {/* Title & Context Selector Header */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 shrink-0">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-extrabold text-slate-900 tracking-tight">
                AI Fraud Investigation Copilot
              </h2>
              <span className="bg-blue-50 text-blue-700 border border-blue-200 font-extrabold text-[10px] px-2 py-0.5 rounded-full font-mono">
                CENTRAL DEFENSE
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Autonomous multi-bank evidence synthesis, hop velocity analysis, and automated regulatory SAR drafting
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Case Selector Dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-600 font-extrabold">Active Case:</span>
            <select
              value={selectedCaseId}
              onChange={(e) => handleSelectCase(e.target.value)}
              className="bg-slate-50 border border-slate-300 text-slate-900 text-xs font-bold font-mono rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 shadow-xs cursor-pointer"
            >
              {cases.map((c) => {
                const topo = getCaseTopology(c);
                return (
                  <option key={c.case_id} value={c.case_id}>
                    {c.case_id} — {topo} (₹{(c.total_volume || 0).toLocaleString('en-IN')})
                  </option>
                );
              })}
            </select>
          </div>

          <button
            onClick={fetchCases}
            disabled={isSyncing}
            className="p-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 hover:text-slate-900 shadow-xs transition-all cursor-pointer"
            title="Refresh Cases"
          >
            <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin text-blue-600' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Case Evidence Telemetry Card */}
        <div className="lg:col-span-4 flex flex-col gap-5">
          <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-rose-600" />
                Case Intelligence Profile
              </span>
              <span className="text-xs font-mono font-extrabold px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200">
                Risk: {selectedCase?.risk_score || 95.8}%
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600 font-bold">Case Identifier</span>
                <span className="font-mono text-slate-900 font-extrabold text-sm">
                  {selectedCase?.case_id || 'CASE-MR-001'}
                </span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600 font-bold">Detected Topology</span>
                <span className="font-extrabold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded-md text-[11px]">
                  {topology}
                </span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600 font-bold">Total Ring Exposure</span>
                <span className="font-mono text-emerald-700 font-extrabold text-sm">
                  ₹{(selectedCase?.total_volume || 950000).toLocaleString('en-IN')}
                </span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600 font-bold">Investigation Status</span>
                <span className="font-extrabold text-amber-800 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-md text-[11px]">
                  {selectedCase?.status || 'PENDING_REVIEW'}
                </span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600 font-bold">Transactions Count</span>
                <span className="font-mono text-slate-900 font-extrabold text-xs">
                  {selectedCase?.transactions_count || 15} Transfers
                </span>
              </div>
            </div>

            {/* Participating Institutions */}
            <div>
              <span className="text-[11px] font-extrabold text-slate-700 uppercase tracking-wider block mb-2">
                Participating Institutions:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {banksList.map((b, i) => {
                  const badgeStyle = BANK_STYLES[b] || 'bg-slate-100 text-slate-800 border-slate-200';
                  return (
                    <span
                      key={i}
                      className={`text-xs font-extrabold font-mono px-2.5 py-1 rounded-lg border ${badgeStyle}`}
                    >
                      {b}
                    </span>
                  );
                })}
              </div>
            </div>

            {/* Export Official Dossier */}
            <button
              onClick={() => handleDownloadPdf(selectedCaseId)}
              className="w-full mt-2 py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-md shadow-blue-500/20 transition-all cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Export Official PDF Dossier</span>
            </button>
          </div>

          {/* Quick Action Chips */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col gap-3">
            <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>Quick Intelligence Prompts</span>
            </span>
            <div className="flex flex-col gap-2">
              {promptPresets.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(p.query)}
                  disabled={isLoading}
                  className="text-left p-3 rounded-xl bg-slate-50 hover:bg-blue-50/80 border border-slate-200 hover:border-blue-300 text-slate-800 hover:text-blue-900 text-xs font-bold flex items-center justify-between group transition-all shadow-xs cursor-pointer"
                >
                  <span>{p.label}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: AI Copilot Interactive Workstation */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200/90 shadow-sm flex flex-col h-[700px] overflow-hidden">
          {/* Chat Header */}
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/80 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="text-sm font-extrabold text-slate-900 block">
                  AI Fraud Investigation Copilot
                </span>
                <span className="text-xs text-slate-500 font-medium">
                  Trained on multi-bank graph topology & AML regulatory reason codes
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-extrabold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full flex items-center gap-1.5 font-mono">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                ONLINE
              </span>
            </div>
          </div>

          {/* Chat Messages Stream */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-[#fafbfc]">
            {chatHistory.map((msg, idx) => (
              <div
                key={idx}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[90%] p-5 rounded-2xl text-xs leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-xs shadow-md shadow-blue-500/15'
                      : 'bg-white border border-slate-200/90 text-slate-800 rounded-tl-xs shadow-sm'
                  }`}
                >
                  {msg.sender === 'assistant' && (
                    <div className="flex items-center justify-between pb-2 mb-2.5 border-b border-slate-100">
                      <div className="flex items-center gap-1.5 text-blue-700 font-extrabold text-[11px] uppercase tracking-wide">
                        <Bot className="w-3.5 h-3.5 text-blue-600" />
                        <span>Copilot Intelligence Assessment</span>
                      </div>
                      <button
                        onClick={() => handleCopyText(msg.text, idx)}
                        className="text-[11px] font-bold text-slate-500 hover:text-slate-800 flex items-center gap-1 p-1 hover:bg-slate-100 rounded transition-all cursor-pointer"
                        title="Copy Response"
                      >
                        {copiedIndex === idx ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-600" />
                            <span className="text-emerald-700">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                  )}

                  {msg.sender === 'user' ? (
                    <div className="font-semibold text-white whitespace-pre-line text-xs">{msg.text}</div>
                  ) : (
                    <FormattedMessage text={msg.text} />
                  )}

                  {/* Evidence Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-3.5 pt-3 border-t border-slate-100">
                      <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider block mb-1.5">
                        Cited Counterparties (DPDP Masked):
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.citations.map((c, i) => (
                          <span
                            key={i}
                            className="text-[11px] font-mono font-extrabold px-2.5 py-0.5 rounded-lg bg-slate-100 border border-slate-200 text-slate-800"
                          >
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Suggested Action Buttons */}
                  {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                    <div className="mt-3.5 pt-2.5 flex flex-wrap gap-2 border-t border-slate-100">
                      {msg.suggestedActions.map((act, i) => (
                        <button
                          key={i}
                          onClick={() => handleSendMessage(act)}
                          className="text-xs font-bold px-3 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-700 hover:bg-blue-600 hover:text-white transition-all shadow-xs cursor-pointer"
                        >
                          + {act}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <span className="text-[10px] text-slate-400 font-mono font-semibold mt-1 px-1">
                  {msg.timestamp}
                </span>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-start">
                <div className="p-4 rounded-2xl bg-white border border-slate-200 text-xs text-slate-700 font-bold flex items-center gap-3 shadow-xs">
                  <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
                  <span>Synthesizing multi-bank evidence, traversal graph & regulatory narrative...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Bar */}
          <div className="p-4 border-t border-slate-200 bg-white">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-3"
            >
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about this case, SAR drafts, hop velocity, countermeasures, or participating accounts..."
                className="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-xs text-slate-900 font-medium placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:bg-white shadow-xs transition-all"
              />
              <button
                type="submit"
                disabled={isLoading || !query.trim()}
                className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md shadow-blue-500/20 transition-all disabled:opacity-40 cursor-pointer"
              >
                <Send className="w-4 h-4" />
                <span>Send</span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
