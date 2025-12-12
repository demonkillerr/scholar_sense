import { NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://backend:5000';

export async function POST(request: Request) {
  const { topic, file_path } = await request.json();

  const response = await fetch(`${API_URL}/analyse`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ topic, file_path }),
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}