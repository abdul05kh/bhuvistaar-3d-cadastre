import React, { useState } from 'react';
import { Download, Copy, Check, FileJson, AlertCircle } from 'lucide-react';
import { StructuredExport } from '../../types';

interface ExportCenterProps {
  exportData: StructuredExport | null;
  onRefreshExport: () => void;
  isLoading: boolean;
}

export const ExportCenter: React.FC<ExportCenterProps> = ({
  exportData,
  onRefreshExport,
  isLoading,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!exportData) return;
    navigator.clipboard.writeText(JSON.stringify(exportData, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!exportData) return;
    const jsonStr = JSON.stringify(exportData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bhuvistaar-export-${exportData.vuid.prototype_vuid}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!exportData) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <FileJson size={24} style={{ marginBottom: '8px', color: 'var(--color-primary)' }} />
        <div>No export generated yet. Click below to fetch structured export from backend.</div>
        <button className="btn btn-sm btn-primary" style={{ marginTop: '10px' }} onClick={onRefreshExport} disabled={isLoading}>
          Generate Structured Export
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Top Banner & Actions */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-main)' }}>
              Deterministic Structured Export
            </span>
            <span className="badge badge-info">{exportData.export_metadata.schema_version}</span>
            <span className="badge badge-prototype">{exportData.export_metadata.authorization_mode}</span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            VUID: <strong className="code-token" style={{ color: 'var(--color-primary)' }}>{exportData.vuid.prototype_vuid}</strong> | Revision: <strong>{exportData.spatial_unit_revision.revision_number}</strong>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-sm" onClick={handleCopy}>
            {copied ? <Check size={12} style={{ color: 'var(--color-success)' }} /> : <Copy size={12} />}
            {copied ? 'Copied' : 'Copy JSON'}
          </button>
          <button className="btn btn-sm btn-primary" onClick={handleDownload}>
            <Download size={12} />
            Download .JSON
          </button>
        </div>
      </div>

      {/* Mandatory Disclaimer */}
      <div
        style={{
          backgroundColor: 'rgba(245, 158, 11, 0.08)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          borderRadius: '4px',
          padding: '6px 10px',
          fontSize: '10px',
          color: '#fbbf24',
          marginBottom: '10px',
        }}
      >
        <AlertCircle size={11} style={{ display: 'inline', marginRight: '4px' }} />
        {exportData.export_metadata.disclaimer}
      </div>

      {/* JSON Viewer */}
      <div style={{ flex: 1, position: 'relative', minHeight: 0 }}>
        <pre
          className="code-token"
          style={{
            position: 'absolute',
            inset: 0,
            overflow: 'auto',
            backgroundColor: 'var(--bg-app)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '6px',
            padding: '12px',
            fontSize: '11px',
            lineHeight: 1.5,
            color: '#cbd5e1',
          }}
        >
          {JSON.stringify(exportData, null, 2)}
        </pre>
      </div>
    </div>
  );
};
