import { Link } from 'react-router-dom';
import { Play, Zap, Shield, Clock, CheckCircle } from 'lucide-react';
import Button from '../components/ui/Button';
import Card, { CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';

export default function Welcome() {
  return (
    <div className="space-y-12 animate-fade-in">
      {/* Hero Section */}
      <section className="text-center py-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Welcome to <span className="text-primary-600">Accelyra</span>
        </h1>
        <p className="text-2xl text-gray-600 mb-8">
          Autonomous Real Estate Closing Platform
        </p>
        <p className="text-xl text-gray-700 max-w-3xl mx-auto mb-10">
          Experience the future of real estate closings. Reduce closing times from <span className="line-through text-gray-400">45 days</span>{' '}
          <span className="font-bold text-primary-600">to ≤10 days</span> with AI-driven automation.
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/simulator">
            <Button size="lg" className="gap-2">
              <Play className="h-5 w-5" />
              Start Simulator
            </Button>
          </Link>
          <Link to="/about">
            <Button size="lg" variant="outline">
              Learn More
            </Button>
          </Link>
        </div>
      </section>

      {/* Stats Section */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card hover padding="lg" className="text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
              <Clock className="h-8 w-8 text-primary-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-2">7-14 Days</h3>
          <p className="text-gray-600">Average Closing Time</p>
          <p className="text-sm text-gray-500 mt-2">vs. traditional 30-45 days</p>
        </Card>

        <Card hover padding="lg" className="text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center">
              <Zap className="h-8 w-8 text-success-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-2">70% Faster</h3>
          <p className="text-gray-600">Processing Speed</p>
          <p className="text-sm text-gray-500 mt-2">Automated workflows</p>
        </Card>

        <Card hover padding="lg" className="text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center">
              <Shield className="h-8 w-8 text-warning-600" />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-2">100%</h3>
          <p className="text-gray-600">Compliance Ready</p>
          <p className="text-sm text-gray-500 mt-2">Embedded regulations</p>
        </Card>
      </section>

      {/* 7-Stage Process */}
      <section>
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">7-Stage Closing Process</h2>
          <p className="text-gray-600">Track your transaction through every milestone</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stages.map((stage, index) => (
            <Card key={stage.name} hover padding="md">
              <CardHeader>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-primary-600 bg-primary-50 px-2 py-1 rounded">
                    Stage {index + 1}
                  </span>
                  <CheckCircle className="h-5 w-5 text-gray-300" />
                </div>
                <CardTitle className="text-base">{stage.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{stage.description}</CardDescription>
                <p className="text-xs text-gray-500 mt-2">{stage.duration}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Quick Start Guide */}
      <section>
        <Card padding="lg">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Start Guide</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="flex items-center mb-3">
                <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
                  1
                </div>
                <h3 className="font-semibold text-gray-900">Choose a Scenario</h3>
              </div>
              <p className="text-sm text-gray-600 ml-11">
                Select from 6 realistic transaction scenarios including perfect closings and challenging situations.
              </p>
            </div>
            <div>
              <div className="flex items-center mb-3">
                <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
                  2
                </div>
                <h3 className="font-semibold text-gray-900">Run the Simulation</h3>
              </div>
              <p className="text-sm text-gray-600 ml-11">
                Watch the transaction progress through each stage with real-time validation and automated checks.
              </p>
            </div>
            <div>
              <div className="flex items-center mb-3">
                <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
                  3
                </div>
                <h3 className="font-semibold text-gray-900">Review Results</h3>
              </div>
              <p className="text-sm text-gray-600 ml-11">
                View detailed activity logs, stage outcomes, and see how issues are detected and resolved.
              </p>
            </div>
          </div>
          <div className="mt-8 text-center">
            <Link to="/simulator">
              <Button size="lg">
                Start Your First Simulation
              </Button>
            </Link>
          </div>
        </Card>
      </section>
    </div>
  );
}

const stages = [
  {
    name: 'Offer Accepted',
    description: 'Buyer offer accepted, escrow opened',
    duration: '1 day',
  },
  {
    name: 'Title Search',
    description: 'Title company researching property',
    duration: '2 days',
  },
  {
    name: 'Underwriting',
    description: 'Lender review and inspections',
    duration: '4 days',
  },
  {
    name: 'Clear to Close',
    description: 'All conditions met',
    duration: '1 day',
  },
  {
    name: 'Final Documents',
    description: 'Closing disclosure prepared',
    duration: '2 days',
  },
  {
    name: 'Funding & Signing',
    description: 'Buyer signs, funds wired',
    duration: '2 days',
  },
  {
    name: 'Recording Complete',
    description: 'Deed recorded with county',
    duration: '1 day',
  },
];
