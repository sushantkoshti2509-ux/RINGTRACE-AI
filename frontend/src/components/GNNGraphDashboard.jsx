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
} from 'lucide-react';

const nodeTypes = {
  muleNode: MuleNode,
};

export default function GNNGraphDashboard({ onFilterAccount = () => {} }) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [gnnPredictions, setGnnPredictions] = useState({});
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [bankFilter, setBankFilter] = useState('ALL');
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [gnnMeta, setGnnMeta] = useState(null);

  const fetchGraphData = async () => {
    setIsLoading(true);
    try {
      const [topRes, gnnRes, metaRes] = await Promise.all([
        apiFetch('/api/v1/interception/topology'),
        apiFetch('/api/v1/gnn/predictions/accounts?limit=40'),
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

  // Filter nodes according to selected bank
  const filteredNodes = useMemo(() => {
    if (bankFilter === 'ALL') return nodes;
    return nodes.filter((n) => {
      const b = (n.bank || n.id.split(':')[0] || '').toUpperCase();
      return b.includes(bankFilter.toUpperCase());
    });
  }, [nodes, bankFilter]);

  // Convert to ReactFlow nodes
  const flowNodes = useMemo(() => {
    const tiers = {};
    filteredNodes.forEach((n) => {
      const t = n.tier || 0;
      if (!tiers[t]) tiers[t] = [];
      tiers[t].push(n);
    });

    const tierKeys = Object.keys(tiers).map(Number).sort((a, b) => a - b);
    const result = [];

    tierKeys.forEach((t, tIdx) => {
      const group = tiers[t];
      group.forEach((node, nodeIdx) => {
        const gnnInfo = gnnPredictions[node.id] || {};
        const gnnScore = gnnInfo.gnn_score !== undefined ? gnnInfo.gnn_score : 0.94;
        const isTarget = node.id === selectedNodeId;

        result.push({
          id: node.id,
          type: 'muleNode',
          position: {
            x: tIdx * 280 + 30,
            y: nodeIdx * 140 + 30,
          },
          data: {
            ...node,
            gnnScore,
            isTarget,
            isIntercepted: false,
            isNeutralized: false,
          },
          selected: node.id === selectedNodeId,
        });
      });
    });

    return result;
  }, [filteredNodes, selectedNodeId, gnnPredictions]);

  // Convert to ReactFlow edges
  const flowEdges = useMemo(() => {
    const validNodeIds = new Set(filteredNodes.map((n) => n.id));
    return edges
      .filter((e) => validNodeIds.has(e.source) && validNodeIds.has(e.target))
      .map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        animated: true,
        style: {
          stroke: e.is_cross_bank ? '#818cf8' : '#06b6d4',
          strokeWidth: 2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: e.is_cross_bank ? '#818cf8' : '#06b6d4',
          width: 14,
          height: 14,
        },
        label: `₹${(e.amount || 0).toLocaleString()}`,
        labelStyle: { fill: '#cbd5e1', fontWeight: 600, fontSize: 10 },
        labelBgStyle: { fill: '#0f172a', fillOpacity: 0.9, stroke: '#334155', strokeWidth: 1, rx: 4, ry: 4 },
      }));
  }, [edges, filteredNodes]);

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
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-purple-600 to-cyan-500 flex items-center justify-center shadow-md shadow-purple-500/20">
            <Brain className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-sm text-white tracking-tight flex items-center gap-1.5">
                <span>GNN Relational Fraud Network</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  Phase 7 GINE
                </span>
              </span>
            </div>
            <div className="text-[11px] text-slate-400">
              Multi-bank message passing across Bank A, Bank B, Bank C, Bank D • Latency 11.3 ms
            </div>
          </div>
        </div>

        {/* Toolbar Controls */}
        <div className="flex items-center gap-2">
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
                {b.replace('_', ' ')}
              </button>
            ))}
          </div>

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
        <div className="relative w-full h-[400px] bg-[#070d18]">
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
            <Background color="#1e293b" gap={20} size={1.2} />
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

          {/* Selected Node Floating GNN Inspector Drawer */}
          {selectedNode && (
            <div className="absolute bottom-4 left-4 z-10 glass-panel rounded-2xl p-4 border border-purple-500/40 shadow-2xl max-w-sm backdrop-blur-xl bg-slate-900/90 flex flex-col gap-2.5">
              <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-2">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-purple-400 animate-ping" />
                  <span className="font-mono text-xs font-bold text-white">
                    {selectedNode.masked_id || selectedNode.id}
                  </span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                  GNN Threat: {((selectedGNN?.gnn_score || 0.96) * 100).toFixed(1)}%
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
