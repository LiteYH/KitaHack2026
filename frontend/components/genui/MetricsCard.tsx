/**
 * Metrics Card Component
 * Displays key performance indicators
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface Metric {
  label: string;
  value: string;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
}

interface MetricsData {
  type: 'metrics';
  title: string;
  metrics: Metric[];
  period?: string;
}

interface MetricsCardProps {
  data: any; // Accept any to support dynamic GenUI data
}

export function MetricsCard({ data }: MetricsCardProps) {
  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getTrendColor = (trend?: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-muted-foreground';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>{data.title}</CardTitle>
        {data.period && (
          <CardDescription>{data.period}</CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {data.metrics.map((metric, index) => (
            <Card key={index} className="border-2">
              <CardContent className="p-4">
                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-foreground">
                    {metric.label}
                  </p>
                  <div className="flex items-baseline justify-between">
                    <p className="text-2xl font-bold">{metric.value}</p>
                    {metric.trend && (
                      <div className="flex items-center">
                        {getTrendIcon(metric.trend)}
                      </div>
                    )}
                  </div>
                  {metric.change && (
                    <p className={`text-xs font-medium ${getTrendColor(metric.trend)}`}>
                      {metric.change}
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
