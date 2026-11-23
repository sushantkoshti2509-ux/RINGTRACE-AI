import React from 'react';
import {
  LayoutGrid,
  Network,
  Brain,
  Bot,
  FolderSearch,
  TrendingUp,
  ShieldAlert,
  Zap,
  Globe,
  Lock,
  Shield,
  Cpu,
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  // Exact 6 core platform fields requested by specification
  const primaryNavItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      subtitle: 'Existing detection and statistics',
      icon: LayoutGrid,
      badge: '27.7k',
    },
    {
      id: 'network',
      label: 'Network Explorer',
      subtitle: 'Cross-bank fraud connections',
      icon: Network,
      badge: '33 RINGS',
    },
    {
      id: 'xai',
      label: 'Explainable AI',
      subtitle: 'SHAP prediction explanations',
      icon: Brain,
      badge: 'SHAP',
    },
    {
      id: 'assistant',
      label: 'Investigation Assistant',
      subtitle: 'AI-supported case investigation',
      icon: Bot,
      badge: 'AI COPILOT',
    },
    {
      id: 'cases',
      label: 'Case Management',
      subtitle: 'Evidence, notes and reports',
      icon: FolderSearch,
      badge: 'DOSSIER',
    },
    {
      id: 'analytics',
      label: 'Advanced Analytics',
      subtitle: 'Bank-wise and network analytics',
      icon: TrendingUp,
      badge: '4 BANKS',
    },
  ];

  const secondaryNavItems = [
    { id: 'gnn', label: 'GNN Intelligence Center', icon: Cpu, badge: 'PHASE 7' },
    { id: 'interception', label: 'Interception & ROI Simulator', icon: ShieldAlert, badge: 'PROACTIVE' },
    { id: 'digital_twin', label: 'Digital Twin Simulator', icon: Zap, badge: 'SIMULATOR' },
    { id: 'globe3d', label: '3D Cyber Clearing Fabric', icon: Globe, badge: '3D' },
  ];

  return (
    <aside className="w-64 glass-panel border-r border-slate-800 flex flex-col justify-between shrink-0 h-screen sticky top-0 overflow-y-auto">
      {/* Brand Header */}
      <div>
        <div className="p-5 border-b border-slate-800 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-extrabold text-base text-white tracking-tight flex items-center gap-1.5">
              <span>RINGTRACE</span>
              <span className="text-cyan-400">AI</span>
            </div>
            <div className="text-[10px] text-slate-400">Multi-Bank Fraud Defense</div>
          </div>
        </div>

        {/* System Active Badge */}
        <div className="px-4 py-3">
          <div className="p-2.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 flex items-center gap-2 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <div>
              <span className="font-bold text-emerald-300 block text-[11px]">Inter-Bank Fabric Online</span>
              <span className="text-[10px] text-emerald-500/90">Bank A, B, C, D Active</span>
            </div>
          </div>
        </div>

        {/* Core Navigation Items (Exact 6 Fields) */}
        <div className="px-4 pt-1 pb-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
            Core Modules
          </span>
        </div>
        <nav className="px-3 space-y-1">
          {primaryNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-md shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-start gap-2.5 truncate">
                  <Icon className={`w-4 h-4 shrink-0 mt-0.5 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                  <div className="text-left truncate">
                    <span className={`block truncate font-bold ${isActive ? 'text-cyan-300' : 'text-slate-200'}`}>
                      {item.label}
                    </span>
                    <span className="block text-[10px] text-slate-500 font-normal truncate">
                      {item.subtitle}
                    </span>
                  </div>
                </div>
                {item.badge && (
                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono font-bold shrink-0 self-start mt-0.5 ${
                    isActive ? 'bg-cyan-400/20 text-cyan-200' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Tactical Utilities */}
        <div className="px-4 pt-4 pb-1">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
            Tactical Extensions
          </span>
        </div>
        <nav className="px-3 space-y-1">
          {secondaryNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-slate-800 text-slate-200 border border-slate-700'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-900/40'
                }`}
              >
                <div className="flex items-center gap-2.5 truncate">
                  <Icon className="w-3.5 h-3.5 shrink-0 text-slate-500" />
                  <span className="truncate">{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[8px] px-1 py-0.5 rounded bg-slate-900 text-slate-500 font-mono">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Safeguards */}
      <div className="p-4 border-t border-slate-800/80 text-[11px] text-slate-400 mt-auto">
        <div className="flex items-center gap-1.5 text-slate-300 font-semibold mb-1">
          <Lock className="w-3.5 h-3.5 text-cyan-400" />
          <span>DPDP Act 2023 Masking</span>
        </div>
        <p className="text-[10px] text-slate-500 leading-normal">
          Zero unmasked PII. Cryptographic SHA-256 audit trail enabled.
        </p>
      </div>
    </aside>
  );
}
