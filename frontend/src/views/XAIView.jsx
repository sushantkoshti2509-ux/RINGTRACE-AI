import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api';
import { Sparkles, Brain, CheckCircle2, TrendingUp, HelpCircle, Shield, Activity } from 'lucide-react';

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
      {/* Top Header Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 shrink-0">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-extrabold text-slate-900 tracking-tight">
                Explainable AI (XAI) & Feature Attribution
              </h2>
              <span className="bg-blue-50 text-blue-700 border border-blue-200 font-extrabold text-[10px] px-2 py-0.5 rounded-full font-mono">
                SHAP TREE-EXPLAINER
              </span>
            </div>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Transparent feature contributions, global model weightings, and transaction-level waterfall attribution
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-extrabold text-blue-800 bg-blue-50 px-3.5 py-1.5 rounded-xl border border-blue-200 shadow-xs">
            Model: XGBoost + TreeExplainer (Ensemble)
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Global Feature Importance */}
        <div className="lg:col-span-6 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-600" />
              Global Model Feature Importance (Weighting)
            </span>
            <span className="text-[11px] font-mono font-extrabold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              Ensemble Impact
            </span>
          </div>

          <div className="space-y-4">
            {(xaiData?.global_importance || []).map((feat, idx) => (
              <div key={idx} className="text-xs">
                <div className="flex justify-between items-center mb-1.5">
                  <span className="font-extrabold text-slate-900 text-xs">{feat.feature}</span>
                  <span className="font-mono text-blue-700 font-extrabold text-xs">
                    {(feat.importance * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2.5 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, feat.importance * 100 * 2.8)}%` }}
                  />
                </div>
                <span className="text-[11px] font-semibold text-slate-500 block mt-1">
                  Category: {feat.category}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Local SHAP Waterfall Attribution */}
        <div className="lg:col-span-6 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-500" />
                Local Transaction SHAP Waterfall Attribution
              </span>
              <span className="text-xs font-mono font-extrabold text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-lg">
                TXN: #TX_MULE_8014
              </span>
            </div>

            <p className="text-xs text-slate-600 font-medium mb-4">
              Shows how specific transactional indicators push the fraud prediction score higher (red) or lower (emerald) from the baseline:
            </p>

            <div className="space-y-3">
              {(xaiData?.sample_attributions || []).map((attr, idx) => {
                const isRisk = attr.impact === 'INCREASES_RISK';
                return (
                  <div
                    key={idx}
                    className={`p-3.5 rounded-xl border flex items-center justify-between gap-3 text-xs ${
                      isRisk
                        ? 'bg-rose-50/70 border-rose-200 text-rose-950'
                        : 'bg-emerald-50/70 border-emerald-200 text-emerald-950'
                    }`}
                  >
                    <div>
                      <span className="font-extrabold block text-xs">{attr.feature}</span>
                      <span className="text-[11px] font-medium opacity-90">{attr.description}</span>
                    </div>
                    <span
                      className={`font-mono font-extrabold text-sm shrink-0 px-2 py-0.5 rounded-md ${
                        isRisk ? 'text-rose-700 bg-rose-100/60' : 'text-emerald-700 bg-emerald-100/60'
                      }`}
                    >
                      {attr.shap_value > 0 ? `+${attr.shap_value}` : attr.shap_value}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Deterministic Rule Flags */}
          <div className="mt-6 p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col gap-2.5">
            <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider">
              Deterministic Regulatory Reason Codes:
            </span>
            <div className="space-y-1.5 text-xs text-slate-700">
              {(xaiData?.deterministic_rules || []).map((rule, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                  <span className="font-semibold text-slate-800">{rule}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
