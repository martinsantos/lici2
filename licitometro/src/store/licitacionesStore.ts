import { create } from 'zustand';
import type { Licitacion } from '../types';

interface LicitacionesState {
  licitaciones: Licitacion[];
  isLoading: boolean;
  error: string | null;
  filters: {
    estado: string[];
    presupuesto: string[];
    searchTerm: string;
  };
  setLicitaciones: (licitaciones: Licitacion[]) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  setFilters: (filters: Partial<LicitacionesState['filters']>) => void;
  fetchLicitaciones: () => Promise<void>;
}

export const useLicitacionesStore = create<LicitacionesState>((set, get) => ({
  licitaciones: [],
  isLoading: false,
  error: null,
  filters: {
    estado: [],
    presupuesto: [],
    searchTerm: '',
  },

  setLicitaciones: (licitaciones) => set({ licitaciones }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setFilters: (filters) =>
    set((state) => ({
      filters: {
        ...state.filters,
        ...filters,
      },
    })),

  fetchLicitaciones: async () => {
    const { setLoading, setError, setLicitaciones } = get();
    try {
      setLoading(true);
      // TODO: Implement API call
      const response = await fetch('/api/licitaciones');
      const data = await response.json();
      setLicitaciones(data);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Error al cargar licitaciones');
    } finally {
      setLoading(false);
    }
  },
}));
