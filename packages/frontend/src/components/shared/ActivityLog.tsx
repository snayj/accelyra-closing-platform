import { Clock, CheckCircle, AlertCircle, TrendingUp, FileText, DollarSign } from 'lucide-react';
import Card, { CardContent, CardHeader, CardTitle } from '../ui/Card';
import { formatDate } from '../../lib/utils';

export interface ActivityEntry {
  timestamp: string;
  type: 'info' | 'success' | 'warning' | 'stage_change';
  message: string;
  details?: string;
}

interface ActivityLogProps {
  activities: ActivityEntry[];
}

export default function ActivityLog({ activities }: ActivityLogProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-success-600" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-warning-600" />;
      case 'stage_change':
        return <TrendingUp className="h-5 w-5 text-primary-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getBackgroundColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-success-50 border-success-200';
      case 'warning':
        return 'bg-warning-50 border-warning-200';
      case 'stage_change':
        return 'bg-primary-50 border-primary-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Activity Log
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {activities.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Clock className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p>No activity yet. Start the simulation to see events.</p>
            </div>
          ) : (
            activities.map((activity, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border ${getBackgroundColor(activity.type)}`}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">{getIcon(activity.type)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                      <span className="text-xs text-gray-500 whitespace-nowrap">
                        {formatDate(activity.timestamp)}
                      </span>
                    </div>
                    {activity.details && (
                      <p className="text-sm text-gray-600 mt-1">{activity.details}</p>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
