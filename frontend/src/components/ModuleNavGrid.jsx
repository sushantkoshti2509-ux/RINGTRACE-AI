import React from 'react';
import {
  LayoutGrid,
  Network,
  Brain,
  Bot,
  FolderSearch,
  TrendingUp,
} from 'lucide-react';

export const MODULE_FIELDS = [
  {
    id: 'dashboard',
    title: 'Dashboard',
    subtitle: 'Existing detection and statistics',
    icon: LayoutGrid,
  },
  {
    id: 'network',
    title: 'Network Explorer',
    subtitle: 'Cross-bank fraud connections',
    icon: Network,
  },
  {
    id: 'xai',
    title: 'Explainable AI',
    subtitle: 'SHAP prediction explanations',
    icon: Brain,
  },
  {
    id: 'assistant',
    title: 'Investigation Assistant',
    subtitle: 'AI-supported case investigation',
    icon: Bot,
  },
  {
    id: 'cases',
    title: 'Case Management',
    subtitle: 'Evidence, notes and reports',
    icon: FolderSearch,
  },
  {
    id: 'analytics',
    title: 'Advanced Analytics',
    subtitle: 'Bank-wise and network analytics',
    icon: TrendingUp,
  },
];

export default function ModuleNavGrid({ activeTab, onSelectTab }) {
  return (
    <div className="w-full">
      {/* 2-Column Exact Module Grid matching System Specification */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {MODULE_FIELDS.map((mod) => {
          const Icon = mod.icon;
          const isActive = activeTab === mod.id;

          return (
            <button
              key={mod.id}
              onClick={() => onSelectTab(mod.id)}
              className={`text-left p-5 rounded-2xl border transition-all duration-200 cursor-pointer flex flex-col justify-between group ${
                isActive
                  ? 'bg-[#0e172e] border-cyan-500 shadow-lg shadow-cyan-500/15 ring-1 ring-cyan-500/40'
                  : 'bg-[#0a0f1d] border-slate-800/80 hover:border-slate-700 hover:bg-[#0d1424]'
              }`}
            >
              <div>
                <Icon
                  className={`w-6 h-6 transition-colors ${
                    isActive ? 'text-cyan-400' : 'text-slate-300 group-hover:text-white'
                  }`}
                />
              </div>
              <div className="mt-4">
                <div
                  className={`font-bold text-base transition-colors ${
                    isActive ? 'text-white' : 'text-slate-100 group-hover:text-white'
                  }`}
                >
                  {mod.title}
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  {mod.subtitle}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
