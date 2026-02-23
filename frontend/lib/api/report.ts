/**
 * Report API Client
 * Handles ROI report generation and download
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_V1_URL = `${API_BASE_URL}/api/v1`;

/**
 * Download PDF report for a user
 * @param userEmail User's email to filter ROI data
 * @param days Optional number of days to filter (e.g., 7 for last 7 days)
 * @returns Promise that resolves when download starts
 */
export async function downloadPDFReport(userEmail?: string, days?: number): Promise<void> {
  try {
    // Build URL with user_email and days as query parameters if provided
    const url = new URL(`${API_V1_URL}/youtube-report/download/pdf`);
    if (userEmail) {
      url.searchParams.append('user_email', userEmail);
    }
    if (days !== undefined && days !== null) {
      url.searchParams.append('days', days.toString());
    }

    const response = await fetch(url.toString());

    if (!response.ok) {
      throw new Error('Failed to download PDF report');
    }

    // Get filename from Content-Disposition header
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = 'youtube_roi_report.pdf';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    // Download the file
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(a);
  } catch (error) {
    console.error('Download error:', error);
    throw error;
  }
}

/**
 * Download HTML report for a user
 * @param userEmail User's email to filter ROI data
 * @param days Optional number of days to filter (e.g., 7 for last 7 days)
 * @returns Promise that resolves when download starts
 */
export async function downloadHTMLReport(userEmail?: string, days?: number): Promise<void> {
  try {
    const url = new URL(`${API_V1_URL}/youtube-report/download/html`);
    if (userEmail) {
      url.searchParams.append('user_email', userEmail);
    }
    if (days !== undefined && days !== null) {
      url.searchParams.append('days', days.toString());
    }

    const response = await fetch(url.toString());

    if (!response.ok) {
      throw new Error('Failed to download HTML report');
    }

    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = 'youtube_roi_report.html';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(a);
  } catch (error) {
    console.error('Download error:', error);
    throw error;
  }
}

/**
 * Generate report and get all formats (HTML, PDF, TEXT, JSON)
 * @param userEmail User's email to filter ROI data
 * @param days Optional number of days to filter (e.g., 7 for last 7 days)
 * @returns Report data in multiple formats
 */
export async function generateReport(userEmail?: string, days?: number): Promise<any> {
  try {
    const url = new URL(`${API_V1_URL}/youtube-report/generate`);
    if (userEmail) {
      url.searchParams.append('user_email', userEmail);
    }
    if (days !== undefined && days !== null) {
      url.searchParams.append('days', days.toString());
    }

    const response = await fetch(url.toString(), {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to generate report');
    }

    return await response.json();
  } catch (error) {
    console.error('Generate report error:', error);
    throw error;
  }
}
