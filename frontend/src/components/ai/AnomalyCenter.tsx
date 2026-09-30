import React from 'react';
import { AlertTriangle, AlertOctagon, Info, ArrowRight, ShieldCheck, Wrench } from 'lucide-react';
import { AIAnomaly } from '../../types';

interface AnomalyCenterProps {
  anomalies: AIAnomaly[];
  onInspectUnit: (levelCode: string) => void;
  onRequestCorrection?: (levelCode: string) => void;
}

export const AnomalyCenter: React.FC<AnomalyCenterProps> = ({
  anomalies,
  onInspectUnit,
  onRequestCorrection,
}) => {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>AI Cadastral Anomaly & Discrepancy Center</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Automated scanning of vertical strata overlaps, inter-floor gaps, missing sequences, and multi-source discrepancies.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/40">
            {anomalies.filter((a) => a.severity === 'BLOCKER').length} Blockers
          </span>
          <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
            {anomalies.filter((a) => a.severity === 'WARNING' || (a.severity as string) === 'WARN').length} Warnings
          </span>
        </div>
      </div>

      {/* Anomalies List */}
      {anomalies.length === 0 ? (
        <div className="bg-slate-900/40 border border-slate-800 rounded-lg p-8 text-center text-slate-400">
          <ShieldCheck className="w-10 h-10 mx-auto text-emerald-500 mb-2" />
          <h4 className="text-sm font-medium text-slate-200">Zero Anomalies Detected</h4>
          <p className="text-xs text-slate-400 mt-1">
            All floor strata boundaries, parcel limits, and evidence alignments satisfy topological consistency.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {anomalies.map((anom) => {
            const isBlocker = anom.severity === 'BLOCKER';
            return (
              <div
                key={anom.anomaly_id}
                className={`border rounded-lg p-4 transition ${
                  isBlocker
                    ? 'bg-red-950/20 border-red-500/50 shadow-lg shadow-red-950/20'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div
                      className={`p-2 rounded-lg mt-0.5 ${
                        isBlocker ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
                      }`}
                    >
                      {isBlocker ? (
                        <AlertOctagon className="w-5 h-5" />
                      ) : (
                        <AlertTriangle className="w-5 h-5" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-bold text-white tracking-wide">
                          {anom.anomaly_type.replace(/_/g, ' ')}
                        </span>
                        <span
                          className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase tracking-wider font-semibold ${
                            isBlocker
                              ? 'bg-red-500/20 text-red-300 border-red-500/40'
                              : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                          }`}
                        >
                          {anom.severity}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 font-mono mt-0.5">
                        ID: {anom.anomaly_id} | Detected by {anom.model.name} (v{anom.model.version})
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 uppercase font-mono block">Affected Units</span>
                    <div className="flex items-center space-x-1 mt-0.5">
                      {anom.affected_units.map((u) => (
                        <span
                          key={u}
                          className="px-2 py-0.5 text-xs font-mono font-bold rounded bg-slate-800 text-cyan-300 border border-slate-700"
                        >
                          {u}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Recommended Review Action */}
                <div className="mt-3 p-3 rounded bg-slate-950/80 border border-slate-800 text-xs font-mono">
                  <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1 flex items-center space-x-1">
                    <Info className="w-3 h-3 text-cyan-400" />
                    <span>Recommended Review Action:</span>
                  </div>
                  <div className={isBlocker ? 'text-red-200' : 'text-slate-300'}>
                    {anom.recommended_action}
                  </div>
                </div>

                {/* Footer with Reasons & Buttons */}
                <div className="mt-3 flex items-center justify-between pt-2">
                  <div className="flex items-center space-x-1.5">
                    {anom.reason_codes.map((r, i) => (
                      <span
                        key={i}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60"
                      >
                        {r.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center space-x-2">
                    {anom.affected_units.length > 0 && (
                      <button
                        onClick={() => onInspectUnit(anom.affected_units[0])}
                        className="px-3 py-1 text-xs font-medium rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-500/30 flex items-center space-x-1"
                      >
                        <span>Inspect in 3D</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
