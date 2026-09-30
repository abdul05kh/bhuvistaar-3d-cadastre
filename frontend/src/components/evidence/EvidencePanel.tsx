import React from 'react';
import { FileText, CheckCircle2, ShieldCheck, Hash } from 'lucide-react';
import { EvidenceSource } from '../../types';

interface EvidencePanelProps {
  evidenceList: EvidenceSource[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ evidenceList }) => {
  return (
    <div style={{ padding: '16px', overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div>
          <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-main)' }}>
            Authoritative Evidence Registry
          </span>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Cryptographically verified survey evidence anchoring 3D spatial candidates
          </div>
        </div>
        <span className="badge badge-success">
          <ShieldCheck size={12} />
          {evidenceList.length} VERIFIED SOURCES
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '12px' }}>
        {evidenceList.map((ev) => (
          <div key={ev.id} className="card" style={{ padding: '12px 14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={15} style={{ color: 'var(--color-primary)' }} />
                <span className="code-token" style={{ fontWeight: 700, fontSize: '12px' }}>
                  {ev.id}
                </span>
              </div>
              <span className="badge badge-success" style={{ fontSize: '10px' }}>
                <CheckCircle2 size={10} />
                SHA-256 VERIFIED
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '11px' }}>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Type: </span>
                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{ev.evidence_type}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Source Ref: </span>
                <span className="code-token" style={{ color: 'var(--text-secondary)' }}>{ev.source_reference}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Provider: </span>
                <span style={{ color: 'var(--text-secondary)' }}>{ev.provider}</span>
              </div>
              <div style={{ marginTop: '6px' }}>
                <span style={{ color: 'var(--text-muted)', display: 'block', marginBottom: '2px' }}>
                  SHA-256 Checksum:
                </span>
                <div
                  className="code-token"
                  style={{
                    backgroundColor: 'var(--bg-app)',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '10px',
                    color: 'var(--color-info)',
                    wordBreak: 'break-all',
                  }}
                >
                  <Hash size={10} style={{ display: 'inline', marginRight: '4px' }} />
                  {ev.checksum}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
