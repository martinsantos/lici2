import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { FaEdit, FaTrash, FaSort, FaSortUp, FaSortDown, FaFile, FaExternalLinkAlt } from 'react-icons/fa';
import type { Licitacion } from '../types';

interface Props {
  initialLicitaciones?: Licitacion[];
}

type SortField = 'titulo' | 'organismo' | 'fechaPublicacion' | 'fechaApertura' | 'presupuesto' | 'estado' | 'documentos';
type SortDirection = 'asc' | 'desc';

const formatCurrency = (amount: number | null | undefined, currency: string = 'ARS') => {
  if (amount == null) return 'No especificado';
  try {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: currency,
      maximumFractionDigits: 0
    }).format(amount);
  } catch (e) {
    console.error('Error formatting currency:', e);
    return 'Monto no disponible';
  }
};

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return 'No especificada';
  try {
    return new Date(dateStr).toLocaleDateString('es-AR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch (e) {
    console.error('Error formatting date:', e);
    return 'Fecha no válida';
  }
};

const LicitacionesTable: React.FC<Props> = ({ initialLicitaciones = [] }) => {
  const [licitaciones, setLicitaciones] = useState<Licitacion[]>(initialLicitaciones);
  const [filteredLicitaciones, setFilteredLicitaciones] = useState<Licitacion[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOrganismo, setFilterOrganismo] = useState('');
  const [filterEstado, setFilterEstado] = useState('');
  const [sortField, setSortField] = useState<SortField>('fechaPublicacion');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  useEffect(() => {
    if (initialLicitaciones.length > 0) {
      setLicitaciones(initialLicitaciones);
    } else {
      fetchLicitaciones();
    }
  }, [initialLicitaciones]);

  const fetchLicitaciones = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/licitaciones');
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      setLicitaciones(data);
    } catch (error) {
      console.error('Error fetching licitaciones:', error);
      toast.error('Error al cargar las licitaciones');
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  useEffect(() => {
    let result = [...licitaciones];

    if (searchTerm) {
      result = result.filter(licitacion => 
        licitacion.titulo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        licitacion.organismo.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filterOrganismo) {
      result = result.filter(licitacion => 
        licitacion.organismo === filterOrganismo
      );
    }

    if (filterEstado) {
      result = result.filter(licitacion => 
        licitacion.estado === filterEstado
      );
    }

    result.sort((a, b) => {
      let comparison = 0;
      
      if (sortField === 'presupuesto') {
        comparison = ((a[sortField] || 0) - (b[sortField] || 0));
      } else if (sortField === 'fechaPublicacion' || sortField === 'fechaApertura') {
        const dateA = a[sortField] ? new Date(a[sortField]).getTime() : 0;
        const dateB = b[sortField] ? new Date(b[sortField]).getTime() : 0;
        comparison = dateA - dateB;
      } else {
        comparison = String(a[sortField] || '').localeCompare(String(b[sortField] || ''));
      }

      return sortDirection === 'asc' ? comparison : -comparison;
    });

    setFilteredLicitaciones(result);
  }, [licitaciones, sortField, sortDirection, searchTerm, filterOrganismo, filterEstado]);

  const handleDelete = async (id: number) => {
    if (!confirm('¿Está seguro que desea eliminar esta licitación?')) {
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/licitaciones/${id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      setLicitaciones(prev => prev.filter(l => l.id !== id));
      toast.success('Licitación eliminada exitosamente');
    } catch (error) {
      console.error('Error deleting licitacion:', error);
      toast.error('Error al eliminar la licitación');
    }
  };

  const organismos = [...new Set(licitaciones.map(l => l.organismo))];
  const estados = [...new Set(licitaciones.map(l => l.estado))];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-700">
            Buscar
          </label>
          <input
            type="text"
            name="search"
            id="search"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Buscar por título u organismo"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="organismo" className="block text-sm font-medium text-gray-700">
            Organismo
          </label>
          <select
            id="organismo"
            name="organismo"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            value={filterOrganismo}
            onChange={(e) => setFilterOrganismo(e.target.value)}
          >
            <option value="">Todos</option>
            {organismos.map(org => (
              <option key={org} value={org}>{org}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="estado" className="block text-sm font-medium text-gray-700">
            Estado
          </label>
          <select
            id="estado"
            name="estado"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            value={filterEstado}
            onChange={(e) => setFilterEstado(e.target.value)}
          >
            <option value="">Todos</option>
            {estados.map(estado => (
              <option key={estado} value={estado}>{estado}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-4">
        <div className="overflow-x-auto">
          <div className="inline-block min-w-full py-2 align-middle">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    {[
                      { field: 'titulo', label: 'Título' },
                      { field: 'organismo', label: 'Organismo' },
                      { field: 'fechaPublicacion', label: 'Fecha de Publicación' },
                      { field: 'fechaApertura', label: 'Fecha de Apertura' },
                      { field: 'presupuesto', label: 'Presupuesto' },
                      { field: 'estado', label: 'Estado' },
                      { field: 'documentos', label: 'Documentos' }
                    ].map(({ field, label }) => (
                      <th
                        key={field}
                        scope="col"
                        className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 cursor-pointer hover:bg-gray-100"
                        onClick={() => handleSort(field as SortField)}
                      >
                        <div className="flex items-center gap-2">
                          {label}
                          {sortField === field ? (
                            sortDirection === 'asc' ? <FaSortUp className="text-indigo-600" /> : <FaSortDown className="text-indigo-600" />
                          ) : (
                            <FaSort className="text-gray-400" />
                          )}
                        </div>
                      </th>
                    ))}
                    <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                      <span className="sr-only">Acciones</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {filteredLicitaciones.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                        No se encontraron licitaciones
                      </td>
                    </tr>
                  ) : (
                    filteredLicitaciones.map((licitacion) => (
                      <tr key={licitacion.id} className="hover:bg-gray-50">
                        <td className="px-3 py-4 text-sm">
                          <div className="max-w-md">
                            <a
                              href={`/licitaciones/${licitacion.id}`}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              {licitacion.titulo}
                            </a>
                          </div>
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-500">
                          <div className="max-w-xs truncate">
                            {licitacion.organismo}
                          </div>
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-500">
                          {formatDate(licitacion.fechaPublicacion)}
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-500">
                          {formatDate(licitacion.fechaApertura)}
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-500">
                          {formatCurrency(licitacion.presupuesto, licitacion.moneda)}
                        </td>
                        <td className="px-3 py-4 text-sm">
                          <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                            licitacion.estado === 'ABIERTA' ? 'bg-green-100 text-green-800' :
                            licitacion.estado === 'CERRADA' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {licitacion.estado}
                          </span>
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-500">
                          <div className="flex items-center gap-2">
                            <FaFile className="text-gray-400" />
                            {licitacion.documentos?.length || 0}
                          </div>
                        </td>
                        <td className="px-3 py-4 text-sm text-right">
                          <div className="flex items-center justify-end gap-3">
                            <a
                              href={`/licitaciones/${licitacion.id}`}
                              className="text-indigo-600 hover:text-indigo-900"
                              title="Ver detalles"
                            >
                              <FaExternalLinkAlt />
                            </a>
                            <a
                              href={`/licitaciones/${licitacion.id}?edit=true`}
                              className="text-indigo-600 hover:text-indigo-900"
                              title="Editar licitación"
                            >
                              <FaEdit />
                            </a>
                            <button
                              onClick={() => handleDelete(licitacion.id)}
                              className="text-red-600 hover:text-red-900"
                              title="Eliminar licitación"
                            >
                              <FaTrash />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LicitacionesTable;
