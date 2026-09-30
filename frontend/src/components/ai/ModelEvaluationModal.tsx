import React, { useEffect, useState } from 'react';
import { X, Award, BarChart3, ShieldAlert, Cpu, CheckCircle2, Play, RefreshCw, FileCode } from 'lucide-react';
import { api } from '../../api/client';
import { ModelCard } from '../../types';

interface ModelEvaluationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ModelEvaluationModal: React.FC<ModelEvaluationModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'cards' | 'benchmark'>('cards');
  const [models, setModels] = useState<ModelCard[]>([]);
  const [selectedModel, setSelectedModel] = useState<ModelCard | null>(null);
  const [evalReport, setEvalReport] = useState<any | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    const fetchModels = async () => {
      try {
        const data = await api.getAiModels();
        setModels(data.registered_models || []);
        if (data.registered_models && data.registered_models.length > 0) {
          setSelectedModel(data.registered_models[0]);
        }
      } catch (err) {
        console.error('Failed to load AI models:', err);
      }
    };
    fetchModels();
  }, [isOpen]);

  const handleRunEvaluation = async () => {
    setIsEvaluating(true);
    try {
      const report = await api.runAiEvaluation();
      setEvalReport(report);
      setActiveTab('benchmark');
    } catch (err) {
      console.error('Failed to run benchmark evaluation:', err);
    } finally {
      setIsEvaluating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/80">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white tracking-wide">
                  Model Governance Cards & Empirical Evaluation
                </h3>
                <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  TRANSPARENCY
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Prototype model disclosures, architectural constraints, and synthetic benchmark metrics.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selector & Actions */}
        <div className="px-5 py-2.5 bg-slate-950/50 border-b border-slate-800 flex items-center justify-between">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('cards')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition ${
                activeTab === 'cards'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              Model Registry & Cards ({models.length})
            </button>
            <button
              onClick={() => setActiveTab('benchmark')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition ${
                activeTab === 'benchmark'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              Empirical Benchmark Report {evalReport && '✓'}
            </button>
          </div>

          <button
            onClick={handleRunEvaluation}
            disabled={isEvaluating}
            className="px-3 py-1.5 text-xs font-medium rounded-md bg-purple-600 hover:bg-purple-500 text-white flex items-center space-x-1.5 transition shadow disabled:opacity-50"
          >
            {isEvaluating ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5" />
            )}
            <span>{isEvaluating ? 'Evaluating Synthetic Scenarios...' : 'Run Benchmark Harness'}</span>
          </button>
        </div>

        {/* Tab 1: Model Cards */}
        {activeTab === 'cards' && (
          <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-slate-800">
            {/* Model List */}
            <div className="p-4 overflow-y-auto space-y-2">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-2">
                Registered Prototype Models:
              </span>
              {models.map((m) => (
                <div
                  key={m.model_id}
                  onClick={() => setSelectedModel(m)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedModel?.model_id === m.model_id
                      ? 'bg-cyan-950/20 border-cyan-500/60 ring-1 ring-cyan-500/30'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{m.name}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300">
                      v{m.version}
                    </span>
                  </div>
                  <div className="text-[11px] font-mono text-slate-400 mt-1 truncate">
                    {m.task}
                  </div>
                </div>
              ))}
            </div>

            {/* Model Detail */}
            <div className="md:col-span-2 p-5 overflow-y-auto max-h-[65vh] space-y-4">
              {selectedModel ? (
                <div className="space-y-4 text-xs font-mono">
                  <div>
                    <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                      <span>{selectedModel.name}</span>
                      <span className="text-xs text-cyan-400 font-mono">(v{selectedModel.version})</span>
                    </h4>
                    <p className="text-slate-300 mt-1 font-sans text-xs">
                      {selectedModel.description}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-3 p-3 rounded bg-slate-950 border border-slate-800">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase block">Architecture</span>
                      <span className="text-cyan-300">{selectedModel.architecture}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase block">Deployment Status</span>
                      <span className="text-amber-300">{selectedModel.status}</span>
                    </div>
                  </div>

                  <div>
                    <span className="text-[10px] text-slate-400 uppercase block mb-1">
                      Training Data Origin Disclosure:
                    </span>
                    <p className="p-2.5 rounded bg-slate-950/60 border border-slate-800 text-slate-300 font-sans">
                      {selectedModel.training_data_disclosure}
                    </p>
                  </div>

                  <div>
                    <span className="text-[10px] text-slate-400 uppercase block mb-1">
                      Known Limitations & Boundary Constraints:
                    </span>
                    <ul className="space-y-1 list-disc list-inside text-slate-300 font-sans">
                      {selectedModel.known_limitations.map((lim, i) => (
                        <li key={i}>{lim}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <span className="text-[10px] text-slate-400 uppercase block mb-1">
                      Benchmark Scores:
                    </span>
                    <pre className="p-2.5 rounded bg-slate-950 border border-slate-800 text-cyan-300">
                      {JSON.stringify(selectedModel.metrics, null, 2)}
                    </pre>
                  </div>

                  <div className="p-3 rounded bg-amber-500/10 border border-amber-500/30 text-amber-200">
                    <span className="text-[10px] uppercase font-bold block mb-1">Mandatory Disclaimer:</span>
                    <p className="text-[11px] font-sans">{selectedModel.disclaimer}</p>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center text-slate-400 text-xs">
                  Select a model to view its governance card.
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 2: Benchmark Evaluation */}
        {activeTab === 'benchmark' && (
          <div className="p-5 overflow-y-auto max-h-[65vh] space-y-4">
            {!evalReport ? (
              <div className="py-16 text-center text-slate-400">
                <BarChart3 className="w-12 h-12 mx-auto text-slate-600 mb-2" />
                <h4 className="text-sm font-medium text-slate-200">No Benchmark Executed Yet</h4>
                <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                  Click 'Run Benchmark Harness' to execute automated verification over synthetic scenarios A through G.
                </p>
                <button
                  onClick={handleRunEvaluation}
                  disabled={isEvaluating}
                  className="mt-4 px-4 py-2 rounded bg-purple-600 hover:bg-purple-500 text-white text-xs font-medium inline-flex items-center space-x-1.5"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Run Benchmark Harness</span>
                </button>
              </div>
            ) : (
              <div className="space-y-4 font-mono text-xs">
                {/* Metrics Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                      Candidate Proposal F1
                    </span>
                    <div className="text-2xl font-bold text-cyan-400 mt-1">
                      {(evalReport.metrics.candidate_detection.f1_score * 100).toFixed(1)}%
                    </div>
                    <span className="text-[10px] text-slate-400 block mt-1">
                      Vertical MAE: {evalReport.metrics.candidate_detection.vertical_mae_metres.toFixed(3)}m
                    </span>
                  </div>

                  <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                      Anomaly Detection F1
                    </span>
                    <div className="text-2xl font-bold text-purple-400 mt-1">
                      {(evalReport.metrics.anomaly_detection.f1_score * 100).toFixed(1)}%
                    </div>
                    <span className="text-[10px] text-slate-400 block mt-1">
                      TP: {evalReport.metrics.anomaly_detection.true_positives} | FP: {evalReport.metrics.anomaly_detection.false_positives}
                    </span>
                  </div>

                  <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                      Baseline Comparison
                    </span>
                    <div className="text-2xl font-bold text-emerald-400 mt-1">
                      +{evalReport.metrics.baseline_comparison.relative_gain_percent}%
                    </div>
                    <span className="text-[10px] text-slate-400 block mt-1">
                      vs {evalReport.metrics.baseline_comparison.baseline_method}
                    </span>
                  </div>
                </div>

                {/* Scenario Results Table */}
                <div>
                  <span className="text-[10px] text-slate-400 uppercase block mb-2">
                    Evaluated Synthetic Scenarios (Scenarios A through G):
                  </span>
                  <div className="border border-slate-800 rounded-lg overflow-hidden">
                    <table className="w-full text-left">
                      <thead className="bg-slate-950 border-b border-slate-800 text-[10px] text-slate-400 uppercase">
                        <tr>
                          <th className="p-2.5">Scenario Title</th>
                          <th className="p-2.5">Candidates</th>
                          <th className="p-2.5">Detected Anomalies</th>
                          <th className="p-2.5 text-right">Outcome</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {evalReport.scenarios.map((sc: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-950/40">
                            <td className="p-2.5 font-bold text-white">{sc.title}</td>
                            <td className="p-2.5 text-slate-300">{sc.candidates_count}</td>
                            <td className="p-2.5">
                              {sc.anomalies_detected.length === 0 ? (
                                <span className="text-slate-400">None (Contiguous)</span>
                              ) : (
                                <span className="text-cyan-300">
                                  {sc.anomalies_detected.join(', ')}
                                </span>
                              )}
                            </td>
                            <td className="p-2.5 text-right">
                              {sc.passed ? (
                                <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[10px]">
                                  PASS
                                </span>
                              ) : (
                                <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/40 text-[10px]">
                                  FAIL
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Disclaimer */}
                <div className="p-3 rounded bg-slate-950 border border-slate-800 text-slate-400 text-[11px] font-sans">
                  <span className="font-bold text-slate-200">Evaluation Disclosure: </span>
                  {evalReport.disclaimer}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950/90 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium rounded bg-slate-800 hover:bg-slate-700 text-white transition"
          >
            Close Model Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
