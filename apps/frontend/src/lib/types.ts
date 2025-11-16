// TypeScript interfaces for ScholarSense API

export interface Paper {
  paper_id: string;
  title: string;
  authors: string;
  year: string;
  upload_date: string;
}

export interface Citation {
  citation_number: number;
  paper_title: string;
  section: string;
  page: string;
  paper_id: string;
}

export interface Context {
  text: string;
  metadata: {
    paper_id: string;
    title: string;
    section: string;
    page: string;
    chunk_index?: number;
  };
  relevance_score: number;
}

export interface QueryResult {
  answer: string;
  citations: Citation[];
  contexts: Context[];
  model: string;
  contexts_used: number;
}

export interface UploadResult {
  paper_id: string;
  title: string;
  chunks_processed: number;
  sections_processed: number;
  filename: string;
  upload_date: string;
}

export interface ComparisonResult {
  comparison: string;
  papers_compared: number;
  aspects: string[];
  model: string;
  papers: {
    paper_id: string;
    title: string;
    authors: string;
    year: string;
    abstract: string;
  }[];
}

export interface ApiResponse<T> {
  status: 'ok' | 'error';
  result?: T;
  error?: string;
  papers?: Paper[];
  total?: number;
  message?: string;
}

export interface RAGStats {
  total_papers: number;
  total_chunks: number;
  embedding_model: string;
  embedding_dimension: number;
  llm_model: string;
}
