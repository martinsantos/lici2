import React from 'react';

export default function Header() {
  return (
    <header className="bg-white shadow">
      <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8" aria-label="Top">
        <div className="flex w-full items-center justify-between border-b border-primary-500 py-6">
          <div className="flex items-center">
            <a href="/">
              <span className="text-2xl font-bold text-primary-600">Licitometro</span>
            </a>
            <div className="ml-10 hidden space-x-8 lg:block">
              <a href="/licitaciones" className="text-base font-medium text-gray-500 hover:text-gray-900">
                Licitaciones
              </a>
              <a href="/documentos" className="text-base font-medium text-gray-500 hover:text-gray-900">
                Documentos
              </a>
              <a href="/estadisticas" className="text-base font-medium text-gray-500 hover:text-gray-900">
                Estadísticas
              </a>
            </div>
          </div>
          <div className="ml-10 space-x-4">
            <a
              href="/buscar"
              className="inline-block rounded-md border border-transparent bg-primary-500 py-2 px-4 text-base font-medium text-white hover:bg-opacity-75"
            >
              Buscar
            </a>
          </div>
        </div>
        {/* Mobile menu */}
        <div className="flex flex-wrap justify-center space-x-6 py-4 lg:hidden">
          <a href="/licitaciones" className="text-base font-medium text-gray-500 hover:text-gray-900">
            Licitaciones
          </a>
          <a href="/documentos" className="text-base font-medium text-gray-500 hover:text-gray-900">
            Documentos
          </a>
          <a href="/estadisticas" className="text-base font-medium text-gray-500 hover:text-gray-900">
            Estadísticas
          </a>
        </div>
      </nav>
    </header>
  );
}
