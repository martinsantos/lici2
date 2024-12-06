import React, { useState } from 'react';

interface FilterOptions {
  categories: string[];
  regions: string[];
  budgetRanges: {
    min: number;
    max: number;
    label: string;
  }[];
  sortOptions: {
    value: string;
    label: string;
  }[];
}

interface AdvancedFiltersProps {
  options: FilterOptions;
  onApplyFilters: (filters: any) => void;
  initialFilters?: any;
  className?: string;
}

export const AdvancedFilters: React.FC<AdvancedFiltersProps> = ({
  options,
  onApplyFilters,
  initialFilters = {},
  className = '',
}) => {
  const [filters, setFilters] = useState({
    categories: [] as string[],
    regions: [] as string[],
    budgetRange: '',
    sortBy: 'newest',
    ...initialFilters,
  });

  const handleCategoryChange = (category: string) => {
    setFilters((prev) => ({
      ...prev,
      categories: prev.categories.includes(category)
        ? prev.categories.filter((c) => c !== category)
        : [...prev.categories, category],
    }));
  };

  const handleRegionChange = (region: string) => {
    setFilters((prev) => ({
      ...prev,
      regions: prev.regions.includes(region)
        ? prev.regions.filter((r) => r !== region)
        : [...prev.regions, region],
    }));
  };

  const handleBudgetRangeChange = (range: string) => {
    setFilters((prev) => ({
      ...prev,
      budgetRange: prev.budgetRange === range ? '' : range,
    }));
  };

  const handleSortChange = (sortValue: string) => {
    setFilters((prev) => ({
      ...prev,
      sortBy: sortValue,
    }));
  };

  const handleApply = () => {
    onApplyFilters(filters);
  };

  const handleReset = () => {
    setFilters({
      categories: [],
      regions: [],
      budgetRange: '',
      sortBy: 'newest',
    });
  };

  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
      <div className="space-y-6">
        {/* Categorías */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Categorías</h3>
          <div className="space-y-2">
            {options.categories.map((category) => (
              <label
                key={category}
                className="flex items-center space-x-3 text-gray-700"
              >
                <input
                  type="checkbox"
                  checked={filters.categories.includes(category)}
                  onChange={() => handleCategoryChange(category)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm">{category}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Regiones */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Regiones</h3>
          <div className="space-y-2">
            {options.regions.map((region) => (
              <label
                key={region}
                className="flex items-center space-x-3 text-gray-700"
              >
                <input
                  type="checkbox"
                  checked={filters.regions.includes(region)}
                  onChange={() => handleRegionChange(region)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm">{region}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Rango de Presupuesto */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Rango de Presupuesto
          </h3>
          <div className="space-y-2">
            {options.budgetRanges.map((range) => (
              <label
                key={`${range.min}-${range.max}`}
                className="flex items-center space-x-3 text-gray-700"
              >
                <input
                  type="radio"
                  checked={filters.budgetRange === `${range.min}-${range.max}`}
                  onChange={() =>
                    handleBudgetRangeChange(`${range.min}-${range.max}`)
                  }
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="text-sm">{range.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Ordenar por */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Ordenar por</h3>
          <select
            value={filters.sortBy}
            onChange={(e) => handleSortChange(e.target.value)}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          >
            {options.sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Botones de acción */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={handleReset}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Limpiar Filtros
          </button>
          <button
            type="button"
            onClick={handleApply}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Aplicar Filtros
          </button>
        </div>
      </div>
    </div>
  );
};
