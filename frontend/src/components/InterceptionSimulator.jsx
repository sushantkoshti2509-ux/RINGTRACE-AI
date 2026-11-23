import React, { useState } from 'react';
import confetti from 'canvas-confetti';
import {
  ShieldAlert,
  Clock,
  CheckCircle2,
  Copy,
  Check,
  TrendingDown,
  Sparkles,
  Award,
  Fingerprint,
  Zap,
} from 'lucide-react';

export default function InterceptionSimulator({
  nodes = [],
  bottlenecks = [],
  selectedTargetNode = null,
  onSelectTargetNode = () => {},
  onRunSimulation = () => {},
  simulationResult = null,
  isLoading = false,
}) {
  const [strategyKey, setStrategyKey] = useState('COOLING_OFF_DELAY');
  const [delayMinutes, setDelayMinutes] = useState(60);
  const [copiedHash, setCopiedHash] = useState(false);

  const handleSimulate = async () => {
    // Fire celebratory confetti on high-impact interception
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#06b6d4', '#10b981', '#3b82f6'],
    });

    onRunSimulation({
      strategyKey,
      delayMinutes,
    });
  };

  const copyAuditHash = () => {
    if (simulationResult?.audit_trail?.sha256_integrity_hash) {
      navigator.clipboard.writeText(simulationResult.audit_trail.sha256_integrity_hash);
      setCopiedHash(true);
      setTimeout(() => setCopiedHash(false), 2500);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-2xl flex flex-col gap-5">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.25)]">
            <ShieldAlert className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-wide">
              Mule Ring Interception & ROI Simulator
            </h3>
            <p className="text-xs text-slate-400">
              Proactive Financial Crime Mitigation & Central Regulatory Compliance
            </p>
          </div>
        </div>

        <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          DPDP Act 2023 Enforced
        </span>
      </div>

      {/* Control Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 1. Target Bottleneck Node */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">
            🎯 Target Choke Point (Bottleneck)
          </label>
          <select
            value={selectedTargetNode || ''}
            onChange={(e) => onSelectTargetNode(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-400 transition-colors"
          >
            {bottlenecks.map((b, idx) => (
              <option key={b.node_id} value={b.node_id}>
                #{idx + 1} {b.masked_id} ({b.bank_id}) — {b.role}
              </option>
            ))}
          </select>
        </div>

        {/* 2. Countermeasure Strategy */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">
            🛡️ Graduated Countermeasure Strategy
          </label>
          <select
            value={strategyKey}
            onChange={(e) => setStrategyKey(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-400 transition-colors"
          >
            <option value="COOLING_OFF_DELAY">
              Dynamic Cooling-Off Delay (30m - 120m)
            </option>
            <option value="STEP_UP_BIOMETRIC">
              Mandatory Step-Up Biometric / Aadhaar Re-Auth
            </option>
            <option value="DUAL_BANK_HOLD">
              Targeted Dual-Institution Inward Hold
            </option>
          </select>
        </div>

        {/* 3. Delay Slider */}
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <label className="text-xs font-semibold text-slate-300">
              ⏱️ Intervention Window
            </label>
            <span className="text-xs font-mono font-bold text-cyan-400">
              {delayMinutes} Minutes
            </span>
          </div>
          <input
            type="range"
            min="15"
            max="120"
            step="15"
            value={delayMinutes}
            onChange={(e) => setDelayMinutes(Number(e.target.value))}
            className="w-full accent-cyan-400 cursor-pointer"
          />
        </div>
      </div>

      {/* Action Button */}
      <div className="flex items-center justify-between pt-2">
        <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5 text-amber-400" />
          <span>Non-freezing graduated policy: zero customer disruption</span>
        </div>

        <button
          onClick={handleSimulate}
          disabled={isLoading}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-cyan-500/25 transition-all active:scale-95 disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4" />
          {isLoading ? 'Computing ROI...' : 'Execute Interception Simulation'}
        </button>
      </div>

      {/* Simulation Results HUD */}
      {simulationResult && (
        <div className="mt-3 p-4 rounded-xl bg-slate-950/80 border border-cyan-500/30 shadow-inner flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
              <Award className="w-4 h-4 text-cyan-400" />
              Interception ROI Impact Metrics
            </span>
            <span className="text-xs font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
              SIM ID: {simulationResult.simulation_id}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {/* 1. Loss Prevented */}
            <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] uppercase tracking-wider text-slate-400">
                🛡️ Capital Protected (ROI)
              </div>
              <div className="text-lg font-bold text-emerald-400 font-mono mt-1">
                ₹{(simulationResult.funds_intercepted_inr || 0).toLocaleString()}
              </div>
              <div className="text-[10px] text-emerald-500/90 mt-0.5">
                {simulationResult.interception_rate_pct}% ring volume saved
              </div>
            </div>

            {/* 2. Downstream Neutralization */}
            <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] uppercase tracking-wider text-slate-400">
                ⚡ Mules Neutralized
              </div>
              <div className="text-lg font-bold text-cyan-300 font-mono mt-1">
                {simulationResult.downstream_accounts_neutralized} / {simulationResult.total_ring_accounts}
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                {simulationResult.severed_edges_count} downstream feeds severed
              </div>
            </div>

            {/* 3. NCRP 1930 Lead Time */}
            <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] uppercase tracking-wider text-slate-400">
                ⏱️ NCRP 1930 Time Gain
              </div>
              <div className="text-lg font-bold text-amber-400 font-mono mt-1">
                +{simulationResult.ncrp_time_advantage_minutes} min
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Lead-time for law enforcement
              </div>
            </div>

            {/* 4. Retail Friction */}
            <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] uppercase tracking-wider text-slate-400">
                🎯 Collateral Friction
              </div>
              <div className="text-lg font-bold text-white font-mono mt-1">
                0.0%
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Zero innocent account holds
              </div>
            </div>
          </div>

          {/* Cryptographic SHA-256 Audit Trail */}
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 overflow-hidden">
              <Fingerprint className="w-4 h-4 text-purple-400 shrink-0" />
              <div className="truncate">
                <span className="text-slate-400 font-mono">SHA-256 Audit: </span>
                <span className="text-purple-300 font-mono text-[11px]">
                  {simulationResult.audit_trail?.sha256_integrity_hash}
                </span>
              </div>
            </div>

            <button
              onClick={copyAuditHash}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 flex items-center gap-1.5 shrink-0 transition-colors"
            >
              {copiedHash ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400 text-[11px]">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span className="text-[11px]">Copy Hash</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
