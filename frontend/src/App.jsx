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

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [summary, setSummary] = useState({
    total_transactions: 46380,
    high_risk_count: 128,
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

  const getPageMeta = () => {
    switch (activeTab) {
      case 'dashboard':
        return {
          title: 'Default',
          subtitle: 'This is a dashboard page example built using this template.',
        };
      case 'network':
        return {
          title: 'Network Explorer',
          subtitle: 'Interconnected multi-bank transaction graph across Bank A, Bank B, Bank C, and Bank D.',
        };
      case 'interception':
        return {
          title: 'Interception Simulator',
          subtitle: 'Proactive bottleneck choke-point disruption and capital preservation engine.',
        };
      case 'xai':
        return {
          title: 'Explainable AI (XAI)',
          subtitle: 'Transparent GNN feature attribution, SHAP graphs, and relational hop explanations.',
        };
      case 'assistant':
        return {
          title: 'AI Investigation Assistant',
          subtitle: 'Regulatory nodal officer copilot for automated Suspicious Activity Reports (SAR).',
        };
      case 'cases':
        return {
          title: 'Case Management',
          subtitle: 'Multi-bank regulatory case dossiers, freezing orders, and cryptographic audit trails.',
        };
      case 'analytics':
        return {
          title: 'Advanced Analytics',
          subtitle: 'Institutional risk velocity distribution and cross-bank liquidity metrics.',
        };
      case 'gnn':
        return {
          title: 'GNN Intelligence Center',
          subtitle: 'Graph Neural Network architecture, message passing layers, and confusion matrices.',
        };
      case 'digital_twin':
        return {
          title: 'Digital Twin Simulator',
          subtitle: 'High-throughput synthetic banking network traffic injector and stress-testing sandbox.',
        };
      case 'globe3d':
        return {
          title: '3D Cyber Clearing Fabric',
          subtitle: 'Real-time spatial visualization of inter-bank settlements and flagged mule flows.',
        };
      case 'alerts':
        return {
          title: 'Alerts & Rules',
          subtitle: 'Real-time rule engine triggers and automated threshold alerts.',
        };
      default:
        return {
          title: 'Default',
          subtitle: 'This is a dashboard page example built using this template.',
        };
    }
  };

  const pageMeta = getPageMeta();

  return (
    <div className="min-h-screen bg-[#f4f6f9] text-slate-800 flex font-['Plus_Jakarta_Sans',sans-serif]">
      {/* Left Sidebar Navigation (Matching Template) */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto h-screen bg-[#f4f6f9]">
        {/* Template Header Bar */}
        <header className="px-8 pt-7 pb-5 flex flex-wrap items-center justify-between gap-4 bg-[#f4f6f9]">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
              {pageMeta.title}
            </h1>
            <p className="text-xs text-slate-600 font-semibold mt-1">
              {pageMeta.subtitle}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 text-xs font-mono">
              <span className="px-3.5 py-1 rounded-full bg-white border border-slate-300 text-slate-800 shadow-xs font-bold">
                Mode: Federated (46,380 Txns)
              </span>
              <span className="px-3.5 py-1 rounded-full bg-emerald-50 border border-emerald-300 text-emerald-800 font-extrabold shadow-xs">
                Latency: 11.4 ms
              </span>
            </div>
          </div>
        </header>

        {/* Content Body */}
        <main className="px-8 pb-10 flex-1 flex flex-col gap-6 max-w-[1400px] w-full">
          {/* Always Visible Row 1: KPI Metrics Bar (Exact Template Cards) */}
          <KPIMetricsBar summary={summary} />

          {/* Active Module Workstation */}
          <div>
            {activeTab === 'dashboard' && <MonitoringView />}
            {activeTab === 'network' && (
              <div className="flex flex-col gap-6">
                <NetworkExplorerView />
                {/* Embedded Topology & Interception Simulator */}
                <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col gap-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      Multi-Bank Synthetic Network Design & Interception Canvas
                    </span>
                    <span className="text-[10px] text-blue-600 font-mono font-bold bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-100">
                      React Flow DAG
                    </span>
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
            {activeTab === 'globe3d' && <CyberGlobe3D />}
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
        <footer className="border-t border-slate-200/80 py-4 px-8 text-center text-xs text-slate-500 bg-white mt-auto">
          <div className="max-w-[1400px] mx-auto flex flex-wrap items-center justify-between gap-2">
            <span className="font-medium text-slate-600">RINGTRACE AI — Multi-Bank Proactive Mule Ring Defense Architecture</span>
            <span className="font-mono text-[11px] text-slate-400">
              DPDP Act 2023 Compliant • SHA-256 Cryptographic Tamper-Proof Audit
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
}
