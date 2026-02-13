/**
 * HITL Approval Card Component
 * 
 * Displays human-in-the-loop approval requests for monitoring configurations
 */

"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, Check, Edit2, X } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import type { InterruptData, ActionRequest, HITLDecision } from "@/lib/api/agent"

interface HITLApprovalCardProps {
  interruptData: InterruptData[];
  onDecision: (decisions: HITLDecision[]) => void;
  className?: string;
}

export function HITLApprovalCard({ interruptData, onDecision, className }: HITLApprovalCardProps) {
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [editedArgs, setEditedArgs] = useState<Record<string, any>>({});
  const [rejectFeedback, setRejectFeedback] = useState("");
  const [frequencyUnit, setFrequencyUnit] = useState<'hours' | 'minutes'>('hours');

  // Extract action requests from interrupt data
  const actionRequests: (ActionRequest & { interruptId?: string })[] = [];
  interruptData.forEach((interrupt) => {
    const requests = interrupt.value?.action_requests || [];
    requests.forEach((req: ActionRequest) => {
      actionRequests.push({
        ...req,
        action: req.action || req.name || '',
        interruptId: interrupt.id,
      });
    });
  });

  if (actionRequests.length === 0) {
    return (
      <Alert className={className}>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Approval required, but no action details available.
        </AlertDescription>
      </Alert>
    );
  }

  const primaryRequest = actionRequests[0];
  const config = primaryRequest.args || {};

  const handleApprove = () => {
    const decisions: HITLDecision[] = actionRequests.map((req) => ({
      type: 'approve',
      interrupt_id: req.interruptId,
    }));
    onDecision(decisions);
  };

  const handleEdit = () => {
    // Initialize edited args with current config
    setEditedArgs({ ...config });
    setShowEditDialog(true);
  };

  const handleConfirmEdit = () => {
    const decisions: HITLDecision[] = actionRequests.map((req) => ({
      type: 'edit',
      interrupt_id: req.interruptId,
      action: req.action || req.name,
      args: editedArgs,
    }));
    onDecision(decisions);
    setShowEditDialog(false);
  };

  const handleReject = () => {
    setShowRejectDialog(true);
  };

  const handleConfirmReject = () => {
    const decisions: HITLDecision[] = actionRequests.map((req) => ({
      type: 'reject',
      interrupt_id: req.interruptId,
      feedback: rejectFeedback || 'User rejected the configuration',
    }));
    onDecision(decisions);
    setShowRejectDialog(false);
  };

  const toggleAspect = (aspect: string) => {
    const currentAspects = editedArgs.aspects || [];
    const newAspects = currentAspects.includes(aspect)
      ? currentAspects.filter((a: string) => a !== aspect)
      : [...currentAspects, aspect];
    setEditedArgs({ ...editedArgs, aspects: newAspects });
  };

  return (
    <>
      <Card className={className}>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="text-lg">Approval Required</CardTitle>
              <CardDescription>
                {primaryRequest.description || 'Monitoring configuration requires your approval'}
              </CardDescription>
            </div>
            <Badge variant="secondary">Pending</Badge>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Competitor Name */}
          {config.competitor && (
            <div>
              <Label className="text-sm font-semibold">Competitor</Label>
              <p className="text-sm text-muted-foreground">{config.competitor}</p>
            </div>
          )}

          {/* Monitoring Aspects */}
          {config.aspects && (
            <div>
              <Label className="text-sm font-semibold">Monitoring Aspects</Label>
              <div className="mt-1 flex flex-wrap gap-2">
                {config.aspects.map((aspect: string) => (
                  <Badge key={aspect} variant="outline">
                    {aspect}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Frequency */}
          {config.frequency_label && (
            <div>
              <Label className="text-sm font-semibold">Frequency</Label>
              <p className="text-sm text-muted-foreground">{config.frequency_label}</p>
            </div>
          )}

          {/* Cost Estimate */}
          {config.estimated_monthly_cost && (
            <div>
              <Label className="text-sm font-semibold">Estimated Cost</Label>
              <p className="text-sm text-muted-foreground">
                {config.estimated_monthly_cost} ({config.estimated_runs_per_month} runs/month)
              </p>
            </div>
          )}

          {/* Notification Preference */}
          {config.notification_preference && (
            <div>
              <Label className="text-sm font-semibold">Notifications</Label>
              <p className="text-sm text-muted-foreground capitalize">
                {config.notification_preference.replace('_', ' ')}
              </p>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex gap-2">
          <Button onClick={handleApprove} className="flex-1" size="sm">
            <Check className="mr-2 h-4 w-4" />
            Approve
          </Button>
          <Button onClick={handleEdit} variant="outline" className="flex-1" size="sm">
            <Edit2 className="mr-2 h-4 w-4" />
            Edit
          </Button>
          <Button onClick={handleReject} variant="destructive" className="flex-1" size="sm">
            <X className="mr-2 h-4 w-4" />
            Reject
          </Button>
        </CardFooter>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Monitoring Configuration</DialogTitle>
            <DialogDescription>
              Modify the settings before approval
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Competitor */}
            <div className="space-y-2">
              <Label htmlFor="edit-competitor">Competitor</Label>
              <Input
                id="edit-competitor"
                value={editedArgs.competitor || ''}
                onChange={(e) => setEditedArgs({ ...editedArgs, competitor: e.target.value })}
              />
            </div>

            {/* Aspects */}
            <div className="space-y-2">
              <Label>Monitoring Aspects</Label>
              <div className="space-y-2">
                {['products', 'pricing', 'news', 'social'].map((aspect) => (
                  <div key={aspect} className="flex items-center space-x-2">
                    <Checkbox
                      id={`aspect-${aspect}`}
                      checked={(editedArgs.aspects || []).includes(aspect)}
                      onCheckedChange={() => toggleAspect(aspect)}
                    />
                    <label
                      htmlFor={`aspect-${aspect}`}
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 capitalize"
                    >
                      {aspect}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Frequency */}
            <div className="space-y-2">
              <Label htmlFor="edit-frequency">Frequency (hours)</Label>
              <div className="space-y-2">
                <select
                  id="edit-frequency-preset"
                  value={
                    editedArgs.frequency_hours === '' || 
                    ![1, 2, 6, 12, 24].includes(Number(editedArgs.frequency_hours))
                      ? 'custom'
                      : editedArgs.frequency_hours
                  }
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === 'custom') {
                      setEditedArgs({ ...editedArgs, frequency_hours: '' });
                    } else {
                      setEditedArgs({ ...editedArgs, frequency_hours: parseInt(value) });
                    }
                  }}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value={1}>Every hour</option>
                  <option value={2}>Every 2 hours</option>
                  <option value={6}>Every 6 hours</option>
                  <option value={12}>Twice daily</option>
                  <option value={24}>Daily</option>
                  <option value="custom">Custom hours (enter any value)...</option>
                </select>
                {(editedArgs.frequency_hours === '' || ![1, 2, 6, 12, 24].includes(Number(editedArgs.frequency_hours))) && (
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="edit-frequency-unit" className="text-xs text-muted-foreground">
                        Unit
                      </Label>
                      <select
                        id="edit-frequency-unit"
                        value={frequencyUnit}
                        onChange={(e) => setFrequencyUnit(e.target.value as 'hours' | 'minutes')}
                        className="rounded-md border border-input bg-background px-2 py-1 text-xs ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      >
                        <option value="hours">Hours</option>
                        <option value="minutes">Minutes</option>
                      </select>
                    </div>
                    <Input
                      id="edit-frequency-custom"
                      type="number"
                      min={frequencyUnit === 'minutes' ? "1" : "0.0167"}
                      step={frequencyUnit === 'minutes' ? "1" : "0.0167"}
                      placeholder={
                        frequencyUnit === 'minutes'
                          ? "Enter minutes (e.g., 5, 15, 30)"
                          : "Enter hours (e.g., 0.5, 1, 3, 8, 24)"
                      }
                      value={
                        editedArgs.frequency_hours === ''
                          ? ''
                          : frequencyUnit === 'minutes'
                            ? Math.round(Number(editedArgs.frequency_hours) * 60)
                            : editedArgs.frequency_hours
                      }
                      onChange={(e) => {
                        const raw = parseFloat(e.target.value);
                        if (Number.isNaN(raw)) {
                          setEditedArgs({ ...editedArgs, frequency_hours: '' });
                          return;
                        }
                        const hoursValue = frequencyUnit === 'minutes' ? raw / 60 : raw;
                        setEditedArgs({ ...editedArgs, frequency_hours: hoursValue });
                      }}
                    />
                    <p className="text-xs text-muted-foreground">Minimum: 1 minute. Enter any custom interval.</p>
                  </div>
                )}
              </div>
            </div>

            {/* Notification Preference */}
            <div className="space-y-2">
              <Label htmlFor="edit-notifications">Notifications</Label>
              <div className="space-y-2">
                <select
                  id="edit-notifications"
                  value={
                    ['always', 'significant_only', 'never'].includes(editedArgs.notification_preference || 'significant_only')
                      ? editedArgs.notification_preference || 'significant_only'
                      : 'custom'
                  }
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === 'custom') {
                      setEditedArgs({ ...editedArgs, notification_preference: '' });
                    } else {
                      setEditedArgs({ ...editedArgs, notification_preference: value });
                    }
                  }}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="always">Always</option>
                  <option value="significant_only">Significant Only</option>
                  <option value="never">Never</option>
                  <option value="custom">Custom preference (enter your own)...</option>
                </select>
                {!['always', 'significant_only', 'never'].includes(editedArgs.notification_preference || 'significant_only') && (
                  <div className="space-y-1">
                    <Input
                      id="edit-notifications-custom"
                      type="text"
                      placeholder="e.g., critical_only, daily_summary, weekly_digest"
                      value={editedArgs.notification_preference || ''}
                      onChange={(e) => setEditedArgs({ ...editedArgs, notification_preference: e.target.value })}
                    />
                    <p className="text-xs text-muted-foreground">Enter any custom notification preference</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleConfirmEdit}>
              Approve Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Reject Configuration</DialogTitle>
            <DialogDescription>
              Provide feedback on why you're rejecting this configuration (optional)
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-2">
            <Label htmlFor="reject-feedback">Feedback</Label>
            <Textarea
              id="reject-feedback"
              placeholder="e.g., Too expensive, not the right competitor, etc."
              value={rejectFeedback}
              onChange={(e) => setRejectFeedback(e.target.value)}
              rows={4}
            />
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRejectDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleConfirmReject}>
              Confirm Rejection
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
