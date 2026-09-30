import React, { useState, useEffect } from 'react';
import { ModelComparisonResponse } from '../../types';
import { api } from '../../api/client';
import { GitCompare, AlertCircle, RefreshCw, X, ArrowRightLeft } from 'lucide-react';

interface ModelComparisonModalProps {
  parentUlpin: string;
  onClose: () => void;
}

export const ModelComparisonModal: React.FC<ModelComparisonModalProps> = ({ parentUlpin, onClose }) => {
  const [data, setData] = useState<ModelComparisonResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadComparison();
  }, [parentUlpin]);

  const loadComparison = async () => {
    setIsLoading(true);
    try {
      const res = await api.compareModels(
        'prismatic-candidate-001',
        'cadastral-heuristic-baseline-001',
        parentUlpin
      );
      setData(res);
    } catch (err: any) {
      console.error('Failed to load model comparison', err);
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
          width: '820px',
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
            <ArrowRightLeft size={20} className="text-cyan-400" />
            <div>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>
                Empirical Model & Baseline Comparison (Slice 4)
              </h3>
              <p style={{ margin: '2px 0 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Side-by-side behavioral comparison on parcel {parentUlpin}
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
              <p>Computing empirical comparison metrics...</p>
            </div>
          ) : data ? (
            <>
              {/* Disclosure Alert */}
              <div
                style={{
                  backgroundColor: 'rgba(56, 189, 248, 0.08)',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  borderRadius: '6px',
                  padding: '10px 14px',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                }}
              >
                <AlertCircle size={18} className="text-cyan-400" style={{ marginTop: '2px', flexShrink: 0 }} />
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.45 }}>
                  <strong style={{ color: 'var(--text-main)' }}>Mandatory Disclosure:</strong> {data.limitations_disclaimer}
                </div>
              </div>

              {/* Models Comparison Banner */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr auto 1fr',
                  gap: '12px',
                  alignItems: 'center',
                }}
              >
                {/* Model A */}
                <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <span className="badge badge-info" style={{ fontSize: '0.7rem', marginBottom: '6px' }}>MODEL A</span>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
                    {data.model_a?.name || 'Prismatic Candidate Generator'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Version: {data.model_a?.version || '0.1.0'}
                  </div>
                </div>

                {/* VS Badge */}
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)' }}>
                  VS
                </div>

                {/* Model B */}
                <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <span className="badge badge-neutral" style={{ fontSize: '0.7rem', marginBottom: '6px' }}>MODEL B (BASELINE)</span>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
                    {data.model_b?.name || 'Cadastral Heuristic Baseline'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Version: {data.model_b?.version || '0.0.1-baseline'}
                  </div>
                </div>
              </div>

              {/* Metrics Table */}
              <div style={{ border: '1px solid var(--border-subtle)', borderRadius: '6px', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem' }}>
                  <thead>
                    <tr style={{ backgroundColor: 'rgba(15, 23, 42, 0.8)', borderBottom: '1px solid var(--border-subtle)', textAlign: 'left' }}>
                      <th style={{ padding: '8px 12px', color: 'var(--text-muted)' }}>Evaluated Metric</th>
                      <th style={{ padding: '8px 12px', color: 'var(--text-muted)' }}>Model A</th>
                      <th style={{ padding: '8px 12px', color: 'var(--text-muted)' }}>Model B (Baseline)</th>
                      <th style={{ padding: '8px 12px', color: 'var(--text-muted)' }}>Observed Delta & Behavior</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.metrics.map((m, idx) => (
                      <tr
                        key={idx}
                        style={{
                          borderBottom: '1px solid var(--border-subtle)',
                          backgroundColor: idx % 2 === 0 ? 'rgba(30, 41, 59, 0.3)' : 'transparent',
                        }}
                      >
                        <td style={{ padding: '10px 12px', fontWeight: 600, color: 'var(--text-main)' }}>{m.metric_name}</td>
                        <td style={{ padding: '10px 12px', color: '#38bdf8', fontFamily: 'monospace' }}>{String(m.model_a_value)}</td>
                        <td style={{ padding: '10px 12px', color: '#94a3b8', fontFamily: 'monospace' }}>{String(m.model_b_value)}</td>
                        <td style={{ padding: '10px 12px', color: 'var(--text-muted)', lineHeight: 1.4 }}>{m.observation}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Summary Notes */}
              <div
                style={{
                  backgroundColor: 'rgba(15, 23, 42, 0.5)',
                  padding: '12px',
                  borderRadius: '6px',
                  fontSize: '0.78rem',
                  color: 'var(--text-main)',
                  lineHeight: 1.5,
                }}
              >
                {data.summary_notes}
              </div>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
              Comparison data unavailable.
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
