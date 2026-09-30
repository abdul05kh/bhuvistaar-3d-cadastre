import React, { useState, useEffect } from 'react';
import {
  Shield,
  Database,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Activity,
  Layers,
  FileCheck,
  RefreshCw,
  Server,
  Cpu
} from 'lucide-react';
import { api } from '../../api/client';
import { SystemReadinessResponse, IntegrityReport, ObservabilityMetrics } from '../../types';

interface SystemReadinessModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SystemReadinessModal: React.FC<SystemReadinessModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'categories' | 'integrity' | 'observability'>('categories');
  const [readiness, setReadiness] = useState<SystemReadinessResponse | null>(null);
  const [integrity, setIntegrity] = useState<IntegrityReport | null>(null);
  const [metrics, setMetrics] = useState<ObservabilityMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReadinessData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [readinessData, obsData] = await Promise.all([
        api.getSystemReadiness(),
        api.getObservabilityMetrics()
      ]);
      setReadiness(readinessData);
      setMetrics(obsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load system readiness.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunIntegrityCheck = async () => {
    setLoading(true);
    try {
      const report = await api.getSystemIntegrity();
      setIntegrity(report);
    } catch (err: any) {
      setError(err.message || 'Failed to run integrity checks.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchReadinessData();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.75)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      backdropFilter: 'blur(3px)'
    }}>
      <div style={{
        width: '840px',
        maxHeight: '90vh',
        backgroundColor: '#0f172a',
        border: '1px solid #334155',
        borderRadius: '10px',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid #1e293b',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#1e293b'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Server size={20} style={{ color: '#38bdf8' }} />
            <div>
              <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                System Readiness & Operational Health
              </h2>
              <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                Reproducible Deployment, Database Integrity & Interoperability Assessment
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              fontSize: '18px',
              fontWeight: 700
            }}
          >
            x
          </button>
        </div>

        {/* Tab Bar */}
        <div style={{
          display: 'flex',
          borderBottom: '1px solid #1e293b',
          backgroundColor: '#0b1329',
          padding: '0 16px'
        }}>
          <button
            onClick={() => setActiveTab('categories')}
            style={{
              padding: '10px 16px',
              background: 'transparent',
              border: 'none',
              borderBottom: activeTab === 'categories' ? '2px solid #38bdf8' : 'none',
              color: activeTab === 'categories' ? '#38bdf8' : '#94a3b8',
              fontWeight: 600,
              fontSize: '12px',
              cursor: 'pointer'
            }}
          >
            Category Matrix
          </button>
          <button
            onClick={() => {
              setActiveTab('integrity');
              if (!integrity) handleRunIntegrityCheck();
            }}
            style={{
              padding: '10px 16px',
              background: 'transparent',
              border: 'none',
              borderBottom: activeTab === 'integrity' ? '2px solid #38bdf8' : 'none',
              color: activeTab === 'integrity' ? '#38bdf8' : '#94a3b8',
              fontWeight: 600,
              fontSize: '12px',
              cursor: 'pointer'
            }}
          >
            Data Integrity Verification
          </button>
          <button
            onClick={() => setActiveTab('observability')}
            style={{
              padding: '10px 16px',
              background: 'transparent',
              border: 'none',
              borderBottom: activeTab === 'observability' ? '2px solid #38bdf8' : 'none',
              color: activeTab === 'observability' ? '#38bdf8' : '#94a3b8',
              fontWeight: 600,
              fontSize: '12px',
              cursor: 'pointer'
            }}
          >
            Observability Metrics
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '20px', overflowY: 'auto', flex: 1 }}>
          {error && (
            <div style={{
              padding: '10px',
              marginBottom: '12px',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid #ef4444',
              borderRadius: '6px',
              color: '#f87171',
              fontSize: '12px'
            }}>
              {error}
            </div>
          )}

          {/* TAB 1: CATEGORY MATRIX */}
          {activeTab === 'categories' && readiness && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{
                padding: '10px 14px',
                backgroundColor: 'rgba(56, 189, 248, 0.08)',
                border: '1px solid rgba(56, 189, 248, 0.25)',
                borderRadius: '6px',
                fontSize: '12px',
                color: '#bae6fd'
              }}>
                <strong>Honest Readiness Principle:</strong> BhuVistaar presents discrete operational category states rather than an arbitrary collapsed percentage.
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                {Object.entries(readiness.categories).map(([key, cat]) => {
                  const isOk = cat.status === 'READY' || cat.status === 'CURRENT' || cat.status === 'AVAILABLE' || cat.status === 'LOADED';
                  const isDegraded = cat.status === 'FALLBACK' || cat.status === 'PROTOTYPE';
                  return (
                    <div
                      key={key}
                      style={{
                        padding: '12px',
                        backgroundColor: '#1e293b',
                        border: '1px solid #334155',
                        borderRadius: '6px'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: '#94a3b8' }}>
                          {key.replace('_', ' ')}
                        </span>
                        <span style={{
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontSize: '10px',
                          fontWeight: 700,
                          backgroundColor: isOk ? 'rgba(34, 197, 94, 0.15)' : (isDegraded ? 'rgba(234, 179, 8, 0.15)' : 'rgba(239, 68, 68, 0.15)'),
                          color: isOk ? '#4ade80' : (isDegraded ? '#facc15' : '#f87171')
                        }}>
                          {cat.status}
                        </span>
                      </div>
                      <div style={{ fontSize: '11px', color: '#cbd5e1', lineHeight: '1.4' }}>
                        {cat.notes || cat.version || `${cat.parcels || 0} parcels, ${cat.units || 0} units`}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Role Context */}
              <div style={{
                marginTop: '10px',
                padding: '12px',
                backgroundColor: '#0c162c',
                border: '1px solid #1e293b',
                borderRadius: '6px'
              }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#38bdf8', marginBottom: '4px' }}>
                  ROLE AUTHORIZATION CONTEXT ({readiness.role_context.authorization_mode})
                </div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>
                  {readiness.role_context.disclaimer} Available simulated roles: {readiness.role_context.available_roles.join(', ')}.
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: DATA INTEGRITY */}
          {activeTab === 'integrity' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                    Deterministic Integrity Checks
                  </h3>
                  <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                    Non-destructive validation of orphans, geometry validity, provenance & stale records
                  </span>
                </div>
                <button
                  className="btn btn-sm btn-primary"
                  onClick={handleRunIntegrityCheck}
                  disabled={loading}
                >
                  <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                  Re-run Integrity Checks
                </button>
              </div>

              {integrity && (
                <div>
                  <div style={{
                    padding: '12px',
                    borderRadius: '6px',
                    marginBottom: '14px',
                    backgroundColor: integrity.status === 'PASS' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    border: `1px solid ${integrity.status === 'PASS' ? '#22c55e' : '#ef4444'}`,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px'
                  }}>
                    {integrity.status === 'PASS' ? (
                      <CheckCircle size={18} style={{ color: '#22c55e' }} />
                    ) : (
                      <AlertTriangle size={18} style={{ color: '#ef4444' }} />
                    )}
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '13px', color: '#f8fafc' }}>
                        Integrity Status: {integrity.status}
                      </div>
                      <div style={{ fontSize: '11px', color: '#cbd5e1' }}>
                        {integrity.summary.total_issues} issues found ({integrity.summary.blockers} blockers, {integrity.summary.warnings} warnings) across {integrity.summary.checks_performed.length} structural checks.
                      </div>
                    </div>
                  </div>

                  {integrity.issues.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '24px', color: '#94a3b8', fontSize: '12px' }}>
                      All data integrity checks passed. Zero orphan records, zero geometry corruptions.
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {integrity.issues.map((iss, i) => (
                        <div
                          key={i}
                          style={{
                            padding: '8px 12px',
                            backgroundColor: '#1e293b',
                            borderRadius: '5px',
                            borderLeft: `3px solid ${iss.severity === 'BLOCKER' ? '#ef4444' : '#f59e0b'}`,
                            fontSize: '11px'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <span style={{ fontWeight: 700, color: '#f8fafc' }}>{iss.check}</span>
                            <span style={{ color: iss.severity === 'BLOCKER' ? '#f87171' : '#fbbf24', fontWeight: 600 }}>
                              {iss.severity}
                            </span>
                          </div>
                          <div style={{ color: '#94a3b8' }}>{iss.description}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: OBSERVABILITY */}
          {activeTab === 'observability' && metrics && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                Operational Observability Counters
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
                {Object.entries(metrics.metrics).map(([key, val]) => (
                  <div
                    key={key}
                    style={{
                      padding: '12px',
                      backgroundColor: '#1e293b',
                      borderRadius: '6px',
                      border: '1px solid #334155'
                    }}
                  >
                    <div style={{ fontSize: '10px', textTransform: 'uppercase', color: '#94a3b8', marginBottom: '4px' }}>
                      {key.replace('_', ' ')}
                    </div>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: '#38bdf8' }}>
                      {val}
                    </div>
                  </div>
                ))}
              </div>

              <div style={{
                padding: '12px',
                backgroundColor: '#0c162c',
                border: '1px solid #1e293b',
                borderRadius: '6px',
                fontSize: '11px',
                color: '#cbd5e1'
              }}>
                <div><strong>Environment:</strong> {metrics.system.environment}</div>
                <div><strong>AI Mode:</strong> {metrics.system.ai_mode}</div>
                <div><strong>Security / Actor Mode:</strong> {metrics.system.authorization_mode}</div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '12px 20px',
          borderTop: '1px solid #1e293b',
          backgroundColor: '#1e293b',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '10px'
        }}>
          <button className="btn btn-sm" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
