import { api } from './api';
import type { ScrapingTemplate, TemplateField } from '../types/recon';

export class TemplateService {
  static async getTemplates(): Promise<ScrapingTemplate[]> {
    try {
      return await api('/templates');
    } catch (error) {
      console.error('Error fetching templates:', error);
      throw error;
    }
  }

  static async getTemplate(id: string): Promise<ScrapingTemplate> {
    try {
      return await api(`/templates/${id}`);
    } catch (error) {
      console.error(`Error fetching template ${id}:`, error);
      throw error;
    }
  }

  static async createTemplate(template: Omit<ScrapingTemplate, 'id' | 'createdAt' | 'updatedAt'>): Promise<ScrapingTemplate> {
    try {
      return await api('/templates', {
        method: 'POST',
        body: template,
      });
    } catch (error) {
      console.error('Error creating template:', error);
      throw error;
    }
  }

  static async updateTemplate(id: string, template: Partial<ScrapingTemplate>): Promise<ScrapingTemplate> {
    try {
      return await api(`/templates/${id}`, {
        method: 'PUT',
        body: template,
      });
    } catch (error) {
      console.error(`Error updating template ${id}:`, error);
      throw error;
    }
  }

  static async deleteTemplate(id: string): Promise<void> {
    try {
      await api(`/templates/${id}`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.error(`Error deleting template ${id}:`, error);
      throw error;
    }
  }

  static async addField(templateId: string, field: Omit<TemplateField, 'id'>): Promise<TemplateField> {
    try {
      return await api(`/templates/${templateId}/fields`, {
        method: 'POST',
        body: field,
      });
    } catch (error) {
      console.error(`Error adding field to template ${templateId}:`, error);
      throw error;
    }
  }

  static async updateField(templateId: string, fieldId: string, field: Partial<TemplateField>): Promise<TemplateField> {
    try {
      return await api(`/templates/${templateId}/fields/${fieldId}`, {
        method: 'PUT',
        body: field,
      });
    } catch (error) {
      console.error(`Error updating field ${fieldId} in template ${templateId}:`, error);
      throw error;
    }
  }

  static async deleteField(templateId: string, fieldId: string): Promise<void> {
    try {
      await api(`/templates/${templateId}/fields/${fieldId}`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.error(`Error deleting field ${fieldId} from template ${templateId}:`, error);
      throw error;
    }
  }

  static async getTemplateHistory(id: string): Promise<any[]> {
    try {
      return await api(`/templates/${id}/history`);
    } catch (error) {
      console.error(`Error fetching template history ${id}:`, error);
      throw error;
    }
  }

  static async runTemplateJob(id: string, options?: { test?: boolean }): Promise<any> {
    try {
      const endpoint = options?.test ? `/templates/${id}/test` : `/templates/${id}/run`;
      return await api(endpoint, {
        method: 'POST',
      });
    } catch (error) {
      console.error(`Error running template ${id}:`, error);
      throw error;
    }
  }

  static async testTemplate(id: string): Promise<any> {
    return this.runTemplateJob(id, { test: true });
  }

  static async runTemplate(templateId: string): Promise<void> {
    try {
      await api(`/templates/${templateId}/run`, {
        method: 'POST',
      });
    } catch (error) {
      console.error(`Error running template ${templateId}:`, error);
      throw error;
    }
  }
}

// Export individual functions to match the import statements
export const getTemplateHistory = TemplateService.getTemplateHistory;
export const getTemplateById = TemplateService.getTemplate;
export const runTemplateJob = TemplateService.runTemplateJob;
export const testTemplate = TemplateService.testTemplate;
