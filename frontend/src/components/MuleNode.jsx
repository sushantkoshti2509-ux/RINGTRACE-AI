import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Shield, AlertTriangle, CheckCircle, Lock, ArrowRight, Ban } from 'lucide-react';

const bankColors = {
  BANK_A: {
    bg: 'bg-cyan-950/70',
    border: 'border-cyan-500/40',
    badge: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
    dot: 'bg-cyan-400',
  },
  BANK_B: {
    bg: 'bg-emerald-950/70',
    border: 'border-emerald-500/40',
    badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    dot: 'bg-emerald-400',
  },
  BANK_C: {
    bg: 'bg-purple-950/70',
    border: 'border-purple-500/40',
    badge: 'bg-purple-500/20 text-purple-300 border-purple-500/40',
    dot: 'bg-purple-400',
  },
};

function MuleNode({ data, selected }) {
  const isIntercepted = data.isIntercepted;
  const isTarget = data.isTarget;
  const isNeutralized = data.isNeutralized;
  const bStyle = bankColors[data.bank] || bankColors.BANK_A;

  return (
    <div
      className={`relative min-w-[220px] max-w-[240px] rounded-xl p-3.5 transition-all duration-300 cursor-pointer backdrop-blur-md ${
        isTarget
          ? 'bg-rose-950/90 border-2 border-rose-500 shadow-[0_0_30px_rgba(244,63,94,0.6)] ring-2 ring-rose-400/50 scale-105'
          : isNeutralized
          ? 'bg-slate-900/90 border border-rose-900/60 opacity-60 grayscale-[0.6]'
          : selected
          ? 'bg-slate-900/95 border-2 border-cyan-400 shadow-[0_0_25px_rgba(6,182,212,0.4)] scale-105'
          : `${bStyle.bg} border ${bStyle.border} hover:border-cyan-400/60 shadow-lg`
      }`}
    >
      {/* Input Handle (Left) */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-cyan-400 !border-2 !border-slate-950 -left-1.5"
      />

      {/* Top Header Badge: Bank & DPDP Masked ID */}
      <div className="flex items-center justify-between gap-1.5 mb-2">
        <span className={`text-[10px] px-2 py-0.5 rounded-md font-mono font-bold border ${bStyle.badge}`}>
          {data.bank}
        </span>

        {isTarget ? (
          <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-rose-500/30 text-rose-300 border border-rose-500/50 flex items-center gap-1 font-bold animate-pulse">
            <Ban className="w-2.5 h-2.5" /> CHOKE POINT
          </span>
        ) : isNeutralized ? (
          <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-rose-900/50 text-rose-300 border border-rose-800/60 flex items-center gap-1">
            <Lock className="w-2.5 h-2.5" /> SEVERED
          </span>
        ) : (
          <span className="text-[10px] text-slate-400 flex items-center gap-1">
            <Lock className="w-2.5 h-2.5 text-slate-400" /> DPDP
          </span>
        )}
      </div>

      {/* Account Number (Masked) */}
      <div className="font-mono text-sm font-bold text-white tracking-wide flex items-center gap-1.5">
        <span className={`w-2 h-2 rounded-full ${isTarget ? 'bg-rose-400 animate-ping' : bStyle.dot}`} />
        <span>{data.masked_id}</span>
      </div>

      {/* Role Tag */}
      <div className="text-[11px] text-slate-300 font-medium mt-1 truncate">
        {data.role}
      </div>

      {/* Stats Line */}
      <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
        <div>
          <span className="text-slate-400">Flow: </span>
          <span className="text-cyan-300 font-mono font-bold">
            ₹{(data.outbound_volume || 0).toLocaleString()}
          </span>
        </div>
        <div className="text-right">
          <span className="text-slate-400">Deg: </span>
          <span className="text-slate-200 font-mono">
            {data.in_degree}↓ {data.out_degree}↑
          </span>
        </div>
      </div>

      {/* Output Handle (Right) */}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-cyan-400 !border-2 !border-slate-950 -right-1.5"
      />
    </div>
  );
}

export default memo(MuleNode);
