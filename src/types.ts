// types.ts - Type definitions for the ResearchLikeIAmFive application

export interface KeyTerm {
  term: string;
  definition: string;
}

export interface Figure {
  caption: string;
  importance: string;
  figure_index: number;
}

export interface ExtractedFigure {
  data: string; // base64 image data
  page: number;
  index: number;
}

export interface PaperSummary {
  gist: string;
  analogy: string;
  experimental_details?: string; // Optional to handle legacy responses
  key_findings: string[];
  why_it_matters: string;
  key_terms: KeyTerm[];
  figures: Figure[];
}

export interface PaperInfo {
  title: string;
  authors: string[];
  published: string | null;
  arxiv_id: string;
  url: string;
}

export interface APIResponse {
  success: boolean;
  data: {
    paper_info: PaperInfo;
    summary: string | PaperSummary; // Can be JSON string or parsed object
    explanation_style: string;
    figures: ExtractedFigure[];
  };
}

// Legacy response format for backward compatibility
export interface LegacyAPIResponse {
  summary: string; // JSON string that needs to be parsed into PaperSummary
  title: string;
  figures: ExtractedFigure[];
}

export interface ParsedAPIResponse {
  summary: PaperSummary;
  title: string;
  figures: ExtractedFigure[];
}
