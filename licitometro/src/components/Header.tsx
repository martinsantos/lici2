import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow">
      <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between items-center">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">Licitometro 2.0</h1>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <a href="/" className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900">
                Inicio
              </a>
              <a href="/licitaciones" className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900">
                Licitaciones
              </a>
              <a href="/documentos" className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900">
                Documentos
              </a>
              <a href="/plantillas" className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900">
                Plantillas
              </a>
            </div>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;
