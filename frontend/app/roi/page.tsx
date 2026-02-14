"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Sidebar } from "@/components/chat/sidebar";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import { 
  TrendingUp, TrendingDown, DollarSign, Eye, Video, 
  Target, Activity, Award, Calendar, Percent 
} from 'lucide-react';

interface Analytics {
  overview: {
    total_videos: number;
    total_views: number;
    total_revenue: number;
    total_cost: number;
    total_profit: number;
    overall_roi: number;
    avg_revenue_per_video: number;
    avg_roi_per_video: number;
  };
  revenue_breakdown: {
    ad_revenue: number;
    sponsorship_revenue: number;
    affiliate_revenue: number;
    ad_revenue_percent: number;
    sponsorship_percent: number;
    affiliate_percent: number;
  };
  cost_breakdown: {
    production_cost: number;
    promotion_cost: number;
    production_percent: number;
    promotion_percent: number;
  };
  engagement: {
    total_likes: number;
    total_comments: number;
    total_shares: number;
    total_subscribers_gained: number;
    avg_retention_rate: number;
    avg_ctr: number;
  };
  top_performers: {
    best_roi_video: {
      title: string;
      roi: number;
      profit: number;
    };
    most_viewed_video: {
      title: string;
      views: number;
      revenue: number;
    };
  };
  monthly_trend: Array<{
    month: string;
    revenue: number;
    cost: number;
    profit: number;
    views: number;
  }>;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function ROIAnalyticsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/auth/signin');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      fetchAnalytics();
    }
  }, [user]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const token = await user?.getIdToken();
      
      const response = await fetch('http://localhost:8000/api/v1/roi/analytics/summary', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch analytics');
      }

      const data = await response.json();
      if (data.success && data.analytics) {
        setAnalytics(data.analytics);
      } else {
        setError('No ROI data available');
      }
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  if (authLoading || loading) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen overflow-hidden bg-background">
          <Sidebar />
          <main className="flex flex-1 flex-col overflow-hidden">
                    <div className="flex items-center justify-center flex-1">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                <p className="mt-4 text-muted-foreground">Loading analytics...</p>
              </div>
                    </div>
          </main>
        </div>
      </ProtectedRoute>
    );
  }

  if (error || !analytics) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen overflow-hidden bg-background">
          <Sidebar />
          <main className="flex flex-1 flex-col overflow-hidden">
                    <div className="flex items-center justify-center flex-1">
              <Card className="w-full max-w-md">
                <CardHeader>
                  <CardTitle>No Data Available</CardTitle>
                  <CardDescription>{error || 'Unable to load analytics'}</CardDescription>
                </CardHeader>
              </Card>
                    </div>
          </main>
        </div>
      </ProtectedRoute>
    );
  }

  const { overview, revenue_breakdown, cost_breakdown, engagement, top_performers, monthly_trend } = analytics;

  // Prepare revenue sources data for pie chart
  const revenueSourcesData = [
    { name: 'Ad Revenue', value: revenue_breakdown.ad_revenue },
    { name: 'Sponsorships', value: revenue_breakdown.sponsorship_revenue },
    { name: 'Affiliate', value: revenue_breakdown.affiliate_revenue },
  ].filter(item => item.value > 0);

  // Prepare cost breakdown data for pie chart
  const costBreakdownData = [
    { name: 'Production', value: cost_breakdown.production_cost },
    { name: 'Promotion', value: cost_breakdown.promotion_cost },
  ];

  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <main className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-auto">
                    <div className="container mx-auto p-6 space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold tracking-tight">YouTube ROI Analytics</h1>
                  <p className="text-muted-foreground">Comprehensive analysis of your video performance and profitability</p>
                </div>
                <button
                  onClick={fetchAnalytics}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                >
                  Refresh Data
                </button>
              </div>

              {/* Key Metrics Cards */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                    <DollarSign className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">{formatCurrency(overview.total_revenue)}</div>
                    <p className="text-xs text-muted-foreground">
                      {formatCurrency(overview.avg_revenue_per_video)} per video
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
                    <TrendingDown className="h-4 w-4 text-red-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-red-600">{formatCurrency(overview.total_cost)}</div>
                    <p className="text-xs text-muted-foreground">
                      Production + Marketing
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Net Profit</CardTitle>
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                  </CardHeader>
                  <CardContent>
                    <div className={`text-2xl font-bold ${overview.total_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(overview.total_profit)}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Revenue - Costs
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Overall ROI</CardTitle>
                    <Percent className="h-4 w-4 text-purple-600" />
                  </CardHeader>
                  <CardContent>
                    <div className={`text-2xl font-bold ${overview.overall_roi >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {overview.overall_roi.toFixed(1)}%
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Return on Investment
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Additional Metrics */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Videos</CardTitle>
                    <Video className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{overview.total_videos}</div>
                      <p className="text-xs text-muted-foreground">Published content</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Views</CardTitle>
                    <Eye className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{formatNumber(overview.total_views)}</div>
                      <p className="text-xs text-muted-foreground">Channel reach</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Avg ROI/Video</CardTitle>
                    <Target className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{overview.avg_roi_per_video.toFixed(1)}%</div>
                      <p className="text-xs text-muted-foreground">Per video performance</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">New Subscribers</CardTitle>
                    <Activity className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{formatNumber(engagement.total_subscribers_gained)}</div>
                      <p className="text-xs text-muted-foreground">From all videos</p>
                  </CardContent>
                </Card>
              </div>

              {/* Charts Row 1: Revenue vs Cost & ROI Trend */}
      <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Revenue vs Cost Trend</CardTitle>
                    <CardDescription>Monthly comparison of revenue and expenses</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthly_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                <Legend />
                <Bar dataKey="revenue" fill="#10b981" name="Revenue" />
                <Bar dataKey="cost" fill="#ef4444" name="Cost" />
              </BarChart>
            </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Profit Trend</CardTitle>
                    <CardDescription>Net profit over time</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={monthly_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="profit" 
                  stroke="#3b82f6" 
                  fill="#3b82f6" 
                  fillOpacity={0.6}
                  name="Profit"
                />
              </AreaChart>
            </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>

              {/* Charts Row 2: Revenue Sources & Cost Breakdown */}
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Revenue Sources</CardTitle>
                    <CardDescription>Breakdown of income streams</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                <Pie
                  data={revenueSourcesData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                        >
                          {revenueSourcesData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="mt-4 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Ad Revenue:</span>
                        <span className="font-semibold">{formatCurrency(revenue_breakdown.ad_revenue)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Sponsorships:</span>
                        <span className="font-semibold">{formatCurrency(revenue_breakdown.sponsorship_revenue)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Affiliate:</span>
                        <span className="font-semibold">{formatCurrency(revenue_breakdown.affiliate_revenue)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Cost Breakdown</CardTitle>
                    <CardDescription>Expense distribution</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={costBreakdownData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {costBreakdownData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index + 3]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="mt-4 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Production Costs:</span>
                        <span className="font-semibold">{formatCurrency(cost_breakdown.production_cost)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Promotion Costs:</span>
                        <span className="font-semibold">{formatCurrency(cost_breakdown.promotion_cost)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Top Performers */}
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5 text-yellow-500" />
              Best Performing Video
            </CardTitle>
                    <CardDescription>Highest ROI</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                      <p className="font-medium">{top_performers.best_roi_video.title}</p>
                    <div className="flex justify-between text-sm">
              <span>ROI:</span>
              <span className="font-bold text-green-600">{top_performers.best_roi_video.roi.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
              <span>Profit:</span>
              <span className="font-bold">{formatCurrency(top_performers.best_roi_video.profit)}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5 text-blue-500" />
              Most Viewed Video
            </CardTitle>
                    <CardDescription>Highest reach</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                      <p className="font-medium">{top_performers.most_viewed_video.title}</p>
                    <div className="flex justify-between text-sm">
              <span>Views:</span>
              <span className="font-bold">{formatNumber(top_performers.most_viewed_video.views)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
              <span>Revenue:</span>
              <span className="font-bold">{formatCurrency(top_performers.most_viewed_video.revenue)}</span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Engagement Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Engagement Metrics</CardTitle>
          <CardDescription>Audience interaction statistics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold">{formatNumber(engagement.total_likes)}</p>
                      <p className="text-sm text-muted-foreground">Total Likes</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold">{formatNumber(engagement.total_comments)}</p>
                      <p className="text-sm text-muted-foreground">Total Comments</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold">{engagement.avg_retention_rate.toFixed(1)}%</p>
                      <p className="text-sm text-muted-foreground">Avg Retention</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold">{engagement.avg_ctr.toFixed(2)}%</p>
                      <p className="text-sm text-muted-foreground">Avg CTR</p>
                    </div>
          </div>
        </CardContent>
      </Card>
                    </div>
          </div>
        </main>
              </div>
    </ProtectedRoute>
  );
}



