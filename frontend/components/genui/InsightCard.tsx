/**
 * Insight Card Component
 * Displays strategic insights and recommendations
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, TrendingUp, Clock } from 'lucide-react';

interface InsightData {
  type: 'insight';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  actions: string[];
  urgency: 'immediate' | 'soon' | 'monitor';
}

interface InsightCardProps {
  data: any; // Accept any to support dynamic GenUI data
}

export function InsightCard({ data }: InsightCardProps) {
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'immediate':
        return 'destructive';
      case 'soon':
        return 'default';
      case 'monitor':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  const getUrgencyLabel = (urgency: string) => {
    switch (urgency) {
      case 'immediate':
        return 'Act Now';
      case 'soon':
        return 'Plan Soon';
      case 'monitor':
        return 'Keep Monitoring';
      default:
        return urgency;
    }
  };

  return (
    <Card className="w-full border-l-4 border-l-primary">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-primary" />
              {data.title}
            </CardTitle>
            <CardDescription className="mt-2">{data.description}</CardDescription>
          </div>
          <div className="flex flex-col gap-2">
            <Badge variant={getImpactColor(data.impact)}>
              <TrendingUp className="mr-1 h-3 w-3" />
              {data.impact.toUpperCase()} Impact
            </Badge>
            <Badge variant={getUrgencyColor(data.urgency)}>
              <Clock className="mr-1 h-3 w-3" />
              {getUrgencyLabel(data.urgency)}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {data.actions && data.actions.length > 0 && (
          <div className="rounded-lg bg-muted p-4">
            <h4 className="mb-3 text-sm font-semibold">Recommended Actions:</h4>
            <ul className="space-y-2">
              {data.actions.map((action, index) => (
                <li key={index} className="flex items-start text-sm">
                  <span className="mr-2 mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                    {index + 1}
                  </span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
