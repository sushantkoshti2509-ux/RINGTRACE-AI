import React, { useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import MuleNode from './MuleNode';
import { ShieldCheck, ShieldAlert, Sparkles, Filter } from 'lucide-react';

const nodeTypes = {
  muleNode: MuleNode,
};

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
  // Convert topology nodes into React Flow nodes arranged Left-to-Right
  const flowNodes = useMemo(() => {
    // Group by tier for left-to-right layering
    const tiers = {};
    nodesData.forEach((n) => {
      const t = n.tier || 0;
      if (!tiers[t]) tiers[t] = [];
      tiers[t].push(n);
    });

    const tierKeys = Object.keys(tiers).map(Number).sort((a, b) => a - b);
    const result = [];

    tierKeys.forEach((t, tIdx) => {
      const group = tiers[t];
      group.forEach((node, nodeIdx) => {
        const isTarget = node.id === targetNodeId;
        const isNeutralized = isPostDisruption && neutralizedNodes.includes(node.id);

        result.push({
          id: node.id,
          type: 'muleNode',
          position: {
            x: tIdx * 300 + 40,
            y: nodeIdx * 150 + 60,
          },
          data: {
            ...node,
            isTarget,
            isNeutralized,
            isIntercepted: isPostDisruption && (isTarget || isNeutralized),
          },
          selected: node.id === selectedNodeId,
        });
      });
    });

    return result;
  }, [nodesData, selectedNodeId, targetNodeId, neutralizedNodes, isPostDisruption]);

  // Convert topology edges into React Flow edges with animated pulses or severed status
  const flowEdges = useMemo(() => {
    return edgesData.map((e) => {
      const isSevered = isPostDisruption && severedEdges.some(
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
            opacity: 0.65,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: '#ef4444',
            width: 16,
            height: 16,
          },
          label: `🛑 BLOCKED ₹${(e.amount || 0).toLocaleString()}`,
          labelStyle: { fill: '#fca5a5', fontWeight: 700, fontSize: 10 },
          labelBgStyle: { fill: '#450a0a', fillOpacity: 0.9, stroke: '#ef4444', strokeWidth: 1, rx: 4, ry: 4 },
        };
      }

      return {
        id: e.id,
        source: e.source,
        target: e.target,
        animated: true,
        style: {
          stroke: e.is_cross_bank ? '#06b6d4' : '#10b981',
          strokeWidth: 2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: e.is_cross_bank ? '#06b6d4' : '#10b981',
          width: 16,
          height: 16,
        },
        label: `₹${(e.amount || 0).toLocaleString()}`,
        labelStyle: { fill: '#94a3b8', fontWeight: 600, fontSize: 10 },
        labelBgStyle: { fill: '#0f172a', fillOpacity: 0.85, stroke: '#334155', strokeWidth: 1, rx: 4, ry: 4 },
      };
    });
  }, [edgesData, severedEdges, isPostDisruption]);

  return (
    <div className="relative w-full h-[540px] rounded-2xl overflow-hidden glass-panel border border-slate-800 shadow-2xl">
      {/* Top Controls Toolbar */}
      <div className="absolute top-4 left-5 right-5 z-10 flex flex-wrap items-center justify-between gap-3 pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto">
          <div className="px-3 py-1.5 rounded-xl bg-slate-900/90 backdrop-blur-md border border-slate-800 text-xs font-semibold text-slate-200 flex items-center gap-2 shadow-lg">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <span>Interactive Topology Flow (Left → Right Timeline)</span>
          </div>

          <div className="px-2.5 py-1 rounded-lg bg-slate-800/80 text-[11px] text-slate-400 border border-slate-700/60 hidden sm:block">
            Click node to inspect & select choke point
          </div>
        </div>

        {/* View Mode Toggle Button */}
        <div className="flex items-center gap-2 pointer-events-auto">
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
                <span>🛡️ View: Post-Disruption (Severed)</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-white" />
                <span>⚡ View: Pre-Disruption (Full Ring)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* React Flow Canvas */}
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        nodeTypes={nodeTypes}
        onNodeClick={(_, node) => onSelectNode(node.id)}
        fitView
        fitViewOptions={{ padding: 0.25 }}
        minZoom={0.3}
        maxZoom={1.5}
        className="bg-[#080d1a]"
      >
        <Background color="#1e293b" gap={24} size={1} />
        <Controls className="!bg-slate-900 !border-slate-800 !fill-slate-300 !rounded-xl !overflow-hidden !shadow-xl" />
        <MiniMap
          nodeColor={(n) => (n.data?.isTarget ? '#f43f5e' : '#06b6d4')}
          maskColor="rgba(7, 11, 20, 0.75)"
          className="!bg-slate-950 !border !border-slate-800 !rounded-xl !overflow-hidden"
        />
      </ReactFlow>

      {/* Bottom Legend */}
      <div className="absolute bottom-4 left-5 z-10 hidden md:flex items-center gap-3 px-3.5 py-1.5 rounded-xl bg-slate-900/90 backdrop-blur-md border border-slate-800 text-[11px] text-slate-300 shadow-lg pointer-events-none">
        <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Legend:</span>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
          <span>Bank A</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
          <span>Bank B</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-purple-400" />
          <span>Bank C</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
          <span>Bank D</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
          <span className="text-rose-300 font-bold">Choke Point Bottleneck</span>
        </div>
      </div>
    </div>
  );
}
