import React, { useState } from 'react';
import { X, XCircle, ShieldAlert } from 'lucide-react';
import { AICandidate } from '../../types';

interface RejectCandidateModalProps {
  candidate: AICandidate | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (candidateId: string, reviewerId: string, justification: string) => Promise<void>;
}

export const RejectCandidateModal: React.FC<RejectCandidateModalProps> = ({
  candidate,
  isOpen,
  onClose,
  onConfirm,
}) => {
  const [reviewerId, setReviewerId] = useState('surveyor_officer_01');
  const [justification, setJustification] = useState(
    'Evidence does not support independent 3D unit or boundary stratum.'
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !candidate) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!justification.trim() || justification.length < 5) {
      setError('A comprehensive officer rejection rationale is mandatory.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await onConfirm(candidate.candidate_id, reviewerId, justification);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to reject candidate.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-lg shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/80">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400">
              <XCircle className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Reject Candidate Proposal</h3>
              <p className="text-xs text-slate-400 font-mono">
                Level {candidate.level_code} ({candidate.candidate_id})
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div className="p-3 rounded-lg bg-red-950/20 border border-red-500/30 text-xs text-red-300 flex items-start space-x-2.5">
            <ShieldAlert className="w-4 h-4 mt-0.5 flex-shrink-0 text-red-400" />
            <div>
              <span className="font-bold">Permanent Audit Preservation:</span>
              <p className="mt-0.5 text-red-200/90 font-sans">
                Rejected AI proposals are permanently preserved in the database and audit trail alongside your justification. They will never be deleted.
              </p>
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">
              Reviewing Officer Identifier:
            </label>
            <input
              type="text"
              value={reviewerId}
              onChange={(e) => setReviewerId(e.target.value)}
              className="w-full px-3 py-1.5 text-xs font-mono rounded bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-red-500"
              required
            />
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">
              Mandatory Rejection Rationale:
            </label>
            <textarea
              rows={3}
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              className="w-full px-3 py-2 text-xs font-sans rounded bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-red-500 resize-none"
              placeholder="State reason for rejecting this AI proposal..."
              required
            />
          </div>

          {error && (
            <div className="p-2.5 rounded bg-red-950/40 border border-red-500/40 text-xs text-red-300">
              {error}
            </div>
          )}

          <div className="pt-2 flex items-center justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 text-xs rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1.5 text-xs font-medium rounded bg-red-600 hover:bg-red-500 text-white flex items-center space-x-1.5 shadow transition disabled:opacity-50"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>{isSubmitting ? 'Recording Rejection...' : 'Confirm Rejection'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
