"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  ComposedChart,
  Area,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { MessageSquare, BarChart3, X } from "lucide-react"

// Campaign type structure (matching the API)
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

interface CampaignVisualizationProps {
  campaigns: Campaign[]
}

const COLORS = {
  Instagram: "#E1306C",
  Facebook: "#1877F2",
  "E-commerce": "#00C851",
  KOL: "#FF6B6B",
  TikTok: "#000000",
}

const CHART_COLORS = ["#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#06b6d4"]

// Custom tooltip for performance trends
const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-card p-2 shadow-md">
        <p className="text-sm font-semibold">{payload[0].payload.name || 'N/A'}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-xs" style={{ color: entry.color }}>
            {entry.name}: {entry.value?.toFixed(2) || 'N/A'}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export function CampaignVisualization({ campaigns }: CampaignVisualizationProps) {
  const [showVisuals, setShowVisuals] = useState<boolean | null>(null)

  // Filter to ongoing campaigns only for visualizations
  const ongoingCampaigns = campaigns.filter(c => c.status === 'ongoing')

  // Calculate metrics for performance trends
  const calculateMetrics = (campaign: Campaign) => {
    const ctr = campaign.impressions > 0 ? (campaign.clicks / campaign.impressions) * 100 : 0
    const cvr = campaign.clicks > 0 ? (campaign.purchases / campaign.clicks) * 100 : 0
    const roas = campaign.amountSpent > 0 ? campaign.conversionValue / campaign.amountSpent : 0
    return { ctr, cvr, roas }
  }

  // Prepare data for performance trends (top 5 campaigns by ROAS)
  const performanceData = ongoingCampaigns
    .map(campaign => {
      const metrics = calculateMetrics(campaign)
      return {
        name: campaign.campaignName.length > 15 
          ? campaign.campaignName.substring(0, 15) + '...' 
          : campaign.campaignName,
        ROAS: metrics.roas,
        CTR: metrics.ctr,
        CVR: metrics.cvr,
      }
    })
    .sort((a, b) => b.ROAS - a.ROAS)
    .slice(0, 5)

  // Prepare data for platform distribution
  const platformData = Object.entries(
    ongoingCampaigns.reduce((acc, campaign) => {
      const platform = campaign.platform
      if (!acc[platform]) {
        acc[platform] = 0
      }
      acc[platform] += campaign.totalBudget || 0
      return acc
    }, {} as Record<string, number>)
  ).map(([platform, budget]) => ({
    platform,
    budget,
  }))

  // Prepare data for campaign comparison (top 10 by revenue)
  const comparisonData = ongoingCampaigns
    .map(campaign => ({
      campaignName: campaign.campaignName.length > 20 
        ? campaign.campaignName.substring(0, 20) + '...' 
        : campaign.campaignName,
      conversionValue: campaign.conversionValue || 0,
      amountSpent: campaign.amountSpent || 0,
    }))
    .sort((a, b) => b.conversionValue - a.conversionValue)
    .slice(0, 10)

  // Initial permission prompt
  if (showVisuals === null) {
    return (
      <Card className="border-blue-500/20 bg-gradient-to-br from-blue-500/5 to-purple-500/5">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="rounded-full bg-blue-500/10 p-3">
              <BarChart3 className="h-6 w-6 text-blue-500" />
            </div>
            <div className="flex-1 space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-2">
                  Do you want illustrative visualization analysis of the campaigns?
                </h3>
                <p className="text-sm text-muted-foreground">
                  I can show you detailed charts including Performance Trends, Platform Distribution, 
                  and Campaign Comparison to help you visualize your campaign data.
                </p>
              </div>
              <div className="flex gap-3">
                <Button 
                  onClick={() => setShowVisuals(true)}
                  className="bg-blue-500 hover:bg-blue-600"
                >
                  <MessageSquare className="mr-2 h-4 w-4" />
                  Yes, Show Visualizations
                </Button>
                <Button 
                  onClick={() => setShowVisuals(false)}
                  variant="outline"
                >
                  <X className="mr-2 h-4 w-4" />
                  No, Thanks
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // If user declined, don't show anything
  if (showVisuals === false) {
    return null
  }

  // Show full visualizations
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Campaign Visualizations</CardTitle>
              <CardDescription>Detailed analytics for ongoing campaigns</CardDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowVisuals(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Performance Trends */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Performance Trends</CardTitle>
                <CardDescription className="text-xs">
                  Top 5 campaigns by ROAS
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <ComposedChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                    <XAxis 
                      dataKey="name" 
                      className="text-xs" 
                      angle={-15} 
                      textAnchor="end" 
                      height={80}
                    />
                    <YAxis 
                      yAxisId="left" 
                      className="text-xs"
                      label={{ value: 'ROAS (x)', angle: -90, position: 'insideLeft', style: { fontSize: '12px' } }}
                    />
                    <YAxis 
                      yAxisId="right" 
                      orientation="right" 
                      className="text-xs"
                      label={{ value: 'CTR/CVR (%)', angle: 90, position: 'insideRight', style: { fontSize: '12px' } }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Area
                      yAxisId="left"
                      type="monotone"
                      dataKey="ROAS"
                      fill="#3b82f6"
                      stroke="#3b82f6"
                      fillOpacity={0.3}
                      name="ROAS (x)"
                    />
                    <Line 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="CTR" 
                      stroke="#8b5cf6" 
                      strokeWidth={2}
                      name="CTR (%)"
                      dot={{ r: 4 }}
                    />
                    <Line 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="CVR" 
                      stroke="#ec4899" 
                      strokeWidth={2}
                      name="CVR (%)"
                      dot={{ r: 4 }}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Platform Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Platform Distribution</CardTitle>
                <CardDescription className="text-xs">
                  Budget allocation across platforms
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center">
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={platformData}
                        cx="50%"
                        cy="50%"
                        labelLine={true}
                        label={({ platform, percent }) =>
                          `${platform} ${(percent * 100).toFixed(0)}%`
                        }
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="budget"
                      >
                        {platformData.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[entry.platform as keyof typeof COLORS] || CHART_COLORS[index]}
                          />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "hsl(var(--card))",
                          border: "1px solid hsl(var(--border))",
                          borderRadius: "6px",
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Campaign Comparison Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Campaign Comparison</CardTitle>
              <CardDescription className="text-xs">
                Revenue vs Spend by campaign (Top 10)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={comparisonData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis
                    dataKey="campaignName"
                    className="text-xs"
                    angle={-15}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis className="text-xs" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "6px",
                    }}
                  />
                  <Legend />
                  <Bar dataKey="conversionValue" fill="#10b981" name="Revenue" />
                  <Bar dataKey="amountSpent" fill="#f59e0b" name="Spend" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </div>
  )
}
