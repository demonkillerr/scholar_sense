import { NextResponse } from 'next/server';
const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://backend:5000';

export async function POST(request: Request) {
  const formData = await request.formData();
  const file = formData.get('file') as File | null;

  if (!file) {
    return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
  }

  if (file.type !== 'application/pdf') {
    return NextResponse.json({ error: 'Only PDF files are allowed' }, { status: 400 });
  }

  // Create a new FormData object to send to the backend
  const backendFormData = new FormData();
    backendFormData.append('file', file);

  const response = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: backendFormData,
  });

  try {
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ error: 'Failed to save file' }, { status: 500 });
  }
}