/**
 * Resolved HITL Card Component
 * 
 * Displays a collapsible summary of completed HITL approvals
 */

"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Check, ChevronDown, ChevronUp, Edit2, X } from "lucide-react"
import type { InterruptData, HITLDecision } from "@/lib/api/agent"

interface ResolvedHITLCardProps {
  interruptData: InterruptData[];
  resolution: {
    type: 'approve' | 'edit' | 'reject';
    decisions: HITLDecision[];
    timestamp: number;
  };
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export function ResolvedHITLCard({ 
  interruptData, 
  resolution, 
  isCollapsed = false,
  onToggleCollapse 
}: ResolvedHITLCardProps) {
  // Extract action requests
  const actionRequests = interruptData.flatMap(
    (interrupt) => interrupt.value?.action_requests || []
  );

  if (actionRequests.length === 0) {
    return null;
  }

  const primaryRequest = actionRequests[0];
  const config = primaryRequest.args || {};

  const getResolutionIcon = () => {
    switch (resolution.type) {
      case 'approve':
        return <Check className="h-4 w-4" />;
      case 'edit':
        return <Edit2 className="h-4 w-4" />;
      case 'reject':
        return <X className="h-4 w-4" />;
    }
  };

  const getResolutionColor = () => {
    switch (resolution.type) {
      case 'approve':
        return 'bg-green-500/10 text-green-500 border-green-500/20';
      case 'edit':
        return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'reject':
        return 'bg-red-500/10 text-red-500 border-red-500/20';
    }
  };

  const getResolutionLabel = () => {
    switch (resolution.type) {
      case 'approve':
        return 'Approved';
      case 'edit':
        return 'Edited & Approved';
      case 'reject':
        return 'Rejected';
    }
  };

  return (
    <Card className={`border ${getResolutionColor()}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center">
              {getResolutionIcon()}
            </div>
            <div>
              <CardTitle className="text-sm font-semibold">
                {resolution.type === 'reject' 
                  ? 'Configuration Rejected' 
                  : 'Configuration Approved'}
              </CardTitle>
              <CardDescription className="text-xs mt-0.5">
                {new Date(resolution.timestamp).toLocaleTimeString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {getResolutionLabel()}
            </Badge>
            {onToggleCollapse && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggleCollapse}
                className="h-6 w-6 p-0"
              >
                {isCollapsed ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronUp className="h-4 w-4" />
                )}
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      {!isCollapsed && (
        <CardContent className="pb-3 pt-0 space-y-2 text-sm">
          {/* Competitor Name */}
          {config.competitor && (
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">Competitor:</span>
              <span className="text-xs">{config.competitor}</span>
            </div>
          )}

          {/* Monitoring Aspects */}
          {config.aspects && (
            <div className="flex items-start gap-2">
              <span className="text-xs font-medium text-muted-foreground">Aspects:</span>
              <div className="flex flex-wrap gap-1">
                {config.aspects.map((aspect: string) => (
                  <Badge key={aspect} variant="secondary" className="text-xs px-1.5 py-0 h-5">
                    {aspect}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Frequency */}
          {config.frequency_label && (
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">Frequency:</span>
              <span className="text-xs">{config.frequency_label}</span>
            </div>
          )}

          {/* Notification Preference */}
          {config.notification_preference && (
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">Notifications:</span>
              <span className="text-xs capitalize">{config.notification_preference.replace('_', ' ')}</span>
            </div>
          )}

          {/* Show edited args if type is 'edit' */}
          {resolution.type === 'edit' && resolution.decisions[0]?.args && (
            <div className="mt-2 rounded-md bg-muted/50 p-2">
              <div className="text-xs font-medium text-muted-foreground mb-1">Modified Configuration:</div>
              <pre className="text-xs overflow-x-auto">
                {JSON.stringify(resolution.decisions[0].args, null, 2)}
              </pre>
            </div>
          )}

          {/* Show feedback if rejected */}
          {resolution.type === 'reject' && resolution.decisions[0]?.feedback && (
            <div className="mt-2 rounded-md bg-destructive/10 p-2">
              <div className="text-xs font-medium text-destructive mb-1">Rejection Reason:</div>
              <div className="text-xs text-destructive/80">
                {resolution.decisions[0].feedback}
              </div>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}
