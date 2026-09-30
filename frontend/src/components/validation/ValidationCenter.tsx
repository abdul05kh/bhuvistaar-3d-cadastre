import React, { useState } from 'react';
import { AlertCircle, CheckCircle, AlertTriangle, Eye, Edit3, Filter } from 'lucide-react';
import { ValidationSummary, ValidationIssue } from '../../types';

interface ValidationCenterProps {
  summary: ValidationSummary | null;
  onInspectUnit: (levelCode: string) => void;
  onRequestCorrection: (levelCode: string) => void;
}

export const ValidationCenter: React.FC<ValidationCenterProps> = ({
  summary,
  onInspectUnit,
  onRequestCorrection,
}) => {
  const [filterSeverity, setFilterSeverity] = useState<'ALL' | 'BLOCKER' | 'FAILED'>('ALL');

  if (!summary) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
        No validation run executed yet. Ingest a parcel and run validation.
      </div>
    );
  }

  const issues = summary.issues || [];
  const filteredIssues = issues.filter((i) => {
    if (filterSeverity === 'BLOCKER') return i.severity === 'BLOCKER' && !i.passed;
    if (filterSeverity === 'FAILED') return !i.passed;
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header Metrics */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 16px',
          borderBottom: '1px solid var(--border-subtle)',
          backgroundColor: 'rgba(14, 23, 38, 0.5)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Rules Evaluated: </span>
            <span style={{ fontWeight: 600 }}>{summary.rules_evaluated}</span>
          </div>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Passed: </span>
            <span style={{ fontWeight: 600, color: 'var(--color-success)' }}>{summary.passed_rules}</span>
          </div>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Blockers: </span>
            <span style={{ fontWeight: 600, color: summary.blocker_count > 0 ? 'var(--color-blocker)' : 'inherit' }}>
              {summary.blocker_count}
            </span>
          </div>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Gate C Status: </span>
            <span
              className={`badge ${summary.can_approve ? 'badge-success' : 'badge-blocker'}`}
              style={{ fontSize: '10px' }}
            >
              {summary.can_approve ? 'ELIGIBLE' : 'BLOCKED'}
            </span>
          </div>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Filter size={12} style={{ color: 'var(--text-muted)' }} />
          <button
            className={`btn btn-sm ${filterSeverity === 'ALL' ? 'btn-primary' : ''}`}
            onClick={() => setFilterSeverity('ALL')}
          >
            All ({issues.length})
          </button>
          <button
            className={`btn btn-sm ${filterSeverity === 'FAILED' ? 'btn-primary' : ''}`}
            onClick={() => setFilterSeverity('FAILED')}
          >
            Failed ({summary.failed_rules})
          </button>
          <button
            className={`btn btn-sm ${filterSeverity === 'BLOCKER' ? 'btn-danger' : ''}`}
            onClick={() => setFilterSeverity('BLOCKER')}
          >
            Blockers ({summary.blocker_count})
          </button>
        </div>
      </div>

      {/* Issues List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 16px' }}>
        {filteredIssues.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '30px', color: 'var(--color-success)' }}>
            <CheckCircle size={24} style={{ marginBottom: '6px' }} />
            <div>No matching validation issues found. All evaluated rules conform to spatial contracts.</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {filteredIssues.map((issue) => {
              const isBlocker = issue.severity === 'BLOCKER' && !issue.passed;
              const isFailed = !issue.passed;

              // Extract levels if VRT-003
              let affectedLevel = 'L01';
              if (issue.measured_value && issue.measured_value.lower_level) {
                affectedLevel = issue.measured_value.lower_level;
              }

              return (
                <div
                  key={issue.id}
                  className="card"
                  style={{
                    borderLeft: isBlocker
                      ? '4px solid var(--color-blocker)'
                      : isFailed
                      ? '4px solid var(--color-warning)'
                      : '4px solid var(--color-success)',
                    padding: '10px 14px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="code-token" style={{ fontWeight: 700, fontSize: '12px' }}>
                        {issue.rule_code}
                      </span>
                      <span
                        className={`badge ${
                          isBlocker ? 'badge-blocker' : isFailed ? 'badge-warning' : 'badge-success'
                        }`}
                      >
                        {issue.passed ? 'PASSED' : issue.severity}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {isBlocker && (
                        <button
                          className="btn btn-sm btn-warning"
                          onClick={() => onRequestCorrection(affectedLevel)}
                        >
                          <Edit3 size={11} />
                          Request Correction
                        </button>
                      )}
                      <button
                        className="btn btn-sm"
                        onClick={() => onInspectUnit(affectedLevel)}
                      >
                        <Eye size={11} />
                        Inspect in 3D
                      </button>
                    </div>
                  </div>

                  <div style={{ fontSize: '12px', color: 'var(--text-main)', marginBottom: '4px' }}>
                    {issue.message}
                  </div>

                  {issue.measured_value && (
                    <div
                      style={{
                        backgroundColor: 'var(--bg-app)',
                        padding: '6px 10px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        display: 'flex',
                        gap: '16px',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      {issue.measured_value.overlap_m !== undefined && (
                        <span>
                          Overlap: <strong style={{ color: 'var(--color-blocker)' }}>{issue.measured_value.overlap_m} m</strong>
                        </span>
                      )}
                      {issue.measured_value.gap_m !== undefined && (
                        <span>
                          Vertical Gap: <strong style={{ color: 'var(--color-blocker)' }}>{issue.measured_value.gap_m} m</strong>
                        </span>
                      )}
                      {issue.suggested_action && (
                        <span>Action: {issue.suggested_action}</span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
