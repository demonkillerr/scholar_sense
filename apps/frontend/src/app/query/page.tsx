'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import type { QueryResult, Paper } from '@/lib/types';

function QueryPageContent() {
  const searchParams = useSearchParams();
  const [query, setQuery] = useState('');
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedPapers, setSelectedPapers] = useState<string[]>([]);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load papers
    api.listPapers()
      .then(setPapers)
      .catch((err) => setError(err.message));

    // Check if paper_id in URL
    const paperId = searchParams.get('paper_id');
    if (paperId) {
      setSelectedPapers([paperId]);
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const queryResult = await api.queryPapers(
        query,
        selectedPapers.length > 0 ? selectedPapers : undefined,
        5
      );
      setResult(queryResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to query papers');
    } finally {
      setIsLoading(false);
    }
  };

  const togglePaper = (paperId: string) => {
    setSelectedPapers((prev) =>
      prev.includes(paperId)
        ? prev.filter((id) => id !== paperId)
        : [...prev, paperId]
    );
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Query Papers</h1>
          <p className="text-lg text-gray-600">
            Ask questions and get citation-grounded answers from your papers
          </p>
        </div>

        {/* Query Form */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Question
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., What are the main findings of this research?"
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={3}
            />

            {/* Paper Filter */}
            {papers.length > 0 && (
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Filter by Papers (optional)
                </label>
                <div className="flex flex-wrap gap-2">
                  {papers.map((paper) => (
                    <button
                      key={paper.paper_id}
                      type="button"
                      onClick={() => togglePaper(paper.paper_id)}
                      className={`px-3 py-1 text-sm rounded-full transition-colors ${
                        selectedPapers.includes(paper.paper_id)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {paper.title.length > 50
                        ? paper.title.substring(0, 50) + '...'
                        : paper.title}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {selectedPapers.length === 0
                    ? 'Searching all papers'
                    : `Searching ${selectedPapers.length} selected paper(s)`}
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="mt-4 w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
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
                  Searching...
                </span>
              ) : (
                'Search Papers'
              )}
            </button>
          </div>
        </form>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Answer */}
            <div className="bg-white p-6 rounded-lg border shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <div className="text-2xl">💡</div>
                <h2 className="text-2xl font-bold text-gray-900">Answer</h2>
              </div>
              <div className="prose max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
                {result.answer}
              </div>
              <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                <span>🤖 {result.model}</span>
                <span>📝 {result.contexts_used} context(s) used</span>
              </div>
            </div>

            {/* Citations */}
            {result.citations && result.citations.length > 0 && (
              <div className="bg-white p-6 rounded-lg border shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <div className="text-2xl">📚</div>
                  <h3 className="text-xl font-bold text-gray-900">Citations</h3>
                </div>
                <div className="space-y-3">
                  {result.citations.map((citation) => (
                    <div
                      key={citation.citation_number}
                      className="p-4 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-start gap-3">
                        <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">
                          {citation.citation_number}
                        </span>
                        <div className="flex-1">
                          <p className="font-semibold text-gray-900">
                            {citation.paper_title}
                          </p>
                          <p className="text-sm text-gray-600 mt-1">
                            Section: {citation.section} | Page: {citation.page}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Context Snippets */}
            {result.contexts && result.contexts.length > 0 && (
              <div className="bg-white p-6 rounded-lg border shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <div className="text-2xl">📄</div>
                  <h3 className="text-xl font-bold text-gray-900">Source Contexts</h3>
                </div>
                <div className="space-y-4">
                  {result.contexts.map((context, idx) => (
                    <details key={idx} className="group">
                      <summary className="cursor-pointer p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="font-medium text-gray-900">
                              {context.metadata.title}
                            </span>
                            <span className="text-sm text-gray-600 ml-2">
                              ({context.metadata.section})
                            </span>
                          </div>
                          <span className="text-sm text-blue-600">
                            {(context.relevance_score * 100).toFixed(0)}% relevant
                          </span>
                        </div>
                      </summary>
                      <div className="mt-2 p-4 bg-white border rounded-lg">
                        <p className="text-sm text-gray-700">{context.text}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          Page: {context.metadata.page}
                        </p>
                      </div>
                    </details>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* No Papers Message */}
        {papers.length === 0 && !isLoading && (
          <div className="text-center p-12 bg-white rounded-lg border">
            <div className="text-6xl mb-4">📚</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Papers Uploaded Yet
            </h3>
            <p className="text-gray-600 mb-4">
              Upload some academic papers first to start querying
            </p>
            <Link
              href="/"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload Papers
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

export default function QueryPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 pt-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading...</p>
          </div>
        </div>
      </div>
    }>
      <QueryPageContent />
    </Suspense>
  );
}
