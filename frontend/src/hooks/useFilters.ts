import { useState, useCallback } from 'react';

export interface FilterState {
  search: string;
  categories: string[];
  regions: string[];
  budgetRange: string;
  sortBy: string;
  status: string[];
  page: number;
  pageSize: number;
  tags: string[];
}

export interface UseFiltersProps {
  initialFilters?: Partial<FilterState>;
  onFilterChange?: (filters: FilterState) => void;
}

const defaultFilters: FilterState = {
  search: '',
  categories: [],
  regions: [],
  budgetRange: '',
  sortBy: 'newest',
  status: [],
  page: 1,
  pageSize: 10,
  tags: [],
};

export const useFilters = ({ initialFilters = {}, onFilterChange }: UseFiltersProps = {}) => {
  const [filters, setFilters] = useState<FilterState>({
    ...defaultFilters,
    ...initialFilters,
  });

  const updateFilters = useCallback((updates: Partial<FilterState>) => {
    setFilters((prev) => {
      const newFilters = { ...prev, ...updates };
      onFilterChange?.(newFilters);
      return newFilters;
    });
  }, [onFilterChange]);

  const resetFilters = useCallback(() => {
    setFilters(defaultFilters);
    onFilterChange?.(defaultFilters);
  }, [onFilterChange]);

  const setPage = useCallback((page: number) => {
    updateFilters({ page });
  }, [updateFilters]);

  const setSearch = useCallback((search: string) => {
    updateFilters({ search, page: 1 });
  }, [updateFilters]);

  const setCategories = useCallback((categories: string[]) => {
    updateFilters({ categories, page: 1 });
  }, [updateFilters]);

  const setRegions = useCallback((regions: string[]) => {
    updateFilters({ regions, page: 1 });
  }, [updateFilters]);

  const setBudgetRange = useCallback((budgetRange: string) => {
    updateFilters({ budgetRange, page: 1 });
  }, [updateFilters]);

  const setSortBy = useCallback((sortBy: string) => {
    updateFilters({ sortBy });
  }, [updateFilters]);

  const setStatus = useCallback((status: string[]) => {
    updateFilters({ status, page: 1 });
  }, [updateFilters]);

  const setTags = useCallback((tags: string[]) => {
    updateFilters({ tags, page: 1 });
  }, [updateFilters]);

  return {
    filters,
    updateFilters,
    resetFilters,
    setPage,
    setSearch,
    setCategories,
    setRegions,
    setBudgetRange,
    setSortBy,
    setStatus,
    setTags,
  };
};
