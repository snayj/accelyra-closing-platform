import { TransactionStage } from '../../types';
import { CheckCircle, XCircle, AlertCircle, FileText, Upload, ScanEye } from 'lucide-react';
import Card, { CardContent, CardHeader, CardTitle } from '../ui/Card';

interface StageDetailsProps {
  stage: TransactionStage;
  scenario: string;
}

interface StageInfo {
  name: string;
  description: string;
  duration: string;
  requiredDocuments: {
    name: string;
    required: boolean;
    uploaded?: boolean;
    ocrPassed?: boolean;
    ocrDetails?: string;
  }[];
  requiredActions: {
    name: string;
    completed?: boolean;
    blocking?: boolean;
  }[];
  validationChecks: {
    name: string;
    passed: boolean;
    reason?: string;
  }[];
}

const stageInfo: Record<TransactionStage, StageInfo> = {
  [TransactionStage.OFFER_ACCEPTED]: {
    name: 'Stage 1: Offer Accepted / Escrow Opened',
    description: 'Buyer\'s offer has been accepted and escrow account opened',
    duration: '1 day',
    requiredDocuments: [
      {
        name: 'Purchase Agreement',
        required: true,
        uploaded: true,
        ocrPassed: true,
        ocrDetails: 'Property address, purchase price, and signatures extracted and validated',
      },
      {
        name: 'Proof of Funds',
        required: true,
        uploaded: true,
        ocrPassed: true,
        ocrDetails: 'Bank statement shows sufficient funds ($125,000 verified)',
      },
    ],
    requiredActions: [
      { name: 'Earnest money deposit ($10,000)', completed: false, blocking: true },
      { name: 'Open escrow account', completed: true, blocking: false },
    ],
    validationChecks: [
      { name: 'Valid purchase agreement', passed: true },
      { name: 'Proof of funds verified', passed: true },
      { name: 'Earnest money deposited', passed: false, reason: 'Waiting for buyer to deposit $10,000' },
    ],
  },
  [TransactionStage.TITLE_SEARCH]: {
    name: 'Stage 2: Title Search Ordered',
    description: 'Title company researching property ownership and liens',
    duration: '2 days',
    requiredDocuments: [
      {
        name: 'Preliminary Title Report',
        required: true,
        uploaded: true,
        ocrPassed: true,
        ocrDetails: 'Property ownership chain verified, no liens found',
      },
    ],
    requiredActions: [
      { name: 'Order title search', completed: true, blocking: false },
      { name: 'Review title report', completed: true, blocking: true },
    ],
    validationChecks: [
      { name: 'Clear title', passed: true },
      { name: 'No outstanding liens', passed: true },
      { name: 'Property boundaries verified', passed: true },
    ],
  },
  [TransactionStage.UNDERWRITING]: {
    name: 'Stage 3: Lender Underwriting / Inspections',
    description: 'Lender reviewing loan application and property inspections',
    duration: '4 days',
    requiredDocuments: [
      {
        name: 'Pre-approval Letter',
        required: true,
        uploaded: true,
        ocrPassed: true,
        ocrDetails: 'Loan amount $400,000 approved, DTI ratio: 28%',
      },
      {
        name: 'Home Inspection Report',
        required: true,
        uploaded: true,
        ocrPassed: true,
        ocrDetails: 'No major issues found, minor repairs recommended',
      },
      {
        name: 'Appraisal Report',
        required: true,
        uploaded: true,
        ocrPassed: true,
        ocrDetails: 'Appraised value: $510,000 (meets purchase price)',
      },
    ],
    requiredActions: [
      { name: 'Complete home inspection', completed: true, blocking: true },
      { name: 'Complete appraisal', completed: true, blocking: true },
      { name: 'Lender underwriting approval', completed: true, blocking: true },
    ],
    validationChecks: [
      { name: 'Income verification', passed: true },
      { name: 'Credit score meets requirements', passed: true },
      { name: 'Appraisal meets purchase price', passed: true },
      { name: 'No inspection deal-breakers', passed: true },
    ],
  },
  [TransactionStage.CLEAR_TO_CLOSE]: {
    name: 'Stage 4: Clear to Close',
    description: 'All conditions met, ready to prepare final documents',
    duration: '1 day',
    requiredDocuments: [],
    requiredActions: [
      { name: 'Final underwriting approval', completed: true, blocking: true },
      { name: 'Buyer funds verification', completed: true, blocking: true },
    ],
    validationChecks: [
      { name: 'All contingencies removed', passed: true },
      { name: 'Loan approved', passed: true },
      { name: 'Funds verified', passed: true },
    ],
  },
  [TransactionStage.FINAL_DOCUMENTS]: {
    name: 'Stage 5: Final Documents Prepared',
    description: 'Closing disclosure and final paperwork prepared',
    duration: '2 days',
    requiredDocuments: [
      {
        name: 'Closing Disclosure',
        required: true,
        uploaded: true,
        ocrPassed: true,
        ocrDetails: 'Final closing costs: $15,500, cash to close: $140,500',
      },
    ],
    requiredActions: [
      { name: 'Prepare closing disclosure', completed: true, blocking: true },
      { name: 'Buyer review period (3 days)', completed: true, blocking: true },
    ],
    validationChecks: [
      { name: 'Closing disclosure accuracy', passed: true },
      { name: '3-day review period completed', passed: true },
    ],
  },
  [TransactionStage.FUNDING_SIGNING]: {
    name: 'Stage 6: Funding & Signing',
    description: 'Buyer signs documents and funds are wired',
    duration: '2 days',
    requiredDocuments: [],
    requiredActions: [
      { name: 'Sign closing documents', completed: true, blocking: true },
      { name: 'Wire funds to escrow', completed: true, blocking: true },
      { name: 'Lender funds loan', completed: true, blocking: true },
    ],
    validationChecks: [
      { name: 'All documents signed', passed: true },
      { name: 'Funds received', passed: true },
    ],
  },
  [TransactionStage.RECORDING_COMPLETE]: {
    name: 'Stage 7: Recording Complete',
    description: 'Deed recorded with county, transaction complete',
    duration: '1 day',
    requiredDocuments: [
      {
        name: 'Recorded Deed',
        required: true,
        uploaded: true,
        ocrPassed: true,
        ocrDetails: 'Deed recorded with county, new owner officially registered',
      },
    ],
    requiredActions: [
      { name: 'Record deed', completed: true, blocking: false },
      { name: 'Distribute funds', completed: true, blocking: false },
    ],
    validationChecks: [
      { name: 'Deed recorded', passed: true },
      { name: 'Keys transferred', passed: true },
      { name: 'Transaction complete', passed: true },
    ],
  },
};

// Scenario-specific modifications
const getScenarioModifications = (stage: TransactionStage, scenario: string) => {
  const info = { ...stageInfo[stage] };

  if (scenario === 'insufficient_funds' && stage === TransactionStage.OFFER_ACCEPTED) {
    info.validationChecks = [
      { name: 'Valid purchase agreement', passed: true },
      {
        name: 'Proof of funds verified',
        passed: false,
        reason: 'Bank statement shows only $50,000 available (need $125,000)',
      },
      { name: 'Earnest money deposited', passed: false, reason: 'Cannot proceed without sufficient funds' },
    ];
  }

  if (scenario === 'title_issue' && stage === TransactionStage.TITLE_SEARCH) {
    info.validationChecks = [
      {
        name: 'Clear title',
        passed: false,
        reason: 'Unresolved lien found from previous owner ($15,000)',
      },
      { name: 'No outstanding liens', passed: false, reason: 'Must resolve lien before proceeding' },
      { name: 'Property boundaries verified', passed: true },
    ];
  }

  if (scenario === 'low_appraisal' && stage === TransactionStage.UNDERWRITING) {
    info.validationChecks = [
      { name: 'Income verification', passed: true },
      { name: 'Credit score meets requirements', passed: true },
      {
        name: 'Appraisal meets purchase price',
        passed: false,
        reason: 'Appraised at $475,000 (below $500,000 purchase price). Need renegotiation.',
      },
      { name: 'No inspection deal-breakers', passed: true },
    ];
  }

  if (scenario === 'failed_inspection' && stage === TransactionStage.UNDERWRITING) {
    info.validationChecks = [
      { name: 'Income verification', passed: true },
      { name: 'Credit score meets requirements', passed: true },
      { name: 'Appraisal meets purchase price', passed: true },
      {
        name: 'No inspection deal-breakers',
        passed: false,
        reason: 'Major foundation issues found ($50,000 repair cost). Requires seller concessions or contract renegotiation.',
      },
    ];
  }

  return info;
};

export default function StageDetails({ stage, scenario }: StageDetailsProps) {
  const info = getScenarioModifications(stage, scenario);
  const allChecksPassed = info.validationChecks.every((check) => check.passed);

  return (
    <div className="space-y-6">
      {/* Stage Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>{info.name}</CardTitle>
            <span className="text-sm text-gray-600">Typical Duration: {info.duration}</span>
          </div>
          <p className="text-gray-600 mt-2">{info.description}</p>
        </CardHeader>
      </Card>

      {/* Documents */}
      {info.requiredDocuments.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Required Documents
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {info.requiredDocuments.map((doc, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-gray-400" />
                        <span className="font-medium text-gray-900">{doc.name}</span>
                        {doc.required && (
                          <span className="text-xs bg-error-100 text-error-700 px-2 py-0.5 rounded">
                            Required
                          </span>
                        )}
                      </div>

                      {doc.uploaded && (
                        <div className="mt-2 ml-6 space-y-2">
                          <div className="flex items-center gap-2 text-sm text-success-700">
                            <Upload className="h-4 w-4" />
                            <span>Document uploaded</span>
                          </div>

                          {doc.ocrPassed !== undefined && (
                            <div
                              className={`flex items-start gap-2 text-sm ${
                                doc.ocrPassed ? 'text-success-700' : 'text-error-700'
                              }`}
                            >
                              <ScanEye className="h-4 w-4 mt-0.5 flex-shrink-0" />
                              <div>
                                <div className="font-medium">
                                  {doc.ocrPassed ? 'OCR Validation Passed' : 'OCR Validation Failed'}
                                </div>
                                {doc.ocrDetails && (
                                  <div className="text-gray-600 mt-1">{doc.ocrDetails}</div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Required Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Required Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {info.requiredActions.map((action, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  {action.completed ? (
                    <CheckCircle className="h-5 w-5 text-success-600" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-warning-600" />
                  )}
                  <span className="text-gray-900">{action.name}</span>
                  {action.blocking && (
                    <span className="text-xs bg-error-100 text-error-700 px-2 py-0.5 rounded">
                      Blocking
                    </span>
                  )}
                </div>
                <span className="text-sm text-gray-600">
                  {action.completed ? 'Complete' : 'Pending'}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Validation Results */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Stage Validation</CardTitle>
            {allChecksPassed ? (
              <span className="flex items-center gap-2 text-success-700 font-semibold">
                <CheckCircle className="h-5 w-5" />
                All Checks Passed
              </span>
            ) : (
              <span className="flex items-center gap-2 text-error-700 font-semibold">
                <XCircle className="h-5 w-5" />
                Issues Detected
              </span>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {info.validationChecks.map((check, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-2 ${
                  check.passed
                    ? 'bg-success-50 border-success-200'
                    : 'bg-error-50 border-error-200'
                }`}
              >
                <div className="flex items-start gap-3">
                  {check.passed ? (
                    <CheckCircle className="h-5 w-5 text-success-700 mt-0.5 flex-shrink-0" />
                  ) : (
                    <XCircle className="h-5 w-5 text-error-700 mt-0.5 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <div className={`font-medium ${check.passed ? 'text-success-900' : 'text-error-900'}`}>
                      {check.name}
                    </div>
                    {check.reason && (
                      <div className={`text-sm mt-1 ${check.passed ? 'text-success-700' : 'text-error-700'}`}>
                        {check.reason}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
