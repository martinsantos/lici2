import React, { useEffect, useState } from 'react';

interface Tender {
  id: string;
  title: string;
  organization: string;
  deadline: string;
  budget: number;
  status: 'active' | 'closed' | 'draft';
}

const RecentTenders: React.FC = () => {
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTenders = async () => {
      try {
        const response = await fetch('/api/tenders/recent');
        const data = await response.json();
        setTenders(data);
      } catch (error) {
        console.error('Error fetching recent tenders:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTenders();
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="mb-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="space-y-3 mt-4">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  const getStatusColor = (status: Tender['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'closed':
        return 'bg-red-100 text-red-800';
      case 'draft':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      {tenders.map((tender) => (
        <div
          key={tender.id}
          className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-lg font-medium text-gray-900">{tender.title}</h3>
            <span
              className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(
                tender.status
              )}`}
            >
              {tender.status.charAt(0).toUpperCase() + tender.status.slice(1)}
            </span>
          </div>
          <div className="text-sm text-gray-500 mb-2">{tender.organization}</div>
          <div className="flex justify-between text-sm">
            <div className="text-gray-500">
              <span className="font-medium">Vencimiento:</span>{' '}
              {new Date(tender.deadline).toLocaleDateString()}
            </div>
            <div className="text-gray-500">
              <span className="font-medium">Presupuesto:</span>{' '}
              {new Intl.NumberFormat('es-AR', {
                style: 'currency',
                currency: 'ARS',
              }).format(tender.budget)}
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <a
              href={`/licitaciones/${tender.id}`}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Ver detalles →
            </a>
          </div>
        </div>
      ))}
      {tenders.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No hay licitaciones recientes para mostrar
        </div>
      )}
      <div className="mt-4 text-center">
        <a
          href="/licitaciones"
          className="text-blue-600 hover:text-blue-800 font-medium"
        >
          Ver todas las licitaciones
        </a>
      </div>
    </div>
  );
};

export default RecentTenders;
