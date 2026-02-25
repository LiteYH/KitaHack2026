/**
 * Trend Chart Component
 * Displays time-series data visualization
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface DataPoint {
  date: string;
  value: number;
}

interface TrendChartData {
  type: 'trend_chart';
  title: string;
  data: DataPoint[];
  metric_name: string;
}

interface TrendChartProps {
  data: any; // Accept any to support dynamic GenUI data
}

export function TrendChart({ data }: TrendChartProps) {
  // Simple SVG-based chart (could be replaced with a charting library like recharts)
  const values = data.data.map(d => d.value);
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);
  const range = maxValue - minValue || 1;

  const getY = (value: number, height: number) => {
    return height - ((value - minValue) / range) * height;
  };

  const chartHeight = 200;
  const chartWidth = 600;
  const padding = 20;

  const points = data.data.map((point, index) => {
    const x = padding + (index / (data.data.length - 1)) * (chartWidth - 2 * padding);
    const y = getY(point.value, chartHeight - 2 * padding) + padding;
    return `${x},${y}`;
  }).join(' ');

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>{data.title}</CardTitle>
        <CardDescription>{data.metric_name}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <svg width={chartWidth} height={chartHeight} className="w-full">
            {/* Grid lines */}
            {[0, 0.25, 0.5, 0.75, 1].map((ratio, index) => {
              const y = padding + ratio * (chartHeight - 2 * padding);
              return (
                <line
                  key={index}
                  x1={padding}
                  y1={y}
                  x2={chartWidth - padding}
                  y2={y}
                  stroke="currentColor"
                  strokeOpacity="0.1"
                  strokeDasharray="4"
                />
              );
            })}

            {/* Line */}
            <polyline
              points={points}
              fill="none"
              stroke="hsl(var(--primary))"
              strokeWidth="2"
            />

            {/* Points */}
            {data.data.map((point, index) => {
              const x = padding + (index / (data.data.length - 1)) * (chartWidth - 2 * padding);
              const y = getY(point.value, chartHeight - 2 * padding) + padding;
              return (
                <circle
                  key={index}
                  cx={x}
                  cy={y}
                  r="4"
                  fill="hsl(var(--primary))"
                />
              );
            })}
          </svg>
        </div>

        {/* Data table */}
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="p-2 text-left">Date</th>
                <th className="p-2 text-right">Value</th>
              </tr>
            </thead>
            <tbody>
              {data.data.map((point, index) => (
                <tr key={index} className="border-b">
                  <td className="p-2">{new Date(point.date).toLocaleDateString()}</td>
                  <td className="p-2 text-right font-semibold">{point.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
