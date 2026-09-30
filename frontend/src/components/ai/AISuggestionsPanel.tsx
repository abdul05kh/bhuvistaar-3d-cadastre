import React from 'react';
import {
  Brain,
  CheckCircle,
  XCircle,
  Eye,
  Info,
  Layers,
  Sparkles,
  GitBranch,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { AICandidate } from '../../types';

interface AISuggestionsPanelProps {
  candidates: AICandidate[];
  selectedCandidateId: string | null;
  onSelectCandidate: (candidateId: string) => void;
  onAcceptCandidate: (candidate: AICandidate) => void;
  onRejectCandidate: (candidate: AICandidate) => void;
  onExplainCandidate: (candidateId: string) => void;
  onTraceLineage: (candidateId: string) => void;
  onRunInference: () => void;
  isLoading: boolean;
}

export const AISuggestionsPanel: React.FC<AISuggestionsPanelProps> = ({
  candidates,
  selectedCandidateId,
  onSelectCandidate,
  onAcceptCandidate,
  onRejectCandidate,
  onExplainCandidate,
  onTraceLineage,
  onRunInference,
  isLoading,
}) => {
  return (
    <div className="space-y-4">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-cyan-950/60 to-slate-900 border border-cyan-500/30 rounded-lg p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-400/30 flex items-center justify-center text-cyan-400">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-semibold text-white tracking-wide">
                AI-Assisted Candidate Spatial Units
              </h3>
              <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                PROPOSAL ONLY
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Proposals derived from architectural drawings & structural blueprints. Deterministic spatial validation and human review remain mandatory.
            </p>
          </div>
        </div>
        <button
          onClick={onRunInference}
          disabled={isLoading}
          className="px-3.5 py-2 text-xs font-medium rounded-md bg-cyan-600 hover:bg-cyan-500 text-white flex items-center space-x-2 transition shadow-lg shadow-cyan-900/30 disabled:opacity-50"
        >
          <Brain className="w-4 h-4" />
          <span>{isLoading ? 'Synthesizing...' : 'Regenerate Proposals'}</span>
        </button>
      </div>

      {/* Candidate List */}
      {candidates.length === 0 ? (
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-8 text-center text-slate-400">
          <Brain className="w-10 h-10 mx-auto text-slate-600 mb-2" />
          <p className="text-sm">No AI candidate proposals generated yet.</p>
          <button
            onClick={onRunInference}
            className="mt-3 px-4 py-1.5 text-xs rounded bg-cyan-600 hover:bg-cyan-500 text-white font-medium inline-flex items-center space-x-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Generate AI Candidates</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {candidates.map((cand) => {
            const isSelected = cand.candidate_id === selectedCandidateId;
            const isAccepted = cand.status === 'ACCEPTED';
            const isRejected = cand.status === 'REJECTED';
            const isPending = cand.status === 'AI_CANDIDATE';

            let bandColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
            if (cand.confidence_band === 'MEDIUM') bandColor = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
            if (cand.confidence_band === 'LOW') bandColor = 'bg-red-500/10 text-red-400 border-red-500/30';

            return (
              <div
                key={cand.candidate_id}
                onClick={() => onSelectCandidate(cand.candidate_id)}
                className={`bg-slate-900/70 border rounded-lg p-4 cursor-pointer transition relative overflow-hidden ${
                  isSelected
                    ? 'border-cyan-400 ring-1 ring-cyan-400/50 bg-cyan-950/20'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                {/* Status Indicator Bar */}
                <div
                  className={`absolute top-0 left-0 right-0 h-1 ${
                    isAccepted
                      ? 'bg-emerald-500'
                      : isRejected
                      ? 'bg-red-500'
                      : 'bg-cyan-500'
                  }`}
                />

                <div className="flex items-start justify-between mt-1">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-base font-bold text-white tracking-wide">
                        Level {cand.level_code}
                      </span>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase tracking-wider ${
                          isAccepted
                            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                            : isRejected
                            ? 'bg-red-500/20 text-red-300 border-red-500/40'
                            : 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30'
                        }`}
                      >
                        {cand.status === 'AI_CANDIDATE' ? 'AI Proposal' : cand.status}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 font-mono mt-0.5">
                      {cand.candidate_id}
                    </div>
                  </div>

                  {/* Confidence Metric */}
                  <div className="text-right">
                    <div className="text-[10px] uppercase tracking-wider text-slate-400">Confidence</div>
                    <div className={`text-xs font-mono font-bold px-2 py-0.5 rounded border mt-0.5 inline-block ${bandColor}`}>
                      {(cand.confidence * 100).toFixed(0)}% ({cand.confidence_band})
                    </div>
                  </div>
                </div>

                {/* Geometric Metrics Grid */}
                <div className="grid grid-cols-3 gap-2 mt-3 p-2.5 rounded bg-slate-950/60 border border-slate-800/80 text-xs font-mono">
                  <div>
                    <span className="text-[10px] text-slate-400 block uppercase">Elevation</span>
                    <span className="text-slate-200">
                      {cand.z_min.toFixed(2)}m – {cand.z_max.toFixed(2)}m
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block uppercase">Footprint</span>
                    <span className="text-slate-200">{cand.footprint_area_sqm.toFixed(1)} m²</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block uppercase">3D Volume</span>
                    <span className="text-slate-200">{cand.volume_cbm.toFixed(1)} m³</span>
                  </div>
                </div>

                {/* Reason Codes */}
                <div className="mt-3">
                  <span className="text-[10px] text-slate-400 uppercase font-mono block mb-1">
                    Explanatory Reasons:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {cand.reason_codes.map((r, i) => (
                      <span
                        key={i}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800/80 text-cyan-300 border border-slate-700/60"
                      >
                        ✓ {r.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center space-x-1.5">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onExplainCandidate(cand.candidate_id);
                      }}
                      className="px-2.5 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center space-x-1 border border-slate-700"
                      title="Fact-based explainability"
                    >
                      <Info className="w-3 h-3 text-cyan-400" />
                      <span>Explain</span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onTraceLineage(cand.candidate_id);
                      }}
                      className="px-2.5 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center space-x-1 border border-slate-700"
                      title="Trace complete data provenance"
                    >
                      <GitBranch className="w-3 h-3 text-purple-400" />
                      <span>Trace</span>
                    </button>
                  </div>

                  {isPending && (
                    <div className="flex items-center space-x-1.5">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onRejectCandidate(cand);
                        }}
                        className="px-2.5 py-1 text-xs rounded bg-red-950/40 hover:bg-red-900/60 text-red-300 border border-red-800/60 flex items-center space-x-1"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        <span>Reject</span>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onAcceptCandidate(cand);
                        }}
                        className="px-3 py-1 text-xs font-medium rounded bg-emerald-600 hover:bg-emerald-500 text-white flex items-center space-x-1 shadow-md shadow-emerald-900/30"
                      >
                        <CheckCircle className="w-3.5 h-3.5" />
                        <span>Accept Unit</span>
                      </button>
                    </div>
                  )}

                  {isAccepted && (
                    <span className="text-xs font-mono text-emerald-400 flex items-center space-x-1">
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>Governed Unit Created</span>
                    </span>
                  )}

                  {isRejected && (
                    <span className="text-xs font-mono text-red-400 flex items-center space-x-1">
                      <XCircle className="w-3.5 h-3.5" />
                      <span>Proposal Rejected</span>
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
