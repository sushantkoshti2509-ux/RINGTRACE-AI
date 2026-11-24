import React, { useState, useEffect, useRef } from 'react';
import { apiFetch } from '../api';
import {
  Play,
  Pause,
  RotateCcw,
  SkipForward,
  SkipBack,
  Sliders,
  Cpu,
  ArrowRight,
  ShieldAlert,
  Layers,
  Clock,
  Zap,
  TrendingUp,
  AlertTriangle,
  RefreshCw,
  GitBranch,
  Split,
  Repeat,
  CheckCircle2,
} from 'lucide-react';

export default function DigitalTwinSimulator() {
  const [activeTab, setActiveTab] = useState('replay'); // 'replay' | 'scenario'
  const [replayData, setReplayData] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playSpeed, setPlaySpeed] = useState(1); // 1x, 2x, 4x
  const [isLoading, setIsLoading] = useState(false);

  // Scenario Simulator State
  const [selectedScenario, setSelectedScenario] = useState('ADD_INTERMEDIARY');
  const [scenarioResult, setScenarioResult] = useState(null);
  const [isSimulatingScenario, setIsSimulatingScenario] = useState(false);

  const timerRef = useRef(null);

  // Fetch initial replay data
  const fetchReplay = async () => {
    setIsLoading(true);
    try {
      const res = await apiFetch('/api/v1/platform/digital-twin/replay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ring_id: 'RING_001' }),
      });
      if (res.ok) {
        const data = await res.json();
        setReplayData(data);
        setCurrentStep(0);
      }
    } catch (err) {
      console.error('Failed to load replay sequence:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const runScenarioSimulation = async (scenarioType) => {
    setIsSimulatingScenario(true);
    try {
      const res = await apiFetch('/api/v1/platform/digital-twin/simulate-scenario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_type: scenarioType || selectedScenario,
          baseline_ring_id: 'RING_001',
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setScenarioResult(data);
      }
    } catch (err) {
      console.error('Failed to run scenario simulation:', err);
    } finally {
      setIsSimulatingScenario(false);
    }
  };

  useEffect(() => {
    fetchReplay();
    runScenarioSimulation('ADD_INTERMEDIARY');
  }, []);

  // Playback timer loop
  useEffect(() => {
    if (isPlaying && replayData?.frames?.length > 0) {
      timerRef.current = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= replayData.frames.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1500 / playSpeed);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, replayData, playSpeed]);

  const activeFrame = replayData?.frames?.[currentStep] || null;

  return (
    <div className="flex flex-col gap-6">
      {/* Top Header Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 shrink-0">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-extrabold text-slate-900 tracking-tight">
                Fraud Network Digital Twin & Scenario Simulator
              </h2>
              <span className="bg-blue-50 text-blue-700 border border-blue-200 font-extrabold text-[10px] px-2 py-0.5 rounded-full font-mono">
                GRAPH SIMULATOR
              </span>
            </div>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Chronological transaction replay and predictive what-if scenario modeling
            </p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-2 bg-slate-100 p-1.5 rounded-xl border border-slate-200">
          <button
            onClick={() => setActiveTab('replay')}
            className={`px-4 py-2 rounded-lg text-xs font-extrabold transition-all flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'replay'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-700 hover:text-slate-900 hover:bg-white'
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>Chronological Replay</span>
          </button>
          <button
            onClick={() => setActiveTab('scenario')}
            className={`px-4 py-2 rounded-lg text-xs font-extrabold transition-all flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'scenario'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-700 hover:text-slate-900 hover:bg-white'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>What-If Scenario Lab</span>
          </button>
        </div>
      </div>

      {/* Mode 1: Chronological Replay */}
      {activeTab === 'replay' && (
        <div className="flex flex-col gap-6">
          {/* Timeline Scrubber & Playback Controls */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col gap-4">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2.5">
                <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider">
                  Replay Progress: Step {currentStep + 1} of {replayData?.total_steps || 1}
                </span>
                <span className="text-xs font-mono font-extrabold px-2.5 py-0.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200">
                  {activeFrame ? activeFrame.timestamp : 'Initializing...'}
                </span>
              </div>

              {/* Transport Controls */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setIsPlaying(false);
                    setCurrentStep(0);
                  }}
                  className="p-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 shadow-xs transition-colors cursor-pointer"
                  title="Reset to Start"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setCurrentStep((prev) => Math.max(0, prev - 1))}
                  disabled={currentStep === 0}
                  className="p-2 rounded-xl bg-white hover:bg-slate-50 disabled:opacity-40 text-slate-700 border border-slate-300 shadow-xs transition-colors cursor-pointer"
                  title="Step Backward"
                >
                  <SkipBack className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs flex items-center gap-1.5 shadow-md shadow-blue-500/20 transition-all cursor-pointer"
                >
                  {isPlaying ? (
                    <>
                      <Pause className="w-3.5 h-3.5 fill-current" /> Pause Replay
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5 fill-current" /> Play Replay
                    </>
                  )}
                </button>
                <button
                  onClick={() =>
                    setCurrentStep((prev) =>
                      Math.min((replayData?.frames?.length || 1) - 1, prev + 1)
                    )
                  }
                  disabled={currentStep >= (replayData?.frames?.length || 1) - 1}
                  className="p-2 rounded-xl bg-white hover:bg-slate-50 disabled:opacity-40 text-slate-700 border border-slate-300 shadow-xs transition-colors cursor-pointer"
                  title="Step Forward"
                >
                  <SkipForward className="w-3.5 h-3.5" />
                </button>

                {/* Speed toggle */}
                <div className="flex items-center gap-1 ml-2 bg-slate-100 border border-slate-200 rounded-xl p-1 text-[11px] font-mono">
                  {[1, 2, 4].map((s) => (
                    <button
                      key={s}
                      onClick={() => setPlaySpeed(s)}
                      className={`px-2.5 py-0.5 rounded-lg font-extrabold transition-all cursor-pointer ${
                        playSpeed === s ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      {s}x
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Scrubber slider */}
            <div className="flex flex-col gap-1.5">
              <input
                type="range"
                min="0"
                max={(replayData?.frames?.length || 1) - 1}
                value={currentStep}
                onChange={(e) => setCurrentStep(Number(e.target.value))}
                className="w-full accent-blue-600 bg-slate-200 h-2.5 rounded-lg cursor-pointer"
              />
              <div className="flex justify-between text-[11px] text-slate-500 font-mono font-semibold">
                <span>Start: First Transfer</span>
                <span>Current: Step {currentStep + 1}</span>
                <span>End: Final Network Hop</span>
              </div>
            </div>
          </div>

          {/* Active Frame Telemetry & Dynamic Inter-Bank Flow */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Visual Fund Hop Simulation */}
            <div className="lg:col-span-8 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between">
              <div>
                <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider block mb-4">
                  Dynamic Inter-Bank Hop Visualization
                </span>

                {activeFrame ? (
                  <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col md:flex-row items-center justify-between gap-6">
                    {/* Sender Bank Box */}
                    <div className="flex flex-col items-center gap-1.5 p-4 rounded-xl bg-blue-50/80 border-2 border-blue-200 w-full md:w-44 text-center">
                      <span className="text-[10px] text-blue-800 uppercase font-mono font-extrabold">
                        Source Institution
                      </span>
                      <span className="text-base font-extrabold text-blue-950 font-mono">
                        {activeFrame.sender_bank}
                      </span>
                      <span className="text-xs font-mono font-bold text-blue-700">
                        {activeFrame.masked_sender}
                      </span>
                    </div>

                    {/* Animated Fund Transfer Vector */}
                    <div className="flex flex-col items-center gap-1.5 flex-1 w-full">
                      <span className="text-sm font-extrabold text-emerald-700 font-mono">
                        ₹{activeFrame.amount.toLocaleString('en-IN')}
                      </span>
                      <div className="w-full flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-gradient-to-r from-blue-500 via-emerald-500 to-amber-500 rounded-full relative">
                          <div className="w-3 h-3 rounded-full bg-blue-600 border-2 border-white shadow-xs absolute top-1/2 -translate-y-1/2 animate-ping" />
                        </div>
                        <ArrowRight className="w-5 h-5 text-emerald-600 shrink-0" />
                      </div>
                      <span className="text-[11px] text-slate-500 font-mono font-bold">
                        {activeFrame.tx_type} • Turnaround &lt; 90s
                      </span>
                    </div>

                    {/* Receiver Bank Box */}
                    <div className="flex flex-col items-center gap-1.5 p-4 rounded-xl bg-emerald-50/80 border-2 border-emerald-200 w-full md:w-44 text-center">
                      <span className="text-[10px] text-emerald-800 uppercase font-mono font-extrabold">
                        Destination Institution
                      </span>
                      <span className="text-base font-extrabold text-emerald-950 font-mono">
                        {activeFrame.receiver_bank}
                      </span>
                      <span className="text-xs font-mono font-bold text-emerald-700">
                        {activeFrame.masked_receiver}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-xs text-slate-500 font-semibold">
                    Loading chronological replay frames...
                  </div>
                )}
              </div>

              {/* Cumulative Metrics Bar */}
              <div className="grid grid-cols-3 gap-3.5 mt-6 pt-4 border-t border-slate-100">
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="text-[10px] text-slate-600 uppercase font-extrabold block">Cumulative Volume</span>
                  <span className="text-base font-extrabold text-emerald-700 font-mono mt-0.5 block">
                    ₹{activeFrame ? activeFrame.cumulative_volume.toLocaleString('en-IN') : '0'}
                  </span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="text-[10px] text-slate-600 uppercase font-extrabold block">Involved Accounts</span>
                  <span className="text-base font-extrabold text-slate-900 font-mono mt-0.5 block">
                    {activeFrame ? activeFrame.total_active_accounts : 0} Accounts
                  </span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="text-[10px] text-slate-600 uppercase font-extrabold block">Cross-Bank Edges</span>
                  <span className="text-base font-extrabold text-blue-700 font-mono mt-0.5 block">
                    {activeFrame ? activeFrame.total_active_connections : 0} Hops
                  </span>
                </div>
              </div>
            </div>

            {/* Right: Step Transaction Inspector */}
            <div className="lg:col-span-4 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between">
              <div>
                <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider block border-b border-slate-100 pb-3 mb-3">
                  Step Transaction Inspector
                </span>

                {activeFrame ? (
                  <div className="space-y-3 text-xs">
                    <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                      <span className="text-slate-600 font-bold">Transaction ID:</span>
                      <span className="font-mono text-slate-900 font-extrabold text-xs">{activeFrame.tx_id}</span>
                    </div>
                    <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                      <span className="text-slate-600 font-bold">Execution Time:</span>
                      <span className="font-mono text-slate-800 font-semibold">{activeFrame.timestamp}</span>
                    </div>
                    <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                      <span className="text-slate-600 font-bold">Transfer Amount:</span>
                      <span className="font-mono text-emerald-700 font-extrabold text-sm">
                        ₹{activeFrame.amount.toLocaleString('en-IN')}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                      <span className="text-slate-600 font-bold">Corridor:</span>
                      <span className="font-mono text-blue-700 font-extrabold text-xs">
                        {activeFrame.sender_bank} ➔ {activeFrame.receiver_bank}
                      </span>
                    </div>
                    <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 mt-3">
                      <span className="text-[11px] text-blue-900 font-extrabold uppercase block mb-1">
                        Turnaround Dynamics:
                      </span>
                      <span className="text-slate-700 text-xs leading-relaxed font-medium">
                        Funds were forwarded within seconds of settlement. The zero-balance retention
                        signature indicates intermediate transit rather than genuine retail customer activity.
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-xs text-slate-500 font-semibold">
                    No active transaction step selected.
                  </div>
                )}
              </div>

              <div className="mt-4 p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-800 font-medium flex items-center gap-2">
                <Zap className="w-4 h-4 text-blue-600 shrink-0" />
                <span>Zero real customer data. Synthetic telemetry generated under DPDP Act 2023.</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mode 2: What-If Scenario Lab */}
      {activeTab === 'scenario' && (
        <div className="flex flex-col gap-6">
          {/* Scenario Selection Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3.5">
            {[
              {
                id: 'ADD_INTERMEDIARY',
                title: 'Add Intermediary Hop',
                desc: 'Inject new mule account to test layering depth',
                icon: GitBranch,
              },
              {
                id: 'SPLIT_SMURFING',
                title: 'Split Into Smurfing',
                desc: 'Split transfer into 5 sub-threshold tranches',
                icon: Split,
              },
              {
                id: 'CREATE_CIRCULAR_LOOP',
                title: 'Create Circular Loop',
                desc: 'Route funds back to initial origin node',
                icon: Repeat,
              },
              {
                id: 'BURST_VELOCITY',
                title: 'Accelerate Velocity',
                desc: 'Compress hop delay from hours to 18 seconds',
                icon: Zap,
              },
            ].map((scen) => {
              const Icon = scen.icon;
              const isSelected = selectedScenario === scen.id;
              return (
                <div
                  key={scen.id}
                  onClick={() => {
                    setSelectedScenario(scen.id);
                    runScenarioSimulation(scen.id);
                  }}
                  className={`p-4 rounded-xl border-2 transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-blue-50/80 border-blue-600 shadow-md shadow-blue-500/10'
                      : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50 shadow-xs'
                  }`}
                >
                  <div className="flex items-center gap-2.5 mb-2">
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        isSelected ? 'bg-blue-600 text-white font-bold' : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="font-extrabold text-xs text-slate-900">{scen.title}</span>
                  </div>
                  <p className="text-xs text-slate-600 font-medium leading-relaxed">{scen.desc}</p>
                </div>
              );
            })}
          </div>

          {/* Simulation Results & Baseline vs Scenario Comparison */}
          {scenarioResult && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Baseline vs Simulated Comparison */}
              <div className="lg:col-span-7 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
                    <div>
                      <h3 className="text-base font-extrabold text-slate-900">{scenarioResult.title}</h3>
                      <p className="text-xs text-slate-500 font-medium mt-0.5">{scenarioResult.description}</p>
                    </div>
                    <span className="px-2.5 py-1 rounded-md text-[10px] font-mono font-extrabold bg-amber-50 text-amber-800 border border-amber-200">
                      SIMULATED SCENARIO
                    </span>
                  </div>

                  {/* Comparative Metrics Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs font-sans">
                      <thead>
                        <tr className="border-b border-slate-300 bg-slate-100 text-slate-700 uppercase text-xs font-extrabold tracking-wider">
                          <th className="py-3 px-3">Metric</th>
                          <th className="py-3 px-3 text-blue-700">Baseline Actual</th>
                          <th className="py-3 px-3 text-amber-700">Simulated Digital Twin</th>
                          <th className="py-3 px-3">Topological Shift</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 font-mono">
                        <tr className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-3 px-3 text-slate-900 font-sans font-bold">Network Hops</td>
                          <td className="py-3 px-3 text-slate-900 font-extrabold">
                            {scenarioResult.baseline_comparison.baseline.hops} Hops
                          </td>
                          <td className="py-3 px-3 text-amber-700 font-extrabold">
                            {scenarioResult.baseline_comparison.simulated.hops} Hops
                          </td>
                          <td className="py-3 px-3 text-slate-600 font-semibold font-sans">
                            +{scenarioResult.baseline_comparison.simulated.hops -
                              scenarioResult.baseline_comparison.baseline.hops}{' '}
                            Synthetic Nodes
                          </td>
                        </tr>
                        <tr className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-3 px-3 text-slate-900 font-sans font-bold">Detection Latency</td>
                          <td className="py-3 px-3 text-slate-900 font-extrabold">
                            {scenarioResult.baseline_comparison.baseline.turnaround_latency_sec}s
                          </td>
                          <td className="py-3 px-3 text-amber-700 font-extrabold">
                            {scenarioResult.baseline_comparison.simulated.turnaround_latency_sec}s
                          </td>
                          <td className="py-3 px-3 text-emerald-700 font-extrabold font-sans">Rapid Anomaly Alert</td>
                        </tr>
                        <tr className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-3 px-3 text-slate-900 font-sans font-bold">Ring Risk Score</td>
                          <td className="py-3 px-3 text-slate-900 font-extrabold">
                            {scenarioResult.baseline_comparison.baseline.risk_score}%
                          </td>
                          <td className="py-3 px-3 text-rose-700 font-extrabold">
                            {scenarioResult.baseline_comparison.simulated.risk_score}%
                          </td>
                          <td className="py-3 px-3 text-rose-700 font-extrabold">
                            +{scenarioResult.baseline_comparison.delta.risk_increase_points} pts
                          </td>
                        </tr>
                        <tr className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-3 px-3 text-slate-900 font-sans font-bold">Evasion Likelihood</td>
                          <td className="py-3 px-3 text-slate-600 font-semibold font-sans">Baseline</td>
                          <td className="py-3 px-3 text-emerald-800 font-sans font-extrabold" colSpan="2">
                            {scenarioResult.baseline_comparison.delta.evasion_analysis}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="mt-6 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                  <span className="font-extrabold text-slate-900 block mb-1">
                    AI Regulatory Defense Takeaway:
                  </span>
                  <p className="text-slate-700 font-medium leading-relaxed">
                    {scenarioResult.recommendation_notes}
                  </p>
                </div>
              </div>

              {/* Synthetic Subgraph Preview */}
              <div className="lg:col-span-5 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3">
                    <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider">
                      Synthetic Topology Nodes
                    </span>
                    <span className="text-xs text-amber-800 font-mono font-extrabold bg-amber-50 border border-amber-200 px-2 py-0.5 rounded">
                      {scenarioResult.synthetic_nodes?.length || 0} Entities
                    </span>
                  </div>

                  <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                    {scenarioResult.synthetic_nodes?.map((node, i) => (
                      <div
                        key={i}
                        className={`p-3 rounded-xl border text-xs flex items-center justify-between ${
                          node.is_synthetic
                            ? 'bg-amber-50/80 border-amber-200 text-amber-950 font-bold'
                            : 'bg-slate-50 border-slate-200 text-slate-900 font-medium'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span
                            className={`w-2.5 h-2.5 rounded-full ${
                              node.is_synthetic ? 'bg-amber-500 animate-pulse' : 'bg-blue-600'
                            }`}
                          />
                          <span className="font-mono font-extrabold">{node.id}</span>
                        </div>
                        <span
                          className={`text-[10px] font-mono font-extrabold px-2 py-0.5 rounded ${
                            node.is_synthetic
                              ? 'bg-amber-100 text-amber-900 border border-amber-300'
                              : 'bg-slate-200 text-slate-800'
                          }`}
                        >
                          {node.role}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Simulation Watermark Banner */}
                <div className="mt-4 p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs font-medium text-amber-900 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                  <span>
                    DIGITAL TWIN ISOLATION: Simulated scenario is evaluated strictly in sandbox memory and
                    never committed to production ledger database.
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
