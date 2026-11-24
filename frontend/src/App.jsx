import React, { useState, useEffect } from 'react';
import { apiFetch } from './api';
import Sidebar from './components/Sidebar';
import KPIMetricsBar from './components/KPIMetricsBar';
import MonitoringView from './views/MonitoringView';
import RealtimeScorerView from './views/RealtimeScorerView';
import NetworkExplorerView from './views/NetworkExplorerView';
import XAIView from './views/XAIView';
import AlertsView from './views/AlertsView';
import CaseManagerView from './views/CaseManagerView';
import InvestigationAssistantView from './views/InvestigationAssistantView';
import AdvancedAnalyticsView from './views/AdvancedAnalyticsView';
import CyberGlobe3D from './components/CyberGlobe3D';
import MuleRingCanvas from './components/MuleRingCanvas';
import InterceptionSimulator from './components/InterceptionSimulator';
import DigitalTwinSimulator from './components/DigitalTwinSimulator';
import GNNIntelligenceView from './views/GNNIntelligenceView';
import LandingPageView from './views/LandingPageView';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [summary, setSummary] = useState({
    total_transactions: 27722,
    high_risk_count: 165,
  });

  // Topology State for Interception Tab
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [bottlenecks, setBottlenecks] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [selectedTargetNode, setSelectedTargetNode] = useState(null);
  const [simulationResult, setSimulationResult] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isPostDisruption, setIsPostDisruption] = useState(false);

  // Fetch initial data
  useEffect(() => {
    const fetchInit = async () => {
      try {
        const topRes = await apiFetch('/api/v1/interception/topology');
        if (topRes.ok) {
          const data = await topRes.json();
          setNodes(data.nodes || []);
          setEdges(data.edges || []);
          setBottlenecks(data.bottlenecks || []);
          if (data.bottlenecks?.length > 0) {
            setSelectedTargetNode(data.bottlenecks[0].node_id);
          }
        }

        const sumRes = await apiFetch('/api/v1/dashboard/summary?mode=federated');
        if (sumRes.ok) {
          const sumData = await sumRes.json();
          setSummary(sumData);
        }
      } catch (err) {
        console.warn('Backend connection fallback:', err);
      }
    };

    fetchInit();
  }, []);

  const handleRunSimulation = async ({ strategyKey, delayMinutes }) => {
    setIsSimulating(true);
    try {
      const target = selectedTargetNode || (bottlenecks[0]?.node_id) || 'BANK_A:BANK_MULE_00001';
      const res = await apiFetch('/api/v1/interception/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ring_id: 'RING_001',
          target_node: target,
          strategy_key: strategyKey,
          delay_minutes: delayMinutes,
          officer_id: 'REGULATORY-NODAL-804',
        }),
      });

      if (res.ok) {
        const result = await res.json();
        setSimulationResult(result);
        setIsPostDisruption(true);
      }
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 cyber-grid flex">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto h-screen">
        {/* Top Header Status Bar */}
        <header className="glass-panel border-b border-slate-800 px-6 py-3.5 flex items-center justify-between sticky top-0 z-30 backdrop-blur-xl">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-xs uppercase font-bold tracking-wider text-slate-300">
              Live Central Oversight & Financial Defense Node
            </span>
          </div>

          <div className="flex items-center gap-3 text-xs font-mono">
            <span className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
              Mode: Federated ({summary.total_transactions?.toLocaleString() || '27,743'} Ledger Txns)
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold">
              Latency: 11.4 ms
            </span>
          </div>
        </header>

        {/* Content Body */}
        <main className="p-6 flex-1 flex flex-col gap-6 max-w-7xl w-full mx-auto">
          {/* Always Visible Top Metrics */}
          <KPIMetricsBar summary={summary} />

          {/* Active Module Workstation */}
          <div>
            {activeTab === 'landing' && <LandingPageView onLaunchDashboard={() => setActiveTab('dashboard')} />}
            {activeTab === 'dashboard' && <MonitoringView />}
            {activeTab === 'network' && (
              <div className="flex flex-col gap-6">
                <NetworkExplorerView />
                {/* Embedded Topology & Interception Simulator */}
                <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col gap-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                      Multi-Bank Synthetic Network Design & Interception Canvas
                    </span>
                    <span className="text-[10px] text-cyan-400 font-mono">React Flow DAG</span>
                  </div>
                  <MuleRingCanvas
                    nodesData={nodes}
                    edgesData={edges}
                    selectedNodeId={selectedNodeId}
                    onSelectNode={(id) => {
                      setSelectedNodeId(id);
                      setSelectedTargetNode(id);
                    }}
                    targetNodeId={selectedTargetNode}
                    neutralizedNodes={simulationResult?.downstream_nodes_list || []}
                    severedEdges={simulationResult?.severed_edges || []}
                    isPostDisruption={isPostDisruption}
                    onToggleDisruption={setIsPostDisruption}
                  />
                  <InterceptionSimulator
                    nodes={nodes}
                    bottlenecks={bottlenecks}
                    selectedTargetNode={selectedTargetNode}
                    onSelectTargetNode={setSelectedTargetNode}
                    onRunSimulation={handleRunSimulation}
                    simulationResult={simulationResult}
                    isLoading={isSimulating}
                  />
                </div>
              </div>
            )}
            {activeTab === 'xai' && <XAIView />}
            {activeTab === 'assistant' && <InvestigationAssistantView />}
            {activeTab === 'cases' && <CaseManagerView />}
            {activeTab === 'analytics' && <AdvancedAnalyticsView />}
            {activeTab === 'gnn' && <GNNIntelligenceView />}
            {activeTab === 'realtime' && <RealtimeScorerView />}
            {activeTab === 'alerts' && <AlertsView />}
            {activeTab === 'globe3d' && (
              <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
                  3D Multi-Bank Cyber Clearing Fabric
                </h3>
                <CyberGlobe3D />
              </div>
            )}
            {activeTab === 'digital_twin' && <DigitalTwinSimulator />}
            {activeTab === 'interception' && (
              <div className="flex flex-col gap-6">
                <MuleRingCanvas
                  nodesData={nodes}
                  edgesData={edges}
                  selectedNodeId={selectedNodeId}
                  onSelectNode={(id) => {
                    setSelectedNodeId(id);
                    setSelectedTargetNode(id);
                  }}
                  targetNodeId={selectedTargetNode}
                  neutralizedNodes={simulationResult?.downstream_nodes_list || []}
                  severedEdges={simulationResult?.severed_edges || []}
                  isPostDisruption={isPostDisruption}
                  onToggleDisruption={setIsPostDisruption}
                />
                <InterceptionSimulator
                  nodes={nodes}
                  bottlenecks={bottlenecks}
                  selectedTargetNode={selectedTargetNode}
                  onSelectTargetNode={setSelectedTargetNode}
                  onRunSimulation={handleRunSimulation}
                  simulationResult={simulationResult}
                  isLoading={isSimulating}
                />
              </div>
            )}
          </div>
        </main>

        {/* Bottom Status Bar */}
        <footer className="border-t border-slate-800/80 py-3.5 px-6 text-center text-xs text-slate-500 glass-panel mt-auto">
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
            <span>RINGTRACE AI — Multi-Bank Proactive Mule Ring Defense Architecture</span>
            <span className="font-mono text-[11px] text-slate-400">
              DPDP Act 2023 Compliant • SHA-256 Cryptographic Tamper-Proof Trail
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
}
