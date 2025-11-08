import { useState } from 'react';
import { Play, RefreshCw, ArrowRight, CheckCircle } from 'lucide-react';
import Button from '../components/ui/Button';
import Card, { CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import StageProgress from '../components/shared/StageProgress';
import StageDetails from '../components/shared/StageDetails';
import ActivityLog, { type ActivityEntry } from '../components/shared/ActivityLog';
import DocumentManager from '../components/shared/DocumentManager';
import { TransactionStage } from '../types';
import { formatCurrency } from '../lib/utils';

const scenarios = [
  {
    id: 'perfect',
    name: '✅ Perfect Transaction',
    description: 'Smooth progression through all 7 stages with no issues',
    canAdvance: true,
  },
  {
    id: 'insufficient_funds',
    name: '💰 Insufficient Funds',
    description: 'Buyer lacks required funds - blocks at Stage 1',
    blocksAt: TransactionStage.OFFER_ACCEPTED,
  },
  {
    id: 'title_issue',
    name: '🏚️ Title Issue',
    description: 'Unresolved lien discovered - blocks at Stage 2',
    blocksAt: TransactionStage.TITLE_SEARCH,
  },
  {
    id: 'low_appraisal',
    name: '⚖️ Low Appraisal',
    description: 'Appraisal below purchase price - blocks at Stage 3',
    blocksAt: TransactionStage.UNDERWRITING,
  },
  {
    id: 'failed_inspection',
    name: '🔍 Failed Inspection',
    description: 'Major property issues found - blocks at Stage 3',
    blocksAt: TransactionStage.UNDERWRITING,
  },
  {
    id: 'missing_docs',
    name: '📋 Missing Documentation',
    description: 'Missing required documents - blocks at Stage 3',
    blocksAt: TransactionStage.UNDERWRITING,
  },
];

const stageOrder = [
  TransactionStage.OFFER_ACCEPTED,
  TransactionStage.TITLE_SEARCH,
  TransactionStage.UNDERWRITING,
  TransactionStage.CLEAR_TO_CLOSE,
  TransactionStage.FINAL_DOCUMENTS,
  TransactionStage.FUNDING_SIGNING,
  TransactionStage.RECORDING_COMPLETE,
];

export default function Simulator() {
  // Form state
  const [selectedScenario, setSelectedScenario] = useState('perfect');
  const [propertyAddress, setPropertyAddress] = useState('123 Main St, Chicago, IL 60601');
  const [purchasePrice, setPurchasePrice] = useState('500000');
  const [buyerName, setBuyerName] = useState('John Doe');
  const [sellerName, setSellerName] = useState('Jane Smith');

  // Simulation state
  const [isSimulating, setIsSimulating] = useState(false);
  const [currentStage, setCurrentStage] = useState<TransactionStage>(TransactionStage.OFFER_ACCEPTED);
  const [transactionId, setTransactionId] = useState<string | null>(null);
  const [activities, setActivities] = useState<ActivityEntry[]>([]);
  const [stageHistory, setStageHistory] = useState<any[]>([]);

  const selectedScenarioInfo = scenarios.find((s) => s.id === selectedScenario);
  const currentStageIndex = stageOrder.indexOf(currentStage);
  const isComplete = currentStage === TransactionStage.RECORDING_COMPLETE;
  const isBlocked = selectedScenarioInfo?.blocksAt === currentStage && selectedScenario !== 'perfect';

  const addActivity = (type: ActivityEntry['type'], message: string, details?: string) => {
    setActivities((prev) => [
      {
        timestamp: new Date().toISOString(),
        type,
        message,
        details,
      },
      ...prev,
    ]);
  };

  const handleStartSimulation = () => {
    setIsSimulating(true);
    setCurrentStage(TransactionStage.OFFER_ACCEPTED);
    setActivities([]);
    setStageHistory([
      {
        stage: TransactionStage.OFFER_ACCEPTED,
        enteredAt: new Date().toISOString(),
      },
    ]);

    // Generate mock transaction ID
    const txnId = `TXN-${new Date().getFullYear()}-${String(Math.floor(Math.random() * 9999)).padStart(4, '0')}`;
    setTransactionId(txnId);

    addActivity(
      'success',
      'Transaction created successfully',
      `${txnId} - ${propertyAddress} - ${formatCurrency(parseInt(purchasePrice))}`
    );

    addActivity(
      'stage_change',
      'Stage 1: Offer Accepted / Escrow Opened',
      'Buyer offer accepted, escrow account opened'
    );

    addActivity(
      'info',
      'Running automated validations',
      'Checking purchase agreement, proof of funds, and earnest money requirements'
    );

    // Simulate document processing
    setTimeout(() => {
      addActivity(
        'success',
        'Document OCR completed',
        'Purchase agreement and proof of funds scanned and validated'
      );
    }, 1000);

    if (selectedScenario === 'insufficient_funds') {
      setTimeout(() => {
        addActivity(
          'warning',
          'Validation failed: Insufficient funds',
          'Bank statement shows only $50,000 available. Need $125,000 for down payment and closing costs.'
        );
      }, 1500);
    } else {
      setTimeout(() => {
        addActivity(
          'success',
          'All Stage 1 validations passed',
          'Ready to advance to Stage 2 once earnest money is deposited'
        );
      }, 1500);
    }
  };

  const handleAdvanceStage = () => {
    if (isBlocked) {
      addActivity(
        'warning',
        'Cannot advance: Blocking issues detected',
        `This scenario demonstrates a common problem that blocks progress. In production, these issues would need to be resolved before advancing.`
      );
      return;
    }

    const nextStageIndex = currentStageIndex + 1;
    if (nextStageIndex >= stageOrder.length) return;

    const nextStage = stageOrder[nextStageIndex];
    setCurrentStage(nextStage);

    const newHistoryEntry = {
      stage: nextStage,
      enteredAt: new Date().toISOString(),
    };

    setStageHistory((prev) => [...prev, newHistoryEntry]);

    const stageNames: Record<TransactionStage, string> = {
      [TransactionStage.OFFER_ACCEPTED]: 'Stage 1: Offer Accepted / Escrow Opened',
      [TransactionStage.TITLE_SEARCH]: 'Stage 2: Title Search Ordered',
      [TransactionStage.UNDERWRITING]: 'Stage 3: Lender Underwriting / Inspections',
      [TransactionStage.CLEAR_TO_CLOSE]: 'Stage 4: Clear to Close',
      [TransactionStage.FINAL_DOCUMENTS]: 'Stage 5: Final Documents Prepared',
      [TransactionStage.FUNDING_SIGNING]: 'Stage 6: Funding & Signing',
      [TransactionStage.RECORDING_COMPLETE]: 'Stage 7: Recording Complete',
    };

    addActivity('stage_change', `Advanced to ${stageNames[nextStage]}`, 'Running automated validations...');

    // Simulate validation
    setTimeout(() => {
      if (selectedScenarioInfo?.blocksAt === nextStage) {
        addActivity(
          'warning',
          'Validation failed',
          `Scenario "${selectedScenarioInfo.name}" blocks at this stage`
        );
      } else {
        addActivity(
          'success',
          'Stage validations passed',
          'All required documents and checks completed successfully'
        );
      }
    }, 800);

    if (nextStage === TransactionStage.RECORDING_COMPLETE) {
      setTimeout(() => {
        addActivity(
          'success',
          '🎉 Transaction Complete!',
          `Property successfully transferred to ${buyerName}. Total time: 13 days vs traditional 42 days (69% faster)`
        );
      }, 1200);
    }
  };

  const handleReset = () => {
    setIsSimulating(false);
    setCurrentStage(TransactionStage.OFFER_ACCEPTED);
    setTransactionId(null);
    setActivities([]);
    setStageHistory([]);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Transaction Simulator</h1>
        <p className="text-gray-600">
          Experience the complete 7-stage closing process with document validation, OCR processing, and automated compliance checks
        </p>
      </div>

      {!isSimulating ? (
        // Configuration Panel (Before Simulation)
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <Card padding="lg">
              <CardHeader>
                <CardTitle>Transaction Configuration</CardTitle>
                <CardDescription>Set up your transaction scenario and property details</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Scenario Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select Scenario
                    </label>
                    <div className="grid grid-cols-1 gap-2">
                      {scenarios.map((scenario) => (
                        <button
                          key={scenario.id}
                          onClick={() => setSelectedScenario(scenario.id)}
                          className={`text-left p-3 rounded-lg border-2 transition-all ${
                            selectedScenario === scenario.id
                              ? 'border-primary-600 bg-primary-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <div className="font-medium text-gray-900">{scenario.name}</div>
                          <div className="text-sm text-gray-600">{scenario.description}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Property Details */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Property Address
                    </label>
                    <input
                      type="text"
                      value={propertyAddress}
                      onChange={(e) => setPropertyAddress(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Purchase Price
                    </label>
                    <div className="relative">
                      <span className="absolute left-3 top-2 text-gray-500">$</span>
                      <input
                        type="number"
                        value={purchasePrice}
                        onChange={(e) => setPurchasePrice(e.target.value)}
                        className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Buyer Name
                      </label>
                      <input
                        type="text"
                        value={buyerName}
                        onChange={(e) => setBuyerName(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Seller Name
                      </label>
                      <input
                        type="text"
                        value={sellerName}
                        onChange={(e) => setSellerName(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <Button className="w-full gap-2 mt-6" size="lg" onClick={handleStartSimulation}>
                    <Play className="h-5 w-5" />
                    Start Simulation
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <div>
            <Card padding="lg">
              <CardHeader>
                <CardTitle>What to Expect</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-gray-700">
                    This simulator demonstrates the complete real estate closing process with:
                  </p>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="h-5 w-5 text-success-600 flex-shrink-0 mt-0.5" />
                      <span><strong>7-Stage Workflow:</strong> From offer acceptance to deed recording</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="h-5 w-5 text-success-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Document Processing:</strong> OCR extraction and validation of key documents</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="h-5 w-5 text-success-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Automated Checks:</strong> Real-time validation of requirements and blockers</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="h-5 w-5 text-success-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Activity Logging:</strong> Complete audit trail of all events and decisions</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="h-5 w-5 text-success-600 flex-shrink-0 mt-0.5" />
                      <span><strong>Problem Detection:</strong> See how issues are caught and prevent delays</span>
                    </li>
                  </ul>

                  <div className="bg-primary-50 border-l-4 border-primary-600 p-4 mt-6">
                    <p className="text-sm text-primary-900">
                      <strong>Demo Mode:</strong> This simulator uses mock data to demonstrate platform capabilities.
                      In production, real integrations with title companies, lenders, and county recorders automate the entire process.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      ) : (
        // Active Simulation View
        <div className="space-y-8">
          {/* Transaction Header */}
          <Card padding="lg">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-2xl font-bold text-gray-900">{transactionId}</h2>
                  {isComplete && (
                    <span className="bg-success-100 text-success-700 px-3 py-1 rounded-full text-sm font-semibold">
                      Complete
                    </span>
                  )}
                  {isBlocked && (
                    <span className="bg-error-100 text-error-700 px-3 py-1 rounded-full text-sm font-semibold">
                      Blocked
                    </span>
                  )}
                </div>
                <p className="text-gray-600">{propertyAddress}</p>
                <p className="text-lg font-semibold text-gray-900 mt-1">
                  {formatCurrency(parseInt(purchasePrice))}
                </p>
                <p className="text-sm text-gray-600 mt-2">
                  Scenario: <span className="font-medium">{selectedScenarioInfo?.name}</span>
                </p>
              </div>
              <Button variant="outline" onClick={handleReset} className="gap-2">
                <RefreshCw className="h-4 w-4" />
                New Simulation
              </Button>
            </div>
          </Card>

          {/* Stage Progress */}
          <Card padding="lg">
            <StageProgress currentStage={currentStage} stageHistory={stageHistory} />
          </Card>

          {/* Stage Details */}
          <StageDetails stage={currentStage} scenario={selectedScenario} />

          {/* Advance Stage Button */}
          {!isComplete && (
            <div className="flex justify-center">
              <Button
                size="lg"
                onClick={handleAdvanceStage}
                disabled={isBlocked}
                className="gap-2"
              >
                {isBlocked ? (
                  <>Cannot Advance - Issues Detected</>
                ) : (
                  <>
                    Advance to Next Stage
                    <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </Button>
              {isBlocked && (
                <p className="text-sm text-error-700 mt-2 text-center">
                  This scenario demonstrates blocking issues. Resolve the validation failures above to proceed.
                </p>
              )}
            </div>
          )}

          {/* Activity Log */}
          <ActivityLog activities={activities} />

          {/* Document Generation & OCR */}
          {transactionId && (
            <DocumentManager transactionId={transactionId} />
          )}
        </div>
      )}
    </div>
  );
}
