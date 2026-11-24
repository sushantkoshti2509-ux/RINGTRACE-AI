import React, { useState, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import MuleNode from './MuleNode';
import {
  ShieldCheck,
  ShieldAlert,
  Sparkles,
  Filter,
  Layers,
  Network,
  Activity,
} from 'lucide-react';

const nodeTypes = {
  muleNode: MuleNode,
};

// 4-Bank Interconnected Layout Generator
function layoutEcosystemNodes(nodes, layoutMode = 'quadrant') {
  if (layoutMode === 'flow') {
    // Left-to-right DAG
    const tiers = {};
    nodes.forEach((n) => {
      const t = n.tier || 0;
      if (!tiers[t]) tiers[t] = [];
      tiers[t].push(n);
    });
    const tierKeys = Object.keys(tiers).map(Number).sort((a, b) => a - b);
    const pos = {};
    tierKeys.forEach((t, tIdx) => {
      tiers[t].forEach((n, idx) => {
        pos[n.id] = {
          x: tIdx * 270 + 40,
          y: idx * 135 + 40,
        };
      });
    });
    return pos;
  }

  // Unified 4-Bank Ecosystem: Institutional Quadrants + Central Corridor
  const buckets = {
    BANK_A: [],
    BANK_B: [],
    BANK_C: [],
    BANK_D: [],
    CENTER: [],
  };

  nodes.forEach((n) => {
    const b = (n.bank || n.id.split(':')[0] || 'BANK_A').toUpperCase();
    const role = (n.role || '').toLowerCase();
    const isBridge =
      (role.includes('collector') || role.includes('bridge') || role.includes('transit')) &&
      n.in_degree >= 1 &&
      n.out_degree >= 1;

    if (isBridge && buckets.CENTER.length < 5) {
      buckets.CENTER.push(n);
    } else if (b.includes('A')) {
      buckets.BANK_A.push(n);
    } else if (b.includes('B')) {
      buckets.BANK_B.push(n);
    } else if (b.includes('C')) {
      buckets.BANK_C.push(n);
    } else if (b.includes('D')) {
      buckets.BANK_D.push(n);
    } else {
      buckets.BANK_A.push(n);
    }
  });

  const pos = {};

  // Bank A (Top-Left: Retail Clearing)
  buckets.BANK_A.forEach((n, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    pos[n.id] = { x: 40 + col * 190, y: 50 + row * 130 };
  });

  // Bank B (Top-Right: Corporate Treasury)
  buckets.BANK_B.forEach((n, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    pos[n.id] = { x: 700 + col * 190, y: 50 + row * 130 };
  });

  // Center Transit / Laundering Corridor
  buckets.CENTER.forEach((n, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    pos[n.id] = { x: 440 + col * 180, y: 240 + row * 130 };
  });

  // Bank C (Bottom-Left: Cooperative Society)
  buckets.BANK_C.forEach((n, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    pos[n.id] = { x: 40 + col * 190, y: 440 + row * 130 };
  });

  // Bank D (Bottom-Right: Wealth & Remittance)
  buckets.BANK_D.forEach((n, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    pos[n.id] = { x: 700 + col * 190, y: 440 + row * 130 };
  });

  return pos;
}

export default function MuleRingCanvas({
  nodesData = [],
  edgesData = [],
  selectedNodeId = null,
  onSelectNode = () => {},
  targetNodeId = null,
  neutralizedNodes = [],
  severedEdges = [],
  isPostDisruption = false,
  onToggleDisruption = () => {},
}) {
  const [layoutMode, setLayoutMode] = useState('quadrant'); // 'quadrant' | 'flow'
  const [patternFilter, setPatternFilter] = useState('ALL');
  const [bankFilter, setBankFilter] = useState('ALL');

  // Compute node positions
  const nodePositions = useMemo(() => {
    return layoutEcosystemNodes(nodesData, layoutMode);
  }, [nodesData, layoutMode]);

  // Convert topology nodes into React Flow nodes arranged in Unified 4-Bank Layout
  const flowNodes = useMemo(() => {
    return nodesData.map((node) => {
      const isTarget = node.id === targetNodeId;
      const isNeutralized = isPostDisruption && neutralizedNodes.includes(node.id);
      const pos = nodePositions[node.id] || { x: 100, y: 100 };

      // Filter check
      const nodeBank = (node.bank || node.id.split(':')[0] || '').toUpperCase();
      const matchesBank = bankFilter === 'ALL' || nodeBank.includes(bankFilter.toUpperCase());
      const matchesPattern =
        patternFilter === 'ALL' || (node.pattern_type && node.pattern_type.includes(patternFilter));
      const isDimmed = !matchesBank || (!matchesPattern && patternFilter !== 'ALL');

      return {
        id: node.id,
        type: 'muleNode',
        position: pos,
        data: {
          ...node,
          isTarget,
          isNeutralized,
          isIntercepted: isPostDisruption && (isTarget || isNeutralized),
          isDimmed,
        },
        style: {
          opacity: isDimmed ? 0.22 : 1.0,
          transition: 'all 0.3s ease',
        },
        selected: node.id === selectedNodeId,
      };
    });
  }, [
    nodesData,
    nodePositions,
    selectedNodeId,
    targetNodeId,
    neutralizedNodes,
    isPostDisruption,
    bankFilter,
    patternFilter,
  ]);

  // Convert topology edges into React Flow edges with animated pulses or severed status
  const flowEdges = useMemo(() => {
    return edgesData.map((e) => {
      const isSevered =
        isPostDisruption &&
        severedEdges.some(
          ([u, v]) => (u === e.source && v === e.target) || (u === e.target && v === e.source)
        );

      if (isSevered) {
        return {
          id: e.id,
          source: e.source,
          target: e.target,
          animated: false,
          style: {
            stroke: '#ef4444',
            strokeWidth: 2.5,
            strokeDasharray: '6 4',
            opacity: 0.75,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: '#ef4444',
            width: 16,
            height: 16,
          },
          label: `🛑 INTERCEPTED ₹${(e.amount || 0).toLocaleString()}`,
          labelStyle: { fill: '#fca5a5', fontWeight: 700, fontSize: 10 },
          labelBgStyle: {
            fill: '#450a0a',
            fillOpacity: 0.9,
            stroke: '#ef4444',
            strokeWidth: 1,
            rx: 4,
            ry: 4,
          },
        };
      }

      const isCirc = (e.pattern_type || '').includes('CIRCULAR');
      const isFanIn = (e.pattern_type || '').includes('FAN_IN');
      const isFanOut = (e.pattern_type || '').includes('FAN_OUT');
      const isSuspicious = e.is_suspicious === 1 || isCirc || isFanIn || isFanOut;

      let strokeColor = '#64748b'; // default legitimate
      if (isCirc) strokeColor = '#f43f5e';
      else if (isFanIn) strokeColor = '#a855f7';
      else if (isFanOut) strokeColor = '#f59e0b';
      else if (e.is_cross_bank) strokeColor = '#10b981';

      let isDimmed = false;
      if (patternFilter !== 'ALL') {
        const matches = (e.pattern_type || '').includes(patternFilter);
        if (!matches) isDimmed = true;
      }
      if (bankFilter !== 'ALL') {
        const sBank = (e.sender_bank || '').toUpperCase();
        const rBank = (e.receiver_bank || '').toUpperCase();
        if (!sBank.includes(bankFilter) && !rBank.includes(bankFilter)) {
          isDimmed = true;
        }
      }

      return {
        id: e.id,
        source: e.source,
        target: e.target,
        animated: isSuspicious,
        style: {
          stroke: strokeColor,
          strokeWidth: isSuspicious ? 2.5 : 1.5,
          opacity: isDimmed ? 0.12 : 0.9,
          strokeDasharray: isSuspicious ? undefined : '5 4',
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: strokeColor,
          width: 14,
          height: 14,
        },
        label: isDimmed ? undefined : `₹${(e.amount || 0).toLocaleString()}`,
        labelStyle: { fill: '#94a3b8', fontWeight: 600, fontSize: 9 },
        labelBgStyle: {
          fill: '#0f172a',
          fillOpacity: 0.85,
          stroke: strokeColor,
          strokeWidth: 1,
          rx: 4,
          ry: 4,
        },
      };
    });
  }, [edgesData, severedEdges, isPostDisruption, patternFilter, bankFilter]);

  return (
    <div className="relative w-full h-[580px] rounded-2xl overflow-hidden glass-panel border border-slate-800 shadow-2xl">
      {/* Top Controls Toolbar */}
      <div className="absolute top-4 left-5 right-5 z-10 flex flex-wrap items-center justify-between gap-3 pointer-events-none">
        <div className="flex flex-wrap items-center gap-2 pointer-events-auto">
          <div className="px-3 py-1.5 rounded-xl bg-slate-900/95 backdrop-blur-md border border-cyan-500/30 text-xs font-bold text-white flex items-center gap-2 shadow-lg">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <span>Four-Bank Unified Interconnected Ecosystem</span>
          </div>

          {/* Pattern Highlights */}
          <div className="hidden sm:flex items-center gap-1 bg-slate-950/90 backdrop-blur-md p-1 rounded-xl border border-slate-800 text-[11px] font-semibold">
            {[
              { id: 'ALL', label: 'All Patterns' },
              { id: 'CIRCULAR', label: '🔄 4-Bank Loop' },
              { id: 'FAN_IN', label: '📥 Smurfing' },
              { id: 'FAN_OUT', label: '📤 Dispersion' },
            ].map((p) => (
              <button
                key={p.id}
                onClick={() => setPatternFilter(p.id)}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  patternFilter === p.id
                    ? 'bg-purple-600 text-white font-bold shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* Bank Quick Filter */}
          <div className="hidden md:flex items-center gap-1 bg-slate-950/90 backdrop-blur-md p-1 rounded-xl border border-slate-800 text-[11px] font-semibold">
            {['ALL', 'BANK_A', 'BANK_B', 'BANK_C', 'BANK_D'].map((b) => (
              <button
                key={b}
                onClick={() => setBankFilter(b)}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  bankFilter === b
                    ? 'bg-cyan-500 text-slate-950 font-bold shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {b === 'ALL' ? 'All Banks' : b.replace('BANK_', 'Bank ')}
              </button>
            ))}
          </div>
        </div>

        {/* View Mode & Layout Buttons */}
        <div className="flex items-center gap-2 pointer-events-auto">
          {/* Layout Toggle */}
          <button
            onClick={() => setLayoutMode(layoutMode === 'quadrant' ? 'flow' : 'quadrant')}
            className="px-3 py-1.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center gap-1.5 shadow-lg transition-all"
            title="Toggle Layout"
          >
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>{layoutMode === 'quadrant' ? '4-Bank Quadrants' : 'Flow DAG'}</span>
          </button>

          {/* Pre vs Post Disruption Toggle */}
          <button
            onClick={() => onToggleDisruption(!isPostDisruption)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all duration-300 flex items-center gap-2 shadow-lg ${
              isPostDisruption
                ? 'bg-rose-600/90 hover:bg-rose-500 text-white border border-rose-400 ring-2 ring-rose-500/30'
                : 'bg-cyan-600/90 hover:bg-cyan-500 text-white border border-cyan-400 ring-2 ring-cyan-500/30'
            }`}
          >
            {isPostDisruption ? (
              <>
                <ShieldAlert className="w-4 h-4 text-white" />
                <span>🛡️ Intercepted Mode</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-white" />
                <span>⚡ Active Ecosystem</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Institutional Quadrant Watermark Overlays */}
      {layoutMode === 'quadrant' && (
        <div className="absolute inset-0 pointer-events-none grid grid-cols-2 grid-rows-2 p-5 gap-6 opacity-35">
          <div className="border border-cyan-500/20 rounded-2xl p-3 flex flex-col justify-start">
            <span className="text-[10px] font-bold tracking-widest text-cyan-400 uppercase">
              BANK A • Retail Clearing & High-Velocity UPI Hub
            </span>
          </div>
          <div className="border border-emerald-500/20 rounded-2xl p-3 flex flex-col justify-start items-end">
            <span className="text-[10px] font-bold tracking-widest text-emerald-400 uppercase">
              BANK B • Corporate Treasury & Merchant Settlement
            </span>
          </div>
          <div className="border border-purple-500/20 rounded-2xl p-3 flex flex-col justify-end">
            <span className="text-[10px] font-bold tracking-widest text-purple-400 uppercase">
              BANK C • Regional Cooperative Credit Society
            </span>
          </div>
          <div className="border border-amber-500/20 rounded-2xl p-3 flex flex-col justify-end items-end">
            <span className="text-[10px] font-bold tracking-widest text-amber-400 uppercase">
              BANK D • Private Wealth & Remittance Gateway
            </span>
          </div>
        </div>
      )}

      {/* React Flow Canvas */}
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        nodeTypes={nodeTypes}
        onNodeClick={(_, node) => onSelectNode(node.id)}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.25}
        maxZoom={1.6}
        className="bg-[#080d1a]"
      >
        <Background color="#1e293b" gap={24} size={1} />
        <Controls className="!bg-slate-900 !border-slate-800 !fill-slate-300 !rounded-xl !overflow-hidden !shadow-xl" />
        <MiniMap
          nodeColor={(n) => {
            const b = (n.data?.bank || '').toUpperCase();
            if (b.includes('A')) return '#06b6d4';
            if (b.includes('B')) return '#10b981';
            if (b.includes('C')) return '#a855f7';
            return '#f59e0b';
          }}
          maskColor="rgba(7, 11, 20, 0.75)"
          className="!bg-slate-950 !border !border-slate-800 !rounded-xl !overflow-hidden"
        />
      </ReactFlow>

      {/* Bottom Ecosystem Legend */}
      <div className="absolute bottom-4 left-5 z-10 hidden md:flex items-center gap-3 px-3.5 py-1.5 rounded-xl bg-slate-900/90 backdrop-blur-md border border-slate-800 text-[11px] text-slate-300 shadow-lg pointer-events-none">
        <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Ecosystem Legend:</span>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
          <span>Bank A (Retail)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
          <span>Bank B (Corporate)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-purple-400" />
          <span>Bank C (Cooperative)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
          <span>Bank D (Wealth)</span>
        </div>
        <span className="text-slate-600">|</span>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
          <span className="text-rose-300 font-bold">Choke Point Bottleneck</span>
        </div>
      </div>
    </div>
  );
}
