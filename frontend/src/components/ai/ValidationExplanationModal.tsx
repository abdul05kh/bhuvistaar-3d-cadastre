import React, { useState, useEffect } from 'react';
import { ValidationExplanationResponse, ValidationExplanationItem } from '../../types';
import { api } from '../../api/client';
import { AlertTriangle, CheckCircle, HelpCircle, X, RefreshCw, ShieldAlert, ArrowDownUp } from 'lucide-react';

interface ValidationExplanationModalProps {
  runId: string;
  onClose: () => void;
}

export const ValidationExplanationModal: React.FC<ValidationExplanationModalProps> = ({ runId, onClose }) => {
  const [data, setData] = useState<ValidationExplanationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadExplanation();
  }, [runId]);

  const loadExplanation = async () => {
    setIsLoading(true);
    try {
      const res = await api.explainValidationRun(runId);
      setData(res);
    } catch (err: any) {
      console.error('Failed to load validation explanation', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        backdropFilter: 'blur(4px)',
      }}
    >
      <div
        style={{
          backgroundColor: 'var(--bg-panel)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '8px',
          width: '780px',
          maxWidth: '92vw',
          maxHeight: '88vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '16px 20px',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: 'rgba(15, 23, 42, 0.8)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <HelpCircle size={20} className="text-cyan-400" />
            <div>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>
                Validation Intelligence & Rule Breakdown (Slice 4)
              </h3>
              <p style={{ margin: '2px 0 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Deterministic Gate A & B Execution Breakdown • Run ID: <span style={{ fontFamily: 'monospace' }}>{runId?.slice(0, 8)}...</span>
              </p>
            </div>
          </div>
          <button className="btn btn-sm btn-icon" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '20px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              <RefreshCw className="animate-spin" size={24} style={{ margin: '0 auto 8px auto' }} />
              <p>Synthesizing validation explanations...</p>
            </div>
          ) : data ? (
            <>
              {/* Summary Strip */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  backgroundColor: data.blocker_count > 0 ? 'rgba(239, 68, 68, 0.08)' : 'rgba(16, 185, 129, 0.08)',
                  border: `1px solid ${data.blocker_count > 0 ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
                  padding: '10px 14px',
                  borderRadius: '6px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {data.blocker_count > 0 ? (
                    <ShieldAlert size={18} className="text-red-400" />
                  ) : (
                    <CheckCircle size={18} className="text-emerald-400" />
                  )}
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
                    {data.blocker_count > 0
                      ? `${data.blocker_count} Blocker(s) Preventing Approval`
                      : 'All Deterministic Rules Passed Cleanly'}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '8px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  <span>Validator: v{data.validator_version}</span>
                  <span>•</span>
                  <span>Ruleset: v{data.ruleset_version}</span>
                  <span>•</span>
                  <span>Evaluated: {data.rules_evaluated} rules</span>
                </div>
              </div>

              {/* Explanations List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {data.explanations && data.explanations.length > 0 ? (
                  data.explanations.map((exp, idx) => (
                    <div
                      key={idx}
                      style={{
                        backgroundColor: exp.severity === 'BLOCKER' ? 'rgba(239, 68, 68, 0.06)' : 'rgba(30, 41, 59, 0.5)',
                        border: `1px solid ${exp.severity === 'BLOCKER' ? 'rgba(239, 68, 68, 0.25)' : 'var(--border-subtle)'}`,
                        borderRadius: '6px',
                        padding: '12px 14px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '6px',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span className={`badge ${exp.severity === 'BLOCKER' ? 'badge-error' : exp.severity === 'WARN' ? 'badge-warning' : 'badge-neutral'}`}>
                            {exp.rule_code}
                          </span>
                          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)' }}>
                            {exp.rule_family} (v{exp.rule_version})
                          </span>
                        </div>
                        <span className={`badge ${exp.severity === 'BLOCKER' ? 'badge-error' : 'badge-success'}`} style={{ fontSize: '0.7rem' }}>
                          {exp.severity}
                        </span>
                      </div>

                      {/* Detailed Explanation */}
                      <p style={{ margin: '4px 0 0 0', fontSize: '0.78rem', color: 'var(--text-main)', lineHeight: 1.45 }}>
                        {exp.detailed_explanation}
                      </p>

                      {/* Measured Values vs Threshold Breakdown */}
                      {exp.measured_values && (
                        <div
                          style={{
                            backgroundColor: 'rgba(15, 23, 42, 0.6)',
                            padding: '8px 10px',
                            borderRadius: '4px',
                            fontSize: '0.72rem',
                            fontFamily: 'monospace',
                            color: 'var(--text-muted)',
                            display: 'flex',
                            gap: '16px',
                            flexWrap: 'wrap',
                          }}
                        >
                          <div><strong>Measured:</strong> {JSON.stringify(exp.measured_values)}</div>
                          {exp.thresholds && <div><strong>Threshold:</strong> {JSON.stringify(exp.thresholds)}</div>}
                        </div>
                      )}

                      {/* Remediation & Implication */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px', fontSize: '0.72rem' }}>
                        <span style={{ color: 'var(--text-muted)' }}>
                          <strong>Action:</strong> {exp.suggested_action}
                        </span>
                        <span style={{ fontWeight: 600, color: exp.severity === 'BLOCKER' ? '#f87171' : '#34d399' }}>
                          {exp.governance_implication}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                    No rule issues found for this run.
                  </div>
                )}
              </div>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
              Validation explanation unavailable.
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: '12px 20px',
            borderTop: '1px solid var(--border-subtle)',
            display: 'flex',
            justifyContent: 'flex-end',
            backgroundColor: 'rgba(15, 23, 42, 0.8)',
          }}
        >
          <button className="btn btn-sm" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
