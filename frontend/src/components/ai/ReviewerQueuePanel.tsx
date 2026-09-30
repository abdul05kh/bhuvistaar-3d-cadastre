import React from 'react';
import { ListOrdered, AlertOctagon, AlertTriangle, HelpCircle, FileCheck, ArrowRight } from 'lucide-react';
import { ReviewerQueueItem } from '../../types';

interface ReviewerQueuePanelProps {
  queueItems: ReviewerQueueItem[];
  onSelectQueueItem: (item: ReviewerQueueItem) => void;
}

export const ReviewerQueuePanel: React.FC<ReviewerQueuePanelProps> = ({
  queueItems,
  onSelectQueueItem,
}) => {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
            <ListOrdered className="w-4 h-4 text-cyan-400" />
            <span>Reviewer Prioritization Assistance Queue</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            AI-ordered workflow queue sorting critical topology blockers, anomalies, and candidate proposals for officer adjudication.
          </p>
        </div>
        <div className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
          {queueItems.length} Items in Queue
        </div>
      </div>

      {/* Queue Items */}
      {queueItems.length === 0 ? (
        <div className="bg-slate-900/40 border border-slate-800 rounded-lg p-8 text-center text-slate-400">
          <FileCheck className="w-10 h-10 mx-auto text-emerald-500 mb-2" />
          <h4 className="text-sm font-medium text-slate-200">Review Queue Empty</h4>
          <p className="text-xs text-slate-400 mt-1">All proposed candidates and topological issues have been processed.</p>
        </div>
      ) : (
        <div className="space-y-2.5">
          {queueItems.map((item, idx) => {
            const isPriority1 = item.priority === 1;
            const isPriority2 = item.priority === 2;
            const isPriority3 = item.priority === 3;

            let badgeColor = 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30';
            if (isPriority1) badgeColor = 'bg-red-500/20 text-red-300 border-red-500/40';
            else if (isPriority2) badgeColor = 'bg-amber-500/20 text-amber-300 border-amber-500/40';
            else if (isPriority3) badgeColor = 'bg-purple-500/20 text-purple-300 border-purple-500/40';

            return (
              <div
                key={item.identifier + idx}
                onClick={() => onSelectQueueItem(item)}
                className={`bg-slate-900/70 border rounded-lg p-3.5 flex items-center justify-between cursor-pointer transition hover:border-slate-600 ${
                  isPriority1
                    ? 'border-red-500/40 bg-red-950/10'
                    : 'border-slate-800'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div
                    className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-mono font-bold ${
                      isPriority1
                        ? 'bg-red-500 text-white'
                        : isPriority2
                        ? 'bg-amber-500 text-slate-950'
                        : isPriority3
                        ? 'bg-purple-500 text-white'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    P{item.priority}
                  </div>

                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-semibold text-white tracking-wide">
                        {item.title}
                      </span>
                      <span className={`text-[10px] font-mono px-2 py-0.2 rounded border font-bold uppercase ${badgeColor}`}>
                        {item.item_type}
                      </span>
                      {item.affected_level && (
                        <span className="text-xs font-mono px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                          {item.affected_level}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-300 mt-1 max-w-2xl line-clamp-1 font-mono">
                      {item.reason}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {item.confidence !== undefined && item.confidence !== null && (
                    <div className="text-right font-mono text-xs text-slate-400">
                      <span className="text-[10px] block uppercase">Confidence</span>
                      <span className="text-slate-200 font-bold">{(item.confidence * 100).toFixed(0)}%</span>
                    </div>
                  )}
                  <button className="px-3 py-1 text-xs font-medium rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-500/30 flex items-center space-x-1">
                    <span>Inspect</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
