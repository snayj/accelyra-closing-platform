import { Zap, Shield, Brain, Clock, TrendingUp, CheckCircle } from 'lucide-react';
import Card, { CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';

export default function About() {
  return (
    <div className="space-y-12 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">About Accelyra</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Revolutionizing real estate closings with AI-driven automation,
          compliance-embedded workflows, and unprecedented speed.
        </p>
      </div>

      {/* Mission */}
      <section>
        <Card padding="lg">
          <CardHeader>
            <CardTitle className="text-2xl">Our Mission</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 text-lg leading-relaxed">
              Accelyra is transforming the real estate closing process from a slow, manual,
              error-prone experience into a fast, automated, and compliant journey. We leverage
              AI-native processing to reduce closing times from 30-45 days to just 7-14 days,
              while ensuring 100% regulatory compliance and providing complete transparency to
              all stakeholders.
            </p>
          </CardContent>
        </Card>
      </section>

      {/* Key Features */}
      <section>
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">Platform Capabilities</h2>
          <p className="text-gray-600">Built for speed, compliance, and intelligence</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title} hover padding="lg">
                <div className="flex justify-center mb-4">
                  <div className={`w-14 h-14 ${feature.color} rounded-lg flex items-center justify-center`}>
                    <Icon className="h-7 w-7 text-white" />
                  </div>
                </div>
                <CardHeader>
                  <CardTitle className="text-center">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-center">{feature.description}</CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Comparison */}
      <section>
        <Card padding="lg">
          <CardHeader>
            <CardTitle className="text-2xl text-center mb-8">Traditional vs. Accelyra</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Traditional */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
                  Traditional Process
                </h3>
                <div className="space-y-3">
                  {traditionalCons.map((item, index) => (
                    <div key={index} className="flex items-start">
                      <span className="text-error-500 mr-2">✗</span>
                      <span className="text-gray-700">{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Accelyra */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
                  Accelyra Platform
                </h3>
                <div className="space-y-3">
                  {accelyraPros.map((item, index) => (
                    <div key={index} className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-success-500 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Value Metrics */}
      <section>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card padding="lg" className="text-center">
            <div className="text-4xl font-bold text-primary-600 mb-2">7-14</div>
            <div className="text-sm text-gray-600">Days to Close</div>
          </Card>
          <Card padding="lg" className="text-center">
            <div className="text-4xl font-bold text-success-600 mb-2">70%</div>
            <div className="text-sm text-gray-600">Time Reduction</div>
          </Card>
          <Card padding="lg" className="text-center">
            <div className="text-4xl font-bold text-warning-600 mb-2">100%</div>
            <div className="text-sm text-gray-600">Compliance Rate</div>
          </Card>
          <Card padding="lg" className="text-center">
            <div className="text-4xl font-bold text-purple-600 mb-2">24/7</div>
            <div className="text-sm text-gray-600">Automated Processing</div>
          </Card>
        </div>
      </section>
    </div>
  );
}

const features = [
  {
    title: 'AI-Native Processing',
    description: 'Intelligent document extraction, validation, and processing with machine learning',
    icon: Brain,
    color: 'bg-primary-600',
  },
  {
    title: 'Compliance-Embedded',
    description: 'Built-in regulatory compliance with automatic validation and audit trails',
    icon: Shield,
    color: 'bg-success-600',
  },
  {
    title: 'Lightning Fast',
    description: 'Reduce closing times from 45 days to 7-14 days with automation',
    icon: Zap,
    color: 'bg-warning-600',
  },
  {
    title: 'Real-Time Tracking',
    description: 'Complete visibility into transaction progress for all stakeholders',
    icon: Clock,
    color: 'bg-purple-600',
  },
  {
    title: 'Smart Workflows',
    description: 'Automated task generation, assignment, and completion tracking',
    icon: TrendingUp,
    color: 'bg-pink-600',
  },
  {
    title: 'Error Prevention',
    description: 'Proactive issue detection and resolution before delays occur',
    icon: CheckCircle,
    color: 'bg-indigo-600',
  },
];

const traditionalCons = [
  '30-45 days average closing time',
  'Manual document review and processing',
  'Error-prone data entry',
  'Limited visibility into progress',
  'Reactive problem solving',
  'Compliance checks at the end',
  'High risk of delays',
];

const accelyraPros = [
  '7-14 days average closing time',
  'Automated document processing with AI',
  'Validated data extraction',
  'Real-time progress tracking',
  'Proactive issue detection',
  'Continuous compliance validation',
  'Predictable timelines',
];
