import { useState } from 'react';
import { Play, RefreshCw } from 'lucide-react';
import Button from '../components/ui/Button';
import Card, { CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';

const scenarios = [
  { id: 'perfect', name: '✅ Perfect Transaction', description: 'Smooth progression through all stages' },
  { id: 'insufficient_funds', name: '💰 Insufficient Funds', description: 'Buyer qualification issues' },
  { id: 'missing_docs', name: '📋 Missing Documentation', description: 'Stalled at underwriting' },
  { id: 'title_issue', name: '🏚️ Title Issue', description: 'Lien discoveries' },
  { id: 'failed_inspection', name: '🔍 Failed Inspection', description: 'Property condition problems' },
  { id: 'low_appraisal', name: '⚖️ Low Appraisal', description: 'Value mismatches' },
];

export default function Simulator() {
  const [selectedScenario, setSelectedScenario] = useState('perfect');
  const [propertyAddress, setPropertyAddress] = useState('123 Main St, Chicago, IL 60601');
  const [purchasePrice, setPurchasePrice] = useState('500000');
  const [buyerName, setBuyerName] = useState('John Doe');
  const [sellerName, setSellerName] = useState('Jane Smith');

  const handleStartSimulation = () => {
    // TODO: Connect to API
    console.log('Starting simulation with:', {
      selectedScenario,
      propertyAddress,
      purchasePrice,
      buyerName,
      sellerName,
    });
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Transaction Simulator</h1>
        <p className="text-gray-600">
          Create and simulate real estate transactions with different scenarios
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Configuration Panel */}
        <div>
          <Card padding="lg">
            <CardHeader>
              <CardTitle>Transaction Details</CardTitle>
              <CardDescription>Configure your transaction parameters</CardDescription>
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

                {/* Property Address */}
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

                {/* Purchase Price */}
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

                {/* Buyer Name */}
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

                {/* Seller Name */}
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

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  <Button className="flex-1 gap-2" onClick={handleStartSimulation}>
                    <Play className="h-4 w-4" />
                    Start Simulation
                  </Button>
                  <Button variant="outline" className="gap-2">
                    <RefreshCw className="h-4 w-4" />
                    Reset
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Simulation Output Panel */}
        <div>
          <Card padding="lg">
            <CardHeader>
              <CardTitle>Simulation Status</CardTitle>
              <CardDescription>Transaction progress and activity log</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-gray-500">
                <Play className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium mb-2">Ready to Simulate</p>
                <p className="text-sm">Configure your transaction and click "Start Simulation"</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
