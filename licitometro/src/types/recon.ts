export interface TemplateField {
  id?: string;
  name: string;
  selector: string;
  type: string;
  required?: boolean;
}

export interface ScrapingTemplate {
  id?: string;
  name: string;
  description?: string;
  url: string;
  fields: TemplateField[];
  createdAt?: string;
  updatedAt?: string;
}

export interface TemplateRunResult {
  templateId: string;
  url: string;
  timestamp: string;
  data: Record<string, any>;
  success: boolean;
  error?: string;
}
