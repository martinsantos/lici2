import React, { useState } from 'react';
import { Dialog, Disclosure, Transition } from '@headlessui/react';
import { FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { ChevronDownIcon } from '@heroicons/react/20/solid';

const filters = {
  estado: [
    { value: 'abierta', label: 'Abierta', checked: false },
    { value: 'cerrada', label: 'Cerrada', checked: false },
    { value: 'adjudicada', label: 'Adjudicada', checked: false },
    { value: 'desierta', label: 'Desierta', checked: false },
  ],
  presupuesto: [
    { value: '0-1000000', label: 'Hasta $1.000.000', checked: false },
    { value: '1000000-10000000', label: '$1.000.000 - $10.000.000', checked: false },
    { value: '10000000-50000000', label: '$10.000.000 - $50.000.000', checked: false },
    { value: '50000000-', label: 'Más de $50.000.000', checked: false },
  ],
};

interface SearchFiltersIslandProps {
  onFilterChange: (filters: any) => void;
  client:boolean;
}

export default function SearchFiltersIsland({ onFilterChange, client = false }: SearchFiltersIslandProps) {
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState({
    estado: [],
    presupuesto: [],
  });

  const handleFilterChange = (section: string, value: string) => {
    setSelectedFilters((prev) => {
      const newFilters = { ...prev };
      if (newFilters[section].includes(value)) {
        newFilters[section] = newFilters[section].filter((v) => v !== value);
      } else {
        newFilters[section] = [...newFilters[section], value];
      }

      // Emitir evento de cambio de filtros
      const event = new CustomEvent('filterChange', {
        detail: newFilters
      });
      window.dispatchEvent(event);

      onFilterChange(newFilters);

      return newFilters;
    });
  };

  if (!client) {
    return <div className="animate-pulse bg-gray-200 h-20 rounded-md"></div>;
  }

  return (
    <div className="bg-white shadow-sm rounded-lg p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium">Filtros</h2>
        <button
          type="button"
          className="lg:hidden text-gray-500 hover:text-gray-700"
          onClick={() => setMobileFiltersOpen(true)}
        >
          <FunnelIcon className="h-5 w-5" />
        </button>
      </div>

      {/* Desktop filters */}
      <div className="hidden lg:block">
        {Object.entries(filters).map(([section, options]) => (
          <Disclosure as="div" key={section} className="border-t border-gray-200 py-4">
            {({ open }) => (
              <>
                <Disclosure.Button className="flex w-full justify-between text-left">
                  <span className="text-sm font-medium">{section.charAt(0).toUpperCase() + section.slice(1)}</span>
                  <ChevronDownIcon
                    className={`${open ? 'rotate-180 transform' : ''} h-5 w-5 text-gray-500`}
                  />
                </Disclosure.Button>
                <Disclosure.Panel className="pt-4 pb-2">
                  <div className="space-y-2">
                    {options.map((option) => (
                      <div key={option.value} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={selectedFilters[section].includes(option.value)}
                          onChange={() => handleFilterChange(section, option.value)}
                          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label className="ml-3 text-sm text-gray-600">{option.label}</label>
                      </div>
                    ))}
                  </div>
                </Disclosure.Panel>
              </>
            )}
          </Disclosure>
        ))}
      </div>

      {/* Mobile filters */}
      <Transition.Root show={mobileFiltersOpen} as={React.Fragment}>
        <Dialog as="div" className="relative z-40 lg:hidden" onClose={setMobileFiltersOpen}>
          <Transition.Child
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-25" />
          </Transition.Child>

          <div className="fixed inset-0 z-40 flex">
            <Dialog.Panel className="relative ml-auto flex h-full w-full max-w-xs flex-col overflow-y-auto bg-white py-4 pb-6 shadow-xl">
              <div className="flex items-center justify-between px-4">
                <h2 className="text-lg font-medium">Filtros</h2>
                <button
                  type="button"
                  className="text-gray-500 hover:text-gray-700"
                  onClick={() => setMobileFiltersOpen(false)}
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              <div className="mt-4">
                {Object.entries(filters).map(([section, options]) => (
                  <Disclosure as="div" key={section} className="border-t border-gray-200 px-4 py-6">
                    {({ open }) => (
                      <>
                        <Disclosure.Button className="flex w-full justify-between text-left">
                          <span className="text-sm font-medium">{section.charAt(0).toUpperCase() + section.slice(1)}</span>
                          <ChevronDownIcon
                            className={`${open ? 'rotate-180 transform' : ''} h-5 w-5 text-gray-500`}
                          />
                        </Disclosure.Button>
                        <Disclosure.Panel className="pt-4 pb-2">
                          <div className="space-y-2">
                            {options.map((option) => (
                              <div key={option.value} className="flex items-center">
                                <input
                                  type="checkbox"
                                  checked={selectedFilters[section].includes(option.value)}
                                  onChange={() => handleFilterChange(section, option.value)}
                                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <label className="ml-3 text-sm text-gray-600">{option.label}</label>
                              </div>
                            ))}
                          </div>
                        </Disclosure.Panel>
                      </>
                    )}
                  </Disclosure>
                ))}
              </div>
            </Dialog.Panel>
          </div>
        </Dialog>
      </Transition.Root>
    </div>
  );
}
