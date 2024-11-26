import { apiClient } from './apiClient';
import type { ScrapingTemplate, TemplateField } from '../types/recon';

export class TemplateService {
  static async getTemplates(): Promise<ScrapingTemplate[]> {
    return apiClient('/templates');
  }

  static async getTemplate(id: string): Promise<ScrapingTemplate> {
    return apiClient(`/templates/${id}`);
  }

  static async createTemplate(template: Omit<ScrapingTemplate, 'id' | 'createdAt' | 'updatedAt'>): Promise<ScrapingTemplate> {
    return apiClient('/templates', {
      method: 'POST',
      body: template,
    });
  }

  static async updateTemplate(id: string, template: Partial<ScrapingTemplate>): Promise<ScrapingTemplate> {
    return apiClient(`/templates/${id}`, {
      method: 'PUT',
      body: template,
    });
  }

  static async deleteTemplate(id: string): Promise<void> {
    await apiClient(`/templates/${id}`, {
      method: 'DELETE',
    });
  }

  static async addField(templateId: string, field: Omit<TemplateField, 'id'>): Promise<TemplateField> {
    return apiClient(`/templates/${templateId}/fields`, {
      method: 'POST',
      body: field,
    });
  }

  static async updateField(templateId: string, fieldId: string, field: Partial<TemplateField>): Promise<TemplateField> {
    return apiClient(`/templates/${templateId}/fields/${fieldId}`, {
      method: 'PUT',
      body: field,
    });
  }

  static async deleteField(templateId: string, fieldId: string): Promise<void> {
    await apiClient(`/templates/${templateId}/fields/${fieldId}`, {
      method: 'DELETE',
    });
  }

  static async runTemplate(templateId: string): Promise<void> {
    await apiClient(`/templates/${templateId}/run`, {
      method: 'POST',
    });
  }

  static async testTemplate(templateId: string): Promise<any> {
    return apiClient(`/templates/${templateId}/test`, {
      method: 'POST',
    });
  }
}
