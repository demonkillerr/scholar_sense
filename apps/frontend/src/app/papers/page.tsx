'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { Paper } from '@/lib/types';
import Link from 'next/link';

export default function PapersPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    loadPapers();
  }, []);

  const loadPapers = async () => {
    try {
      setIsLoading(true);
      const papersList = await api.listPapers();
      setPapers(papersList);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load papers');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (paperId: string, title: string) => {
    if (!confirm(`Are you sure you want to delete "${title}"?`)) {
      return;
    }

    setDeletingId(paperId);
    try {
      await api.deletePaper(paperId);
      setPapers((prev) => prev.filter((p) => p.paper_id !== paperId));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete paper');
    } finally {
      setDeletingId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <svg className="animate-spin h-12 w-12 mx-auto text-blue-600" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <p className="mt-4 text-gray-600">Loading papers...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Paper Library</h1>
            <p className="text-lg text-gray-600">
              Manage your uploaded academic papers
            </p>
          </div>
          <Link
            href="/"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            + Upload New Paper
          </Link>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Papers Grid */}
        {papers.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {papers.map((paper) => (
              <div
                key={paper.paper_id}
                className="bg-white p-6 rounded-lg border shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {paper.title}
                    </h3>
                    {paper.authors && (
                      <p className="text-sm text-gray-600 mb-2">
                        👤 {paper.authors}
                      </p>
                    )}
                    <div className="flex gap-4 text-sm text-gray-500">
                      {paper.year && <span>📅 {paper.year}</span>}
                      <span>
                        🕒 {new Date(paper.upload_date).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 mt-4">
                  <Link
                    href={`/query?paper_id=${paper.paper_id}`}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center text-sm font-medium"
                  >
                    Query
                  </Link>
                  <button
                    onClick={() => handleDelete(paper.paper_id, paper.title)}
                    disabled={deletingId === paper.paper_id}
                    className="px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium disabled:opacity-50"
                  >
                    {deletingId === paper.paper_id ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center p-12 bg-white rounded-lg border">
            <div className="text-6xl mb-4">📚</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Papers Yet
            </h3>
            <p className="text-gray-600 mb-6">
              Start by uploading some academic papers to build your library
            </p>
            <Link
              href="/"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload Your First Paper
            </Link>
          </div>
        )}

        {/* Stats */}
        {papers.length > 0 && (
          <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-2">Library Stats</h3>
            <div className="flex gap-6 text-sm text-blue-800">
              <span>📚 {papers.length} paper(s)</span>
              <span>
                📅 Latest:{' '}
                {new Date(
                  Math.max(...papers.map((p) => new Date(p.upload_date).getTime()))
                ).toLocaleDateString()}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
