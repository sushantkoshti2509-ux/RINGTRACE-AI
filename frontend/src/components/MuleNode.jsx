import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Shield, AlertTriangle, CheckCircle, Lock, ArrowRight, Ban } from 'lucide-react';

const bankColors = {
  BANK_A: {
    bg: 'bg-white',
    border: 'border-cyan-400',
    badge: 'bg-cyan-50 text-cyan-800 border-cyan-200',
    dot: 'bg-cyan-500',
    accentText: 'text-cyan-700',
  },
  BNKA: {
    bg: 'bg-white',
    border: 'border-cyan-400',
    badge: 'bg-cyan-50 text-cyan-800 border-cyan-200',
    dot: 'bg-cyan-500',
    accentText: 'text-cyan-700',
  },
  BANK_B: {
    bg: 'bg-white',
    border: 'border-emerald-400',
    badge: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    dot: 'bg-emerald-500',
    accentText: 'text-emerald-700',
  },
  BNKB: {
    bg: 'bg-white',
    border: 'border-emerald-400',
    badge: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    dot: 'bg-emerald-500',
    accentText: 'text-emerald-700',
  },
  BANK_C: {
    bg: 'bg-white',
    border: 'border-purple-400',
    badge: 'bg-purple-50 text-purple-800 border-purple-200',
    dot: 'bg-purple-500',
    accentText: 'text-purple-700',
  },
  BNKC: {
    bg: 'bg-white',
    border: 'border-purple-400',
    badge: 'bg-purple-50 text-purple-800 border-purple-200',
    dot: 'bg-purple-500',
    accentText: 'text-purple-700',
  },
  BANK_D: {
    bg: 'bg-white',
    border: 'border-amber-400',
    badge: 'bg-amber-50 text-amber-800 border-amber-200',
    dot: 'bg-amber-500',
    accentText: 'text-amber-700',
  },
  BNKD: {
    bg: 'bg-white',
    border: 'border-amber-400',
    badge: 'bg-amber-50 text-amber-800 border-amber-200',
    dot: 'bg-amber-500',
    accentText: 'text-amber-700',
  },
};

function MuleNode({ data, selected }) {
  const isTarget = data.isTarget;
  const isNeutralized = data.isNeutralized;
  const bStyle = bankColors[data.bank] || bankColors.BANK_A;

  return (
    <div
      className={`relative min-w-[220px] max-w-[240px] rounded-xl p-3.5 transition-all duration-300 cursor-pointer shadow-sm ${
        isTarget
          ? 'bg-rose-50 border-2 border-rose-500 shadow-lg shadow-rose-500/20 ring-4 ring-rose-400/20 scale-105'
          : isNeutralized
          ? 'bg-slate-100 border border-slate-300 opacity-60 grayscale-[0.6]'
          : selected
          ? 'bg-white border-2 border-blue-600 shadow-xl ring-4 ring-blue-500/20 scale-105'
          : `${bStyle.bg} border-2 ${bStyle.border} hover:border-blue-500 hover:shadow-md`
      }`}
    >
      {/* Input Handle (Left) */}
      <Handle
        type="target"
        id="left"
        position={Position.Left}
        className="!w-2.5 !h-2.5 !bg-blue-600 !border-2 !border-white !rounded-full -left-1.5"
      />
      {/* Top Handle */}
      <Handle
        type="target"
        id="top"
        position={Position.Top}
        className="!w-2.5 !h-2.5 !bg-blue-600 !border-2 !border-white !rounded-full -top-1"
      />

      {/* Top Header Badge: Bank & DPDP Masked ID */}
      <div className="flex items-center justify-between gap-1.5 mb-2">
        <span className={`text-[10px] px-2 py-0.5 rounded-md font-mono font-bold border ${bStyle.badge}`}>
          {data.bank}
        </span>

        {isTarget ? (
          <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-rose-100 text-rose-700 border border-rose-300 flex items-center gap-1 font-bold animate-pulse">
            <Ban className="w-2.5 h-2.5" /> CHOKE POINT
          </span>
        ) : isNeutralized ? (
          <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-slate-200 text-slate-700 border border-slate-300 flex items-center gap-1 font-semibold">
            <Lock className="w-2.5 h-2.5" /> SEVERED
          </span>
        ) : (
          <span className="text-[10px] text-slate-500 flex items-center gap-1 font-medium">
            <Lock className="w-2.5 h-2.5 text-slate-400" /> DPDP
          </span>
        )}
      </div>

      {/* Account Code & Masked ID */}
      <div className="font-mono text-sm font-bold text-slate-900 tracking-wide flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span className={`w-2.5 h-2.5 rounded-full ${isTarget ? 'bg-rose-500 animate-ping' : bStyle.dot}`} />
          <span className="text-slate-900 font-extrabold text-sm">{data.account_code || data.masked_id}</span>
        </div>
        {data.account_code && (
          <span className="text-[10px] text-slate-500 font-mono font-medium">
            {data.masked_id}
          </span>
        )}
      </div>

      {/* Role Tag */}
      <div className="text-[11px] text-slate-600 font-medium mt-1 truncate">
        {data.role}
      </div>

      {/* Stats Line */}
      <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px]">
        <div>
          <span className="text-slate-400">Flow: </span>
          <span className="text-slate-900 font-mono font-bold">
            ₹{(data.outbound_volume || 0).toLocaleString()}
          </span>
        </div>
        <div className="text-right">
          <span className="text-slate-400">Deg: </span>
          <span className="text-slate-600 font-mono font-medium">
            {data.in_degree}↓ {data.out_degree}↑
          </span>
        </div>
      </div>

      {/* Output Handle (Right) */}
      <Handle
        type="source"
        id="right"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-blue-600 !border-2 !border-white !rounded-full -right-1.5"
      />
      {/* Bottom Handle */}
      <Handle
        type="source"
        id="bottom"
        position={Position.Bottom}
        className="!w-2.5 !h-2.5 !bg-blue-600 !border-2 !border-white !rounded-full -bottom-1"
      />
    </div>
  );
}

export default memo(MuleNode);
