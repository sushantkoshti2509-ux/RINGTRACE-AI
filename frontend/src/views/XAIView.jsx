import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api';
import { Sparkles, Brain, CheckCircle2, TrendingUp, HelpCircle, Shield } from 'lucide-react';

export default function XAIView() {
  const [xaiData, setXaiData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchXAI = async () => {
      setIsLoading(true);
      try {
        const res = await apiFetch('/api/v1/platform/xai/features');
        if (res.ok) {
          const data = await res.json();
          setXaiData(data);
        }
      } catch (err) {
        console.error('Failed to fetch XAI data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchXAI();
  }, []);

  return (
    <div className="flex flex-col gap-6">
      {/* Title */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-400" />
            <span>Explainable AI (XAI) & SHAP TreeExplainer Attributions</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Transparent, human-understandable reason codes complying with central regulatory directives
          </p>
        </div>
        <span className="text-xs font-mono font-bold text-purple-300 bg-purple-500/10 px-3 py-1 rounded-xl border border-purple-500/30">
          SHAP Model: XGBoost + TreeExplainer
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Global Feature Importance */}
        <div className="lg:col-span-6 glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              Global Model Feature Importance (Weighting)
            </span>
            <span className="text-[10px] text-slate-400">Ensemble Impact</span>
          </div>

          <div className="space-y-3.5">
            {(xaiData?.global_importance || []).map((feat, idx) => (
              <div key={idx} className="text-xs">
                <div className="flex justify-between items-center mb-1">
                  <span className="font-semibold text-slate-200">{feat.feature}</span>
                  <span className="font-mono text-cyan-300 font-bold">{(feat.importance * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-cyan-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${feat.importance * 100 * 2.8}%` }}
                  />
                </div>
                <span className="text-[10px] text-slate-500 block mt-0.5">{feat.category}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Local SHAP Waterfall Attribution */}
        <div className="lg:col-span-6 glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                Local Transaction SHAP Waterfall Attribution
              </span>
              <span className="text-[10px] text-slate-400 font-mono">TXN: #TX_MULE_8014</span>
            </div>

            <p className="text-xs text-slate-400 mb-4 font-sans">
              Shows how specific transactional indicators push the fraud prediction score higher (red) or lower (emerald) from the baseline:
            </p>

            <div className="space-y-3">
              {(xaiData?.sample_attributions || []).map((attr, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-xl border flex items-center justify-between gap-3 text-xs ${
                    attr.impact === 'INCREASES_RISK'
                      ? 'bg-rose-950/30 border-rose-500/30 text-rose-200'
                      : 'bg-emerald-950/30 border-emerald-500/30 text-emerald-200'
                  }`}
                >
                  <div>
                    <span className="font-bold block">{attr.feature}</span>
                    <span className="text-[11px] opacity-80">{attr.description}</span>
                  </div>
                  <span className={`font-mono font-bold text-sm shrink-0 ${
                    attr.impact === 'INCREASES_RISK' ? 'text-rose-400' : 'text-emerald-400'
                  }`}>
                    {attr.shap_value > 0 ? `+${attr.shap_value}` : attr.shap_value}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Deterministic Rule Flags */}
          <div className="mt-5 p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col gap-2">
            <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Deterministic Regulatory Reason Codes:
            </span>
            <div className="space-y-1 text-xs text-slate-300 font-sans">
              {(xaiData?.deterministic_rules || []).map((rule, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                  <span>{rule}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
