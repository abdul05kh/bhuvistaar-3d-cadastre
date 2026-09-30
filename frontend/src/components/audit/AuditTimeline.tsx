import React from 'react';
import { History, Shield, Clock, ArrowRight, UserCheck } from 'lucide-react';
import { AuditEvent } from '../../types';

interface AuditTimelineProps {
  events: AuditEvent[];
}

export const AuditTimeline: React.FC<AuditTimelineProps> = ({ events }) => {
  return (
    <div style={{ padding: '16px', overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div>
          <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-main)' }}>
            Append-Only Audit Ledger
          </span>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Immutable chronological record of all state transitions and governance decisions
          </div>
        </div>
        <span className="badge badge-prototype">
          <Shield size={12} />
          {events.length} EVENTS RECORDED
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {events.map((evt, idx) => (
          <div
            key={evt.id || idx}
            className="card"
            style={{
              padding: '10px 14px',
              borderLeft: '3px solid var(--color-primary)',
              display: 'flex',
              flexDirection: 'column',
              gap: '4px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="code-token" style={{ fontWeight: 700, color: 'var(--text-main)', fontSize: '12px' }}>
                  {evt.action}
                </span>
                <span className="badge badge-info" style={{ fontSize: '10px' }}>
                  {evt.entity_type}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                <Clock size={12} />
                <span>{new Date(evt.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-secondary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <UserCheck size={12} style={{ color: 'var(--color-primary)' }} />
                <span>Actor: <strong>{evt.actor_id}</strong></span>
                <span className="badge badge-prototype" style={{ fontSize: '9px' }}>
                  {evt.authorization_mode}
                </span>
              </div>

              {evt.new_state && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{evt.previous_state || 'null'}</span>
                  <ArrowRight size={10} />
                  <span className="badge badge-success" style={{ fontSize: '10px' }}>
                    {evt.new_state}
                  </span>
                </div>
              )}
            </div>

            {evt.reason && (
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px', fontStyle: 'italic' }}>
                "{evt.reason}"
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
