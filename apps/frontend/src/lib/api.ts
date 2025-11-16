// API client for ScholarSense backend

import type {
  Paper,
  QueryResult,
  UploadResult,
  ComparisonResult,
  ApiResponse,
  RAGStats,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  // Check system status
  async getStatus(): Promise<{ services: Record<string, unknown>; rag_stats: RAGStats | null }> {
    const response = await fetch(`${this.baseUrl}/status`);
    const data = await response.json();
    
    if (data.status === 'error') {
      throw new Error(data.error || 'Failed to get status');
    }
    
    return {
      services: data.services,
      rag_stats: data.rag_stats,
    };
  }

  // Upload a paper
  async uploadPaper(file: File): Promise<UploadResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      body: formData,
    });

    const data: ApiResponse<UploadResult> = await response.json();

    if (data.status === 'error') {
      throw new Error(data.error || 'Failed to upload paper');
    }

    return data.result!;
  }

  // Query papers
  async queryPapers(
    query: string,
    paperIds?: string[],
    nResults: number = 5
  ): Promise<QueryResult> {
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        paper_ids: paperIds,
        n_results: nResults,
      }),
    });

    const data: ApiResponse<QueryResult> = await response.json();

    if (data.status === 'error') {
      throw new Error(data.error || 'Failed to query papers');
    }

    return data.result!;
  }

  // List all papers
  async listPapers(): Promise<Paper[]> {
    const response = await fetch(`${this.baseUrl}/papers`);
    const data: ApiResponse<never> = await response.json();

    if (data.status === 'error') {
      throw new Error(data.error || 'Failed to list papers');
    }

    return data.papers || [];
  }

  // Delete a paper
  async deletePaper(paperId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/papers/${paperId}`, {
      method: 'DELETE',
    });

    const data: ApiResponse<never> = await response.json();

    if (data.status === 'error') {
      throw new Error(data.error || 'Failed to delete paper');
    }
  }

  // Compare papers
  async comparePapers(
    paperIds: string[],
    aspects?: string[]
  ): Promise<ComparisonResult> {
    const response = await fetch(`${this.baseUrl}/compare`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        paper_ids: paperIds,
        aspects: aspects || ['methodology', 'results', 'conclusions', 'limitations'],
      }),
    });

    const data: ApiResponse<ComparisonResult> = await response.json();

    if (data.status === 'error') {
      throw new Error(data.error || 'Failed to compare papers');
    }

    return data.result!;
  }
}

// Export singleton instance
export const api = new ApiClient();
