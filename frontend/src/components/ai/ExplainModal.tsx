import React, { useEffect, useState } from 'react';
import { X, Info, ShieldCheck, AlertOctagon, CheckCircle2, FileText, Compass } from 'lucide-react';
import { api } from '../../api/client';
import { FactBasedExplanation } from '../../types';

interface ExplainModalProps {
  candidateId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ExplainModal: React.FC<ExplainModalProps> = ({
  candidateId,
  isOpen,
  onClose,
}) => {
  const [explanation, setExplanation] = useState<FactBasedExplanation | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isOpen || !candidateId) return;
    const fetchExplanation = async () => {
      setIsLoading(true);
      try {
        const data = await api.getFactExplanation(candidateId);
        setExplanation(data);
      } catch (err) {
        console.error('Failed to load fact-based explanation:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchExplanation();
  }, [isOpen, candidateId]);

  if (!isOpen || !candidateId) return null;

  const isBlocker = explanation?.validation_status === 'BLOCKER';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-lg shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/80">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Info className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Fact-Based Cadastral Explanation</h3>
              <p className="text-xs text-slate-400 font-mono">
                Target: {candidateId}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 space-y-4">
          {isLoading ? (
            <div className="py-8 text-center text-slate-400 font-mono text-xs">
              Synthesizing structured topological facts...
            </div>
          ) : !explanation ? (
            <div className="py-8 text-center text-slate-400 font-mono text-xs">
              Explanation unavailable.
            </div>
          ) : (
            <>
              {/* Summary Statement */}
              <div
                className={`p-3 rounded-lg border text-xs ${
                  isBlocker
                    ? 'bg-red-950/20 border-red-500/40 text-red-200'
                    : 'bg-cyan-950/20 border-cyan-500/40 text-cyan-200'
                }`}
              >
                <div className="flex items-start space-x-2">
                  {isBlocker ? (
                    <AlertOctagon className="w-4 h-4 mt-0.5 text-red-400 flex-shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 mt-0.5 text-cyan-400 flex-shrink-0" />
                  )}
                  <div>
                    <span className="font-bold block uppercase text-[10px] tracking-wider mb-0.5">
                      Synthesis:
                    </span>
                    <p className="font-sans leading-relaxed">{explanation.summary}</p>
                  </div>
                </div>
              </div>

              {/* Geometric Measurements */}
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 flex items-center space-x-1 mb-1.5">
                  <Compass className="w-3 h-3 text-cyan-400" />
                  <span>Verified Geometric Facts</span>
                </span>
                <div className="p-3 rounded bg-slate-950 border border-slate-800 space-y-1 font-mono text-xs text-slate-300">
                  {explanation.geometric_facts.map((f, i) => (
                    <div key={i} className="flex items-center space-x-2">
                      <span className="text-cyan-400">•</span>
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Evidence Basis */}
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 flex items-center space-x-1 mb-1.5">
                  <FileText className="w-3 h-3 text-amber-400" />
                  <span>Evidence & Provenance Basis</span>
                </span>
                <div className="p-3 rounded bg-slate-950 border border-slate-800 space-y-1 font-mono text-xs text-slate-300">
                  {explanation.evidence_basis.map((e, i) => (
                    <div key={i} className="flex items-center space-x-2">
                      <span className="text-amber-400">•</span>
                      <span>{e}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Disclaimer */}
              <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80 text-[11px] font-sans text-slate-400">
                <span className="font-bold text-slate-300">Grounding Guarantee: </span>
                {explanation.disclaimer}
              </div>
            </>
          )}

          <div className="pt-2 flex items-center justify-end">
            <button
              onClick={onClose}
              className="px-4 py-1.5 text-xs font-medium rounded bg-slate-800 hover:bg-slate-700 text-white transition"
            >
              Close Explanation
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
