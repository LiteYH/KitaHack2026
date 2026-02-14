/**
 * Competitor Comparison Card Component
 * Displays side-by-side competitor analysis
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface Competitor {
  name: string;
  strengths: string[];
  weaknesses: string[];
  pricing: string;
  market_position: string;
}

interface CompetitorComparisonData {
  type: 'competitor_comparison';
  competitors: Competitor[];
  recommendation?: string;
}

interface CompetitorComparisonCardProps {
  data: any; // Accept any to support dynamic GenUI data
}

export function CompetitorComparisonCard({ data }: CompetitorComparisonCardProps) {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Competitor Comparison</CardTitle>
        <CardDescription>
          Strategic analysis of {data.competitors.length} competitors
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data.competitors.map((competitor, index) => (
            <Card key={index} className="border-2">
              <CardHeader>
                <CardTitle className="text-lg">{competitor.name || 'Unknown'}</CardTitle>
                <CardDescription className="text-xs">
                  {competitor.market_position || 'Market position not available'}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {/* Pricing */}
                {competitor.pricing && (
                  <div>
                    <Badge variant="outline" className="mb-2">
                      {competitor.pricing}
                    </Badge>
                  </div>
                )}

                {/* Strengths */}
                {competitor.strengths && competitor.strengths.length > 0 && (
                  <div>
                    <h4 className="mb-2 flex items-center text-sm font-semibold text-green-600">
                      <TrendingUp className="mr-1 h-4 w-4" />
                      Strengths
                    </h4>
                    <ul className="space-y-1 text-xs">
                      {competitor.strengths.map((strength, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="mr-2">✓</span>
                          <span>{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Weaknesses */}
                {competitor.weaknesses && competitor.weaknesses.length > 0 && (
                  <div>
                    <h4 className="mb-2 flex items-center text-sm font-semibold text-red-600">
                      <TrendingDown className="mr-1 h-4 w-4" />
                      Weaknesses
                    </h4>
                    <ul className="space-y-1 text-xs">
                      {competitor.weaknesses.map((weakness, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="mr-2">✗</span>
                          <span>{weakness}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recommendation */}
        {data.recommendation && (
          <div className="mt-6 rounded-lg border border-primary/20 bg-primary/5 p-4">
            <h4 className="mb-2 flex items-center text-sm font-semibold">
              <span className="mr-2">💡</span>
              Strategic Recommendation
            </h4>
            <p className="text-sm">{data.recommendation}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
