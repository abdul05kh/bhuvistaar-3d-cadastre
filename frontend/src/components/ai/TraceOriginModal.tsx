import React, { useEffect, useState } from 'react';
import {
  X,
  GitBranch,
  FileText,
  Eye,
  Brain,
  CheckCircle,
  ShieldCheck,
  UserCheck,
  Layers,
  Award,
  Download,
  Clock,
  User,
  Hash,
  ChevronRight
} from 'lucide-react';
import { api } from '../../api/client';
import { TraceOriginResponse, TraceOriginNode } from '../../types';

interface TraceOriginModalProps {
  identifier: string;
  isOpen: boolean;
  onClose: () => void;
}

export const TraceOriginModal: React.FC<TraceOriginModalProps> = ({
  identifier,
  isOpen,
  onClose,
}) => {
  const [lineage, setLineage] = useState<TraceOriginResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<TraceOriginNode | null>(null);

  useEffect(() => {
    if (!isOpen || !identifier) return;
    const fetchLineage = async () => {
      setIsLoading(true);
      try {
        const data = await api.traceOrigin(identifier);
        setLineage(data);
        if (data.lineage_path && data.lineage_path.length > 0) {
          setSelectedNode(data.lineage_path[data.lineage_path.length - 1]);
        }
      } catch (err) {
        console.error('Failed to load trace origin:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchLineage();
  }, [isOpen, identifier]);

  if (!isOpen) return null;

  const getStageIcon = (stage: string) => {
    switch (stage) {
      case 'EVIDENCE':
        return <FileText className="w-4 h-4 text-amber-400" />;
      case 'AI_OBSERVATION':
        return <Eye className="w-4 h-4 text-cyan-400" />;
      case 'INFERENCE_RUN':
      case 'AI_CANDIDATE':
        return <Brain className="w-4 h-4 text-purple-400" />;
      case 'DETERMINISTIC_VALIDATION':
        return <ShieldCheck className="w-4 h-4 text-blue-400" />;
      case 'HUMAN_REVIEW':
        return <UserCheck className="w-4 h-4 text-emerald-400" />;
      case 'GOVERNED_REVISION':
        return <Layers className="w-4 h-4 text-indigo-400" />;
      case 'GATE_C_APPROVAL':
        return <Award className="w-4 h-4 text-emerald-400" />;
      case 'EXPORT':
        return <Download className="w-4 h-4 text-sky-400" />;
      default:
        return <CheckCircle className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/80">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <GitBranch className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white tracking-wide">
                  End-to-End Cadastral Data Lineage (Trace Origin)
                </h3>
                <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  AUTHORITATIVE AUDIT GRAPH
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Target: {identifier} | Parent ULPIN: {lineage?.parent_ulpin || '...'}
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

        {/* Modal Content */}
        <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-slate-800">
          {/* Left Column: Timeline Steps */}
          <div className="md:col-span-2 p-5 overflow-y-auto max-h-[70vh] space-y-4">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center justify-between">
              <span>Lifecycle Traversal Path</span>
              <span className="text-[10px] font-mono text-cyan-400">
                {lineage?.lineage_path.length || 0} Stages Recorded
              </span>
            </div>

            {isLoading ? (
              <div className="py-12 text-center text-slate-400 font-mono text-xs">
                Traversing cryptographic provenance and governance tree...
              </div>
            ) : !lineage || lineage.lineage_path.length === 0 ? (
              <div className="py-12 text-center text-slate-400 font-mono text-xs">
                No lineage records found for {identifier}
              </div>
            ) : (
              <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
                {lineage.lineage_path.map((node) => {
                  const isCurrentSelected = selectedNode?.identifier === node.identifier && selectedNode?.stage === node.stage;
                  return (
                    <div
                      key={node.step + node.identifier}
                      onClick={() => setSelectedNode(node)}
                      className={`relative p-3 rounded-lg border cursor-pointer transition ${
                        isCurrentSelected
                          ? 'bg-purple-950/20 border-purple-500/60 ring-1 ring-purple-500/30'
                          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      {/* Step Indicator Dot */}
                      <div className="absolute -left-[27px] top-4 w-5 h-5 rounded-full bg-slate-900 border-2 border-purple-500 flex items-center justify-center text-[10px] font-mono text-purple-300 font-bold">
                        {node.step}
                      </div>

                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-2">
                          {getStageIcon(node.stage)}
                          <span className="text-xs font-bold text-white tracking-wide">
                            {node.title}
                          </span>
                        </div>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                          {node.status}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 mt-2 text-[11px] font-mono text-slate-400">
                        <div className="flex items-center space-x-1 truncate">
                          <User className="w-3 h-3 text-slate-400 flex-shrink-0" />
                          <span className="truncate">{node.actor}</span>
                        </div>
                        {node.timestamp && (
                          <div className="flex items-center space-x-1 justify-end text-slate-400 truncate">
                            <Clock className="w-3 h-3 text-slate-400 flex-shrink-0" />
                            <span className="truncate">{new Date(node.timestamp).toLocaleTimeString()}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Right Column: Node Details Inspector */}
          <div className="p-5 overflow-y-auto max-h-[70vh] bg-slate-950/40">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
              Stage Artifact Details
            </div>

            {selectedNode ? (
              <div className="space-y-4">
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
                  <div className="text-xs font-bold text-white flex items-center space-x-2">
                    {getStageIcon(selectedNode.stage)}
                    <span>{selectedNode.title}</span>
                  </div>
                  <div className="text-xs text-slate-400 font-mono">
                    ID: <span className="text-slate-200">{selectedNode.identifier}</span>
                  </div>
                  <div className="text-xs text-slate-400 font-mono">
                    Stage: <span className="text-purple-300 font-bold">{selectedNode.stage}</span>
                  </div>
                  <div className="text-xs text-slate-400 font-mono">
                    Responsible Actor: <span className="text-cyan-300">{selectedNode.actor}</span>
                  </div>
                  {selectedNode.timestamp && (
                    <div className="text-xs text-slate-400 font-mono">
                      Timestamp: <span className="text-slate-200">{new Date(selectedNode.timestamp).toLocaleString()}</span>
                    </div>
                  )}
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-mono block mb-1">
                    Structured Node Metadata:
                  </span>
                  <pre className="p-3 rounded bg-slate-950 border border-slate-800 text-[11px] font-mono text-cyan-300 overflow-x-auto max-h-60">
                    {JSON.stringify(selectedNode.details, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-400 text-xs font-mono">
                Select a stage node from the traversal graph to inspect metadata.
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950/90 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center space-x-2 font-mono">
            <span className="text-slate-400">Governance Status:</span>
            <span className={`px-2 py-0.5 rounded font-bold ${lineage?.is_authoritative ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30'}`}>
              {lineage?.is_authoritative ? 'AUTHORITATIVE APPROVED' : 'PROTOTYPE CANDIDATE'}
            </span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium rounded bg-slate-800 hover:bg-slate-700 text-white transition"
          >
            Close Lineage
          </button>
        </div>
      </div>
    </div>
  );
};
