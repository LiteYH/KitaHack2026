/**
 * GenUI Component Parser and Renderer
 * 
 * Parses GENUI markers in agent responses and renders appropriate components
 */

import React from 'react';
import { CompetitorComparisonCard } from './CompetitorComparisonCard';
import { MetricsCard } from './MetricsCard';
import { TrendChart } from './TrendChart';
import { FeatureComparisonTable } from './FeatureComparisonTable';
import { InsightCard } from './InsightCard';

export interface GenUIData {
  type: string;
  [key: string]: any;
}

export interface GenUISegment {
  type: 'text' | 'genui';
  content: string;
  data?: GenUIData;
}

/**
 * Parse message content for GenUI markers
 * Format: [GENUI:component_type]{json}[/GENUI]
 */
export function parseGenUI(content: string | undefined | null): GenUISegment[] {
  // Defensive check: handle undefined, null, or non-string content
  if (!content || typeof content !== 'string') {
    return [{
      type: 'text',
      content: '',
    }];
  }

  const segments: GenUISegment[] = [];
  const genUIRegex = /\[GENUI:(\w+)\]([\s\S]*?)\[\/GENUI\]/g;
  
  let lastIndex = 0;
  let match;

  while ((match = genUIRegex.exec(content)) !== null) {
    // Add text before GenUI marker
    if (match.index > lastIndex) {
      const textContent = content.slice(lastIndex, match.index).trim();
      if (textContent) {
        segments.push({
          type: 'text',
          content: textContent,
        });
      }
    }

    // Parse GenUI component
    const componentType = match[1];
    const jsonString = match[2].trim();
    
    try {
      const data = JSON.parse(jsonString);
      segments.push({
        type: 'genui',
        content: '',
        data: {
          type: componentType,
          ...data,
        },
      });
    } catch (error) {
      console.error('Failed to parse GenUI JSON:', error);
      // Fallback to text
      segments.push({
        type: 'text',
        content: jsonString,
      });
    }

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < content.length) {
    const textContent = content.slice(lastIndex).trim();
    if (textContent) {
      segments.push({
        type: 'text',
        content: textContent,
      });
    }
  }

  // If no GenUI found, return entire content as text
  if (segments.length === 0) {
    segments.push({
      type: 'text',
      content: content,
    });
  }

  return segments;
}

/**
 * Render a GenUI component based on type
 */
export function renderGenUIComponent(data: GenUIData): React.ReactNode {
  switch (data.type) {
    case 'competitor_comparison':
      return <CompetitorComparisonCard data={data as any} />;
    
    case 'metrics':
      return <MetricsCard data={data as any} />;
    
    case 'trend_chart':
      return <TrendChart data={data as any} />;
    
    case 'feature_table':
      return <FeatureComparisonTable data={data as any} />;
    
    case 'insight':
      return <InsightCard data={data as any} />;
    
    default:
      console.warn(`Unknown GenUI component type: ${data.type}`);
      return (
        <div className="rounded-lg border border-border bg-muted p-4">
          <p className="text-sm text-muted-foreground">
            Unknown component type: {data.type}
          </p>
        </div>
      );
  }
}

interface GenUIRendererProps {
  content: string;
  className?: string;
}

/**
 * Main GenUI Renderer Component
 * Parses and renders GenUI markers within message content
 */
export function GenUIRenderer({ content, className = '' }: GenUIRendererProps) {
  const segments = parseGenUI(content);

  return (
    <div className={`space-y-4 ${className}`}>
      {segments.map((segment, index) => {
        // Generate unique key using index + type + first 10 chars of content
        const uniqueKey = `${segment.type}-${index}-${segment.content?.slice(0, 10) || segment.data?.type || ''}`;
        
        if (segment.type === 'text') {
          return (
            <div
              key={uniqueKey}
              className="prose prose-sm dark:prose-invert max-w-none"
              dangerouslySetInnerHTML={{ __html: segment.content }}
            />
          );
        } else if (segment.type === 'genui' && segment.data) {
          return (
            <div key={uniqueKey} className="my-4">
              {renderGenUIComponent(segment.data)}
            </div>
          );
        }
        return null;
      })}
    </div>
  );
}
