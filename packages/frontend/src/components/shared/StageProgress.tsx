import { TransactionStage } from '../../types';
import { CheckCircle, Circle, Clock } from 'lucide-react';
import { cn } from '../../lib/utils';

interface StageProgressProps {
  currentStage: TransactionStage;
  stageHistory: any[];
}

const stages = [
  { key: TransactionStage.OFFER_ACCEPTED, name: 'Offer Accepted', order: 1 },
  { key: TransactionStage.TITLE_SEARCH, name: 'Title Search', order: 2 },
  { key: TransactionStage.UNDERWRITING, name: 'Underwriting', order: 3 },
  { key: TransactionStage.CLEAR_TO_CLOSE, name: 'Clear to Close', order: 4 },
  { key: TransactionStage.FINAL_DOCUMENTS, name: 'Final Documents', order: 5 },
  { key: TransactionStage.FUNDING_SIGNING, name: 'Funding & Signing', order: 6 },
  { key: TransactionStage.RECORDING_COMPLETE, name: 'Recording Complete', order: 7 },
];

export default function StageProgress({ currentStage, stageHistory }: StageProgressProps) {
  const currentStageIndex = stages.findIndex((s) => s.key === currentStage);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Transaction Progress</h3>
        <span className="text-sm text-gray-600">
          Stage {currentStageIndex + 1} of {stages.length}
        </span>
      </div>

      <div className="relative">
        {/* Progress bar background */}
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200" />

        {/* Progress bar fill */}
        <div
          className="absolute top-5 left-0 h-0.5 bg-primary-600 transition-all duration-500"
          style={{ width: `${(currentStageIndex / (stages.length - 1)) * 100}%` }}
        />

        {/* Stage markers */}
        <div className="relative flex justify-between">
          {stages.map((stage, index) => {
            const isCompleted = index < currentStageIndex;
            const isCurrent = index === currentStageIndex;
            const isPending = index > currentStageIndex;

            return (
              <div key={stage.key} className="flex flex-col items-center" style={{ width: '14%' }}>
                <div
                  className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300',
                    isCompleted && 'bg-primary-600 border-primary-600',
                    isCurrent && 'bg-white border-primary-600 ring-4 ring-primary-100',
                    isPending && 'bg-white border-gray-300'
                  )}
                >
                  {isCompleted && <CheckCircle className="h-6 w-6 text-white" />}
                  {isCurrent && <Clock className="h-6 w-6 text-primary-600" />}
                  {isPending && <Circle className="h-6 w-6 text-gray-300" />}
                </div>

                <div className="mt-2 text-center">
                  <div
                    className={cn(
                      'text-xs font-medium',
                      (isCompleted || isCurrent) && 'text-gray-900',
                      isPending && 'text-gray-400'
                    )}
                  >
                    {stage.name}
                  </div>
                  {isCurrent && (
                    <div className="text-xs text-primary-600 font-semibold mt-1">Current</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Progress percentage */}
      <div className="mt-6 bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span className="text-sm font-bold text-primary-600">
            {Math.round(((currentStageIndex + 1) / stages.length) * 100)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${((currentStageIndex + 1) / stages.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
