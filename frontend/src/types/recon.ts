export interface Field {
  id: string;
  name: string;
  type: 'text' | 'number' | 'date' | 'url';
  selector?: string;
}

export interface Mapping {
  sourceId: string;
  destinationId: string;
  transformation?: string;
}

export interface Template {
  name: string;
  description: string;
  sourceFields: Field[];
  destinationFields: Field[];
  mappings: Mapping[];
}

export interface ScrapingJob {
  id: string;
  templateId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: Date;
  endTime?: Date;
  error?: string;
  stats?: {
    pagesProcessed: number;
    itemsScraped: number;
    errors: number;
  };
}

export interface DocumentAnalysisJob {
  id: string;
  fileName: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  results?: {
    extractedFields: Record<string, any>;
    confidence: number;
  };
  error?: string;
}
