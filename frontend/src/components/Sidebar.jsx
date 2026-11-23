import React from 'react';
import {
  LayoutDashboard,
  ShieldAlert,
  Network,
  Zap,
  Brain,
  Bell,
  Briefcase,
  Globe,
  Lock,
  ChevronRight,
  Shield,
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Multi-Bank Monitoring', icon: LayoutDashboard, badge: '25.4k' },
    { id: 'interception', label: 'Interception & ROI Simulator', icon: ShieldAlert, badge: 'PROACTIVE' },
    { id: 'network', label: 'Network & Cycle Explorer', icon: Network, badge: '18 LOOPS' },
    { id: 'realtime', label: 'Real-Time Stream Scorer', icon: Zap, badge: '<15ms' },
    { id: 'xai', label: 'Explainable AI (SHAP)', icon: Brain },
    { id: 'alerts', label: 'Alert & Incident Center', icon: Bell, badge: 'LIVE' },
    { id: 'cases', label: 'Investigation & PDF Dossier', icon: Briefcase },
    { id: 'globe3d', label: '3D Cyber Clearing Fabric', icon: Globe, badge: '3D' },
  ];

  return (
    <aside className="w-64 glass-panel border-r border-slate-800 flex flex-col justify-between shrink-0 h-screen sticky top-0">
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
            <div className="text-[10px] text-slate-400">Anti-Mule Defense HUD</div>
          </div>
        </div>

        {/* System Active Badge */}
        <div className="px-4 py-3">
          <div className="p-2.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 flex items-center gap-2 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <div>
              <span className="font-bold text-emerald-300 block text-[11px]">UPI Network Online</span>
              <span className="text-[10px] text-emerald-500/90">6 Institutions Online</span>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="px-3 space-y-1 mt-2">
          {navItems.map((item) => {
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
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono font-bold ${
                    isActive ? 'bg-cyan-400/20 text-cyan-200' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Safeguards */}
      <div className="p-4 border-t border-slate-800/80 text-[11px] text-slate-400">
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
