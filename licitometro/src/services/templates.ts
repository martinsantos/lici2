import { api } from './api';
import type { ScrapingTemplate, TemplateField } from '../types/recon';

export class TemplateService {
  static async getTemplates(): Promise<ScrapingTemplate[]> {
    try {
      console.log('Fetching templates...');
      const templates = await api('/templates');
      console.log('Templates fetched:', templates);
      return templates;
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
      console.log('Creating template:', template);
      const newTemplate = await api('/templates', {
        method: 'POST',
        body: template,
      });
      console.log('Template created:', newTemplate);
      return newTemplate;
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

  static async testTemplate(templateId: string): Promise<any> {
    try {
      return await api(`/templates/${templateId}/test`, {
        method: 'POST',
      });
    } catch (error) {
      console.error(`Error testing template ${templateId}:`, error);
      throw error;
    }
  }
}
