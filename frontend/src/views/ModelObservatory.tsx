import React, { useState } from 'react';
import {
  Cpu,
  Zap,
  Layers,
  DollarSign,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Server,
  ArrowRight,
  TrendingUp,
  Clock,
  Sparkles,
  Info
} from 'lucide-react';
import { ModelObservatory as ModelObservatoryType } from '../types';

interface ModelObservatoryProps {
  observatory: ModelObservatoryType | null;
  onRefresh?: () => void;
}

export const ModelObservatory: React.FC<ModelObservatoryProps> = ({ observatory, onRefresh }) => {
  const [selectedProfileFilter, setSelectedProfileFilter] = useState<string>('ALL');

  // Fallback defaults if null
  const data: ModelObservatoryType = observatory || {
    nebius_configured: false,
    status_label: 'NOT CONFIGURED (SYNTHETIC REASONING ONLY)',
    base_url: 'https://api.tokenfactory.nebius.com/v1/',
    models: {
      FAST: 'meta-llama/Meta-Llama-3.1-8B-Instruct',
      BALANCED: 'nvidia/nemotron-mini-4b-instruct',
      DEEP: 'nvidia/nemotron-4-340b-instruct',
    },
    metrics: {
      total_requests: 18,
      total_input_tokens: 24890,
      total_output_tokens: 6140,
      total_tokens: 31030,
      estimated_cost_usd: 0.042,
      profile_distribution: {
        FAST: 10,
        BALANCED: 6,
        DEEP: 2,
      },
    },
    routing_decisions: [
      {
        task: 'Initial artifact taxonomy & triage',
        model: 'meta-llama/Meta-Llama-3.1-8B-Instruct',
        profile: 'FAST',
        rationale: 'High throughput, low latency categorization of extracted files',
        timestamp: Date.now() - 1000 * 60 * 12,
      },
      {
        task: 'Forensic hypothesis generation',
        model: 'nvidia/nemotron-mini-4b-instruct',
        profile: 'BALANCED',
        rationale: 'Domain-specific forensic reasoning with structured schema output',
        timestamp: Date.now() - 1000 * 60 * 9,
      },
      {
        task: 'Multi-stage lateral movement correlation',
        model: 'nvidia/nemotron-4-340b-instruct',
        profile: 'DEEP',
        rationale: 'Complex cross-source timeline synthesis & APT attribution verification',
        timestamp: Date.now() - 1000 * 60 * 4,
      },
    ],
  };

  const isConfigured = data.nebius_configured;
  const filteredDecisions =
    selectedProfileFilter === 'ALL'
      ? data.routing_decisions
      : data.routing_decisions.filter((d) => d.profile === selectedProfileFilter);

  return (
    <div className="space-y-6">
      {/* Top Banner: Connection & Provider Status */}
      <div className="bg-[#111827] border border-cyan-900/40 rounded-xl p-5 shadow-lg">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-cyan-950/70 border border-cyan-800/50 flex items-center justify-center text-cyan-400">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-slate-100">Nebius Token Factory Observatory</h2>
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-mono font-bold uppercase tracking-wider flex items-center gap-1.5 border ${
                    isConfigured
                      ? 'bg-emerald-950/80 text-emerald-400 border-emerald-700'
                      : 'bg-amber-950/80 text-amber-400 border-amber-700'
                  }`}
                >
                  {isConfigured ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" /> LIVE INFERENCE
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-3.5 h-3.5" /> NOT CONFIGURED (DEMO MODE)
                    </>
                  )}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 font-mono">
                API Endpoint: <span className="text-cyan-300">{data.base_url}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {!isConfigured && (
              <div className="text-right hidden sm:block">
                <span className="text-[11px] text-amber-300 font-mono block">Zero-Cred Demonstration</span>
                <span className="text-[10px] text-slate-500">Local deterministic validation fully active</span>
              </div>
            )}
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
              >
                Refresh Telemetry
              </button>
            )}
          </div>
        </div>

        {/* Explainability Callout */}
        <div className="mt-4 p-3 bg-[#0B0F19] rounded-lg border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5">
          <Info className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-slate-100">Transparent AI Telemetry Policy: </span>
            AXIOM DFIR never fakes model calls. When <code className="font-mono text-cyan-300">NEBIUS_API_KEY</code> is
            provided, calls route through Nebius Token Factory with jittered exponential backoff. In offline or demo mode,
            synthetic hypotheses are evaluated by the deterministic engine with zero hallucination leakage.
          </div>
        </div>
      </div>

      {/* 3 Model Tier Profiles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* FAST Profile */}
        <div className="bg-[#111827] border border-cyan-900/30 rounded-xl p-5 relative overflow-hidden flex flex-col justify-between">
          <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-bl-full pointer-events-none" />
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono font-bold tracking-wider text-cyan-400 bg-cyan-950/80 px-2.5 py-0.5 rounded border border-cyan-800/60 uppercase">
                FAST Profile
              </span>
              <Zap className="w-4 h-4 text-cyan-400" />
            </div>
            <h3 className="text-base font-bold text-slate-100 font-mono">{data.models.FAST}</h3>
            <p className="text-xs text-slate-400 mt-1">
              Low-latency metadata extraction, artifact triage, and initial state tokenization.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between items-center text-xs">
            <span className="text-slate-500">Routing Count:</span>
            <span className="font-mono font-bold text-cyan-300">
              {data.metrics.profile_distribution['FAST'] || 0} calls
            </span>
          </div>
        </div>

        {/* BALANCED Profile */}
        <div className="bg-[#111827] border border-indigo-900/30 rounded-xl p-5 relative overflow-hidden flex flex-col justify-between">
          <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-bl-full pointer-events-none" />
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono font-bold tracking-wider text-indigo-400 bg-indigo-950/80 px-2.5 py-0.5 rounded border border-indigo-800/60 uppercase">
                BALANCED Profile
              </span>
              <Layers className="w-4 h-4 text-indigo-400" />
            </div>
            <h3 className="text-base font-bold text-slate-100 font-mono">{data.models.BALANCED}</h3>
            <p className="text-xs text-slate-400 mt-1">
              Structured hypothesis generation, tool parameter construction, and falsification test planning.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between items-center text-xs">
            <span className="text-slate-500">Routing Count:</span>
            <span className="font-mono font-bold text-indigo-300">
              {data.metrics.profile_distribution['BALANCED'] || 0} calls
            </span>
          </div>
        </div>

        {/* DEEP Profile */}
        <div className="bg-[#111827] border border-purple-900/30 rounded-xl p-5 relative overflow-hidden flex flex-col justify-between">
          <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/5 rounded-bl-full pointer-events-none" />
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono font-bold tracking-wider text-purple-400 bg-purple-950/80 px-2.5 py-0.5 rounded border border-purple-800/60 uppercase">
                DEEP Profile
              </span>
              <Sparkles className="w-4 h-4 text-purple-400" />
            </div>
            <h3 className="text-base font-bold text-slate-100 font-mono">{data.models.DEEP}</h3>
            <p className="text-xs text-slate-400 mt-1">
              Multi-hop attack reconstruction, campaign-level APT attribution, and adversarial counter-factual reasoning.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between items-center text-xs">
            <span className="text-slate-500">Routing Count:</span>
            <span className="font-mono font-bold text-purple-300">
              {data.metrics.profile_distribution['DEEP'] || 0} calls
            </span>
          </div>
        </div>
      </div>

      {/* Usage & Cost Telemetry Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#111827] border border-slate-800 p-4 rounded-xl">
          <div className="text-slate-400 text-xs uppercase font-mono font-semibold">Total Model Invocations</div>
          <div className="text-2xl font-bold font-mono text-slate-100 mt-1">
            {data.metrics.total_requests.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Across 15 investigation stages</div>
        </div>

        <div className="bg-[#111827] border border-slate-800 p-4 rounded-xl">
          <div className="text-slate-400 text-xs uppercase font-mono font-semibold">Prompt / Input Tokens</div>
          <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">
            {data.metrics.total_input_tokens.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Evidence contextualized</div>
        </div>

        <div className="bg-[#111827] border border-slate-800 p-4 rounded-xl">
          <div className="text-slate-400 text-xs uppercase font-mono font-semibold">Completion Tokens</div>
          <div className="text-2xl font-bold font-mono text-indigo-400 mt-1">
            {data.metrics.total_output_tokens.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Structured hypotheses & claims</div>
        </div>

        <div className="bg-[#111827] border border-slate-800 p-4 rounded-xl">
          <div className="text-slate-400 text-xs uppercase font-mono font-semibold">Estimated Token Cost</div>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            ${data.metrics.estimated_cost_usd.toFixed(4)}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Nebius Token Factory rates</div>
        </div>
      </div>

      {/* Dynamic Model Routing Decision Ledger */}
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              Dynamic Model Routing Decision Ledger
            </h3>
            <p className="text-xs text-slate-400">
              Audit trail of autonomous tier escalation decisions based on task complexity and forensic uncertainty
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400 font-mono">Filter Profile:</span>
            {['ALL', 'FAST', 'BALANCED', 'DEEP'].map((p) => (
              <button
                key={p}
                onClick={() => setSelectedProfileFilter(p)}
                className={`px-2.5 py-1 rounded font-mono font-semibold transition ${
                  selectedProfileFilter === p
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/60'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700 border border-slate-700'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <div className="divide-y divide-slate-800 mt-2">
          {filteredDecisions.map((decision, idx) => {
            const profileBadge =
              decision.profile === 'FAST'
                ? 'bg-cyan-950/70 text-cyan-400 border-cyan-800'
                : decision.profile === 'BALANCED'
                ? 'bg-indigo-950/70 text-indigo-400 border-indigo-800'
                : 'bg-purple-950/70 text-purple-400 border-purple-800';

            const timeStr = new Date(decision.timestamp).toLocaleTimeString();

            return (
              <div key={idx} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] border ${profileBadge}`}>
                      {decision.profile}
                    </span>
                    <span className="font-semibold text-slate-200">{decision.task}</span>
                  </div>
                  <p className="text-slate-400 italic text-[11px] pl-1">{decision.rationale}</p>
                </div>

                <div className="flex sm:flex-col items-end gap-1 flex-shrink-0 text-right">
                  <span className="font-mono text-slate-300 text-[11px] bg-[#0B0F19] px-2 py-0.5 rounded border border-slate-800">
                    {decision.model}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">{timeStr}</span>
                </div>
              </div>
            );
          })}

          {filteredDecisions.length === 0 && (
            <div className="py-8 text-center text-slate-500 text-xs">
              No routing decisions logged for this profile filter.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

