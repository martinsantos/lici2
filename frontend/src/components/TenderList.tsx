import React from 'react';
import { Link } from 'react-router-dom';

interface Tender {
  id: string;
  title: string;
  description: string;
  budget: number;
  publishDate: string;
  closeDate: string;
  status: string;
}

interface TenderListProps {
  tenders?: Tender[];
  isLoading?: boolean;
}

const LoadingSkeleton = () => (
  <div className="animate-pulse space-y-4">
    {[1, 2, 3].map((i) => (
      <div key={i} className="bg-white p-4">
        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        <div className="mt-4 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
      </div>
    ))}
  </div>
);

const TenderList: React.FC<TenderListProps> = ({ tenders = [], isLoading = false }) => {
  // Mock data for testing
  const mockTenders: Tender[] = [
    {
      id: '1',
      title: 'TRANCA PANFILOAS',
      description: 'Esta es una licitación de prueba',
      budget: 444,
      publishDate: '2024-03-12',
      closeDate: '2024-04-12',
      status: 'Publicada'
    },
    {
      id: '2',
      title: 'Licitación de prueba',
      description: 'Esta es una licitación de prueba',
      budget: 0,
      publishDate: '2024-03-12',
      closeDate: '2024-04-12',
      status: 'Publicada'
    }
  ];

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  return (
    <div className="bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">Licitaciones</h1>
          <Link
            to="/licitaciones/new"
            className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 focus:outline-none"
          >
            Nueva Licitación
          </Link>
        </div>

        <div className="divide-y divide-gray-200">
          {mockTenders.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No se encontraron licitaciones</p>
            </div>
          ) : (
            mockTenders.map((tender) => (
              <div key={tender.id} className="py-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Link 
                        to={`/licitaciones/${tender.id}`} 
                        className="text-indigo-600 hover:text-indigo-900 font-medium"
                      >
                        {tender.title}
                      </Link>
                      <span className="text-gray-500 text-sm">en</span>
                    </div>
                    <p className="text-gray-600 mt-1">{tender.description}</p>
                    <p className="text-gray-600">Presupuesto: ${tender.budget}</p>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {tender.status}
                    </span>
                    <div className="mt-2 text-sm text-gray-500 space-x-4">
                      <span>Publicación: {tender.publishDate}</span>
                      <span>Cierre: {tender.closeDate}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default TenderList;
