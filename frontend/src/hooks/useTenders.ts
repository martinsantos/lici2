import { useState, useCallback, useEffect } from 'react';
import { FilterState } from './useFilters';

interface Tender {
  id: string;
  title: string;
  description: string;
  budget: number;
  deadline: string;
  status: string;
  category: string;
  region: string;
  tags: string[];
}

interface UseTendersProps {
  initialFilters?: Partial<FilterState>;
  apiEndpoint: string;
}

interface TenderResponse {
  tenders: Tender[];
  totalCount: number;
}

export const useTenders = ({ initialFilters = {}, apiEndpoint }: UseTendersProps) => {
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTenders = useCallback(
    async (filters: FilterState) => {
      setIsLoading(true);
      setError(null);

      try {
        const queryParams = new URLSearchParams();
        
        // Añadir todos los filtros activos a los parámetros de consulta
        if (filters.search) queryParams.append('search', filters.search);
        if (filters.categories.length) queryParams.append('categories', filters.categories.join(','));
        if (filters.regions.length) queryParams.append('regions', filters.regions.join(','));
        if (filters.budgetRange) queryParams.append('budgetRange', filters.budgetRange);
        if (filters.sortBy) queryParams.append('sortBy', filters.sortBy);
        if (filters.status.length) queryParams.append('status', filters.status.join(','));
        if (filters.tags.length) queryParams.append('tags', filters.tags.join(','));
        
        queryParams.append('page', filters.page.toString());
        queryParams.append('pageSize', filters.pageSize.toString());

        const response = await fetch(`${apiEndpoint}?${queryParams.toString()}`);
        
        if (!response.ok) {
          throw new Error('Error al cargar las licitaciones');
        }

        const data: TenderResponse = await response.json();
        setTenders(data.tenders);
        setTotalCount(data.totalCount);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
        setTenders([]);
        setTotalCount(0);
      } finally {
        setIsLoading(false);
      }
    },
    [apiEndpoint]
  );

  const refreshTenders = useCallback(
    (filters: FilterState) => {
      fetchTenders(filters);
    },
    [fetchTenders]
  );

  return {
    tenders,
    totalCount,
    isLoading,
    error,
    refreshTenders,
  };
};
