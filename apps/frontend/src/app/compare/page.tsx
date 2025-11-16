'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import type { Paper, ComparisonResult } from '@/lib/types';

export default function ComparePage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedPapers, setSelectedPapers] = useState<string[]>([]);
  const [selectedAspects, setSelectedAspects] = useState<string[]>([
    'methodology',
    'results',
    'conclusions',
    'limitations',
  ]);
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const aspects = [
    'methodology',
    'results',
    'conclusions',
    'limitations',
    'datasets',
    'evaluation',
  ];

  useEffect(() => {
    api
      .listPapers()
      .then(setPapers)
      .catch((err) => setError(err.message));
  }, []);

  const togglePaper = (paperId: string) => {
    setSelectedPapers((prev) =>
      prev.includes(paperId)
        ? prev.filter((id) => id !== paperId)
        : [...prev, paperId]
    );
  };

  const toggleAspect = (aspect: string) => {
    setSelectedAspects((prev) =>
      prev.includes(aspect)
        ? prev.filter((a) => a !== aspect)
        : [...prev, aspect]
    );
  };

  const handleCompare = async () => {
    if (selectedPapers.length < 2) {
      setError('Please select at least 2 papers to compare');
      return;
    }

    if (selectedAspects.length === 0) {
      setError('Please select at least one comparison aspect');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const comparisonResult = await api.comparePapers(
        selectedPapers,
        selectedAspects
      );
      setResult(comparisonResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to compare papers');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Compare Papers
          </h1>
          <p className="text-lg text-gray-600">
            Compare multiple papers across different aspects
          </p>
        </div>

        {/* Selection Panel */}
        <div className="bg-white p-6 rounded-lg border shadow-sm mb-8">
          {/* Paper Selection */}
          <div className="mb-6">
            <label className="block text-lg font-semibold text-gray-900 mb-3">
              Select Papers to Compare
              <span className="text-sm font-normal text-gray-500 ml-2">
                (minimum 2)
              </span>
            </label>
            {papers.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {papers.map((paper) => (
                  <button
                    key={paper.paper_id}
                    onClick={() => togglePaper(paper.paper_id)}
                    className={`p-4 text-left rounded-lg border-2 transition-all ${
                      selectedPapers.includes(paper.paper_id)
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`flex-shrink-0 w-6 h-6 rounded border-2 flex items-center justify-center ${
                          selectedPapers.includes(paper.paper_id)
                            ? 'border-blue-600 bg-blue-600'
                            : 'border-gray-300'
                        }`}
                      >
                        {selectedPapers.includes(paper.paper_id) && (
                          <svg
                            className="w-4 h-4 text-white"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{paper.title}</p>
                        {paper.authors && (
                          <p className="text-sm text-gray-600 mt-1">
                            {paper.authors}
                          </p>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">
                No papers available. Upload some papers first.
              </p>
            )}
            <p className="text-sm text-gray-600 mt-2">
              {selectedPapers.length} paper(s) selected
            </p>
          </div>

          {/* Aspect Selection */}
          <div className="mb-6">
            <label className="block text-lg font-semibold text-gray-900 mb-3">
              Comparison Aspects
            </label>
            <div className="flex flex-wrap gap-2">
              {aspects.map((aspect) => (
                <button
                  key={aspect}
                  onClick={() => toggleAspect(aspect)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedAspects.includes(aspect)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {aspect.charAt(0).toUpperCase() + aspect.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Compare Button */}
          <button
            onClick={handleCompare}
            disabled={isLoading || selectedPapers.length < 2}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
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
                Comparing...
              </span>
            ) : (
              'Compare Papers'
            )}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Comparison Results */}
        {result && (
          <div className="space-y-6">
            {/* Papers Being Compared */}
            <div className="bg-white p-6 rounded-lg border shadow-sm">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Papers Compared ({result.papers_compared})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.papers.map((paper, idx) => (
                  <div key={paper.paper_id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-start gap-2">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                        {idx + 1}
                      </span>
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900">{paper.title}</p>
                        {paper.authors && (
                          <p className="text-sm text-gray-600 mt-1">{paper.authors}</p>
                        )}
                        {paper.year && (
                          <p className="text-sm text-gray-500 mt-1">Year: {paper.year}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Comparison Analysis */}
            <div className="bg-white p-6 rounded-lg border shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <div className="text-2xl">⚖️</div>
                <h2 className="text-xl font-bold text-gray-900">
                  Comparative Analysis
                </h2>
              </div>
              <div className="prose max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
                {result.comparison}
              </div>
              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex flex-wrap gap-4 text-sm text-blue-800">
                  <span>🤖 Model: {result.model}</span>
                  <span>📋 Aspects: {result.aspects.join(', ')}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {papers.length === 0 && (
          <div className="text-center p-12 bg-white rounded-lg border">
            <div className="text-6xl mb-4">📚</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Papers Available
            </h3>
            <p className="text-gray-600 mb-6">
              Upload at least 2 papers to compare them
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
