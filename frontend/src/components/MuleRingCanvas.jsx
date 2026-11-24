import React, { useState, useEffect, useMemo } from 'react';
import { apiFetch } from '../api';
import {
  ReactFlow,
  Background,
  Controls,
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
  AlertTriangle,
  Info,
} from 'lucide-react';

const nodeTypes = {
  muleNode: MuleNode,
};

function getBankKey(node) {
  const raw = (node.bank || node.id || '').toUpperCase();
  if (raw.includes('_B') || raw.includes(':B') || raw.endsWith('BANK_B') || raw.includes('BANK B')) return 'BANK_B';
  if (raw.includes('_C') || raw.includes(':C') || raw.endsWith('BANK_C') || raw.includes('BANK C')) return 'BANK_C';
  if (raw.includes('_D') || raw.includes(':D') || raw.endsWith('BANK_D') || raw.includes('BANK D')) return 'BANK_D';
  return 'BANK_A';
}

// 4-Bank Interconnected Layout Generator with balanced quadrant spacing & zero line-crossing
function layoutEcosystemNodes(nodes, layoutMode = 'quadrant') {
  if (layoutMode === 'flow') {
    // Left-to-right pass-through pipeline across Bank A -> Bank B -> Bank C -> Bank D
    const pos = {};
    const bankOrder = ['BANK_A', 'BANK_B', 'BANK_C', 'BANK_D'];
    const bankBuckets = { BANK_A: [], BANK_B: [], BANK_C: [], BANK_D: [] };
    nodes.forEach((n) => {
      const bKey = getBankKey(n);
      bankBuckets[bKey].push(n);
    });
    bankOrder.forEach((bKey, colIdx) => {
      bankBuckets[bKey].forEach((n, rowIdx) => {
        pos[n.id] = {
          x: 60 + colIdx * 270,
          y: 100 + rowIdx * 170,
        };
      });
    });
    return pos;
  }

  // Unified 4-Quadrant Institutional Ecosystem:
  // Bank A (Top-Left: 60, 70)       ────────►   Bank B (Top-Right: 680, 70)
  //         ▲                                             │
  //         │                                             ▼
  // Bank D (Bottom-Left: 60, 390)    ◄────────   Bank C (Bottom-Right: 680, 390)
  const pos = {};
  const buckets = { BANK_A: [], BANK_B: [], BANK_C: [], BANK_D: [] };
  nodes.forEach((n) => {
    const bKey = getBankKey(n);
    buckets[bKey].push(n);
  });

  // Top-Left: Bank A (Retail Clearing Hub)
  buckets.BANK_A.forEach((n, i) => {
    pos[n.id] = { x: 60, y: 70 + i * 140 };
  });

  // Top-Right: Bank B (Corporate Treasury Core)
  buckets.BANK_B.forEach((n, i) => {
    pos[n.id] = { x: 680, y: 70 + i * 140 };
  });

  // Bottom-Right: Bank C (Regional Cooperative Society)
  buckets.BANK_C.forEach((n, i) => {
    pos[n.id] = { x: 680, y: 390 + i * 140 };
  });

  // Bottom-Left: Bank D (Wealth & Remittance Gateway)
  buckets.BANK_D.forEach((n, i) => {
    pos[n.id] = { x: 60, y: 390 + i * 140 };
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
  const [localNodes, setLocalNodes] = useState(nodesData);
  const [localEdges, setLocalEdges] = useState(edgesData);
  const [topoMetadata, setTopoMetadata] = useState(null);
  const [layoutMode, setLayoutMode] = useState('quadrant'); // 'quadrant' | 'flow'
  const [bankFilter, setBankFilter] = useState('ALL');

  const fetchTopology = async () => {
    try {
      const res = await apiFetch('/api/v1/interception/topology?topology_type=HYBRID');
      if (res.ok) {
        const data = await res.json();
        setLocalNodes(data.nodes || []);
        setLocalEdges(data.edges || []);
        setTopoMetadata(data);
      }
    } catch (e) {
      console.warn('Failed to switch topology:', e);
    }
  };

  useEffect(() => {
    fetchTopology();
  }, []);

  // Compute node positions
  const nodePositions = useMemo(() => {
    return layoutEcosystemNodes(localNodes, layoutMode);
  }, [localNodes, layoutMode]);

  // Convert topology nodes into React Flow nodes arranged in Unified 4-Bank Layout
  const flowNodes = useMemo(() => {
    return localNodes.map((node) => {
      const isTarget = node.id === targetNodeId;
      const isNeutralized = isPostDisruption && neutralizedNodes.includes(node.id);
      const pos = nodePositions[node.id] || { x: 100, y: 100 };

      // Filter check
      const nodeBank = (node.bank || node.id.split(':')[0] || '').toUpperCase();
      const matchesBank = bankFilter === 'ALL' || nodeBank.includes(bankFilter.toUpperCase());
      const isDimmed = !matchesBank;

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
    localNodes,
    nodePositions,
    selectedNodeId,
    targetNodeId,
    neutralizedNodes,
    isPostDisruption,
    bankFilter,
  ]);

  // Convert topology edges into React Flow edges with animated pulses or severed status
  const flowEdges = useMemo(() => {
    return localEdges.map((e) => {
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
      const isTransit =
        (e.pattern_type || '').includes('TRANSIT') ||
        (e.pattern_type || '').includes('CHAIN') ||
        (e.pattern_type || '').includes('LAYERED');
      const isSuspicious = e.is_suspicious === 1 || isCirc || isFanIn || isFanOut || isTransit;

      let strokeColor = '#64748b'; // default legitimate
      if (isCirc) strokeColor = '#f43f5e';
      else if (isFanIn) strokeColor = '#a855f7';
      else if (isFanOut) strokeColor = '#f59e0b';
      else if (isTransit) strokeColor = '#06b6d4';
      else if (e.is_cross_bank) strokeColor = '#10b981';

      let isDimmed = false;
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
        type: 'smoothstep',
        pathOptions: { borderRadius: 16 },
        animated: isSuspicious,
        style: {
          stroke: strokeColor,
          strokeWidth: isSuspicious ? 2.5 : 1.5,
          opacity: isDimmed ? 0.12 : 0.95,
          strokeDasharray: isSuspicious ? undefined : '5 4',
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: strokeColor,
          width: 15,
          height: 15,
        },
        label: isDimmed ? undefined : `₹${(e.amount || 0).toLocaleString()}`,
        labelStyle: { fill: '#f1f5f9', fontWeight: 700, fontSize: 10 },
        labelBgStyle: {
          fill: '#0f172a',
          fillOpacity: 0.92,
          stroke: strokeColor,
          strokeWidth: 1.5,
          rx: 4,
          ry: 4,
        },
      };
    });
  }, [localEdges, severedEdges, isPostDisruption, bankFilter]);

  return (
    <div className="relative w-full rounded-2xl overflow-hidden glass-panel border border-slate-800 shadow-2xl flex flex-col">
      {/* Top Controls Toolbar */}
      <div className="p-3.5 bg-slate-900/95 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-cyan-500/30 text-xs font-bold text-white flex items-center gap-2 shadow-lg">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <span>Four-Bank Unified Relational Fraud Network</span>
          </div>

          {/* Bank Quick Filter */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-[11px] font-semibold">
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
        <div className="flex items-center gap-2">
          {/* Layout Toggle */}
          <button
            onClick={() => setLayoutMode(layoutMode === 'quadrant' ? 'flow' : 'quadrant')}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center gap-1.5 shadow-lg transition-all"
            title="Toggle Layout"
          >
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>{layoutMode === 'quadrant' ? '4-Bank Quadrants' : 'Flow DAG'}</span>
          </button>

          {/* Pre vs Post Disruption Toggle */}
          <button
            onClick={() => onToggleDisruption(!isPostDisruption)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all duration-300 flex items-center gap-2 shadow-lg ${
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
                <span>⚡ Active Flow</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* React Flow Canvas Body */}
      <div className="relative w-full h-[600px] bg-[#080d1a]">
        {/* Institutional Quadrant Watermark Overlays (Clockwise 4-Bank Topology: A -> B -> C -> D -> A) */}
        {layoutMode === 'quadrant' && (
          <div className="absolute inset-0 pointer-events-none grid grid-cols-2 grid-rows-2 p-5 gap-6">
            {/* Top-Left: Bank A */}
            <div className="border border-cyan-500/25 bg-cyan-950/10 rounded-2xl p-3 flex flex-col justify-start">
              <div className="inline-flex items-center gap-1.5 w-fit px-2.5 py-1 rounded-lg bg-cyan-950/70 border border-cyan-500/40 shadow-xs">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                <span className="text-[10px] font-extrabold tracking-widest text-cyan-300 uppercase">
                  BANK A • Retail Clearing Hub (A101 · A102)
                </span>
              </div>
            </div>

            {/* Top-Right: Bank B */}
            <div className="border border-emerald-500/25 bg-emerald-950/10 rounded-2xl p-3 flex flex-col justify-start items-end">
              <div className="inline-flex items-center gap-1.5 w-fit px-2.5 py-1 rounded-lg bg-emerald-950/70 border border-emerald-500/40 shadow-xs">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-[10px] font-extrabold tracking-widest text-emerald-300 uppercase">
                  BANK B • Corporate Treasury Core (B201 · B205)
                </span>
              </div>
            </div>

            {/* Bottom-Left: Bank D */}
            <div className="border border-amber-500/25 bg-amber-950/10 rounded-2xl p-3 flex flex-col justify-end">
              <div className="inline-flex items-center gap-1.5 w-fit px-2.5 py-1 rounded-lg bg-amber-950/70 border border-amber-500/40 shadow-xs">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                <span className="text-[10px] font-extrabold tracking-widest text-amber-300 uppercase">
                  BANK D • Wealth & Remittance Gateway (D401 · D410)
                </span>
              </div>
            </div>

            {/* Bottom-Right: Bank C */}
            <div className="border border-purple-500/25 bg-purple-950/10 rounded-2xl p-3 flex flex-col justify-end items-end">
              <div className="inline-flex items-center gap-1.5 w-fit px-2.5 py-1 rounded-lg bg-purple-950/70 border border-purple-500/40 shadow-xs">
                <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                <span className="text-[10px] font-extrabold tracking-widest text-purple-300 uppercase">
                  BANK C • Regional Cooperative Society (C301 · C310)
                </span>
              </div>
            </div>
          </div>
        )}

        <ReactFlow
          nodes={flowNodes}
          edges={flowEdges}
          nodeTypes={nodeTypes}
          onNodeClick={(_, node) => onSelectNode(node.id)}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.25}
          maxZoom={1.6}
          proOptions={{ hideAttribution: true }}
          className="bg-[#080d1a]"
        >
          <Background color="#1e293b" gap={24} size={1} />
          <Controls className="!bg-slate-900 !border-slate-800 !fill-slate-300 !rounded-xl !overflow-hidden !shadow-xl" />
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
    </div>
  );
}
