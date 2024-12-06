import { create } from 'zustand';
import type { ScrapingTemplate } from '../types/recon';
import { api } from '../services/api';

interface TemplateStore {
  templates: ScrapingTemplate[];
  selectedTemplate: ScrapingTemplate | null;
  error: string | null;
  loading: boolean;
  fetchTemplates: () => Promise<void>;
  addTemplate: (template: ScrapingTemplate) => Promise<void>;
  updateTemplate: (id: string, template: ScrapingTemplate) => Promise<void>;
  deleteTemplate: (id: string) => Promise<void>;
  selectTemplate: (template: ScrapingTemplate | null) => void;
}

export const useTemplateStore = create<TemplateStore>((set, get) => ({
  templates: [],
  selectedTemplate: null,
  error: null,
  loading: false,

  fetchTemplates: async () => {
    try {
      set({ loading: true, error: null });
      const templates = await api('/api/recon/templates');
      set({ templates, loading: false });
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Error al cargar las plantillas',
        loading: false 
      });
    }
  },

  addTemplate: async (template: ScrapingTemplate) => {
    try {
      set({ loading: true, error: null });
      const newTemplate = await api('/templates', {
        method: 'POST',
        body: template,
      });
      set(state => ({
        templates: [...state.templates, newTemplate],
        loading: false
      }));
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Error al crear la plantilla',
        loading: false 
      });
      throw error;
    }
  },

  updateTemplate: async (id: string, template: ScrapingTemplate) => {
    try {
      set({ loading: true, error: null });
      const updatedTemplate = await api(`/templates/${id}`, {
        method: 'PUT',
        body: template,
      });
      set(state => ({
        templates: state.templates.map(t => 
          t.id === id ? updatedTemplate : t
        ),
        loading: false
      }));
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Error al actualizar la plantilla',
        loading: false 
      });
      throw error;
    }
  },

  deleteTemplate: async (id: string) => {
    try {
      set({ loading: true, error: null });
      await api(`/templates/${id}`, {
        method: 'DELETE',
      });
      set(state => ({
        templates: state.templates.filter(t => t.id !== id),
        loading: false
      }));
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Error al eliminar la plantilla',
        loading: false 
      });
      throw error;
    }
  },

  selectTemplate: (template: ScrapingTemplate | null) => {
    set({ selectedTemplate: template });
  },
}));
