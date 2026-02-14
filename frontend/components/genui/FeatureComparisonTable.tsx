/**
 * Feature Comparison Table Component
 * Displays feature/pricing matrices
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Check, X } from 'lucide-react';

interface FeatureComparisonTableData {
  type: 'feature_table';
  title: string;
  headers: string[];
  rows: string[][];
}

interface FeatureComparisonTableProps {
  data: any; // Accept any to support dynamic GenUI data
}

export function FeatureComparisonTable({ data }: FeatureComparisonTableProps) {
  const renderCell = (cell: string) => {
    if (cell === '✓' || cell.toLowerCase() === 'yes') {
      return <Check className="mx-auto h-5 w-5 text-green-600" />;
    }
    if (cell === '✗' || cell.toLowerCase() === 'no') {
      return <X className="mx-auto h-5 w-5 text-red-600" />;
    }
    return <span>{cell}</span>;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>{data.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b-2 border-border">
                {data.headers.map((header, index) => (
                  <th
                    key={index}
                    className={`p-3 text-left font-semibold ${
                      index === 0 ? 'sticky left-0 bg-card' : 'text-center'
                    }`}
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.rows.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  className="border-b border-border hover:bg-muted/50"
                >
                  {row.map((cell, cellIndex) => (
                    <td
                      key={cellIndex}
                      className={`p-3 ${
                        cellIndex === 0
                          ? 'sticky left-0 bg-card font-medium'
                          : 'text-center'
                      }`}
                    >
                      {renderCell(cell)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
