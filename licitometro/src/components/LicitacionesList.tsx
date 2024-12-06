import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

interface Licitacion {
  id: number;
  titulo: string;
  descripcion: string;
  presupuesto: number;
  fecha_publicacion: string;
  fecha_cierre: string;
  estado: string;
  organismo: string;
}

interface LicitacionesListProps {
  isLoading?: boolean;
}

const LoadingSkeleton = () => (
  <div className="animate-pulse space-y-4">
    {[1, 2, 3].map((i) => (
      <div key={i} className="bg-white p-4 rounded-lg shadow">
        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        <div className="mt-4 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
      </div>
    ))}
  </div>
);

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('es-AR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS'
  }).format(amount);
};

const LicitacionesList: React.FC<LicitacionesListProps> = () => {
  const [licitaciones, setLicitaciones] = useState<Licitacion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLicitaciones = async () => {
      try {
        const response = await axios.get(`${import.meta.env.PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/licitaciones`);
        setLicitaciones(response.data);
      } catch (err) {
        setError('Error al cargar las licitaciones');
        console.error('Error fetching licitaciones:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLicitaciones();
  }, []);

  if (isLoading) return <LoadingSkeleton />;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Título
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Organismo
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Presupuesto
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Fecha Cierre
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Estado
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {licitaciones.map((licitacion) => (
            <tr key={licitacion.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">
                  {licitacion.titulo}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500">{licitacion.organismo}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500">{formatCurrency(licitacion.presupuesto)}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500">{formatDate(licitacion.fecha_cierre)}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                  ${licitacion.estado === 'Abierta' ? 'bg-green-100 text-green-800' : 
                    licitacion.estado === 'Cerrada' ? 'bg-red-100 text-red-800' : 
                    'bg-yellow-100 text-yellow-800'}`}>
                  {licitacion.estado}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <Link
                  to={`/licitaciones/${licitacion.id}`}
                  className="text-indigo-600 hover:text-indigo-900 mr-4"
                >
                  Ver
                </Link>
                <Link
                  to={`/licitaciones/${licitacion.id}?edit=true`}
                  className="text-green-600 hover:text-green-900"
                >
                  Editar
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LicitacionesList;
