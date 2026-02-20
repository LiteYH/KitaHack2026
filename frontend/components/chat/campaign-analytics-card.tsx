"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { 
  DollarSign, 
  Target, 
  MousePointer, 
  TrendingUp, 
  Edit, 
  Pause, 
  Play,
  Eye
} from "lucide-react"
import { updateCampaign } from "@/lib/api/campaigns"
import { useAuth } from "@/contexts/AuthContext"

interface Campaign {
  id?: string
  campaignName: string
  platform: string
  status: string
  totalBudget: number
  amountSpent: number
  impressions: number
  clicks: number
  purchases: number
  conversionValue: number
}

interface CampaignMetrics {
  ctr: number
  cvr: number
  roas: number
  budget_utilization: number
  cost_per_click: number
  cost_per_conversion: number
}

interface CampaignAnalyticsCardProps {
  campaigns: Campaign[]
  metrics: CampaignMetrics[]
  summary: any
  type: 'analytics' | 'edit_request'
}

export function CampaignAnalyticsCard({ campaigns, metrics, summary, type }: CampaignAnalyticsCardProps) {
  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null)
  const [newBudget, setNewBudget] = useState<string>("")
  const [isUpdating, setIsUpdating] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [localCampaigns, setLocalCampaigns] = useState<Campaign[]>(campaigns)
  const [localMetrics, setLocalMetrics] = useState<CampaignMetrics[]>(metrics)
  const { user } = useAuth()

  // Calculate metrics from ongoing campaigns only (always)
  const ongoingCampaigns = localCampaigns.filter(c => c.status === 'ongoing')
  const ongoingMetrics = ongoingCampaigns.map((_, idx) => {
    const originalIdx = localCampaigns.findIndex(c => c.id === ongoingCampaigns[idx].id)
    return localMetrics[originalIdx]
  })

  // Calculate summary from ongoing campaigns
  const calculatedSummary = {
    total_conversion_value: ongoingCampaigns.reduce((sum, c) => sum + (c.conversionValue || 0), 0),
    total_purchases: ongoingCampaigns.reduce((sum, c) => sum + (c.purchases || 0), 0),
    total_spent: ongoingCampaigns.reduce((sum, c) => sum + (c.amountSpent || 0), 0),
    overall_ctr: ongoingMetrics.length > 0 
      ? ongoingMetrics.reduce((sum, m) => sum + m.ctr, 0) / ongoingMetrics.length 
      : 0,
    overall_roas: ongoingCampaigns.reduce((sum, c) => sum + (c.amountSpent || 0), 0) > 0
      ? ongoingCampaigns.reduce((sum, c) => sum + (c.conversionValue || 0), 0) / ongoingCampaigns.reduce((sum, c) => sum + (c.amountSpent || 0), 0)
      : 0
  }

  // Filter campaigns based on status
  const filteredCampaigns = statusFilter === "all" 
    ? localCampaigns 
    : localCampaigns.filter(c => c.status === statusFilter)
  
  const filteredMetrics = filteredCampaigns.map(campaign => {
    const idx = localCampaigns.findIndex(c => c.id === campaign.id)
    return localMetrics[idx]
  })

  const handleEditBudget = (campaign: Campaign) => {
    setEditingCampaign(campaign)
    setNewBudget(campaign.totalBudget.toString())
  }

  const handleSaveBudget = async () => {
    if (!editingCampaign || !newBudget || !user?.uid || !editingCampaign.id) return

    try {
      setIsUpdating(true)
      
      const updatedCampaign = await updateCampaign(
        editingCampaign.id,
        user.uid,
        { totalBudget: parseFloat(newBudget) }
      )

      // Update local state instead of reloading
      setLocalCampaigns(localCampaigns.map(c => 
        c.id === editingCampaign.id ? { ...c, totalBudget: updatedCampaign.totalBudget } : c
      ))

      setEditingCampaign(null)
      setNewBudget("")
    } catch (error) {
      console.error("Failed to update budget:", error)
      alert("Failed to update campaign budget. Please try again.")
    } finally {
      setIsUpdating(false)
    }
  }

  const handleToggleStatus = async (campaign: Campaign) => {
    if (!user?.uid || !campaign.id) return

    const newStatus = campaign.status === "ongoing" ? "paused" : "ongoing"
    
    try {
      setIsUpdating(true)
      
      const updatedCampaign = await updateCampaign(
        campaign.id,
        user.uid,
        { status: newStatus }
      )

      // Update local state instead of reloading
      setLocalCampaigns(localCampaigns.map(c => 
        c.id === campaign.id ? { ...c, status: updatedCampaign.status } : c
      ))
    } catch (error) {
      console.error("Failed to toggle status:", error)
      alert("Failed to update campaign status. Please try again.")
    } finally {
      setIsUpdating(false)
    }
  }

  return (
    <Card className="mt-3 mb-2 border-primary/20 bg-primary/5">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Campaign Performance Overview
            </CardTitle>
            <CardDescription className="text-xs mt-1">
              {filteredCampaigns.length} campaign{filteredCampaigns.length !== 1 ? 's' : ''} • 
              {type === 'edit_request' ? ' Click below to edit' : ' Real-time metrics'}
            </CardDescription>
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[130px] h-8 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Campaigns</SelectItem>
              <SelectItem value="ongoing">Ongoing</SelectItem>
              <SelectItem value="paused">Paused</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Summary Cards - Always based on ongoing campaigns */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <div className="bg-card rounded-lg p-3 border">
            <div className="flex items-center gap-2 mb-1">
              <DollarSign className="h-3 w-3 text-green-500" />
              <span className="text-xs text-muted-foreground">Revenue (Ongoing)</span>
            </div>
            <div className="text-lg font-bold">${calculatedSummary.total_conversion_value?.toLocaleString() || 0}</div>
          </div>
          <div className="bg-card rounded-lg p-3 border">
            <div className="flex items-center gap-2 mb-1">
              <Target className="h-3 w-3 text-blue-500" />
              <span className="text-xs text-muted-foreground">ROAS (Ongoing)</span>
            </div>
            <div className="text-lg font-bold">{calculatedSummary.overall_roas?.toFixed(2) || 0}x</div>
          </div>
          <div className="bg-card rounded-lg p-3 border">
            <div className="flex items-center gap-2 mb-1">
              <MousePointer className="h-3 w-3 text-purple-500" />
              <span className="text-xs text-muted-foreground">CTR (Ongoing)</span>
            </div>
            <div className="text-lg font-bold">{calculatedSummary.overall_ctr?.toFixed(2) || 0}%</div>
          </div>
          <div className="bg-card rounded-lg p-3 border">
            <div className="flex items-center gap-2 mb-1">
              <Eye className="h-3 w-3 text-orange-500" />
              <span className="text-xs text-muted-foreground">Conversions (Ongoing)</span>
            </div>
            <div className="text-lg font-bold">{calculatedSummary.total_purchases?.toLocaleString() || 0}</div>
          </div>
        </div>

        {/* Campaign List - Filtered by status */}
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {filteredCampaigns.map((campaign, index) => {
            const metric = filteredMetrics[index]
            return (
              <Card key={campaign.id || index} className="overflow-hidden">
                <CardContent className="p-3">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-sm truncate">{campaign.campaignName}</h4>
                        <Badge 
                          variant={campaign.status === 'ongoing' ? 'default' : 'secondary'}
                          className="text-xs"
                        >
                          {campaign.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">{campaign.platform}</p>
                    </div>
                    {type === 'edit_request' && (
                      <div className="flex gap-1 ml-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-7 px-2"
                          onClick={() => handleEditBudget(campaign)}
                          disabled={isUpdating}
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-7 px-2"
                          onClick={() => handleToggleStatus(campaign)}
                          disabled={isUpdating}
                        >
                          {campaign.status === 'ongoing' ? (
                            <Pause className="h-3 w-3" />
                          ) : (
                            <Play className="h-3 w-3" />
                          )}
                        </Button>
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-muted-foreground">Budget:</span>{" "}
                      <span className="font-medium">${campaign.totalBudget.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Spent:</span>{" "}
                      <span className="font-medium">${campaign.amountSpent.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">ROAS:</span>{" "}
                      <span className="font-medium">{metric.roas.toFixed(2)}x</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">CTR:</span>{" "}
                      <span className="font-medium">{metric.ctr.toFixed(2)}%</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Conversions:</span>{" "}
                      <span className="font-medium">{campaign.purchases.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Revenue:</span>{" "}
                      <span className="font-medium">${campaign.conversionValue.toLocaleString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Edit Budget Dialog */}
        <Dialog open={!!editingCampaign} onOpenChange={(open) => !open && setEditingCampaign(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Campaign Budget</DialogTitle>
              <DialogDescription>
                Update the total budget for {editingCampaign?.campaignName}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="budget">Total Budget ($)</Label>
                <Input
                  id="budget"
                  type="number"
                  value={newBudget}
                  onChange={(e) => setNewBudget(e.target.value)}
                  placeholder="Enter new budget"
                  min="0"
                  step="100"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setEditingCampaign(null)} disabled={isUpdating}>
                Cancel
              </Button>
              <Button onClick={handleSaveBudget} disabled={isUpdating || !newBudget}>
                {isUpdating ? "Saving..." : "Save Changes"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  )
}
