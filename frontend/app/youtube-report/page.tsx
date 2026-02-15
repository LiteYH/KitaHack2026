"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Loader2, Download, FileText, FileJson, Eye, BarChart3 } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface ReportMetadata {
  generated_at: string;
  user_id: string | null;
  record_count: number;
  total_videos: number;
  overall_roi: number;
}

interface ReportContent {
  html: string;
  pdf_base64: string | null;
  text: string;
  json: string;
}

interface ReportFilenames {
  html: string;
  pdf: string;
  text: string;
  json: string;
}

interface ReportData {
  success: boolean;
  message: string;
  data: ReportContent;
  filenames: ReportFilenames;
  metadata: ReportMetadata;
}

interface PreviewData {
  success: boolean;
  message: string;
  data: {
    record_count: number;
    has_data: boolean;
    preview?: {
      total_views: number;
      total_revenue: number;
      total_ad_spend: number;
      overall_roi: number;
    };
  };
}

export default function YouTubeReportPage() {
  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('preview');

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  // Preview report metadata
  const handlePreview = async () => {
    try {
      setPreviewLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/v1/youtube-report/preview`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch preview data');
      }

      const data: PreviewData = await response.json();
      setPreviewData(data);

      if (!data.data.has_data) {
        setError('No YouTube ROI data found. Please add data to the Firestore collection first.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load preview');
      console.error('Preview error:', err);
    } finally {
      setPreviewLoading(false);
    }
  };

  // Generate full report
  const handleGenerateReport = async () => {
    try {
      setLoading(true);
      setError(null);
      setReportData(null);

      const response = await fetch(`${API_BASE_URL}/api/v1/youtube-report/generate`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to generate report');
      }

      const data: ReportData = await response.json();
      setReportData(data);
      setActiveTab('report');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate report');
      console.error('Generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Download report in specific format
  const handleDownload = async (format: 'html' | 'pdf' | 'text' | 'json') => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/v1/youtube-report/download/${format}`);

      if (!response.ok) {
        throw new Error(`Failed to download ${format.toUpperCase()} report`);
      }

      // Get filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `youtube_report.${format}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      // Download the file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to download ${format.toUpperCase()}`);
      console.error('Download error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Format numbers for display
  const formatNumber = (num: number): string => {
    if (num >= 1_000_000_000) return `${(num / 1_000_000_000).toFixed(1)}B`;
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
    return num.toFixed(0);
  };

  const formatCurrency = (num: number): string => {
    if (num >= 1_000_000_000) return `$${(num / 1_000_000_000).toFixed(1)}B`;
    if (num >= 1_000_000) return `$${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `$${(num / 1_000).toFixed(1)}K`;
    return `$${num.toFixed(2)}`;
  };

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 flex items-center gap-2">
          <BarChart3 className="w-10 h-10 text-red-600" />
          YouTube ROI Report Generator
        </h1>
        <p className="text-muted-foreground">
          Generate comprehensive ROI analysis reports for your YouTube channel performance
        </p>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="preview">Preview Data</TabsTrigger>
          <TabsTrigger value="report">Full Report</TabsTrigger>
        </TabsList>

        <TabsContent value="preview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Data Preview</CardTitle>
              <CardDescription>
                Check your YouTube ROI data before generating a full report
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                onClick={handlePreview}
                disabled={previewLoading}
                className="w-full md:w-auto"
              >
                {previewLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading Preview...
                  </>
                ) : (
                  <>
                    <Eye className="mr-2 h-4 w-4" />
                    Preview Data
                  </>
                )}
              </Button>

              {previewData && previewData.data.has_data && previewData.data.preview && (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mt-6">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Total Records
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {previewData.data.record_count}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Total Views
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-blue-600">
                        {formatNumber(previewData.data.preview.total_views)}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Total Revenue
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-green-600">
                        {formatCurrency(previewData.data.preview.total_revenue)}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Overall ROI
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-purple-600">
                        {previewData.data.preview.overall_roi.toFixed(1)}%
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {previewData && previewData.data.has_data && (
                <Alert className="mt-6">
                  <AlertTitle>Data Available</AlertTitle>
                  <AlertDescription>
                    You have {previewData.data.record_count} YouTube ROI records available. 
                    Click the "Full Report" tab to generate a detailed analysis.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="report" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Generate Full Report</CardTitle>
              <CardDescription>
                Create a comprehensive YouTube ROI analysis report with AI-powered insights
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                onClick={handleGenerateReport}
                disabled={loading}
                size="lg"
                className="w-full md:w-auto"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Report...
                  </>
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    Generate Report
                  </>
                )}
              </Button>

              {reportData && reportData.success && (
                <div className="mt-8 space-y-6">
                  <Alert>
                    <AlertTitle>Report Generated Successfully!</AlertTitle>
                    <AlertDescription>
                      Your YouTube ROI report has been generated with {reportData.metadata.record_count} records 
                      covering {reportData.metadata.total_videos} videos.
                    </AlertDescription>
                  </Alert>

                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">
                          Total Videos
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {reportData.metadata.total_videos}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">
                          Data Records
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {reportData.metadata.record_count}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">
                          Overall ROI
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold text-green-600">
                          {reportData.metadata.overall_roi.toFixed(1)}%
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  <div className="border rounded-lg p-4">
                    <h3 className="text-lg font-semibold mb-4">Download Report</h3>
                    <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
                      <Button
                        onClick={() => handleDownload('html')}
                        variant="outline"
                        className="w-full"
                      >
                        <Download className="mr-2 h-4 w-4" />
                        HTML
                      </Button>

                      <Button
                        onClick={() => handleDownload('pdf')}
                        variant="outline"
                        className="w-full"
                        disabled={!reportData.data.pdf_base64}
                      >
                        <Download className="mr-2 h-4 w-4" />
                        PDF
                      </Button>

                      <Button
                        onClick={() => handleDownload('text')}
                        variant="outline"
                        className="w-full"
                      >
                        <Download className="mr-2 h-4 w-4" />
                        Text
                      </Button>

                      <Button
                        onClick={() => handleDownload('json')}
                        variant="outline"
                        className="w-full"
                      >
                        <FileJson className="mr-2 h-4 w-4" />
                        JSON Data
                      </Button>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4">
                    <h3 className="text-lg font-semibold mb-4">Report Preview</h3>
                    <div 
                      className="bg-white border rounded p-4 max-h-[600px] overflow-auto"
                      dangerouslySetInnerHTML={{ __html: reportData.data.html }}
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
