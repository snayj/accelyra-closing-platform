import { useState } from 'react';
import { Calendar, DollarSign, Home } from 'lucide-react';
import Card, { CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { formatCurrency, formatDate } from '../lib/utils';

// Mock data - will be replaced with API calls
const mockTransactions = [
  {
    id: 'TXN-2025-001',
    propertyAddress: '456 Oak Ave, Naperville, IL',
    purchasePrice: 625000,
    currentStage: 'FUNDING_SIGNING',
    createdAt: '2025-01-15T10:00:00Z',
    buyer: { name: 'Alice Johnson' },
    seller: { name: 'Bob Williams' },
  },
  {
    id: 'TXN-2025-002',
    propertyAddress: '789 Elm St, Evanston, IL',
    purchasePrice: 485000,
    currentStage: 'UNDERWRITING',
    createdAt: '2025-01-20T14:30:00Z',
    buyer: { name: 'Carol Martinez' },
    seller: { name: 'David Brown' },
  },
];

const stageLabels: Record<string, string> = {
  OFFER_ACCEPTED: 'Offer Accepted',
  TITLE_SEARCH: 'Title Search',
  UNDERWRITING: 'Underwriting',
  CLEAR_TO_CLOSE: 'Clear to Close',
  FINAL_DOCUMENTS: 'Final Documents',
  FUNDING_SIGNING: 'Funding & Signing',
  RECORDING_COMPLETE: 'Recording Complete',
};

const stageColors: Record<string, string> = {
  OFFER_ACCEPTED: 'bg-blue-100 text-blue-700',
  TITLE_SEARCH: 'bg-purple-100 text-purple-700',
  UNDERWRITING: 'bg-yellow-100 text-yellow-700',
  CLEAR_TO_CLOSE: 'bg-green-100 text-green-700',
  FINAL_DOCUMENTS: 'bg-indigo-100 text-indigo-700',
  FUNDING_SIGNING: 'bg-pink-100 text-pink-700',
  RECORDING_COMPLETE: 'bg-emerald-100 text-emerald-700',
};

export default function History() {
  const [filterStage, setFilterStage] = useState<string>('all');

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Transaction History</h1>
          <p className="text-gray-600">View and manage all your transactions</p>
        </div>
      </div>

      {/* Filters */}
      <Card padding="md">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">Filter by Stage:</label>
          <select
            value={filterStage}
            onChange={(e) => setFilterStage(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">All Stages</option>
            {Object.entries(stageLabels).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </Card>

      {/* Transaction List */}
      <div className="grid grid-cols-1 gap-6">
        {mockTransactions.map((transaction) => (
          <Card key={transaction.id} hover padding="lg">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <CardTitle className="text-lg">{transaction.id}</CardTitle>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      stageColors[transaction.currentStage]
                    }`}
                  >
                    {stageLabels[transaction.currentStage]}
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center text-gray-700">
                    <Home className="h-4 w-4 mr-2 text-gray-400" />
                    <span className="text-sm">{transaction.propertyAddress}</span>
                  </div>
                  <div className="flex items-center text-gray-700">
                    <DollarSign className="h-4 w-4 mr-2 text-gray-400" />
                    <span className="text-sm font-medium">
                      {formatCurrency(transaction.purchasePrice)}
                    </span>
                  </div>
                  <div className="flex items-center text-gray-700">
                    <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                    <span className="text-sm">Created {formatDate(transaction.createdAt)}</span>
                  </div>
                </div>

                <div className="mt-4 flex gap-4 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">Buyer:</span> {transaction.buyer.name}
                  </div>
                  <div>
                    <span className="font-medium">Seller:</span> {transaction.seller.name}
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <button className="px-4 py-2 text-sm font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors">
                  View Details
                </button>
              </div>
            </div>
          </Card>
        ))}

        {mockTransactions.length === 0 && (
          <Card padding="lg">
            <div className="text-center py-12 text-gray-500">
              <Calendar className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium mb-2">No Transactions Found</p>
              <p className="text-sm">Start a new transaction in the Simulator</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
