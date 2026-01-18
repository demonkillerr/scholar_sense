'use client';

import { useState } from 'react';
import UploadTab from '@/components/UploadTab';
import ChatTab from '@/components/ChatTab';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'upload' | 'chat'>('upload');
  const [uploadedDocuments, setUploadedDocuments] = useState<string[]>([]);

  const handleUploadSuccess = (filename: string) => {
    if (!uploadedDocuments.includes(filename)) {
      setUploadedDocuments([...uploadedDocuments, filename]);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6">
            <h1 className="text-3xl font-bold text-white">Scholar Sense</h1>
            <p className="text-blue-100 mt-2">Sentiment analysis for research papers</p>
          </div>

          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex-1 px-6 py-4 text-center font-medium transition-colors ${
                activeTab === 'upload'
                  ? 'bg-white text-blue-600 border-b-2 border-blue-600'
                  : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
              }`}
            >
              📤 Upload Document
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex-1 px-6 py-4 text-center font-medium transition-colors ${
                activeTab === 'chat'
                  ? 'bg-white text-blue-600 border-b-2 border-blue-600'
                  : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
              }`}
            >
              💬 Sentiment Analysis
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-8">
            {activeTab === 'upload' ? (
              <UploadTab onUploadSuccess={handleUploadSuccess} />
            ) : (
              <ChatTab documents={uploadedDocuments} />
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
