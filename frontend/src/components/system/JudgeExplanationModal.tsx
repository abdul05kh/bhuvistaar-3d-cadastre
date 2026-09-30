import React from 'react';
import { X, HelpCircle, Shield, CheckCircle, AlertTriangle, Layers, GitBranch, Database, FileText } from 'lucide-react';

interface JudgeExplanationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const JudgeExplanationModal: React.FC<JudgeExplanationModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const faqs = [
    {
      q: "WHY 3D?",
      icon: <Layers size={18} className="text-cyan-400" />,
      a: "Vertical property strata—such as multi-storey apartments, commercial floors, basements, and elevated utility easements—occupy the same 2D ground footprint. A 2D GIS representation collapses these distinct legal spaces into a single polygon, causing geometric ambiguity. Explicit 3D volumetric extents [z_min, z_max] are required to disambiguate vertical rights without data loss."
    },
    {
      q: "WHY VUID (NOT OFFICIAL 3D ULPIN)?",
      icon: <Shield size={18} className="text-amber-400" />,
      a: "The Government of India's 14-digit ULPIN (Bhu-Aadhaar) is an authoritative national standard for 2D land parcels. No statutory 3D ULPIN standard exists yet. BhuVistaar introduces a deterministic Volumetric Unique Identifier (VUID) derived from canonical WKB geometry hashes and vertical intervals. It is strictly a prototype data key and is never marketed as an official government identifier."
    },
    {
      q: "WHY MACHINE ASSISTANCE (AI / ANALYTICS)?",
      icon: <HelpCircle size={18} className="text-purple-400" />,
      a: "Digitizing 3D cadastre from architectural drawings, LandXML files, or point clouds is laborious and error-prone. AI and heuristic models assist surveyors by proposing initial 3D prismatic candidate units, detecting anomalies across floorplans, and prioritizing human attention on complex inconsistencies."
    },
    {
      q: "WHY NOT TRUST AI AS THE AUTHORITY?",
      icon: <AlertTriangle size={18} className="text-rose-400" />,
      a: "Machine learning models hallucinate, misinterpret unstandardized drawings, and produce uncertain confidence. In statutory land administration, geometry must have zero tolerance for overlapping rights. Therefore, AI proposals are strictly non-authoritative: they must pass independent deterministic spatial validation and receive explicit human officer sign-off before entering any governance state."
    },
    {
      q: "HOW IS GEOMETRY DETERMINISTICALLY VALIDATED?",
      icon: <CheckCircle size={18} className="text-emerald-400" />,
      a: "Independent mathematical algorithms (Gate A) check physical boundary containment (TOP-001) using Shapely 2.0 and PostGIS ST_Contains without auto-clipping, and verify vertical non-overlap (VRT-003) by calculating exact vertical gaps. If lower ceiling > upper floor (e.g. 106.50m vs 106.00m), an immovable BLOCKER issue is emitted."
    },
    {
      q: "WHY MANDATORY HUMAN REVIEW?",
      icon: <FileText size={18} className="text-blue-400" />,
      a: "Statutory authority and legal accountability must always rest with human officers. A human reviewer examines evidence, evaluates machine anomaly flags, and either accepts, rejects, or requests corrections. Gate C enforces that an unreviewed candidate revision can never be approved."
    },
    {
      q: "WHY IMMUTABLE REVISIONS (NOT IN-PLACE EDITING)?",
      icon: <GitBranch size={18} className="text-teal-400" />,
      a: "In cadastral disputes, destroying previous versions makes legal audits impossible. When an officer corrects an elevation or footprint, BhuVistaar never overwrites the candidate. It spawns a new Revision (e.g., Revision 2), recalculates a new deterministic VUID, links predecessor lineage, and preserves the defective predecessor intact."
    },
    {
      q: "WHY EVIDENCE PROVENANCE & REPRODUCIBILITY?",
      icon: <Database size={18} className="text-indigo-400" />,
      a: "Every spatial unit revision explicitly points to the underlying raw evidence files (total station survey, architectural PDF, LandXML) pinned by SHA-256 cryptographic hashes. If an evidence file is modified, dependent candidates are automatically flagged as STALE_EVIDENCE, guaranteeing end-to-end auditability."
    }
  ];

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(5, 10, 20, 0.85)',
      backdropFilter: 'blur(6px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: '#0c1729',
        border: '1px solid #1e3a5f',
        borderRadius: '12px',
        width: '900px',
        maxWidth: '95vw',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 24px',
          borderBottom: '1px solid #1e3a5f',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: '#08101e'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <HelpCircle size={20} className="text-cyan-400" />
            <div>
              <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                Judge Technical FAQ & Core Architecture Rationale
              </h2>
              <p style={{ fontSize: '11px', color: '#94a3b8', margin: 0 }}>
                Concise, defensible answers to foundational 3D cadastral intelligence questions
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* FAQ Grid */}
        <div style={{ padding: '20px 24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {faqs.map((item, idx) => (
            <div key={idx} style={{
              backgroundColor: '#111f38',
              border: '1px solid #1e293b',
              borderRadius: '8px',
              padding: '14px 18px',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {item.icon}
                <span style={{ fontWeight: 700, fontSize: '13px', color: '#38bdf8', letterSpacing: '0.02em' }}>
                  {item.q}
                </span>
              </div>
              <p style={{ fontSize: '12px', lineHeight: 1.5, color: '#cbd5e1', margin: 0 }}>
                {item.a}
              </p>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div style={{
          padding: '12px 24px',
          borderTop: '1px solid #1e3a5f',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#08101e',
          fontSize: '11px',
          color: '#64748b'
        }}>
          <span>Prototype VUID — not an official 3D ULPIN. Controlled synthetic evaluation.</span>
          <button className="btn btn-sm btn-primary" onClick={onClose}>
            Close FAQ
          </button>
        </div>
      </div>
    </div>
  );
};
