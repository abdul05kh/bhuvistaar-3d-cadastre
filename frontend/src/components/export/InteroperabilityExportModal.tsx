import React, { useState } from 'react';
import { Download, Copy, CheckCircle, FileText, Globe, Box, ShieldCheck, AlertCircle } from 'lucide-react';
import { api } from '../../api/client';
import { StructuredExport, RoundTripVerificationResult } from '../../types';

interface InteroperabilityExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  exportData: StructuredExport | null;
  ulpin: string;
  revisionId: string;
}

export const InteroperabilityExportModal: React.FC<InteroperabilityExportModalProps> = ({
  isOpen,
  onClose,
  exportData,
  ulpin,
  revisionId
}) => {
  const [activeTab, setActiveTab] = useState<'json' | 'geojson' | 'obj' | 'roundtrip'>('json');
  const [geoJsonData, setGeoJsonData] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [roundTripResult, setRoundTripResult] = useState<RoundTripVerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !exportData) return null;

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const fetchGeoJson = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.exportGeoJson(ulpin);
      setGeoJsonData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch GeoJSON.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadObj = () => {
    window.open(`/api/v1/export/3d/${revisionId}`, '_blank');
  };

  const handleRunRoundTrip = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.verifyExportRoundtrip(exportData);
      setRoundTripResult(result);
    } catch (err: any) {
      setError(err.message || 'Roundtrip verification failed.');
    } finally {
      setLoading(false);
    }
  };

  const jsonString = JSON.stringify(exportData, null, 2);

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
          <div>
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
              Interoperability Export & Verification
            </h2>
            <span style={{ fontSize: '11px', color: '#94a3b8' }}>
              Standard Structured Formats: JSON (v1.0.0), 2D GeoJSON & 3D Wavefront OBJ
            </span>
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

        {/* Disclaimer Banner */}
        <div style={{
          padding: '10px 18px',
          backgroundColor: '#1e1b4b',
          borderBottom: '1px solid #3730a3',
          fontSize: '11px',
          color: '#c7d2fe',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <ShieldCheck size={14} style={{ color: '#818cf8', flexShrink: 0 }} />
          <span>
            <strong>Mandatory Prototype Notice:</strong> Prototype VUID is NOT an official 3D ULPIN. Does not constitute legal title adjudication.
          </span>
        </div>

        {/* Tab Bar */}
        <div style={{
          display: 'flex',
          borderBottom: '1px solid #1e293b',
          backgroundColor: '#0b1329',
          padding: '0 16px'
        }}>
          <button
            onClick={() => setActiveTab('json')}
            style={{
              padding: '10px 16px',
              background: 'transparent',
              border: 'none',
              borderBottom: activeTab === 'json' ? '2px solid #38bdf8' : 'none',
              color: activeTab === 'json' ? '#38bdf8' : '#94a3b8',
              fontWeight: 600,
              fontSize: '12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <FileText size={14} />
            Structured JSON
          </button>
          <button
            onClick={() => {
              setActiveTab('geojson');
              if (!geoJsonData) fetchGeoJson();
            }}
            style={{
              padding: '10px 16px',
              background: 'transparent',
              border: 'none',
              borderBottom: activeTab === 'geojson' ? '2px solid #38bdf8' : 'none',
              color: activeTab === 'geojson' ? '#38bdf8' : '#94a3b8',
              fontWeight: 600,
              fontSize: '12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Globe size={14} />
            2D GeoJSON
          </button>
          <button
            onClick={() => setActiveTab('obj')}
            style={{
              padding: '10px 16px',
              background: 'transparent',
              border: 'none',
              borderBottom: activeTab === 'obj' ? '2px solid #38bdf8' : 'none',
              color: activeTab === 'obj' ? '#38bdf8' : '#94a3b8',
              fontWeight: 600,
              fontSize: '12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Box size={14} />
            3D Mesh (OBJ)
          </button>
          <button
            onClick={() => {
              setActiveTab('roundtrip');
              if (!roundTripResult) handleRunRoundTrip();
            }}
            style={{
              padding: '10px 16px',
              background: 'transparent',
              border: 'none',
              borderBottom: activeTab === 'roundtrip' ? '2px solid #38bdf8' : 'none',
              color: activeTab === 'roundtrip' ? '#38bdf8' : '#94a3b8',
              fontWeight: 600,
              fontSize: '12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <ShieldCheck size={14} />
            Round-Trip Verify
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '16px 20px', overflowY: 'auto', flex: 1 }}>
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

          {/* TAB 1: JSON */}
          {activeTab === 'json' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button
                  className="btn btn-sm"
                  onClick={() => handleCopy(jsonString)}
                  title="Copy full JSON payload"
                >
                  {copied ? <CheckCircle size={12} color="#4ade80" /> : <Copy size={12} />}
                  {copied ? 'Copied' : 'Copy JSON'}
                </button>
                <button
                  className="btn btn-sm btn-primary"
                  onClick={() => handleDownload(jsonString, `bhuvistaar_export_${exportData.vuid.prototype_vuid}.json`, 'application/json')}
                >
                  <Download size={12} />
                  Download JSON
                </button>
              </div>
              <pre style={{
                backgroundColor: '#070d19',
                padding: '12px',
                borderRadius: '6px',
                border: '1px solid #1e293b',
                color: '#e2e8f0',
                fontSize: '11px',
                fontFamily: 'monospace',
                overflowX: 'auto',
                maxHeight: '400px'
              }}>
                {jsonString}
              </pre>
            </div>
          )}

          {/* TAB 2: GEOJSON */}
          {activeTab === 'geojson' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{
                padding: '8px 12px',
                backgroundColor: '#1e293b',
                borderRadius: '6px',
                fontSize: '11px',
                color: '#94a3b8'
              }}>
                <strong>GeoJSON Projection:</strong> Represents 2D planar footprint polygons. 3D vertical bounds (`z_min`, `z_max`, `height_m`) are preserved in GeoJSON properties.
              </div>
              {geoJsonData && (
                <>
                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                    <button
                      className="btn btn-sm"
                      onClick={() => handleCopy(JSON.stringify(geoJsonData, null, 2))}
                    >
                      <Copy size={12} />
                      Copy GeoJSON
                    </button>
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={() => handleDownload(JSON.stringify(geoJsonData, null, 2), `cadastre_${ulpin}.geojson`, 'application/geo+json')}
                    >
                      <Download size={12} />
                      Download GeoJSON
                    </button>
                  </div>
                  <pre style={{
                    backgroundColor: '#070d19',
                    padding: '12px',
                    borderRadius: '6px',
                    border: '1px solid #1e293b',
                    color: '#e2e8f0',
                    fontSize: '11px',
                    fontFamily: 'monospace',
                    overflowX: 'auto',
                    maxHeight: '380px'
                  }}>
                    {JSON.stringify(geoJsonData, null, 2)}
                  </pre>
                </>
              )}
            </div>
          )}

          {/* TAB 3: OBJ */}
          {activeTab === 'obj' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', alignItems: 'center', padding: '30px 0' }}>
              <Box size={48} style={{ color: '#38bdf8' }} />
              <div style={{ textAlign: 'center', maxWidth: '480px' }}>
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc', marginBottom: '6px' }}>
                  Wavefront OBJ 3D Cadastral Unit Mesh
                </h3>
                <p style={{ fontSize: '12px', color: '#94a3b8', lineHeight: '1.5' }}>
                  Exports candidate volumetric prism with top/bottom polygon caps and vertical extrusion side quads in standard Wavefront OBJ format for AutoCAD, Blender, or QGIS.
                </p>
              </div>
              <button
                className="btn btn-primary"
                onClick={handleDownloadObj}
              >
                <Download size={14} />
                Download 3D OBJ Model
              </button>
            </div>
          )}

          {/* TAB 4: ROUND TRIP */}
          {activeTab === 'roundtrip' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                    Deterministic Import-Verify Round-Trip
                  </h3>
                  <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                    Recomputes SHA-256 and VUID from geometry & elevations to prove data preservation
                  </span>
                </div>
                <button
                  className="btn btn-sm btn-primary"
                  onClick={handleRunRoundTrip}
                  disabled={loading}
                >
                  <ShieldCheck size={12} />
                  Re-Verify Round-Trip
                </button>
              </div>

              {roundTripResult && (
                <div style={{
                  padding: '14px',
                  borderRadius: '6px',
                  backgroundColor: roundTripResult.verified ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  border: `1px solid ${roundTripResult.verified ? '#22c55e' : '#ef4444'}`
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    {roundTripResult.verified ? (
                      <CheckCircle size={18} style={{ color: '#22c55e' }} />
                    ) : (
                      <AlertCircle size={18} style={{ color: '#ef4444' }} />
                    )}
                    <span style={{ fontWeight: 700, fontSize: '13px', color: '#f8fafc' }}>
                      Round-Trip Status: {roundTripResult.status}
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: '#cbd5e1', lineHeight: '1.5' }}>
                    <div><strong>Claimed VUID:</strong> <code>{roundTripResult.claimed_vuid}</code></div>
                    <div><strong>Recalculated VUID:</strong> <code>{roundTripResult.recalculated_vuid}</code></div>
                    <div><strong>Coordinate Preserved:</strong> {roundTripResult.discrepancies.length === 0 ? 'YES (100% representation-invariant)' : 'NO'}</div>
                  </div>
                </div>
              )}
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
