import React from 'react';
import { Link } from 'react-router-dom';
import { FaPlus } from 'react-icons/fa';

const TableHeader: React.FC = () => {
  return (
    <div className="sm:flex sm:items-center sm:justify-between mb-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Licitaciones</h1>
        <p className="mt-2 text-sm text-gray-700">
          Lista de todas las licitaciones disponibles en el sistema
        </p>
      </div>
      <div className="mt-4 sm:mt-0">
        <Link
          to="/licitaciones/new"
          className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
        >
          <FaPlus className="mr-2 -ml-1 h-4 w-4" />
          Nueva Licitación
        </Link>
      </div>
    </div>
  );
};

export default TableHeader;
