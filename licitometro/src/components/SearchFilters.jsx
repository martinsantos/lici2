import { useState } from 'react';

const SearchFilters = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    search: '',
    estado: '',
    entidad: '',
    fechaDesde: '',
    fechaHasta: '',
    presupuestoMin: '',
    presupuestoMax: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    const newFilters = {
      ...filters,
      [name]: value
    };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Búsqueda por texto */}
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-700">
            Búsqueda
          </label>
          <input
            type="text"
            name="search"
            id="search"
            value={filters.search}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="Buscar por título o descripción"
          />
        </div>

        {/* Estado */}
        <div>
          <label htmlFor="estado" className="block text-sm font-medium text-gray-700">
            Estado
          </label>
          <select
            id="estado"
            name="estado"
            value={filters.estado}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          >
            <option value="">Todos</option>
            <option value="abierta">Abierta</option>
            <option value="cerrada">Cerrada</option>
            <option value="adjudicada">Adjudicada</option>
            <option value="desierta">Desierta</option>
          </select>
        </div>

        {/* Entidad */}
        <div>
          <label htmlFor="entidad" className="block text-sm font-medium text-gray-700">
            Entidad
          </label>
          <input
            type="text"
            name="entidad"
            id="entidad"
            value={filters.entidad}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="Nombre de la entidad"
          />
        </div>

        {/* Fecha desde */}
        <div>
          <label htmlFor="fechaDesde" className="block text-sm font-medium text-gray-700">
            Fecha desde
          </label>
          <input
            type="date"
            name="fechaDesde"
            id="fechaDesde"
            value={filters.fechaDesde}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>

        {/* Fecha hasta */}
        <div>
          <label htmlFor="fechaHasta" className="block text-sm font-medium text-gray-700">
            Fecha hasta
          </label>
          <input
            type="date"
            name="fechaHasta"
            id="fechaHasta"
            value={filters.fechaHasta}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>

        {/* Presupuesto mínimo */}
        <div>
          <label htmlFor="presupuestoMin" className="block text-sm font-medium text-gray-700">
            Presupuesto mínimo
          </label>
          <input
            type="number"
            name="presupuestoMin"
            id="presupuestoMin"
            value={filters.presupuestoMin}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="0"
          />
        </div>

        {/* Presupuesto máximo */}
        <div>
          <label htmlFor="presupuestoMax" className="block text-sm font-medium text-gray-700">
            Presupuesto máximo
          </label>
          <input
            type="number"
            name="presupuestoMax"
            id="presupuestoMax"
            value={filters.presupuestoMax}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="0"
          />
        </div>
      </div>
    </div>
  );
};

export default SearchFilters;
