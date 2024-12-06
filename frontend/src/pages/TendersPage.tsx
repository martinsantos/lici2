import React, { useEffect } from 'react';
import { TenderList } from '../components/TenderList';
import { useFilters } from '../hooks/useFilters';
import { useTenders } from '../hooks/useTenders';

const filterOptions = {
  categories: [
    'Construcción',
    'Tecnología',
    'Servicios',
    'Consultoría',
    'Suministros',
    'Infraestructura',
  ],
  regions: [
    'Norte',
    'Centro',
    'Sur',
    'Este',
    'Oeste',
    'Nacional',
  ],
  budgetRanges: [
    { min: 0, max: 50000, label: 'Hasta $50,000' },
    { min: 50000, max: 200000, label: '$50,000 - $200,000' },
    { min: 200000, max: 1000000, label: '$200,000 - $1,000,000' },
    { min: 1000000, max: -1, label: 'Más de $1,000,000' },
  ],
  sortOptions: [
    { value: 'newest', label: 'Más recientes' },
    { value: 'oldest', label: 'Más antiguos' },
    { value: 'budget_high', label: 'Mayor presupuesto' },
    { value: 'budget_low', label: 'Menor presupuesto' },
    { value: 'deadline_close', label: 'Próximos a vencer' },
  ],
};

export const TendersPage: React.FC = () => {
  const { filters, updateFilters } = useFilters();
  const { tenders, totalCount, isLoading, error, refreshTenders } = useTenders({
    apiEndpoint: '/api/tenders',
    initialFilters: filters,
  });

  useEffect(() => {
    refreshTenders(filters);
  }, [filters, refreshTenders]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Licitaciones</h1>
        <p className="mt-2 text-sm text-gray-500">
          Encuentra y filtra licitaciones según tus necesidades
        </p>
      </div>

      {error ? (
        <div className="rounded-md bg-red-50 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Error al cargar las licitaciones
              </h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      ) : (
        <TenderList
          tenders={tenders}
          totalCount={totalCount}
          filterOptions={filterOptions}
          onFilterChange={updateFilters}
          isLoading={isLoading}
        />
      )}
    </div>
  );
};
