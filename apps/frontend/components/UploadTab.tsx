'use client';

import { useState, useCallback } from 'react';
import axios from 'axios';

interface UploadTabProps {
  onUploadSuccess: (filename: string) => void;
}

export default function UploadTab({ onUploadSuccess }: UploadTabProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });
  const [dragActive, setDragActive] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
        setUploadStatus({ type: null, message: '' });
      } else {
        setUploadStatus({ type: 'error', message: 'Please upload a PDF file' });
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setUploadStatus({ type: null, message: '' });
      } else {
        setUploadStatus({ type: 'error', message: 'Please upload a PDF file' });
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus({ type: 'error', message: 'Please select a file first' });
      return;
    }

    setUploading(true);
    setUploadStatus({ type: null, message: '' });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadStatus({
        type: 'success',
        message: `Successfully processed ${response.data.filename} (${response.data.pages} pages, ${response.data.chunks} chunks)`,
      });
      onUploadSuccess(response.data.filename);
      setFile(null);
    } catch (error: any) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Error uploading file',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome!</h2>
        <p className="text-gray-600">
          Upload your academic research paper (PDF) to begin sentiment analysis.
        </p>
      </div>

      {/* Drag and Drop Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-gray-50 hover:bg-gray-100'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="mb-4">
          <svg
            className="mx-auto h-16 w-16 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>

        <div className="mb-4">
          <p className="text-lg text-gray-700 mb-2">
            Drag and drop your PDF here, or
          </p>
          <label className="inline-block">
            <span className="px-6 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors">
              Browse Files
            </span>
            <input
              type="file"
              className="hidden"
              accept=".pdf"
              onChange={handleFileChange}
            />
          </label>
        </div>

        {file && (
          <div className="mt-4 p-4 bg-white rounded-lg border border-gray-200">
            <p className="text-sm text-gray-600">Selected file:</p>
            <p className="font-medium text-gray-800">{file.name}</p>
            <p className="text-xs text-gray-500 mt-1">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        )}
      </div>

      {/* Upload Button */}
      {file && (
        <div className="mt-6 text-center">
          <button
            onClick={handleUpload}
            disabled={uploading}
            className={`px-8 py-3 rounded-lg font-medium text-white transition-colors ${
              uploading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {uploading ? 'Processing...' : 'Upload and Process'}
          </button>
        </div>
      )}

      {/* Status Messages */}
      {uploadStatus.type && (
        <div
          className={`mt-6 p-4 rounded-lg ${
            uploadStatus.type === 'success'
              ? 'bg-green-50 border border-green-200 text-green-800'
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}
        >
          <p className="font-medium">
            {uploadStatus.type === 'success' ? '✓ Success!' : '✗ Error'}
          </p>
          <p className="text-sm mt-1">{uploadStatus.message}</p>
        </div>
      )}

      {/* Info Box */}
      <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">How it works:</h3>
        <ul className="text-sm text-blue-800 space-y-2">
          <li>• Upload your research paper in PDF format</li>
          <li>• The system extracts text and identifies sections</li>
          <li>• Content is chunked and embedded into a vector database</li>
          <li>• Switch to the Chat tab to analyze sentiment against keywords</li>
        </ul>
      </div>
    </div>
  );
}
