import React, { useState } from 'react';
import {
  Shield,
  Zap,
  ArrowRight,
  Play,
  CheckCircle2,
  Cpu,
  Network,
  Lock,
  Brain,
  Layers,
  Sparkles,
} from 'lucide-react';

export default function LandingPageView({ onLaunchDashboard = () => {} }) {
  const [activeTab, setActiveTab] = useState('creative');

  return (
    <div className="bg-[#F7F7F5] text-[#111111] rounded-[28px] border border-[#E7E7E4] shadow-2xl overflow-hidden font-sans pb-16">
      {/* Top Banner / Hero Navigation */}
      <nav className="border-b border-[#E7E7E4] bg-white/90 backdrop-blur-md px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-black flex items-center justify-center text-white font-bold">
            <Shield className="w-4 h-4 text-cyan-400" />
          </div>
          <span className="font-bold text-lg tracking-tight text-[#111111]">
            RINGTRACE <span className="text-cyan-600 font-extrabold">AI</span>
          </span>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#F3F2EF] text-[#666666] font-mono border border-[#E7E7E4] ml-2">
            Auralis SaaS Edition
          </span>
        </div>

        <div className="flex items-center gap-4 text-xs font-semibold">
          <span className="text-[#666666] hidden sm:inline">Bank A • Bank B • Bank C • Bank D</span>
          <button
            onClick={onLaunchDashboard}
            className="px-4 py-2 rounded-full bg-black text-white hover:bg-zinc-800 transition-all font-bold shadow-sm flex items-center gap-1.5"
          >
            <span>Open Live HUD</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-[1100px] mx-auto px-8 pt-12 pb-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-7 flex flex-col gap-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#F3F2EF] border border-[#E7E7E4] text-xs font-medium text-[#666666] w-fit">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Multi-Bank Clearing Fabric Online</span>
            </div>
            <h1 className="text-5xl lg:text-6xl font-bold tracking-tight text-[#111111] leading-[1.05]">
              Unified Multi-Bank Fraud Network Defense.
            </h1>
            <p className="text-base text-[#666666] leading-relaxed max-w-xl">
              Transform isolated transaction monitoring into interconnected graph intelligence. Real-time GNN mule detection, explainable AI, and proactive multi-bank interception across Bank A, Bank B, Bank C, and Bank D.
            </p>
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={onLaunchDashboard}
                className="bg-black text-white px-6 py-3 rounded-full text-xs font-bold transition-all hover:bg-zinc-800 shadow-md shadow-black/10 flex items-center gap-2"
              >
                <span>Launch Interactive HUD</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
              <a
                href="#features"
                className="bg-white border border-[#E7E7E4] text-[#111111] px-5 py-3 rounded-full text-xs font-semibold hover:bg-[#F3F2EF] transition-colors"
              >
                Explore Modules
              </a>
            </div>
          </div>

          <div className="lg:col-span-5 flex flex-col gap-4 lg:pt-4">
            <div className="bg-white rounded-2xl p-5 border border-[#E7E7E4] shadow-sm">
              <span className="text-[10px] uppercase font-bold text-[#888888] tracking-wider block mb-1">
                Inter-Bank Latency
              </span>
              <div className="text-3xl font-extrabold text-[#111111] font-mono">11.4 ms</div>
              <p className="text-xs text-[#666666] mt-1">Sub-90s Rapid Dispersion Interception SLA</p>
            </div>
            <div className="bg-white rounded-2xl p-5 border border-[#E7E7E4] shadow-sm">
              <span className="text-[10px] uppercase font-bold text-[#888888] tracking-wider block mb-1">
                Reconciliation Scale
              </span>
              <div className="text-3xl font-extrabold text-cyan-700 font-mono">46,380 Txns</div>
              <p className="text-xs text-[#666666] mt-1">Dual-Ledger Verified Across 4 Institutions</p>
            </div>
          </div>
        </div>
      </section>

      {/* Hero Product Panel with Center Glowing Orbs (Exact Auralis Concept) */}
      <section className="max-w-[1100px] mx-auto px-8 mb-16">
        <div className="bg-[#F3F2EF] rounded-[28px] p-8 flex flex-col relative overflow-hidden border border-[#E7E7E4] min-h-[460px] justify-between shadow-inner">
          {/* Top Segmented Controls */}
          <div className="flex justify-between items-center z-10">
            <div className="flex bg-white/90 p-1 rounded-full border border-[#E7E7E4] shadow-sm text-xs font-semibold">
              <button
                onClick={() => setActiveTab('creative')}
                className={`px-4 py-1.5 rounded-full transition-all ${
                  activeTab === 'creative' ? 'bg-black text-white shadow-sm' : 'text-[#666666] hover:text-black'
                }`}
              >
                GNN Topology
              </button>
              <button
                onClick={() => setActiveTab('agents')}
                className={`px-4 py-1.5 rounded-full transition-all ${
                  activeTab === 'agents' ? 'bg-black text-white shadow-sm' : 'text-[#666666] hover:text-black'
                }`}
              >
                XAI Reason Codes
              </button>
              <button
                onClick={() => setActiveTab('api')}
                className={`px-4 py-1.5 rounded-full transition-all ${
                  activeTab === 'api' ? 'bg-black text-white shadow-sm' : 'text-[#666666] hover:text-black'
                }`}
              >
                Zero-Knowledge PSI
              </button>
            </div>
            <span className="text-[11px] font-mono text-[#777777] bg-white px-3 py-1 rounded-full border border-[#E7E7E4]">
              DPDP Act 2023 Masked
            </span>
          </div>

          {/* Center Glowing Orbs */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-90 gap-10">
            <div className="w-[120px] h-[120px] rounded-full bg-gradient-to-tr from-cyan-400 to-blue-300 blur-2xl" />
            <div className="w-[160px] h-[160px] rounded-full bg-gradient-to-tr from-indigo-300 to-purple-400 blur-xl flex items-center justify-center relative">
              <div className="absolute inset-0 bg-white/30 rounded-full backdrop-blur-sm border border-white/50" />
            </div>
            <div className="w-[120px] h-[120px] rounded-full bg-gradient-to-tr from-emerald-300 to-teal-200 blur-2xl" />
          </div>

          {/* Center Interactive Button */}
          <div className="z-10 self-center my-auto flex flex-col items-center gap-3">
            <button
              onClick={onLaunchDashboard}
              className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-xl border border-[#E7E7E4] transition-transform hover:scale-110 group relative z-20 cursor-pointer"
            >
              <Play className="w-6 h-6 text-black fill-black group-hover:text-cyan-600 group-hover:fill-cyan-600 transition-colors ml-1" />
            </button>
            <span className="text-xs font-bold text-[#444444] bg-white/80 px-3 py-1 rounded-full border border-[#E7E7E4]">
              Click to Open Live Fraud Ledger
            </span>
          </div>

          {/* Bottom Bar Controls */}
          <div className="flex flex-wrap justify-between items-center z-10 bg-white/90 backdrop-blur-md p-3.5 rounded-2xl border border-[#E7E7E4] gap-3">
            <div className="flex gap-2 overflow-x-auto no-scrollbar text-xs">
              <span className="px-3 py-1 bg-[#F7F7F5] rounded-full font-medium text-[#111111] border border-[#E7E7E4]">
                Circular Cycles
              </span>
              <span className="px-3 py-1 bg-[#F7F7F5] rounded-full font-medium text-[#111111] border border-[#E7E7E4]">
                Fan-In Smurfing
              </span>
              <span className="px-3 py-1 bg-[#F7F7F5] rounded-full font-medium text-[#111111] border border-[#E7E7E4]">
                Rapid Dispersion
              </span>
              <span className="px-3 py-1 bg-[#F7F7F5] rounded-full font-medium text-[#111111] border border-[#E7E7E4]">
                Hybrid Rings
              </span>
            </div>
            <button
              onClick={onLaunchDashboard}
              className="bg-black text-white px-5 py-1.5 rounded-full text-xs font-bold whitespace-nowrap hover:bg-zinc-800 transition-colors"
            >
              Inspect DAG Network
            </button>
          </div>
        </div>
      </section>

      {/* Trust Strip: The 4 Banks */}
      <section className="max-w-[1100px] mx-auto px-8 mb-16 text-center">
        <h3 className="text-xs font-bold uppercase tracking-widest text-[#777777] mb-8">
          Connected Institutional Clearing Entities
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-2xl border border-[#E7E7E4] shadow-sm flex items-center justify-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-500" />
            <span className="font-bold text-xs text-[#111111]">bank_A (Retail Clearing)</span>
          </div>
          <div className="bg-white p-4 rounded-2xl border border-[#E7E7E4] shadow-sm flex items-center justify-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <span className="font-bold text-xs text-[#111111]">bank_B (Corp Treasury)</span>
          </div>
          <div className="bg-white p-4 rounded-2xl border border-[#E7E7E4] shadow-sm flex items-center justify-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
            <span className="font-bold text-xs text-[#111111]">bank_C (Cooperative Credit)</span>
          </div>
          <div className="bg-white p-4 rounded-2xl border border-[#E7E7E4] shadow-sm flex items-center justify-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
            <span className="font-bold text-xs text-[#111111]">bank_D (Wealth Remittance)</span>
          </div>
        </div>
      </section>

      {/* Modular Platform Overview Cards */}
      <section id="features" className="max-w-[1100px] mx-auto px-8">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-3xl font-bold text-[#111111] tracking-tight mb-2">
            Engineered Anti-Mule Capabilities
          </h2>
          <p className="text-xs text-[#666666]">
            High-performance modular detection algorithms built for national clearinghouse scale.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl p-6 border border-[#E7E7E4] shadow-sm flex flex-col justify-between h-[220px]">
            <div className="w-10 h-10 rounded-xl bg-cyan-50 text-cyan-800 border border-cyan-200 flex items-center justify-center">
              <Brain className="w-5 h-5 text-cyan-600" />
            </div>
            <div>
              <h4 className="font-bold text-base text-[#111111] mb-1">Graph Neural Networks</h4>
              <p className="text-xs text-[#666666]">
                Edge-aware message passing incorporating cross-bank transaction attributes and payment channels.
              </p>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-[#E7E7E4] shadow-sm flex flex-col justify-between h-[220px]">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-800 border border-purple-200 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h4 className="font-bold text-base text-[#111111] mb-1">SHAP Explainable AI</h4>
              <p className="text-xs text-[#666666]">
                Exact additive feature contributions and human-understandable reason codes for every prediction.
              </p>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-[#E7E7E4] shadow-sm flex flex-col justify-between h-[220px]">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center justify-center">
              <Shield className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <h4 className="font-bold text-base text-[#111111] mb-1">Proactive Interception</h4>
              <p className="text-xs text-[#666666]">
                Nodal choke-point freezes severing fund outflows before final layering withdrawal occurs.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
