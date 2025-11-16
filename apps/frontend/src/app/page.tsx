'use client';

import { useState } from 'react';
import { UploadZone } from '@/components/upload-zone';
import type { UploadResult } from '@/lib/types';
import Link from 'next/link';

export default function Home() {
  const [uploadedPapers, setUploadedPapers] = useState<UploadResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleUploadSuccess = (result: UploadResult) => {
    setUploadedPapers((prev) => [result, ...prev]);
    setSuccess(`Successfully uploaded "${result.title}"`);
    setError(null);
    
    // Clear success message after 5 seconds
    setTimeout(() => setSuccess(null), 5000);
  };

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
    setSuccess(null);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Upload Academic Papers
          </h1>
          <p className="text-lg text-gray-600">
            Upload PDF papers to query them with AI-powered citation-grounded answers
          </p>
        </div>

        {/* Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            <strong>Error:</strong> {error}
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
            <strong>Success!</strong> {success}
          </div>
        )}

        {/* Upload Zone */}
        <UploadZone
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
        />

        {/* Recently Uploaded Papers */}
        {uploadedPapers.length > 0 && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Recently Uploaded Papers
            </h2>
            <div className="space-y-4">
              {uploadedPapers.map((paper) => (
                <div
                  key={paper.paper_id}
                  className="bg-white p-6 rounded-lg border shadow-sm"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {paper.title}
                      </h3>
                      <div className="flex gap-6 text-sm text-gray-600">
                        <span>📄 {paper.sections_processed} sections</span>
                        <span>🔢 {paper.chunks_processed} chunks</span>
                        <span>📅 {new Date(paper.upload_date).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <Link
                      href={`/query?paper_id=${paper.paper_id}`}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                    >
                      Query This Paper
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            href="/query"
            className="p-6 bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow text-center"
          >
            <div className="text-4xl mb-3">🔍</div>
            <h3 className="font-semibold text-gray-900 mb-2">Query Papers</h3>
            <p className="text-sm text-gray-600">
              Ask questions across all uploaded papers
            </p>
          </Link>

          <Link
            href="/papers"
            className="p-6 bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow text-center"
          >
            <div className="text-4xl mb-3">📚</div>
            <h3 className="font-semibold text-gray-900 mb-2">Paper Library</h3>
            <p className="text-sm text-gray-600">
              Browse and manage uploaded papers
            </p>
          </Link>

          <Link
            href="/compare"
            className="p-6 bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow text-center"
          >
            <div className="text-4xl mb-3">⚖️</div>
            <h3 className="font-semibold text-gray-900 mb-2">Compare Papers</h3>
            <p className="text-sm text-gray-600">
              Compare methodologies and findings
            </p>
          </Link>
        </div>
      </div>
    </div>
  );
}