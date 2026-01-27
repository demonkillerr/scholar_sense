'use client';

import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

interface ChatTabProps {
  documents: string[];
}

interface Evidence {
  text: string;
  page_number: number;
  section: string;
  citations: string;
}

interface AnalysisResult {
  sentiment: string;
  summary: string;
  evidence: Evidence[];
}

export default function ChatTab({ documents }: ChatTabProps) {
  const [keyword, setKeyword] = useState('');
  const [selectedDocument, setSelectedDocument] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const handleAnalyze = async () => {
    if (!keyword.trim()) {
      alert('Please enter a keyword');
      return;
    }

    setAnalyzing(true);
    setResult(null);

    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        keyword: keyword.trim(),
        document_name: selectedDocument || null,
      });

      setResult(response.data);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error analyzing sentiment');
    } finally {
      setAnalyzing(false);
    }
  };

  const getSentimentColor = (sentiment: string) => {
    const s = sentiment.toLowerCase();
    if (s.includes('positive')) return 'text-green-600 bg-green-50 border-green-200';
    if (s.includes('negative')) return 'text-red-600 bg-red-50 border-red-200';
    if (s.includes('mixed')) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-gray-600 bg-gray-50 border-gray-200';
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Sentiment Analysis</h2>
        <p className="text-gray-600">
          Analyze the research paper's sentiment towards a specific keyword or topic.
        </p>
      </div>

      {/* Input Section */}
      <div className="bg-gray-50 rounded-lg p-6 mb-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Keyword or Topic
          </label>
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="e.g., machine learning, neural networks, data privacy..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            onKeyPress={(e) => {
              if (e.key === 'Enter') handleAnalyze();
            }}
          />
        </div>

        {documents.length > 0 && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Document (Optional - leave blank to search all)
            </label>
            <select
              value={selectedDocument}
              onChange={(e) => setSelectedDocument(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All documents</option>
              {documents.map((doc) => (
                <option key={doc} value={doc}>
                  {doc}
                </option>
              ))}
            </select>
          </div>
        )}

        <button
          onClick={handleAnalyze}
          disabled={analyzing || !keyword.trim()}
          className={`w-full px-6 py-3 rounded-lg font-medium text-white transition-colors ${
            analyzing || !keyword.trim()
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {analyzing ? 'Analyzing...' : 'Analyze Sentiment'}
        </button>
      </div>

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Sentiment Badge */}
          <div className="flex items-center gap-3">
            <span className="text-gray-700 font-medium">Overall Sentiment:</span>
            <span
              className={`px-4 py-2 rounded-full font-semibold border ${getSentimentColor(
                result.sentiment
              )}`}
            >
              {result.sentiment}
            </span>
          </div>

          {/* Summary */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Analysis Summary</h3>
            <div className="prose prose-sm max-w-none text-gray-700">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {result.summary}
              </ReactMarkdown>
            </div>
          </div>

          {/* Evidence with Citations */}
          {result.evidence && result.evidence.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Supporting Evidence
              </h3>
              <div className="space-y-4">
                {result.evidence.map((evidence, index) => (
                  <div
                    key={index}
                    className="bg-blue-50 rounded-lg p-4 border border-blue-100"
                  >
                    <p className="text-gray-700 mb-3 italic">"{evidence.text}"</p>
                    <div className="flex flex-wrap gap-3 text-sm">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">
                        📄 Page {evidence.page_number}
                      </span>
                      <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full">
                        📑 {evidence.section}
                      </span>
                      {evidence.citations && (
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full">
                          📚 {evidence.citations}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!result && !analyzing && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <p className="text-gray-500">
            Enter a keyword above to analyze the sentiment of your research papers
          </p>
          {documents.length === 0 && (
            <p className="text-sm text-orange-600 mt-2">
              ⚠️ No documents uploaded yet. Upload a PDF first!
            </p>
          )}
        </div>
      )}
    </div>
  );
}
