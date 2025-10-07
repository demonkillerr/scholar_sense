'use client';

import { useState } from 'react';

interface AnalysisResult {
  topic_analysis?: {
    topic: string;
    low_relevance?: boolean;
    message?: string;
    stance?: 'support' | 'oppose' | 'neutral';
    relevance_score: number;
    sentiment: { score: number };
    topic_sentences?: string[];
    topic_keywords?: [string, number][];
  };
}


export default function Home() {
  const [topic, setTopic] = useState('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [filePath, setFilePath] = useState<string | null>(null);
  const [uploadMessage, setUploadMessage] = useState<React.ReactNode | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!topic.trim()) {
      alert('Please enter a topic');
      return;
    }

    if (!filePath) {
      alert('Please upload a file first');
      return;
    }

    const response = await fetch('/api/analyse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, file_path: filePath }),
    });

    const data = await response.json();
    setResult(data.result);
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setUploadMessage('No file selected');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    if (response.ok) {
      // 保存返回的文件路径
      if (data.result && data.result.file_info && data.result.file_info.saved_filename) {
        setFilePath(data.result.file_info.saved_filename);
        setUploadMessage(`File uploaded successfully. Ready for analysis.`);
      } else {
        setUploadMessage('File uploaded but could not get file path');
      }
    } else {
      setUploadMessage(data.error || 'Failed to upload file');
    }
  };

  const getFileStatusMessage = () => {
    if (!file) return null;
    return (
      <p className="mt-2 text-sm text-blue-600">
        Selected file: {file.name}
      </p>
    );
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
      // 重置文件路径，因为需要重新上传
      setFilePath(null);
    } else {
      setUploadMessage('Only PDF files are allowed');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      {/* Title and Horizontal Line */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800">Welcome to our Sentiment Analysis Website</h1>
        <hr className="mt-2 border-gray-300" />
      </div>

      {/* Input and Submit Button */}
      <div className="flex flex-col items-center justify-center">
        <form onSubmit={handleSubmit} className="w-full max-w-2xl">
          <div className="flex items-center gap-4">
            <input
              type="text"
              placeholder="Enter topic: ex AI, LLM, IoT"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={!topic.trim() || !filePath}
              className={`px-6 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500
                ${topic.trim() && filePath
                  ? 'bg-blue-500 text-white hover:bg-blue-600'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
            >
              Submit
            </button>
          </div>
        </form>

        {/* Upload Section */}
        <div className="mt-6 w-full max-w-md">
          <label className="block text-sm font-medium text-gray-700">Upload PDF</label>
          <div 
            className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <div className="space-y-1 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="flex text-sm text-gray-600">
                <label
                  htmlFor="file-upload"
                  className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none"
                >
                  <span>Upload a file</span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    className="sr-only"
                    onChange={(e) => {
                      setFile(e.target.files?.[0] || null);
                      // 重置文件路径，因为需要重新上传
                      setFilePath(null);
                    }}
                  />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">PDF only</p>
              {getFileStatusMessage()}
              {filePath && (
                <p className="mt-2 text-sm text-green-600">
                  File uploaded and ready for analysis
                </p>
              )}
            </div>
          </div>
          <button
            onClick={handleFileUpload}
            disabled={!file}
            className={`mt-4 w-full px-6 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500
              ${file 
                ? 'bg-green-500 text-white hover:bg-green-600' 
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
          >
            Upload
          </button>
          {uploadMessage && (
            <p className="mt-2 text-sm text-gray-600" 
               dangerouslySetInnerHTML={{ __html: uploadMessage }}
            />
          )}
        </div>
      </div>

      {/* Result Display */}
      {result && (
        <div className="mt-8 w-full max-w-2xl mx-auto p-4 bg-white rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
          
          {result.topic_analysis && (
            <div>
              <p className="text-lg font-medium">Topic: {result.topic_analysis.topic}</p>
              
              {result.topic_analysis.low_relevance ? (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                  <p className="text-md text-yellow-800">{result.topic_analysis.message}</p>
                </div>
              ) : (
                <>
                  <p className="text-lg font-medium">Stance: 
                    <span className={`ml-2 px-2 py-1 rounded ${
                      result.topic_analysis.stance === 'support' ? 'bg-green-100 text-green-800' :
                      result.topic_analysis.stance === 'oppose' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {result.topic_analysis.stance === 'support' ? 'Support' :
                      result.topic_analysis.stance === 'oppose' ? 'Oppose' : 'Neutral'}
                    </span>
                  </p>
                  <p className="text-md">Relevance Score: {(result.topic_analysis.relevance_score * 100).toFixed(1)}%</p>
                  <p className="text-md">Sentiment Score: {(result.topic_analysis.sentiment.score * 100).toFixed(1)}%</p>
                  
                  {result.topic_analysis.topic_sentences && result.topic_analysis.topic_sentences.length > 0 && (
                    <div className="mt-4">
                      <p className="font-medium">Related Sentences:</p>
                      <ul className="list-disc pl-5 mt-2">
                        {result.topic_analysis.topic_sentences.slice(0, 5).map((sentence: string, index: number) => (
                          <li key={index} className="text-sm text-gray-700 mb-1">{sentence}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {result.topic_analysis.topic_keywords && result.topic_analysis.topic_keywords.length > 0 && (
                    <div className="mt-4">
                      <p className="font-medium">Keywords:</p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {result.topic_analysis.topic_keywords.map((keyword: [string, number], index: number) => (
                          <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                            {keyword[0]} ({keyword[1]})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}