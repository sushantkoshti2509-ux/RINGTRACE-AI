import React, { useState, useEffect, useMemo } from 'react';
import { apiFetch } from '../api';
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
  Brain,
  Network,
  Sparkles,
  Zap,
  Filter,
  Eye,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Activity,
  ShieldCheck,
  ShieldAlert,
  Layers,
  Repeat,
  ArrowRight,
} from 'lucide-react';

const nodeTypes = {
  muleNode: MuleNode,
};

// 4-Bank Interconnected Layout Generator
function layoutEcosystemNodes(nodes, edges, layoutMode = 'quadrant') {
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

  // Unified 4-Bank Ecosystem: Institutional Quadrants + Central Laundering Corridor
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
    const isBridge = (role.includes('collector') || role.includes('bridge') || role.includes('transit')) && (n.in_degree >= 1 && n.out_degree >= 1);

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

export default function GNNGraphDashboard({ onFilterAccount = () => {} }) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [gnnPredictions, setGnnPredictions] = useState({});
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [bankFilter, setBankFilter] = useState('ALL');
  const [patternFilter, setPatternFilter] = useState('ALL');
  const [layoutMode, setLayoutMode] = useState('quadrant'); // 'quadrant' | 'flow'
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [gnnMeta, setGnnMeta] = useState(null);

  const fetchGraphData = async () => {
    setIsLoading(true);
    try {
      const [topRes, gnnRes, metaRes] = await Promise.all([
        apiFetch('/api/v1/interception/topology'),
        apiFetch('/api/v1/gnn/predictions/accounts?limit=60'),
        apiFetch('/api/v1/gnn/metadata'),
      ]);

      if (topRes.ok) {
        const topData = await topRes.json();
        setNodes(topData.nodes || []);
        setEdges(topData.edges || []);
        if (topData.nodes?.length > 0 && !selectedNodeId) {
          setSelectedNodeId(topData.nodes[0].id);
        }
      }

      if (gnnRes.ok) {
        const gnnData = await gnnRes.json();
        const map = {};
        (gnnData.predictions || []).forEach((p) => {
          map[p.account_id] = p;
        });
        setGnnPredictions(map);
      }

      if (metaRes.ok) {
        setGnnMeta(await metaRes.json());
      }
    } catch (err) {
      console.error('Failed to load GNN dashboard graph:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphData();
  }, []);

  // Compute positions
  const nodePositions = useMemo(() => {
    return layoutEcosystemNodes(nodes, edges, layoutMode);
  }, [nodes, edges, layoutMode]);

  // Convert to ReactFlow nodes with active highlighting
  const flowNodes = useMemo(() => {
    return nodes.map((node) => {
      const gnnInfo = gnnPredictions[node.id] || {};
      const gnnScore = gnnInfo.gnn_score !== undefined ? gnnInfo.gnn_score : (node.is_mule ? 0.94 : 0.08);
      const isTarget = node.id === selectedNodeId;
      const pos = nodePositions[node.id] || { x: 100, y: 100 };

      // Highlight checking
      const nodeBank = (node.bank || node.id.split(':')[0] || '').toUpperCase();
      const matchesBank = bankFilter === 'ALL' || nodeBank.includes(bankFilter.toUpperCase());
      const matchesPattern = patternFilter === 'ALL' || (node.pattern_type && node.pattern_type.includes(patternFilter));
      const isDimmed = !matchesBank || (!matchesPattern && patternFilter !== 'ALL');

      return {
        id: node.id,
        type: 'muleNode',
        position: pos,
        data: {
          ...node,
          gnnScore,
          isTarget,
          isIntercepted: false,
          isNeutralized: false,
          isDimmed,
        },
        style: {
          opacity: isDimmed ? 0.22 : 1.0,
          transition: 'all 0.3s ease',
        },
        selected: node.id === selectedNodeId,
      };
    });
  }, [nodes, nodePositions, selectedNodeId, gnnPredictions, bankFilter, patternFilter]);

  // Convert to ReactFlow edges
  const flowEdges = useMemo(() => {
    return edges.map((e) => {
      const isCirc = (e.pattern_type || '').includes('CIRCULAR');
      const isFanIn = (e.pattern_type || '').includes('FAN_IN');
      const isFanOut = (e.pattern_type || '').includes('FAN_OUT');
      const isTransit = (e.pattern_type || '').includes('TRANSIT') || (e.pattern_type || '').includes('CHAIN');
      const isSuspicious = e.is_suspicious === 1;

      // Color coding per topology
      let strokeColor = '#64748b'; // default legitimate
      if (isCirc) strokeColor = '#f43f5e'; // glowing red
      else if (isFanIn) strokeColor = '#a855f7'; // violet
      else if (isFanOut) strokeColor = '#f59e0b'; // amber
      else if (isTransit) strokeColor = '#06b6d4'; // cyan
      else if (e.is_cross_bank) strokeColor = '#10b981'; // emerald interbank clearing

      // Check pattern match for dimming
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
        labelStyle: { fill: '#cbd5e1', fontWeight: 600, fontSize: 9 },
        labelBgStyle: { fill: '#0f172a', fillOpacity: 0.9, stroke: strokeColor, strokeWidth: 1, rx: 4, ry: 4 },
      };
    });
  }, [edges, patternFilter, bankFilter]);

  const selectedNode = useMemo(() => {
    return nodes.find((n) => n.id === selectedNodeId);
  }, [nodes, selectedNodeId]);

  const selectedGNN = useMemo(() => {
    return selectedNodeId ? gnnPredictions[selectedNodeId] : null;
  }, [selectedNodeId, gnnPredictions]);

  return (
    <div className="glass-panel rounded-2xl border border-cyan-500/25 shadow-2xl overflow-hidden flex flex-col transition-all">
      {/* Top Banner Toolbar */}
      <div className="p-4 bg-slate-900/95 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-600 via-cyan-500 to-emerald-500 flex items-center justify-center shadow-md shadow-purple-500/20">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-sm text-white tracking-tight flex items-center gap-1.5">
                <span>Four-Bank Unified Relational Fraud Network</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  Interconnected Ecosystem
                </span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  GINE + GATv2
                </span>
              </span>
            </div>
            <div className="text-[11px] text-slate-400">
              One unified directed graph containing Bank A, Bank B, Bank C, Bank D • Seamless cross-bank clearing & mule detection
            </div>
          </div>
        </div>

        {/* Toolbar Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Pattern Highlights */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-[11px] font-semibold">
            {[
              { id: 'ALL', label: 'All Patterns' },
              { id: 'CIRCULAR', label: '🔄 Circular Loop' },
              { id: 'FAN_IN', label: '📥 Smurfing' },
              { id: 'FAN_OUT', label: '📤 Dispersion' },
              { id: 'CLEARING', label: '✅ Normal Clearing' },
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

          {/* Layout Mode Toggle */}
          <button
            onClick={() => setLayoutMode(layoutMode === 'quadrant' ? 'flow' : 'quadrant')}
            className="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center gap-1.5 transition-colors"
            title="Toggle between 4-Bank Ecosystem Mesh and Flow DAG"
          >
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>{layoutMode === 'quadrant' ? '4-Bank Quadrants' : 'Flow DAG'}</span>
          </button>

          <button
            onClick={fetchGraphData}
            disabled={isLoading}
            className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
            title="Refresh GNN Topology"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
            title={isCollapsed ? 'Expand GNN Graph' : 'Collapse GNN Graph'}
          >
            {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Collapsible Canvas Body */}
      {!isCollapsed && (
        <div className="relative w-full h-[480px] bg-[#070d18]">
          {/* Institutional Quadrant Overlays (When in Quadrant layout) */}
          {layoutMode === 'quadrant' && (
            <div className="absolute inset-0 pointer-events-none grid grid-cols-2 grid-rows-2 p-4 gap-4 opacity-40">
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

          <ReactFlow
            nodes={flowNodes}
            edges={flowEdges}
            nodeTypes={nodeTypes}
            onNodeClick={(_, node) => setSelectedNodeId(node.id)}
            fitView
            minZoom={0.2}
            maxZoom={1.8}
            attributionPosition="bottom-right"
          >
            <Background color="#1e293b" gap={24} size={1.2} />
            <Controls className="!bg-slate-900 !border-slate-800 !text-slate-300 !fill-slate-300" />
            <MiniMap
              nodeColor={(n) => {
                const b = (n.data?.bank || '').toUpperCase();
                if (b.includes('A')) return '#06b6d4';
                if (b.includes('B')) return '#10b981';
                if (b.includes('C')) return '#a855f7';
                return '#f59e0b';
              }}
              maskColor="rgba(7, 13, 24, 0.75)"
              className="!bg-slate-950/90 !border !border-slate-800 !rounded-xl"
            />
          </ReactFlow>

          {/* Topology Legend Footer Bar */}
          <div className="absolute top-3 left-4 z-10 flex flex-wrap items-center gap-3 bg-slate-950/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-800 text-[10px] text-slate-300">
            <span className="font-bold text-white flex items-center gap-1">
              <Network className="w-3 h-3 text-cyan-400" /> Ecosystem Legend:
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-cyan-400" /> Bank A
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400" /> Bank B
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-purple-400" /> Bank C
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-amber-400" /> Bank D
            </span>
            <span className="text-slate-600">|</span>
            <span className="flex items-center gap-1 text-rose-300 font-semibold">
              <span className="w-2.5 h-0.5 bg-rose-500 rounded" /> Circular Loop
            </span>
            <span className="flex items-center gap-1 text-purple-300 font-semibold">
              <span className="w-2.5 h-0.5 bg-purple-500 rounded" /> Smurfing Fan-In
            </span>
            <span className="flex items-center gap-1 text-emerald-300">
              <span className="w-2.5 h-0.5 bg-emerald-500 rounded" /> Inter-Bank Clearing
            </span>
          </div>

          {/* Selected Node Floating GNN Inspector Drawer */}
          {selectedNode && (
            <div className="absolute bottom-4 left-4 z-10 glass-panel rounded-2xl p-4 border border-cyan-500/40 shadow-2xl max-w-sm backdrop-blur-xl bg-slate-900/90 flex flex-col gap-2.5">
              <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-2">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
                  <span className="font-mono text-xs font-bold text-white">
                    {selectedNode.masked_id || selectedNode.id}
                  </span>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                  selectedNode.is_mule
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                    : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                }`}>
                  GNN Score: {((selectedGNN?.gnn_score || (selectedNode.is_mule ? 0.94 : 0.08)) * 100).toFixed(1)}%
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="p-2 rounded-lg bg-slate-950/80 border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Bank Institution</span>
                  <span className="font-bold text-cyan-300 font-mono">{selectedNode.bank}</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-950/80 border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Relational Role</span>
                  <span className="font-semibold text-slate-200 truncate block">
                    {selectedNode.role || 'Transit Relay'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between gap-2 pt-1">
                <button
                  onClick={() => onFilterAccount(selectedNode.id)}
                  className="w-full px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-[11px] flex items-center justify-center gap-1.5 shadow-md shadow-cyan-600/30 transition-all"
                >
                  <Filter className="w-3 h-3" />
                  <span>Filter Ledger by This Account</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
