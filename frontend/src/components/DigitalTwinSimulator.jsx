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
      <div className="glass-panel rounded-2xl p-5 border border-cyan-500/20 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <span>Fraud Network Digital Twin & Scenario Simulator</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Chronological transaction replay and predictive what-if scenario modeling
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-2 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('replay')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === 'replay'
                ? 'bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>Chronological Replay</span>
          </button>
          <button
            onClick={() => setActiveTab('scenario')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === 'scenario'
                ? 'bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200'
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
          <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col gap-4">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  Replay Progress: Step {currentStep + 1} of {replayData?.total_steps || 1}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
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
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
                  title="Reset to Start"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setCurrentStep((prev) => Math.max(0, prev - 1))}
                  disabled={currentStep === 0}
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 border border-slate-700"
                  title="Step Backward"
                >
                  <SkipBack className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-cyan-600/20"
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
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 border border-slate-700"
                  title="Step Forward"
                >
                  <SkipForward className="w-3.5 h-3.5" />
                </button>

                {/* Speed toggle */}
                <div className="flex items-center gap-1 ml-2 bg-slate-900 border border-slate-700 rounded-lg p-0.5 text-[10px] font-mono">
                  {[1, 2, 4].map((s) => (
                    <button
                      key={s}
                      onClick={() => setPlaySpeed(s)}
                      className={`px-2 py-0.5 rounded ${
                        playSpeed === s ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400'
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
                className="w-full accent-cyan-400 bg-slate-800 h-2 rounded-lg cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                <span>Start: First Transfer</span>
                <span>Current: Step {currentStep + 1}</span>
                <span>End: Network Final Hop</span>
              </div>
            </div>
          </div>

          {/* Active Frame Telemetry & Dynamic Inter-Bank Flow */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Visual Fund Hop Simulation */}
            <div className="lg:col-span-8 glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl flex flex-col justify-between">
              <div>
                <span className="text-xs font-bold text-white uppercase tracking-wider block mb-4">
                  Dynamic Inter-Bank Hop Visualization
                </span>

                {activeFrame ? (
                  <div className="p-6 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-6">
                    {/* Sender Bank Box */}
                    <div className="flex flex-col items-center gap-2 p-4 rounded-xl bg-slate-900 border border-cyan-500/30 w-full md:w-44 text-center">
                      <span className="text-[10px] text-cyan-400 uppercase font-mono font-bold">
                        Source Institution
                      </span>
                      <span className="text-base font-bold text-white font-mono">
                        {activeFrame.sender_bank}
                      </span>
                      <span className="text-xs font-mono text-slate-300">
                        {activeFrame.masked_sender}
                      </span>
                    </div>

                    {/* Animated Fund Transfer Vector */}
                    <div className="flex flex-col items-center gap-1.5 flex-1 w-full">
                      <span className="text-sm font-extrabold text-emerald-400 font-mono">
                        ₹{activeFrame.amount.toLocaleString()}
                      </span>
                      <div className="w-full flex items-center gap-2">
                        <div className="flex-1 h-0.5 bg-gradient-to-r from-cyan-500 via-emerald-400 to-amber-500 relative">
                          <div className="w-2.5 h-2.5 rounded-full bg-white absolute top-1/2 -translate-y-1/2 animate-ping" />
                        </div>
                        <ArrowRight className="w-5 h-5 text-emerald-400 shrink-0" />
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {activeFrame.tx_type} • Turnaround &lt; 90s
                      </span>
                    </div>

                    {/* Receiver Bank Box */}
                    <div className="flex flex-col items-center gap-2 p-4 rounded-xl bg-slate-900 border border-emerald-500/30 w-full md:w-44 text-center">
                      <span className="text-[10px] text-emerald-400 uppercase font-mono font-bold">
                        Destination Institution
                      </span>
                      <span className="text-base font-bold text-white font-mono">
                        {activeFrame.receiver_bank}
                      </span>
                      <span className="text-xs font-mono text-slate-300">
                        {activeFrame.masked_receiver}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-xs text-slate-400">
                    Loading chronological replay frames...
                  </div>
                )}
              </div>

              {/* Cumulative Metrics Bar */}
              <div className="grid grid-cols-3 gap-3 mt-6 pt-4 border-t border-slate-800">
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase block">Cumulative Volume</span>
                  <span className="text-base font-bold text-cyan-300 font-mono mt-0.5 block">
                    ₹{activeFrame ? activeFrame.cumulative_volume.toLocaleString() : '0'}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase block">Involved Accounts</span>
                  <span className="text-base font-bold text-white font-mono mt-0.5 block">
                    {activeFrame ? activeFrame.total_active_accounts : 0} Accounts
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase block">Cross-Bank Edges</span>
                  <span className="text-base font-bold text-emerald-400 font-mono mt-0.5 block">
                    {activeFrame ? activeFrame.total_active_connections : 0} Hops
                  </span>
                </div>
              </div>
            </div>

            {/* Right: Step Transaction Inspector */}
            <div className="lg:col-span-4 glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col justify-between">
              <div>
                <span className="text-xs font-bold text-white uppercase tracking-wider block border-b border-slate-800 pb-3 mb-3">
                  Step Transaction Inspector
                </span>

                {activeFrame ? (
                  <div className="space-y-3 text-xs font-sans">
                    <div className="flex justify-between items-center py-1.5 border-b border-slate-850">
                      <span className="text-slate-400">Transaction ID:</span>
                      <span className="font-mono text-cyan-300 font-bold">{activeFrame.tx_id}</span>
                    </div>
                    <div className="flex justify-between items-center py-1.5 border-b border-slate-850">
                      <span className="text-slate-400">Execution Time:</span>
                      <span className="font-mono text-slate-200">{activeFrame.timestamp}</span>
                    </div>
                    <div className="flex justify-between items-center py-1.5 border-b border-slate-850">
                      <span className="text-slate-400">Transfer Amount:</span>
                      <span className="font-mono text-emerald-400 font-bold">
                        ₹{activeFrame.amount.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-1.5 border-b border-slate-850">
                      <span className="text-slate-400">Corridor:</span>
                      <span className="font-mono text-slate-200">
                        {activeFrame.sender_bank} ➔ {activeFrame.receiver_bank}
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 mt-2">
                      <span className="text-[10px] text-cyan-400 font-bold uppercase block mb-1">
                        Turnaround Dynamics:
                      </span>
                      <span className="text-slate-300 text-[11px] leading-relaxed">
                        Funds were forwarded within seconds of settlement. The zero-balance retention
                        signature indicates intermediate transit rather than genuine customer deposit.
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-xs text-slate-400">
                    No active transaction step selected.
                  </div>
                )}
              </div>

              <div className="mt-4 p-3 rounded-xl bg-cyan-950/30 border border-cyan-500/30 text-[11px] text-cyan-200 flex items-center gap-2">
                <Zap className="w-4 h-4 text-cyan-400 shrink-0" />
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
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
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
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-cyan-950/50 border-cyan-400 shadow-lg shadow-cyan-500/10'
                      : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2.5 mb-2">
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                        isSelected ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="font-bold text-xs text-white">{scen.title}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-snug">{scen.desc}</p>
                </div>
              );
            })}
          </div>

          {/* Simulation Results & Baseline vs Scenario Comparison */}
          {scenarioResult && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Baseline vs Simulated Comparison */}
              <div className="lg:col-span-7 glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                    <div>
                      <h3 className="text-base font-bold text-white">{scenarioResult.title}</h3>
                      <p className="text-xs text-slate-400 mt-0.5">{scenarioResult.description}</p>
                    </div>
                    <span className="px-2.5 py-1 rounded-md text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                      [SIMULATED SCENARIO]
                    </span>
                  </div>

                  {/* Comparative Metrics Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs font-sans">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                          <th className="py-2.5 px-3">Metric</th>
                          <th className="py-2.5 px-3 text-cyan-300">Baseline Actual</th>
                          <th className="py-2.5 px-3 text-amber-400">Simulated Digital Twin</th>
                          <th className="py-2.5 px-3">Topological Shift</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800 font-mono">
                        <tr>
                          <td className="py-3 px-3 text-slate-300 font-sans">Network Hops</td>
                          <td className="py-3 px-3 text-white">
                            {scenarioResult.baseline_comparison.baseline.hops} Hops
                          </td>
                          <td className="py-3 px-3 text-amber-400 font-bold">
                            {scenarioResult.baseline_comparison.simulated.hops} Hops
                          </td>
                          <td className="py-3 px-3 text-slate-400">
                            +{scenarioResult.baseline_comparison.simulated.hops -
                              scenarioResult.baseline_comparison.baseline.hops}{' '}
                            Synthetic Nodes
                          </td>
                        </tr>
                        <tr>
                          <td className="py-3 px-3 text-slate-300 font-sans">Detection Latency</td>
                          <td className="py-3 px-3 text-white">
                            {scenarioResult.baseline_comparison.baseline.turnaround_latency_sec}s
                          </td>
                          <td className="py-3 px-3 text-amber-400 font-bold">
                            {scenarioResult.baseline_comparison.simulated.turnaround_latency_sec}s
                          </td>
                          <td className="py-3 px-3 text-emerald-400">Rapid Anomaly Alert</td>
                        </tr>
                        <tr>
                          <td className="py-3 px-3 text-slate-300 font-sans">Ring Risk Score</td>
                          <td className="py-3 px-3 text-white">
                            {scenarioResult.baseline_comparison.baseline.risk_score}%
                          </td>
                          <td className="py-3 px-3 text-rose-400 font-bold">
                            {scenarioResult.baseline_comparison.simulated.risk_score}%
                          </td>
                          <td className="py-3 px-3 text-rose-400">
                            +{scenarioResult.baseline_comparison.delta.risk_increase_points} pts
                          </td>
                        </tr>
                        <tr>
                          <td className="py-3 px-3 text-slate-300 font-sans">Evasion Likelihood</td>
                          <td className="py-3 px-3 text-slate-400">Baseline</td>
                          <td className="py-3 px-3 text-emerald-400 font-sans font-bold" colSpan="2">
                            {scenarioResult.baseline_comparison.delta.evasion_analysis}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="mt-6 p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                  <span className="font-bold text-white block mb-1">
                    AI Regulatory Defense Takeaway:
                  </span>
                  <p className="text-slate-300 font-sans leading-relaxed">
                    {scenarioResult.recommendation_notes}
                  </p>
                </div>
              </div>

              {/* Synthetic Subgraph Preview */}
              <div className="lg:col-span-5 glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                      Synthetic Topology Nodes
                    </span>
                    <span className="text-[10px] text-amber-400 font-mono font-bold">
                      {scenarioResult.synthetic_nodes?.length || 0} Entities
                    </span>
                  </div>

                  <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                    {scenarioResult.synthetic_nodes?.map((node, i) => (
                      <div
                        key={i}
                        className={`p-2.5 rounded-xl border text-xs flex items-center justify-between ${
                          node.is_synthetic
                            ? 'bg-amber-950/30 border-amber-500/50 text-amber-200'
                            : 'bg-slate-900 border-slate-800 text-slate-300'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span
                            className={`w-2 h-2 rounded-full ${
                              node.is_synthetic ? 'bg-amber-400 animate-pulse' : 'bg-cyan-400'
                            }`}
                          />
                          <span className="font-mono font-bold">{node.id}</span>
                        </div>
                        <span
                          className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                            node.is_synthetic
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          {node.role}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Simulation Watermark Banner */}
                <div className="mt-4 p-3 rounded-xl bg-amber-950/40 border border-amber-500/40 text-[10px] font-mono text-amber-300 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
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
