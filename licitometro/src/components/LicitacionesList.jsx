import { formatDate, formatCurrency } from '../utils/formatters';

const LicitacionesList = ({ licitaciones }) => {
  return (
    <div className="overflow-hidden bg-white shadow sm:rounded-md">
      <ul role="list" className="divide-y divide-gray-200">
        {licitaciones.map((licitacion) => (
          <li key={licitacion.id}>
            <a href={`/licitaciones/${licitacion.id}`} className="block hover:bg-gray-50">
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="truncate">
                    <div className="flex text-sm">
                      <p className="font-medium text-primary-600 truncate">{licitacion.titulo}</p>
                      <p className="ml-1 flex-shrink-0 font-normal text-gray-500">
                        en {licitacion.entidad}
                      </p>
                    </div>
                    <div className="mt-2 flex">
                      <div className="flex items-center text-sm text-gray-500">
                        <span className="truncate">{licitacion.descripcion}</span>
                      </div>
                    </div>
                  </div>
                  <div className="ml-2 flex flex-shrink-0">
                    <span
                      className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                        licitacion.estado === 'abierta'
                          ? 'bg-green-100 text-green-800'
                          : licitacion.estado === 'cerrada'
                          ? 'bg-red-100 text-red-800'
                          : licitacion.estado === 'adjudicada'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {licitacion.estado.charAt(0).toUpperCase() + licitacion.estado.slice(1)}
                    </span>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <div className="flex items-center text-sm text-gray-500">
                      <span>Presupuesto: {formatCurrency(licitacion.presupuesto)}</span>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                    <div className="flex space-x-4">
                      <div>
                        <span className="font-medium">Publicación:</span>{' '}
                        {formatDate(licitacion.fechaPublicacion)}
                      </div>
                      <div>
                        <span className="font-medium">Cierre:</span>{' '}
                        {formatDate(licitacion.fechaCierre)}
                      </div>
                    </div>
                  </div>
                </div>
                {licitacion.tags && licitacion.tags.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {licitacion.tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default LicitacionesList;
