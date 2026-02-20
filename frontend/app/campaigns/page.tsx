"use client"

import { useEffect, useState } from "react"
import { Sidebar } from "@/components/chat/sidebar"
import { ChatHeader } from "@/components/chat/chat-header"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { getCampaigns, updateCampaign, type Campaign, type CampaignMetrics } from "@/lib/api/campaigns"
import { useAuth } from "@/contexts/AuthContext"
import {
  LineChart,
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
  Area,
  AreaChart,
  ComposedChart,
} from "recharts"
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  MousePointer,
  Eye,
  Users,
  ArrowUpRight,
  ArrowDownRight,
  Edit,
  Filter,
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface CampaignWithMetrics extends Campaign {
  metrics?: CampaignMetrics
}

// Helper function to calculate metrics for a campaign
const calculateCampaignMetrics = (campaign: Campaign): CampaignMetrics => {
  const ctr = campaign.impressions > 0 ? (campaign.clicks / campaign.impressions) * 100 : 0
  const cvr = campaign.clicks > 0 ? (campaign.purchases / campaign.clicks) * 100 : 0
  const roas = campaign.amountSpent > 0 ? campaign.conversionValue / campaign.amountSpent : 0
  const budgetUtilization = campaign.totalBudget > 0 ? (campaign.amountSpent / campaign.totalBudget) * 100 : 0
  const costPerClick = campaign.clicks > 0 ? campaign.amountSpent / campaign.clicks : 0
  const costPerConversion = campaign.purchases > 0 ? campaign.amountSpent / campaign.purchases : 0

  return {
    campaign_id: campaign.id || '',
    campaign_name: campaign.campaignName,
    ctr,
    cvr,
    roas,
    budget_utilization: budgetUtilization,
    cost_per_click: costPerClick,
    cost_per_conversion: costPerConversion,
  }
}

const COLORS = {
  Instagram: "#E1306C",
  Facebook: "#1877F2",
  "E-commerce": "#00C851",
  KOL: "#FF6B6B",
  TikTok: "#000000",
}

const CHART_COLORS = ["#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#06b6d4"]

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<CampaignWithMetrics[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [displayCount, setDisplayCount] = useState<string>("5")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [editingCampaign, setEditingCampaign] = useState<CampaignWithMetrics | null>(null)
  const [newBudget, setNewBudget] = useState<string>("")
  const [isUpdating, setIsUpdating] = useState(false)
  const { user } = useAuth()

  useEffect(() => {
    const fetchCampaigns = async () => {
      if (!user?.uid) return

      try {
        setIsLoading(true)
        const data = await getCampaigns({ user_id: user.uid })
        // Add calculated metrics to each campaign
        const campaignsWithMetrics = data.campaigns.map(campaign => ({
          ...campaign,
          metrics: calculateCampaignMetrics(campaign)
        }))
        setCampaigns(campaignsWithMetrics)
      } catch (error) {
        console.error("Error fetching campaigns:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchCampaigns()
  }, [user?.uid])

  // Calculate aggregate metrics - only from ONGOING campaigns
  const aggregateMetrics = campaigns
    .filter(c => c.status === 'ongoing')
    .reduce(
      (acc, campaign) => {
        acc.totalSpend += campaign.amountSpent || 0
        acc.totalClicks += campaign.clicks || 0
        acc.totalConversions += campaign.purchases || 0
        acc.totalImpressions += campaign.impressions || 0
        acc.totalRevenue += campaign.conversionValue || 0
        return acc
      },
      {
        totalSpend: 0,
        totalClicks: 0,
        totalConversions: 0,
        totalImpressions: 0,
        totalRevenue: 0,
      }
    )

  const avgCTR =
    aggregateMetrics.totalImpressions > 0
      ? (aggregateMetrics.totalClicks / aggregateMetrics.totalImpressions) * 100
      : 0

  const avgCVR =
    aggregateMetrics.totalClicks > 0
      ? (aggregateMetrics.totalConversions / aggregateMetrics.totalClicks) * 100
      : 0

  const totalROAS =
    aggregateMetrics.totalSpend > 0 ? aggregateMetrics.totalRevenue / aggregateMetrics.totalSpend : 0

  // Calculate trends by comparing ongoing campaigns against ALL campaigns
  const allCampaignsMetrics = campaigns.reduce((acc, c) => {
    acc.revenue += c.conversionValue || 0
    acc.spend += c.amountSpent || 0
    acc.clicks += c.clicks || 0
    acc.impressions += c.impressions || 0
    acc.conversions += c.purchases || 0
    return acc
  }, { revenue: 0, spend: 0, clicks: 0, impressions: 0, conversions: 0 })

  // Calculate all campaigns averages
  const allROAS = allCampaignsMetrics.spend > 0 
    ? allCampaignsMetrics.revenue / allCampaignsMetrics.spend 
    : 0
  const allCTR = allCampaignsMetrics.impressions > 0 
    ? (allCampaignsMetrics.clicks / allCampaignsMetrics.impressions) * 100 
    : 0
  const allAvgRevenue = campaigns.length > 0 ? allCampaignsMetrics.revenue / campaigns.length : 0
  const allAvgConversions = campaigns.length > 0 ? allCampaignsMetrics.conversions / campaigns.length : 0

  // Calculate ongoing campaigns averages
  const ongoingCount = campaigns.filter(c => c.status === 'ongoing').length
  const ongoingAvgRevenue = ongoingCount > 0 ? aggregateMetrics.totalRevenue / ongoingCount : 0
  const ongoingAvgConversions = ongoingCount > 0 ? aggregateMetrics.totalConversions / ongoingCount : 0

  // Calculate percentage differences (ongoing vs all campaigns baseline)
  const revenueTrend = allAvgRevenue > 0 
    ? ((ongoingAvgRevenue - allAvgRevenue) / allAvgRevenue) * 100 
    : 0

  const roasTrend = allROAS > 0
    ? ((totalROAS - allROAS) / allROAS) * 100
    : 0

  const ctrTrend = allCTR > 0
    ? ((avgCTR - allCTR) / allCTR) * 100
    : 0

  const conversionTrend = allAvgConversions > 0
    ? ((ongoingAvgConversions - allAvgConversions) / allAvgConversions) * 100
    : 0

  // Platform distribution data - only from ONGOING campaigns
  const platformData = Object.entries(
    campaigns
      .filter(c => c.status === 'ongoing')
      .reduce((acc, campaign) => {
        const platform = campaign.platform
        if (!acc[platform]) {
          acc[platform] = { platform, budget: 0, count: 0 }
        }
        acc[platform].budget += campaign.totalBudget || 0
        acc[platform].count += 1
        return acc
      }, {} as Record<string, { platform: string; budget: number; count: number }>)
  ).map(([_, data]) => data)

  // Performance trends - separate data for each metric to handle different scales
  const performanceData = campaigns
    .filter((c) => c.status === "ongoing")
    .slice(0, 7)
    .map((campaign) => ({
      name: campaign.campaignName.length > 15 
        ? campaign.campaignName.substring(0, 15) + "..." 
        : campaign.campaignName,
      fullName: campaign.campaignName,
      ROAS: Number((campaign.metrics?.roas || 0).toFixed(2)),
      CTR: Number((campaign.metrics?.ctr || 0).toFixed(2)),
      CVR: Number((campaign.metrics?.cvr || 0).toFixed(2)),
    }))

  // Filter and sort top campaigns based on user selection
  const filteredCampaigns = statusFilter === "all" 
    ? campaigns 
    : campaigns.filter(c => c.status === statusFilter)

  const topCampaigns = [...filteredCampaigns]
    .sort((a, b) => (b.metrics?.roas || 0) - (a.metrics?.roas || 0))
    .slice(0, displayCount === "all" ? filteredCampaigns.length : parseInt(displayCount))

  const handleEditBudget = (campaign: CampaignWithMetrics) => {
    setEditingCampaign(campaign)
    setNewBudget(campaign.totalBudget.toString())
  }

  const handleSaveBudget = async () => {
    if (!editingCampaign || !newBudget || !user?.uid) return

    try {
      setIsUpdating(true)
      
      // Call API to update Firestore
      const updatedCampaign = await updateCampaign(
        editingCampaign.id!,
        user.uid,
        { totalBudget: parseFloat(newBudget) }
      )
      
      // Update local state with new metrics
      const updatedWithMetrics = {
        ...updatedCampaign,
        metrics: calculateCampaignMetrics(updatedCampaign)
      }
      
      setCampaigns(campaigns.map(c => 
        c.id === editingCampaign.id ? updatedWithMetrics : c
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

  const handleToggleStatus = async (campaign: CampaignWithMetrics) => {
    if (!user?.uid || !campaign.id) return

    const newStatus = campaign.status === "ongoing" ? "paused" : "ongoing"
    
    try {
      setIsUpdating(true)
      
      // Call API to update Firestore
      const updatedCampaign = await updateCampaign(
        campaign.id,
        user.uid,
        { status: newStatus }
      )
      
      // Update local state with new metrics
      const updatedWithMetrics = {
        ...updatedCampaign,
        metrics: calculateCampaignMetrics(updatedCampaign)
      }
      
      setCampaigns(campaigns.map(c => 
        c.id === campaign.id ? updatedWithMetrics : c
      ))
    } catch (error) {
      console.error("Failed to toggle status:", error)
      alert("Failed to update campaign status. Please try again.")
    } finally {
      setIsUpdating(false)
    }
  }

  // Custom tooltip for better metric display
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-lg border bg-card p-3 shadow-lg">
          <p className="font-semibold text-foreground">{payload[0]?.payload?.fullName || label}</p>
          <div className="mt-2 space-y-1">
            <p className="text-sm">
              <span className="font-medium text-blue-500">ROAS:</span> {payload[0]?.value}x
            </p>
            <p className="text-sm">
              <span className="font-medium text-purple-500">CTR:</span> {payload[1]?.value}%
            </p>
            <p className="text-sm">
              <span className="font-medium text-pink-500">CVR:</span> {payload[2]?.value}%
            </p>
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <main className="flex flex-1 flex-col overflow-hidden">
          <ChatHeader />

          <div className="flex-1 overflow-y-auto">
            <div className="mx-auto max-w-7xl p-6">
              {/* Header */}
              <div className="mb-6">
                <h1 className="text-3xl font-bold text-foreground">Campaign Analytics</h1>
                <p className="text-sm text-muted-foreground">
                  Real-time insights from Firestore - Showing metrics for ongoing campaigns only | User ID: {user?.uid?.substring(0, 8)}...
                </p>
              </div>

              {isLoading ? (
                <div className="flex h-96 items-center justify-center">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                </div>
              ) : (
                <>
                  {/* Overview Cards */}
                  <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                        <DollarSign className="h-4 w-4 text-green-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          ${aggregateMetrics.totalRevenue.toLocaleString()}
                        </div>
                        <p className="flex items-center text-xs text-muted-foreground">
                          {revenueTrend >= 0 ? (
                            <>
                              <ArrowUpRight className="mr-1 h-3 w-3 text-green-500" />
                              <span className="text-green-500">+{revenueTrend.toFixed(1)}%</span>
                            </>
                          ) : (
                            <>
                              <ArrowDownRight className="mr-1 h-3 w-3 text-red-500" />
                              <span className="text-red-500">{revenueTrend.toFixed(1)}%</span>
                            </>
                          )}
                          <span className="ml-1">vs portfolio avg</span>
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total ROAS</CardTitle>
                        <Target className="h-4 w-4 text-blue-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{totalROAS.toFixed(2)}x</div>
                        <p className="flex items-center text-xs text-muted-foreground">
                          {roasTrend >= 0 ? (
                            <>
                              <ArrowUpRight className="mr-1 h-3 w-3 text-green-500" />
                              <span className="text-green-500">+{roasTrend.toFixed(1)}%</span>
                            </>
                          ) : (
                            <>
                              <ArrowDownRight className="mr-1 h-3 w-3 text-red-500" />
                              <span className="text-red-500">{roasTrend.toFixed(1)}%</span>
                            </>
                          )}
                          <span className="ml-1">vs portfolio avg</span>
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Avg CTR</CardTitle>
                        <MousePointer className="h-4 w-4 text-purple-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{avgCTR.toFixed(2)}%</div>
                        <p className="flex items-center text-xs text-muted-foreground">
                          {ctrTrend >= 0 ? (
                            <>
                              <ArrowUpRight className="mr-1 h-3 w-3 text-green-500" />
                              <span className="text-green-500">+{ctrTrend.toFixed(1)}%</span>
                            </>
                          ) : (
                            <>
                              <ArrowDownRight className="mr-1 h-3 w-3 text-red-500" />
                              <span className="text-red-500">{ctrTrend.toFixed(1)}%</span>
                            </>
                          )}
                          <span className="ml-1">vs portfolio avg</span>
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Conversions</CardTitle>
                        <Users className="h-4 w-4 text-orange-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {aggregateMetrics.totalConversions.toLocaleString()}
                        </div>
                        <p className="flex items-center text-xs text-muted-foreground">
                          {conversionTrend >= 0 ? (
                            <>
                              <ArrowUpRight className="mr-1 h-3 w-3 text-green-500" />
                              <span className="text-green-500">+{conversionTrend.toFixed(1)}%</span>
                            </>
                          ) : (
                            <>
                              <ArrowDownRight className="mr-1 h-3 w-3 text-red-500" />
                              <span className="text-red-500">{conversionTrend.toFixed(1)}%</span>
                            </>
                          )}
                          <span className="ml-1">vs portfolio avg</span>
                        </p>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Charts Row */}
                  <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
                    {/* Performance Trends - Improved with dual Y-axis */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Performance Trends</CardTitle>
                        <CardDescription>ROAS, CTR, and CVR across ongoing campaigns</CardDescription>
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
                              height={60}
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
                        <CardTitle>Platform Distribution</CardTitle>
                        <CardDescription>Budget allocation across platforms</CardDescription>
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
                  <Card className="mb-6">
                    <CardHeader>
                      <CardTitle>Campaign Comparison</CardTitle>
                      <CardDescription>Revenue vs Spend by campaign</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={350}>
                        <BarChart data={topCampaigns.slice(0, 10)}>
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

                  {/* Top Performing Campaigns Table with Filters */}
                  <Card>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle>Top Performing Campaigns</CardTitle>
                          <CardDescription>Sorted by ROAS - Data synced from Firestore</CardDescription>
                        </div>
                        <div className="flex gap-2">
                          <Select value={statusFilter} onValueChange={setStatusFilter}>
                            <SelectTrigger className="w-[140px]">
                              <Filter className="mr-2 h-4 w-4" />
                              <SelectValue placeholder="Filter" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="all">All Campaigns</SelectItem>
                              <SelectItem value="ongoing">Ongoing Only</SelectItem>
                              <SelectItem value="paused">Paused Only</SelectItem>
                            </SelectContent>
                          </Select>

                          <Select value={displayCount} onValueChange={setDisplayCount}>
                            <SelectTrigger className="w-[120px]">
                              <SelectValue placeholder="Show" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="5">Show 5</SelectItem>
                              <SelectItem value="10">Show 10</SelectItem>
                              <SelectItem value="15">Show 15</SelectItem>
                              <SelectItem value="20">Show 20</SelectItem>
                              <SelectItem value="all">Show All</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="relative overflow-x-auto">
                        <table className="w-full text-left text-sm">
                          <thead className="border-b text-xs uppercase text-muted-foreground">
                            <tr>
                              <th scope="col" className="px-6 py-3">
                                Campaign
                              </th>
                              <th scope="col" className="px-6 py-3">
                                Platform
                              </th>
                              <th scope="col" className="px-6 py-3">
                                Status
                              </th>
                              <th scope="col" className="px-6 py-3 text-right">
                                ROAS
                              </th>
                              <th scope="col" className="px-6 py-3 text-right">
                                CTR
                              </th>
                              <th scope="col" className="px-6 py-3 text-right">
                                Revenue
                              </th>
                              <th scope="col" className="px-6 py-3 text-right">
                                Budget
                              </th>
                              <th scope="col" className="px-6 py-3 text-center">
                                Actions
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            {topCampaigns.length === 0 ? (
                              <tr>
                                <td colSpan={8} className="px-6 py-8 text-center text-muted-foreground">
                                  No campaigns found matching the selected filters
                                </td>
                              </tr>
                            ) : (
                              topCampaigns.map((campaign, index) => (
                                <tr key={index} className="border-b bg-card hover:bg-muted/50">
                                  <td className="px-6 py-4 font-medium">{campaign.campaignName}</td>
                                  <td className="px-6 py-4">
                                    <Badge
                                      variant="outline"
                                      style={{
                                        borderColor:
                                          COLORS[campaign.platform as keyof typeof COLORS] || "#3b82f6",
                                        color:
                                          COLORS[campaign.platform as keyof typeof COLORS] || "#3b82f6",
                                      }}
                                    >
                                      {campaign.platform}
                                    </Badge>
                                  </td>
                                  <td className="px-6 py-4">
                                    <Badge
                                      variant={campaign.status === "ongoing" ? "default" : "secondary"}
                                    >
                                      {campaign.status}
                                    </Badge>
                                  </td>
                                  <td className="px-6 py-4 text-right font-semibold">
                                    {campaign.metrics?.roas?.toFixed(2) || "0.00"}x
                                  </td>
                                  <td className="px-6 py-4 text-right">
                                    {campaign.metrics?.ctr?.toFixed(2) || "0.00"}%
                                  </td>
                                  <td className="px-6 py-4 text-right font-semibold text-green-600">
                                    ${campaign.conversionValue?.toLocaleString() || 0}
                                  </td>
                                  <td className="px-6 py-4 text-right text-muted-foreground">
                                    ${campaign.totalBudget?.toLocaleString() || 0}
                                  </td>
                                  <td className="px-6 py-4">
                                    <div className="flex items-center justify-center gap-2">
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => handleEditBudget(campaign)}
                                        disabled={isUpdating}
                                        title="Edit Budget"
                                      >
                                        <Edit className="h-4 w-4" />
                                      </Button>
                                      <Button
                                        variant={campaign.status === "ongoing" ? "default" : "outline"}
                                        size="sm"
                                        onClick={() => handleToggleStatus(campaign)}
                                        disabled={isUpdating}
                                        title={campaign.status === "ongoing" ? "Pause Campaign" : "Resume Campaign"}
                                      >
                                        {campaign.status === "ongoing" ? "Pause" : "Resume"}
                                      </Button>
                                    </div>
                                  </td>
                                </tr>
                              ))
                            )}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                </>
              )}
            </div>
          </div>
        </main>
      </div>

      {/* Edit Budget Dialog */}
      <Dialog open={!!editingCampaign} onOpenChange={() => setEditingCampaign(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Campaign Budget</DialogTitle>
            <DialogDescription>
              Update the total budget for {editingCampaign?.campaignName}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="budget" className="text-right">
                Budget ($)
              </Label>
              <Input
                id="budget"
                type="number"
                value={newBudget}
                onChange={(e) => setNewBudget(e.target.value)}
                className="col-span-3"
                placeholder="Enter new budget"
              />
            </div>
            <div className="rounded-lg bg-muted p-3 text-sm">
              <p className="text-muted-foreground">
                <strong>Current:</strong> ${editingCampaign?.totalBudget.toLocaleString()}
              </p>
              <p className="text-muted-foreground">
                <strong>Spent:</strong> ${editingCampaign?.amountSpent.toLocaleString()}
              </p>
              <p className="text-muted-foreground">
                <strong>Utilization:</strong> {editingCampaign?.metrics?.budget_utilization.toFixed(2)}%
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setEditingCampaign(null)}
              disabled={isUpdating}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleSaveBudget}
              disabled={isUpdating || !newBudget}
            >
              {isUpdating ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </ProtectedRoute>
  )
}
