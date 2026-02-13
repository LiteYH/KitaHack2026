"use client";

import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Clock,
  Pause,
  Play,
  Trash2,
  MoreVertical,
  BarChart3,
  AlertCircle,
  RefreshCw,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

import {
  listCronJobs,
  pauseCronJob,
  resumeCronJob,
  deleteCronJob,
  updateCronJob,
  bulkDeleteCronJobs,
  getCronStats,
  type CronJob,
  type CronStats,
} from "@/lib/api/crons";

/**
 * CronJobsSidebar Component
 * 
 * Displays and manages scheduled monitoring jobs:
 * - List all active/paused jobs
 * - Pause/resume/delete jobs
 * - View job status and next run time
 * - Show error counts
 */
interface CronJobsSidebarProps {
  variant?: "sidebar" | "page";
  className?: string;
}

export function CronJobsSidebar({ variant = "sidebar", className }: CronJobsSidebarProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [jobToDelete, setJobToDelete] = useState<CronJob | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [jobToEdit, setJobToEdit] = useState<CronJob | null>(null);
  const [selectedJobIds, setSelectedJobIds] = useState<Set<string>>(new Set());
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false);
  const [editFrequencyValue, setEditFrequencyValue] = useState<number>(1);
  const [editFrequencyUnit, setEditFrequencyUnit] = useState<'hours' | 'minutes'>('hours');
  const [editAspects, setEditAspects] = useState<string[]>([]);
  const [editNotificationPreference, setEditNotificationPreference] = useState("significant_only");

  // Fetch cron jobs
  const {
    data: jobs,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["cron-jobs"],
    queryFn: listCronJobs,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ["cron-stats"],
    queryFn: getCronStats,
    refetchInterval: 30000,
  });

  // Pause mutation
  const pauseMutation = useMutation({
    mutationFn: pauseCronJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cron-jobs"] });
      queryClient.invalidateQueries({ queryKey: ["cron-stats"] });
      toast({
        title: "Job Paused",
        description: "The monitoring job has been paused.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Resume mutation
  const resumeMutation = useMutation({
    mutationFn: resumeCronJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cron-jobs"] });
      queryClient.invalidateQueries({ queryKey: ["cron-stats"] });
      toast({
        title: "Job Resumed",
        description: "The monitoring job has been resumed.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: deleteCronJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cron-jobs"] });
      queryClient.invalidateQueries({ queryKey: ["cron-stats"] });
      setDeleteDialogOpen(false);
      setJobToDelete(null);
      toast({
        title: "Job Deleted",
        description: "The monitoring job has been deleted permanently.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ jobId, payload }: { jobId: string; payload: { frequency_hours?: number; aspects?: string[]; notification_preference?: string } }) =>
      updateCronJob(jobId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cron-jobs"] });
      queryClient.invalidateQueries({ queryKey: ["cron-stats"] });
      setEditDialogOpen(false);
      setJobToEdit(null);
      toast({
        title: "Job Updated",
        description: "The monitoring job has been updated.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: bulkDeleteCronJobs,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["cron-jobs"] });
      queryClient.invalidateQueries({ queryKey: ["cron-stats"] });
      setBulkDeleteOpen(false);
      setSelectedJobIds(new Set());
      toast({
        title: "Jobs Deleted",
        description: `Deleted ${result.deleted} of ${result.requested} jobs.`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handlePauseResume = (job: CronJob) => {
    if (job.status === "running") {
      pauseMutation.mutate(job.job_id);
    } else if (job.status === "paused") {
      resumeMutation.mutate(job.job_id);
    }
  };

  const handleDeleteClick = (job: CronJob) => {
    setJobToDelete(job);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (jobToDelete) {
      deleteMutation.mutate(jobToDelete.job_id);
    }
  };

  const handleEditClick = (job: CronJob) => {
    setJobToEdit(job);
    const isMinutes = job.frequency_hours < 1;
    setEditFrequencyUnit(isMinutes ? 'minutes' : 'hours');
    setEditFrequencyValue(isMinutes ? Math.round(job.frequency_hours * 60) : job.frequency_hours);
    setEditAspects(job.aspects || []);
    setEditNotificationPreference(job.notification_preference || "significant_only");
    setEditDialogOpen(true);
  };

  const handleEditConfirm = () => {
    if (!jobToEdit) return;
    const frequencyHours = editFrequencyUnit === 'minutes'
      ? editFrequencyValue / 60
      : editFrequencyValue;
    updateMutation.mutate({
      jobId: jobToEdit.job_id,
      payload: {
        frequency_hours: frequencyHours,
        aspects: editAspects,
        notification_preference: editNotificationPreference,
      },
    });
  };

  const handleToggleSelect = (jobId: string) => {
    setSelectedJobIds((prev) => {
      const next = new Set(prev);
      if (next.has(jobId)) {
        next.delete(jobId);
      } else {
        next.add(jobId);
      }
      return next;
    });
  };

  const handleSelectAll = () => {
    if (!jobs || jobs.length === 0) return;
    setSelectedJobIds((prev) => {
      if (prev.size === jobs.length) {
        return new Set();
      }
      return new Set(jobs.map((job) => job.job_id));
    });
  };

  const handleBulkDelete = () => {
    if (selectedJobIds.size === 0) return;
    bulkDeleteMutation.mutate(Array.from(selectedJobIds));
  };

  const formatRelativeTime = (dateString?: string) => {
    if (!dateString) return "Unknown";
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return "Now";
    if (diffMins < 60) return `in ${diffMins}m`;
    if (diffHours < 24) return `in ${diffHours}h`;
    return `in ${diffDays}d`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running":
        return "bg-green-500/10 text-green-500 border-green-500/20";
      case "paused":
        return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
      case "failed":
        return "bg-red-500/10 text-red-500 border-red-500/20";
      default:
        return "bg-muted text-muted-foreground border-border";
    }
  };

  const getFrequencyLabel = (frequencyHours: number) => {
    if (frequencyHours < 1) {
      return `Every ${Math.round(frequencyHours * 60)} min`;
    }
    return `Every ${frequencyHours}h`;
  };

  return (
    <div
      className={cn(
        "flex flex-col h-full",
        variant === "sidebar"
          ? "w-80 border-r border-border bg-background"
          : "w-full bg-card border border-border rounded-xl",
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-500" />
            Monitoring Jobs
          </h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => refetch()}
            className="h-8 w-8"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>

        {jobs && jobs.length > 0 && (
          <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
            <div className="flex items-center gap-2">
              <Checkbox
                checked={selectedJobIds.size > 0 && selectedJobIds.size === jobs.length}
                onCheckedChange={handleSelectAll}
              />
              <span>Select all</span>
            </div>
            <Button
              variant="destructive"
              size="sm"
              disabled={selectedJobIds.size === 0}
              onClick={() => setBulkDeleteOpen(true)}
            >
              Delete ({selectedJobIds.size})
            </Button>
          </div>
        )}

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="text-center p-2 bg-muted rounded">
              <div className="text-muted-foreground">Active</div>
              <div className="text-green-500 font-semibold">{stats.active}</div>
            </div>
            <div className="text-center p-2 bg-muted rounded">
              <div className="text-muted-foreground">Paused</div>
              <div className="text-yellow-500 font-semibold">{stats.paused}</div>
            </div>
            <div className="text-center p-2 bg-muted rounded">
              <div className="text-muted-foreground">Failed</div>
              <div className="text-red-500 font-semibold">{stats.failed}</div>
            </div>
          </div>
        )}
      </div>

      {/* Job List */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {isLoading ? (
            <div className="text-center text-muted-foreground py-8">
              Loading jobs...
            </div>
          ) : error ? (
            <div className="text-center text-red-500 py-8">
              <AlertCircle className="w-8 h-8 mx-auto mb-2" />
              <p className="text-sm">Failed to load jobs</p>
            </div>
          ) : !jobs || jobs.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p className="text-sm">No monitoring jobs yet</p>
              <p className="text-xs mt-1">
                Set up monitoring in chat to get started
              </p>
            </div>
          ) : (
            jobs.map((job: CronJob) => (
              <Card
                key={job.id}
                className="p-3 hover:border-primary/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-start gap-2 flex-1 min-w-0">
                    <Checkbox
                      checked={selectedJobIds.has(job.job_id)}
                      onCheckedChange={() => handleToggleSelect(job.job_id)}
                      className="mt-1"
                    />
                    <div className="min-w-0">
                      <div className="font-semibold text-sm truncate">
                        {job.competitor}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {getFrequencyLabel(job.frequency_hours)}
                      </div>
                    </div>
                  </div>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 -mr-2"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => handleEditClick(job)}>
                        <Clock className="w-4 h-4 mr-2" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => handlePauseResume(job)}
                        disabled={pauseMutation.isPending || resumeMutation.isPending}
                      >
                        {job.status === "running" ? (
                          <>
                            <Pause className="w-4 h-4 mr-2" />
                            Pause
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4 mr-2" />
                            Resume
                          </>
                        )}
                      </DropdownMenuItem>
                      <DropdownMenuItem disabled>
                        <BarChart3 className="w-4 h-4 mr-2" />
                        View Results
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        className="text-red-500 focus:text-red-500"
                        onClick={() => handleDeleteClick(job)}
                        disabled={deleteMutation.isPending}
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>

                {/* Aspects */}
                <div className="flex flex-wrap gap-1 mb-2">
                  {job.aspects.map((aspect: string) => (
                    <Badge
                      key={aspect}
                      variant="outline"
                      className="text-xs px-2 py-0 h-5"
                    >
                      {aspect}
                    </Badge>
                  ))}
                </div>

                {/* Status and Next Run */}
                <div className="flex items-center justify-between text-xs">
                  <Badge
                    variant="outline"
                    className={`${getStatusColor(job.status)} text-xs`}
                  >
                    {job.status}
                  </Badge>
                  <span className="text-muted-foreground">
                    Next: {formatRelativeTime(job.next_run)}
                  </span>
                </div>

                {/* Error indicator */}
                {job.error_count > 0 && (
                  <div className="mt-2 text-xs text-red-400 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" />
                    {job.error_count} error{job.error_count > 1 ? "s" : ""}
                  </div>
                )}
              </Card>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Monitoring Job</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete the monitoring job for{" "}
              <strong>{jobToDelete?.competitor}</strong>? This action cannot be
              undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Job Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Monitoring Job</DialogTitle>
            <DialogDescription>
              Update schedule and preferences for {jobToEdit?.competitor}.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Frequency</Label>
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  min={editFrequencyUnit === 'minutes' ? "1" : "0.0167"}
                  step={editFrequencyUnit === 'minutes' ? "1" : "0.0167"}
                  value={editFrequencyValue}
                  onChange={(e) => setEditFrequencyValue(Number(e.target.value))}
                />
                <select
                  value={editFrequencyUnit}
                  onChange={(e) => setEditFrequencyUnit(e.target.value as 'hours' | 'minutes')}
                  className="rounded-md border border-input bg-background px-2 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="hours">Hours</option>
                  <option value="minutes">Minutes</option>
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Monitoring Aspects</Label>
              <div className="grid grid-cols-2 gap-2">
                {["products", "pricing", "news", "social"].map((aspect) => (
                  <label key={aspect} className="flex items-center gap-2 text-sm">
                    <Checkbox
                      checked={editAspects.includes(aspect)}
                      onCheckedChange={() => {
                        setEditAspects((prev) =>
                          prev.includes(aspect)
                            ? prev.filter((item) => item !== aspect)
                            : [...prev, aspect]
                        );
                      }}
                    />
                    <span className="capitalize">{aspect}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label>Notifications</Label>
              <select
                value={editNotificationPreference}
                onChange={(e) => setEditNotificationPreference(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="always">Always</option>
                <option value="significant_only">Significant Only</option>
                <option value="never">Never</option>
              </select>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleEditConfirm}
              disabled={updateMutation.isPending || editAspects.length === 0}
            >
              {updateMutation.isPending ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Bulk Delete Dialog */}
      <Dialog open={bulkDeleteOpen} onOpenChange={setBulkDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Selected Jobs</DialogTitle>
            <DialogDescription>
              Delete {selectedJobIds.size} monitoring job(s). This cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setBulkDeleteOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleBulkDelete}
              disabled={bulkDeleteMutation.isPending || selectedJobIds.size === 0}
            >
              {bulkDeleteMutation.isPending ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
