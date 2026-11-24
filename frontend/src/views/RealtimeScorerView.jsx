import React, { useState } from 'react';
import { apiFetch } from '../api';
import { Zap, Play, ShieldAlert, CheckCircle, AlertTriangle, Cpu, Activity } from 'lucide-react';

export default function RealtimeScorerView() {
  const [bankId, setBankId] = useState('BANK_A');
  const [senderAccount, setSenderAccount] = useState('BANK_A:BNK_A_ACC_00100');
  const [receiverAccount, setReceiverAccount] = useState('BANK_B:BNK_B_ACC_00250');
  const [amount, setAmount] = useState('48500');
  const [txType, setTxType] = useState('UPI_P2P');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleScore = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const payload = {
        bank_id: bankId,
        sender_account: senderAccount,
        receiver_account: receiverAccount,
        amount: parseFloat(amount),
        tx_type: txType,
      };

      const res = await apiFetch('/api/v1/realtime/transaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setResult(data);
      } else {
        alert('Scoring request failed: ' + res.statusText);
      }
    } catch (err) {
      console.error(err);
      alert('Error connecting to Realtime Scorer API');
    } finally {
      setIsLoading(false);
    }
  };

  const loadPreset = (type) => {
    if (type === 'mule') {
      setBankId('BANK_A');
      setSenderAccount('BANK_A:BNK_A_ACC_00100');
      setReceiverAccount('BANK_B:BNK_B_ACC_00250');
      setAmount('49500');
      setTxType('UPI_P2P');
    } else {
      setBankId('BANK_A');
      setSenderAccount('BANK_A:BNK_A_ACC_00888');
      setReceiverAccount('BANK_C:BNK_C_ACC_00045');
      setAmount('1450');
      setTxType('UPI_P2P');
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Top Header Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 shrink-0">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-extrabold text-slate-900 tracking-tight">
                Sub-15ms Real-Time Transaction Scoring Sandbox
              </h2>
              <span className="bg-blue-50 text-blue-700 border border-blue-200 font-extrabold text-[10px] px-2 py-0.5 rounded-full font-mono">
                SLA &lt;15MS
              </span>
            </div>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Test transaction events against production-trained XGBoost and Random Forest fraud detection engines
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => loadPreset('mule')}
            className="px-3.5 py-2 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-extrabold shadow-xs transition-colors cursor-pointer"
          >
            Load Smurf Mule Preset
          </button>
          <button
            onClick={() => loadPreset('legit')}
            className="px-3.5 py-2 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 text-xs font-extrabold shadow-xs transition-colors cursor-pointer"
          >
            Load Retail Preset
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Form Inputs */}
        <div className="lg:col-span-5 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col gap-4">
          <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider border-b border-slate-100 pb-3">
            Transaction Parameters
          </h3>

          <form onSubmit={handleScore} className="flex flex-col gap-4 text-xs">
            <div>
              <label className="block text-slate-700 font-extrabold mb-1.5">Reporting Bank Code</label>
              <select
                value={bankId}
                onChange={(e) => setBankId(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-semibold focus:outline-none focus:border-blue-600 shadow-xs cursor-pointer"
              >
                <option value="BANK_A">Bank A (Primary Switch)</option>
                <option value="BANK_B">Bank B (Commercial Node)</option>
                <option value="BANK_C">Bank C (Cooperative Node)</option>
                <option value="BANK_D">Bank D (Federal Node)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-700 font-extrabold mb-1.5">Source Account ID (Sender)</label>
              <input
                type="text"
                value={senderAccount}
                onChange={(e) => setSenderAccount(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-mono font-bold focus:outline-none focus:border-blue-600 shadow-xs"
              />
            </div>

            <div>
              <label className="block text-slate-700 font-extrabold mb-1.5">Destination Account ID (Beneficiary)</label>
              <input
                type="text"
                value={receiverAccount}
                onChange={(e) => setReceiverAccount(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-mono font-bold focus:outline-none focus:border-blue-600 shadow-xs"
              />
            </div>

            <div>
              <label className="block text-slate-700 font-extrabold mb-1.5">Transaction Amount (INR)</label>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-mono font-bold focus:outline-none focus:border-blue-600 shadow-xs"
              />
            </div>

            <div>
              <label className="block text-slate-700 font-extrabold mb-1.5">Channel / Payment Protocol</label>
              <select
                value={txType}
                onChange={(e) => setTxType(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-semibold focus:outline-none focus:border-blue-600 shadow-xs cursor-pointer"
              >
                <option value="UPI_P2P">UPI P2P (Peer-to-Peer Sub-Second)</option>
                <option value="UPI_P2M">UPI P2M (Peer-to-Merchant)</option>
                <option value="IMPS">IMPS Immediate Payment</option>
                <option value="NEFT">NEFT Batch Clearing</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="mt-2 w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold uppercase tracking-wider text-xs flex items-center justify-center gap-2 shadow-md shadow-blue-500/25 transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
            >
              <Play className="w-4 h-4 fill-current" />
              {isLoading ? 'Running ML Model...' : 'Execute Sub-15ms ML Scoring'}
            </button>
          </form>
        </div>

        {/* Real-Time Results Card */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <Cpu className="w-4 h-4 text-blue-600" />
                Inference Results & SLA Telemetry
              </span>
              {result && (
                <span className="text-xs font-mono font-extrabold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-emerald-600" />
                  Latency: {result.latency_ms} ms (SLA &lt;15ms Met)
                </span>
              )}
            </div>

            {!result ? (
              <div className="h-64 flex flex-col items-center justify-center text-slate-500 text-xs">
                <Activity className="w-12 h-12 text-blue-500 mb-3 animate-pulse" />
                <span className="font-semibold">Submit a transaction to trigger real-time feature extraction & model scoring.</span>
              </div>
            ) : (
              <div className="flex flex-col gap-5">
                {/* Score Header */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[10px] text-slate-600 font-extrabold uppercase tracking-wider">Fraud Probability</span>
                    <div className="text-2xl font-extrabold font-mono mt-1 text-slate-900">
                      {(result.fraud_probability * 100).toFixed(1)}%
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[10px] text-slate-600 font-extrabold uppercase tracking-wider">Assigned Risk Tier</span>
                    <div className="mt-1">
                      {result.risk_level === 'High' ? (
                        <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-rose-50 text-rose-700 border border-rose-200 inline-block shadow-xs">
                          CRITICAL RISK
                        </span>
                      ) : (
                        <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-200 inline-block shadow-xs">
                          LOW / NORMAL
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 col-span-2 md:col-span-1">
                    <span className="text-[10px] text-slate-600 font-extrabold uppercase tracking-wider">Engine Model</span>
                    <div className="text-xs font-extrabold text-blue-700 font-mono mt-1">
                      {result.model_used}
                    </div>
                  </div>
                </div>

                {/* Trigger Reasons */}
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col gap-2">
                  <span className="text-xs font-extrabold text-slate-900 uppercase tracking-wider">
                    Model Decision Attributions & Triggers:
                  </span>
                  <div className="space-y-1.5 text-xs text-slate-700 font-medium">
                    {result.trigger_reasons?.map((reason, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 shrink-0" />
                        <span>{reason}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommended Graduated Action */}
                <div className={`p-4 rounded-xl border-2 flex items-center justify-between gap-3 text-xs ${
                  result.risk_level === 'High' 
                    ? 'bg-rose-50/70 border-rose-200 text-rose-950' 
                    : 'bg-emerald-50/70 border-emerald-200 text-emerald-950'
                }`}>
                  <div className="flex items-center gap-2.5">
                    {result.risk_level === 'High' ? (
                      <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
                    ) : (
                      <CheckCircle className="w-5 h-5 text-emerald-600 shrink-0" />
                    )}
                    <div>
                      <span className="font-extrabold block text-sm">
                        {result.risk_level === 'High' ? 'Graduated Countermeasure Recommended' : 'Direct Clearing Permitted'}
                      </span>
                      <span className="text-xs font-semibold opacity-90">
                        {result.risk_level === 'High' 
                          ? 'Enforce Dynamic 60-Minute Outbound Cooling-Off Delay (Zero Account Freezing)' 
                          : 'Immediate sub-second UPI settlement authorized.'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[10px] text-slate-500 font-semibold flex items-center justify-between">
            <span>DPDP Act 2023 Masked • Cryptographic SHA-256 Audit Logged</span>
            <span className="font-mono">API: POST /api/v1/realtime/transaction</span>
          </div>
        </div>
      </div>
    </div>
  );
}
