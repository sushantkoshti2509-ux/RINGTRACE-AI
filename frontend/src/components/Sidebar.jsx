import React, { useState } from 'react';
import {
  Shield,
  ChevronDown,
  ChevronRight,
  LayoutGrid,
  Network,
  Cpu,
  Brain,
  Bot,
  FolderSearch,
  TrendingUp,
  ShieldAlert,
  Zap,
  Globe,
  Bell,
  CheckCircle2,
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  // Accordion state matching the template screenshot
  const [openSections, setOpenSections] = useState({
    dashboards: true,
    investigation: true,
    intelligence: true,
    compliance: false,
  });

  const toggleSection = (section) => {
    setOpenSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const menuSections = [
    {
      key: 'dashboards',
      label: 'Dashboards',
      badge: null,
      items: [
        { id: 'dashboard', label: 'Default', icon: LayoutGrid },
        { id: 'gnn', label: 'Unified GNN Network', icon: Cpu },
      ],
    },
    {
      key: 'investigation',
      label: 'Elements & Investigation',
      badge: null,
      items: [
        { id: 'network', label: 'Network Explorer', icon: Network },
        { id: 'interception', label: 'Interception Simulator', icon: ShieldAlert },
        { id: 'cases', label: 'Case Management', icon: FolderSearch },
        { id: 'assistant', label: 'AI Copilot Assistant', icon: Bot },
      ],
    },
    {
      key: 'intelligence',
      label: 'Widgets & Intelligence',
      badge: null,
      items: [
        { id: 'xai', label: 'Explainable AI (XAI)', icon: Brain },
        { id: 'digital_twin', label: 'Digital Twin Simulator', icon: Zap },
        { id: 'globe3d', label: '3D Cyber Clearing Fabric', icon: Globe },
      ],
    },
    {
      key: 'compliance',
      label: 'Regular Tables & Oversight',
      badge: null,
      items: [
        { id: 'alerts', label: 'Alerts & Rules', icon: Bell },
        { id: 'analytics', label: 'Advanced Analytics', icon: TrendingUp },
      ],
    },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200/90 flex flex-col justify-between shrink-0 h-screen sticky top-0 overflow-y-auto select-none shadow-sm">
      {/* Brand Header */}
      <div>
        <div className="p-5 border-b border-slate-100 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shadow-md shadow-blue-500/20 text-white font-bold">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-extrabold text-base text-slate-900 tracking-tight flex items-center gap-1">
              <span>RINGTRACE</span>
              <span className="text-blue-600">AI</span>
            </div>
            <div className="text-[10px] text-slate-400 font-medium">Central Regulatory Defense</div>
          </div>
        </div>

        {/* Navigation Accordion Sections */}
        <div className="p-3 flex flex-col gap-1.5">
          {menuSections.map((sec) => {
            const isOpen = openSections[sec.key];
            const hasActiveChild = sec.items.some((item) => item.id === activeTab);

            return (
              <div key={sec.key} className="flex flex-col">
                {/* Accordion Group Header */}
                <button
                  onClick={() => toggleSection(sec.key)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-bold tracking-tight transition-all ${
                    hasActiveChild
                      ? 'text-blue-600 bg-blue-50/70 font-bold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <span>{sec.label}</span>
                  </span>
                  {isOpen ? (
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
                  )}
                </button>

                {/* Sub-items */}
                {isOpen && (
                  <div className="mt-1 flex flex-col gap-0.5 pl-3 border-l-2 border-slate-100 ml-3">
                    {sec.items.map((item) => {
                      const isActive = activeTab === item.id;
                      const Icon = item.icon;
                      return (
                        <button
                          key={item.id}
                          onClick={() => setActiveTab(item.id)}
                          className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                            isActive
                              ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/20 font-bold'
                              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                          }`}
                        >
                          <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                          <span className="truncate">{item.label}</span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Sidebar Footer Status */}
      <div className="p-4 border-t border-slate-100 text-[11px] text-slate-500 bg-slate-50/50">
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-1.5 font-semibold text-slate-700">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>4 Banks Online</span>
          </span>
          <span className="font-mono text-[10px] text-blue-600 font-bold bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
            DPDPA 2023
          </span>
        </div>
      </div>
    </aside>
  );
}
