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
  AlertTriangle,
  Info,
  CheckCircle,
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

// 4-Bank Interconnected Layout Generator with balanced quadrant spacing & zero line-crossings
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

export default function GNNGraphDashboard({ onFilterAccount = () => {} }) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [gnnPredictions, setGnnPredictions] = useState({});
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [topologyInfo, setTopologyInfo] = useState(null);
  const [bankFilter, setBankFilter] = useState('ALL');
  const [layoutMode, setLayoutMode] = useState('quadrant'); // 'quadrant' | 'flow'
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const fetchGraphData = async () => {
    setIsLoading(true);
    try {
      const [topRes, gnnRes] = await Promise.all([
        apiFetch('/api/v1/interception/topology?topology_type=HYBRID'),
        apiFetch('/api/v1/gnn/predictions/accounts?limit=60'),
      ]);

      if (topRes.ok) {
        const topData = await topRes.json();
        setNodes(topData.nodes || []);
        setEdges(topData.edges || []);
        setTopologyInfo(topData);
        if (topData.nodes?.length > 0) {
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
    return layoutEcosystemNodes(nodes, layoutMode);
  }, [nodes, layoutMode]);

  // Convert to ReactFlow nodes with active highlighting
  const flowNodes = useMemo(() => {
    return nodes.map((node) => {
      const gnnInfo = gnnPredictions[node.id] || {};
      const gnnScore =
        gnnInfo.gnn_score !== undefined
          ? gnnInfo.gnn_score
          : node.is_mule
          ? 0.94
          : 0.08;
      const isTarget = node.id === selectedNodeId;
      const pos = nodePositions[node.id] || { x: 100, y: 100 };

      // Highlight checking
      const nodeBank = (node.bank || node.id.split(':')[0] || '').toUpperCase();
      const matchesBank = bankFilter === 'ALL' || nodeBank.includes(bankFilter.toUpperCase());
      const isDimmed = !matchesBank;

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
  }, [nodes, nodePositions, selectedNodeId, gnnPredictions, bankFilter]);

  // Convert to ReactFlow edges
  const flowEdges = useMemo(() => {
    return edges.map((e) => {
      const isCirc = (e.pattern_type || '').includes('CIRCULAR');
      const isFanIn = (e.pattern_type || '').includes('FAN_IN');
      const isFanOut = (e.pattern_type || '').includes('FAN_OUT');
      const isTransit =
        (e.pattern_type || '').includes('TRANSIT') ||
        (e.pattern_type || '').includes('CHAIN') ||
        (e.pattern_type || '').includes('LAYERED');
      const isSuspicious = e.is_suspicious === 1 || isCirc || isFanIn || isFanOut || isTransit;

      // Color coding per topology
      let strokeColor = '#64748b'; // default legitimate
      if (isCirc) strokeColor = '#f43f5e'; // glowing red
      else if (isFanIn) strokeColor = '#a855f7'; // violet
      else if (isFanOut) strokeColor = '#f59e0b'; // amber
      else if (isTransit) strokeColor = '#06b6d4'; // cyan
      else if (e.is_cross_bank) strokeColor = '#10b981'; // emerald interbank clearing

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
        labelStyle: { fill: '#0f172a', fontWeight: 800, fontSize: 10 },
        labelBgStyle: {
          fill: '#ffffff',
          fillOpacity: 0.98,
          stroke: strokeColor,
          strokeWidth: 1.5,
          rx: 6,
          ry: 6,
        },
      };
    });
  }, [edges, bankFilter]);

  const selectedNode = useMemo(() => {
    return nodes.find((n) => n.id === selectedNodeId);
  }, [nodes, selectedNodeId]);

  const selectedGNN = useMemo(() => {
    return selectedNodeId ? gnnPredictions[selectedNodeId] : null;
  }, [selectedNodeId, gnnPredictions]);

  return (
    <div className="rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col transition-all bg-white">
      {/* Top Banner Toolbar (Light Template Theme) */}
      <div className="p-4 bg-white border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-md shadow-blue-500/20 text-white">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base text-slate-900 tracking-tight flex items-center gap-2">
                <span>Four-Bank Unified Relational Fraud Network</span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-extrabold bg-blue-50 text-blue-700 border border-blue-200 shadow-xs">
                  Bank A · B · C · D
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-xs">
                  Unified Ecosystem
                </span>
              </span>
            </div>
            <div className="text-xs text-slate-600 font-semibold mt-0.5">
              One unified network combining accounts and transactions across all four banks with GNN relational fraud detection
            </div>
          </div>
        </div>

        {/* Toolbar Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Bank Quick Filter */}
          <div className="flex items-center gap-1 bg-slate-50 p-1 rounded-xl border border-slate-200 text-xs font-bold">
            {['ALL', 'BANK_A', 'BANK_B', 'BANK_C', 'BANK_D'].map((b) => (
              <button
                key={b}
                onClick={() => setBankFilter(b)}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  bankFilter === b
                    ? 'bg-blue-600 text-white font-extrabold shadow-xs'
                    : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                {b === 'ALL' ? 'All Banks' : b.replace('BANK_', 'Bank ')}
              </button>
            ))}
          </div>

          {/* Layout Mode Toggle */}
          <button
            onClick={() => setLayoutMode(layoutMode === 'quadrant' ? 'flow' : 'quadrant')}
            className="px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 text-slate-800 text-xs font-bold border border-slate-200 flex items-center gap-1.5 transition-colors shadow-xs"
            title="Toggle between 4-Bank Ecosystem Mesh and Flow DAG"
          >
            <Layers className="w-4 h-4 text-blue-600" />
            <span>{layoutMode === 'quadrant' ? '4-Bank Quadrants' : 'Flow DAG'}</span>
          </button>

          <button
            onClick={fetchGraphData}
            disabled={isLoading}
            className="p-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 transition-colors shadow-xs"
            title="Refresh GNN Topology"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
          </button>

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 transition-colors shadow-xs"
            title={isCollapsed ? 'Expand GNN Graph' : 'Collapse GNN Graph'}
          >
            {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Collapsible Canvas Body */}
      {!isCollapsed && (
        <div className="relative w-full h-[600px] bg-[#f8fafc] border-t border-slate-100">
          {/* Institutional Quadrant Overlays (Clockwise 4-Bank Topology: A -> B -> C -> D -> A) */}
          {layoutMode === 'quadrant' && (
            <div className="absolute inset-0 pointer-events-none grid grid-cols-2 grid-rows-2 p-5 gap-6">
              {/* Top-Left: Bank A */}
              <div className="border-2 border-dashed border-cyan-400 bg-cyan-50/50 rounded-2xl p-3 flex flex-col justify-start">
                <div className="inline-flex items-center gap-2 w-fit px-3 py-1.5 rounded-xl bg-white border border-cyan-300 shadow-xs">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-500 animate-pulse" />
                  <span className="text-xs font-extrabold tracking-wider text-cyan-950 uppercase font-mono">
                    BANK A • Retail Clearing Hub (A101 · A102)
                  </span>
                </div>
              </div>

              {/* Top-Right: Bank B */}
              <div className="border-2 border-dashed border-emerald-400 bg-emerald-50/50 rounded-2xl p-3 flex flex-col justify-start items-end">
                <div className="inline-flex items-center gap-2 w-fit px-3 py-1.5 rounded-xl bg-white border border-emerald-300 shadow-xs">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-xs font-extrabold tracking-wider text-emerald-950 uppercase font-mono">
                    BANK B • Corporate Treasury Core (B201 · B205)
                  </span>
                </div>
              </div>

              {/* Bottom-Left: Bank D */}
              <div className="border-2 border-dashed border-amber-400 bg-amber-50/50 rounded-2xl p-3 flex flex-col justify-end">
                <div className="inline-flex items-center gap-2 w-fit px-3 py-1.5 rounded-xl bg-white border border-amber-300 shadow-xs">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse" />
                  <span className="text-xs font-extrabold tracking-wider text-amber-950 uppercase font-mono">
                    BANK D • Wealth & Remittance Gateway (D401 · D410)
                  </span>
                </div>
              </div>

              {/* Bottom-Right: Bank C */}
              <div className="border-2 border-dashed border-purple-400 bg-purple-50/50 rounded-2xl p-3 flex flex-col justify-end items-end">
                <div className="inline-flex items-center gap-2 w-fit px-3 py-1.5 rounded-xl bg-white border border-purple-300 shadow-xs">
                  <span className="w-2.5 h-2.5 rounded-full bg-purple-500 animate-pulse" />
                  <span className="text-xs font-extrabold tracking-wider text-purple-950 uppercase font-mono">
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
            onNodeClick={(_, node) => setSelectedNodeId(node.id)}
            fitView
            fitViewOptions={{ padding: 0.16 }}
            minZoom={0.25}
            maxZoom={1.6}
            proOptions={{ hideAttribution: true }}
            className="bg-[#f8fafc]"
          >
            <Background color="#cbd5e1" gap={24} size={1.2} />
            <Controls className="!bg-white !border !border-slate-300 !text-slate-800 !fill-slate-800 !rounded-xl !overflow-hidden !shadow-md" />
          </ReactFlow>

          {/* Topology Legend Bar (Top-Right, neatly positioned without overlapping Bank A) */}
          <div className="absolute top-4 right-4 z-10 hidden md:flex flex-wrap items-center gap-3 bg-white/98 backdrop-blur-md px-4 py-2 rounded-xl border border-slate-200 text-xs text-slate-800 font-bold shadow-md pointer-events-none">
            <span className="font-extrabold text-slate-900 flex items-center gap-1.5">
              <Network className="w-4 h-4 text-blue-600" /> Legend:
            </span>
            <span className="flex items-center gap-1 text-cyan-900 font-extrabold">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-500" /> Bank A
            </span>
            <span className="flex items-center gap-1 text-emerald-900 font-extrabold">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Bank B
            </span>
            <span className="flex items-center gap-1 text-purple-900 font-extrabold">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500" /> Bank C
            </span>
            <span className="flex items-center gap-1 text-amber-900 font-extrabold">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Bank D
            </span>
            <span className="text-slate-300">|</span>
            <span className="flex items-center gap-1 text-rose-700 font-extrabold">
              <span className="w-3 h-1 bg-rose-500 rounded" /> Circular Loop
            </span>
            <span className="flex items-center gap-1 text-purple-700 font-extrabold">
              <span className="w-3 h-1 bg-purple-500 rounded" /> Smurfing Fan-In
            </span>
            <span className="flex items-center gap-1 text-emerald-700 font-extrabold">
              <span className="w-3 h-1 bg-emerald-500 rounded" /> Clearing
            </span>
          </div>

          {/* Selected Node Floating GNN Inspector Drawer (Clean Light Card, High Contrast) */}
          {selectedNode && (
            <div className="absolute bottom-4 left-4 z-20 bg-white/98 backdrop-blur-xl rounded-2xl p-4 border border-slate-200 shadow-xl max-w-sm flex flex-col gap-3 animate-fadeIn">
              <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-2">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-pulse shrink-0" />
                  <span className="font-mono text-base font-extrabold text-slate-900">
                    {selectedNode.account_code || selectedNode.id}
                  </span>
                  <span className="text-xs text-slate-600 font-mono font-bold">
                    ({selectedNode.masked_id})
                  </span>
                </div>
                <span
                  className={`px-2.5 py-1 rounded-full text-xs font-mono font-extrabold border shadow-xs ${
                    selectedNode.is_mule
                      ? 'bg-rose-50 text-rose-700 border-rose-200'
                      : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  }`}
                >
                  GNN Threat: {((selectedGNN?.gnn_score || (selectedNode.is_mule ? 0.94 : 0.08)) * 100).toFixed(1)}%
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="text-slate-600 block text-xs font-bold uppercase tracking-wider">Bank Institution</span>
                  <span className="font-extrabold text-slate-900 font-mono text-sm mt-0.5 block">{selectedNode.bank}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="text-slate-600 block text-xs font-bold uppercase tracking-wider">Relational Role</span>
                  <span className="font-bold text-slate-800 truncate block text-xs mt-0.5">
                    {selectedNode.role || 'Transit Relay'}
                  </span>
                </div>
              </div>

              <div className="pt-1">
                <button
                  onClick={() => onFilterAccount(selectedNode.account_code || selectedNode.id)}
                  className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-blue-500/25 transition-all"
                >
                  <Filter className="w-4 h-4" />
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
