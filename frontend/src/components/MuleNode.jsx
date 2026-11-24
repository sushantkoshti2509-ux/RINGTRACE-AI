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
        <span className={`text-xs px-2.5 py-0.5 rounded-md font-mono font-extrabold border shadow-xs ${bStyle.badge}`}>
          {data.bank}
        </span>

        {isTarget ? (
          <span className="text-[11px] px-2 py-0.5 rounded-md bg-rose-100 text-rose-800 border border-rose-300 flex items-center gap-1 font-extrabold animate-pulse">
            <Ban className="w-3 h-3" /> CHOKE POINT
          </span>
        ) : isNeutralized ? (
          <span className="text-[11px] px-2 py-0.5 rounded-md bg-slate-200 text-slate-800 border border-slate-300 flex items-center gap-1 font-bold">
            <Lock className="w-3 h-3" /> SEVERED
          </span>
        ) : (
          <span className="text-xs text-slate-600 flex items-center gap-1 font-bold">
            <Lock className="w-3 h-3 text-slate-500" /> DPDP
          </span>
        )}
      </div>

      {/* Account Code & Masked ID */}
      <div className="font-mono text-base font-extrabold text-slate-900 tracking-wide flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span className={`w-2.5 h-2.5 rounded-full ${isTarget ? 'bg-rose-500 animate-ping' : bStyle.dot}`} />
          <span className="text-slate-900 font-extrabold text-base">{data.account_code || data.masked_id}</span>
        </div>
        {data.account_code && (
          <span className="text-xs text-slate-600 font-mono font-bold">
            {data.masked_id}
          </span>
        )}
      </div>

      {/* Role Tag */}
      <div className="text-xs text-slate-700 font-bold mt-1 truncate">
        {data.role}
      </div>

      {/* Stats Line */}
      <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
        <div>
          <span className="text-slate-500 font-bold">Flow: </span>
          <span className="text-slate-900 font-mono font-extrabold">
            ₹{(data.outbound_volume || 0).toLocaleString()}
          </span>
        </div>
        <div className="text-right">
          <span className="text-slate-500 font-bold">Deg: </span>
          <span className="text-slate-800 font-mono font-bold">
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
