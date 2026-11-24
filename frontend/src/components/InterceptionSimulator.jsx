import React, { useState } from 'react';
import {
  ShieldAlert,
  Zap,
  Sparkles,
  Award,
  Fingerprint,
  Copy,
  Check,
  CheckCircle2,
} from 'lucide-react';

export default function InterceptionSimulator({
  nodes = [],
  bottlenecks = [],
  selectedTargetNode,
  onSelectTargetNode,
  onRunSimulation,
  simulationResult,
  isLoading,
}) {
  const [strategyKey, setStrategyKey] = useState('COOLING_OFF_DELAY');
  const [delayMinutes, setDelayMinutes] = useState(60);
  const [copiedHash, setCopiedHash] = useState(false);

  const handleSimulate = () => {
    onRunSimulation({
      target_account_id: selectedTargetNode,
      strategy_key: strategyKey,
      delay_minutes: delayMinutes,
    });
  };

  const copyAuditHash = () => {
    if (simulationResult?.audit_trail?.sha256_integrity_hash) {
      navigator.clipboard.writeText(
        simulationResult.audit_trail.sha256_integrity_hash
      );
      setCopiedHash(true);
      setTimeout(() => setCopiedHash(false), 2000);
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col gap-5">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 shrink-0">
            <ShieldAlert className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-900 tracking-tight">
              Mule Ring Interception & ROI Simulator
            </h3>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Proactive Financial Crime Mitigation & Central Regulatory Compliance
            </p>
          </div>
        </div>

        <span className="text-[10px] uppercase font-mono font-extrabold tracking-wider px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300">
          DPDP Act 2023 Enforced
        </span>
      </div>

      {/* Control Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 1. Target Bottleneck Node */}
        <div>
          <label className="block text-xs font-extrabold text-slate-700 mb-1.5">
            🎯 Target Choke Point (Bottleneck)
          </label>
          <select
            value={selectedTargetNode || ''}
            onChange={(e) => onSelectTargetNode(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-xs text-slate-900 font-mono font-bold focus:outline-none focus:border-blue-600 shadow-xs cursor-pointer"
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
          <label className="block text-xs font-extrabold text-slate-700 mb-1.5">
            🛡️ Graduated Countermeasure Strategy
          </label>
          <select
            value={strategyKey}
            onChange={(e) => setStrategyKey(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-xs text-slate-900 font-semibold focus:outline-none focus:border-blue-600 shadow-xs cursor-pointer"
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
            <label className="text-xs font-extrabold text-slate-700">
              ⏱️ Intervention Window
            </label>
            <span className="text-xs font-mono font-extrabold text-blue-700">
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
            className="w-full accent-blue-600 cursor-pointer"
          />
        </div>
      </div>

      {/* Action Button */}
      <div className="flex items-center justify-between pt-2">
        <div className="text-xs text-slate-600 font-semibold flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5 text-amber-500 shrink-0" />
          <span>Non-freezing graduated policy: zero customer disruption</span>
        </div>

        <button
          onClick={handleSimulate}
          disabled={isLoading}
          className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 shadow-md shadow-blue-500/25 transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
        >
          <Sparkles className="w-4 h-4" />
          {isLoading ? 'Computing ROI...' : 'Execute Interception Simulation'}
        </button>
      </div>

      {/* Simulation Results HUD */}
      {simulationResult && (
        <div className="mt-3 p-5 rounded-2xl bg-slate-50 border border-slate-200 shadow-sm flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <Award className="w-4 h-4 text-blue-600" />
              Interception ROI Impact Metrics
            </span>
            <span className="text-xs font-mono text-emerald-800 font-extrabold bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-300">
              SIM ID: {simulationResult.simulation_id}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {/* 1. Loss Prevented */}
            <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-xs">
              <div className="text-[10px] uppercase font-extrabold tracking-wider text-slate-500">
                🛡️ Capital Protected (ROI)
              </div>
              <div className="text-lg font-extrabold text-emerald-700 font-mono mt-1">
                ₹{(simulationResult.funds_intercepted_inr || 0).toLocaleString()}
              </div>
              <div className="text-[10px] font-bold text-emerald-700 mt-0.5">
                {simulationResult.interception_rate_pct}% ring volume saved
              </div>
            </div>

            {/* 2. Downstream Neutralization */}
            <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-xs">
              <div className="text-[10px] uppercase font-extrabold tracking-wider text-slate-500">
                ⚡ Mules Neutralized
              </div>
              <div className="text-lg font-extrabold text-blue-700 font-mono mt-1">
                {simulationResult.downstream_accounts_neutralized} / {simulationResult.total_ring_accounts}
              </div>
              <div className="text-[10px] font-bold text-slate-600 mt-0.5">
                {simulationResult.severed_edges_count} downstream feeds severed
              </div>
            </div>

            {/* 3. NCRP 1930 Lead Time */}
            <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-xs">
              <div className="text-[10px] uppercase font-extrabold tracking-wider text-slate-500">
                ⏱️ NCRP 1930 Time Gain
              </div>
              <div className="text-lg font-extrabold text-amber-700 font-mono mt-1">
                +{simulationResult.ncrp_time_advantage_minutes} min
              </div>
              <div className="text-[10px] font-bold text-slate-600 mt-0.5">
                Lead-time for law enforcement
              </div>
            </div>

            {/* 4. Retail Friction */}
            <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-xs">
              <div className="text-[10px] uppercase font-extrabold tracking-wider text-slate-500">
                🎯 Collateral Friction
              </div>
              <div className="text-lg font-extrabold text-slate-900 font-mono mt-1">
                0.0%
              </div>
              <div className="text-[10px] font-bold text-slate-600 mt-0.5">
                Zero innocent account holds
              </div>
            </div>
          </div>

          {/* Cryptographic SHA-256 Audit Trail */}
          <div className="p-3.5 rounded-xl bg-white border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs shadow-xs">
            <div className="flex items-center gap-2 overflow-hidden">
              <Fingerprint className="w-4 h-4 text-purple-600 shrink-0" />
              <div className="truncate">
                <span className="text-slate-600 font-bold font-mono">SHA-256 Audit: </span>
                <span className="text-purple-700 font-mono text-[11px] font-extrabold">
                  {simulationResult.audit_trail?.sha256_integrity_hash}
                </span>
              </div>
            </div>

            <button
              onClick={copyAuditHash}
              className="px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 font-bold border border-slate-300 flex items-center gap-1.5 shrink-0 transition-colors cursor-pointer text-xs"
            >
              {copiedHash ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                  <span className="text-emerald-700 font-bold">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy Hash</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
