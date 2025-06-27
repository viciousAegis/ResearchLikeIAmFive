// types.ts - Type definitions for the ResearchLikeIAmFive application

export interface KeyTerm {
  term: string;
  definition: string;
}

export interface PaperSummary {
  gist: string;
  analogy: string;
  experimental_details?: string; // Optional to handle legacy responses
  key_findings: string[];
  why_it_matters: string;
  key_terms: KeyTerm[];
}

export interface APIResponse {
  summary: string; // JSON string that needs to be parsed into PaperSummary
  title: string;
}

export interface ParsedAPIResponse {
  summary: PaperSummary;
  title: string;
}
