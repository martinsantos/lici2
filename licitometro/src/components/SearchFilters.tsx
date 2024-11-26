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

interface SearchFiltersProps {
  onFilterChange: (filters: any) => void;
}

export default function SearchFilters({ onFilterChange }: SearchFiltersProps) {
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
      return newFilters;
    });
    onFilterChange(selectedFilters);
  };

  return (
    <div className="bg-white">
      {/* Mobile filter dialog */}
      <Transition.Root show={mobileFiltersOpen} as={React.Fragment}>
        <Dialog as="div" className="relative z-40 lg:hidden" onClose={setMobileFiltersOpen}>
          <div className="fixed inset-0 bg-black bg-opacity-25" />
          
          <div className="fixed inset-0 z-40 flex">
            <Dialog.Panel className="relative ml-auto flex h-full w-full max-w-xs flex-col overflow-y-auto bg-white py-4 pb-6 shadow-xl">
              <div className="flex items-center justify-between px-4">
                <h2 className="text-lg font-medium text-gray-900">Filtros</h2>
                <button
                  type="button"
                  className="-mr-2 flex h-10 w-10 items-center justify-center rounded-md bg-white p-2 text-gray-400 hover:bg-gray-50"
                  onClick={() => setMobileFiltersOpen(false)}
                >
                  <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                </button>
              </div>

              {/* Filters */}
              <form className="mt-4">
                {Object.entries(filters).map(([sectionId, section]) => (
                  <Disclosure as="div" key={sectionId} className="border-t border-gray-200 px-4 py-6">
                    {({ open }) => (
                      <>
                        <h3 className="-mx-2 -my-3 flow-root">
                          <Disclosure.Button className="flex w-full items-center justify-between bg-white px-2 py-3 text-sm text-gray-400">
                            <span className="font-medium text-gray-900">
                              {sectionId.charAt(0).toUpperCase() + sectionId.slice(1)}
                            </span>
                            <span className="ml-6 flex items-center">
                              <ChevronDownIcon
                                className={`h-5 w-5 ${open ? '-rotate-180' : 'rotate-0'}`}
                                aria-hidden="true"
                              />
                            </span>
                          </Disclosure.Button>
                        </h3>
                        <Disclosure.Panel className="pt-6">
                          <div className="space-y-6">
                            {section.map((option, optionIdx) => (
                              <div key={option.value} className="flex items-center">
                                <input
                                  id={`filter-mobile-${sectionId}-${optionIdx}`}
                                  name={`${sectionId}[]`}
                                  defaultValue={option.value}
                                  type="checkbox"
                                  defaultChecked={option.checked}
                                  onChange={() => handleFilterChange(sectionId, option.value)}
                                  className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                                />
                                <label
                                  htmlFor={`filter-mobile-${sectionId}-${optionIdx}`}
                                  className="ml-3 text-sm text-gray-500"
                                >
                                  {option.label}
                                </label>
                              </div>
                            ))}
                          </div>
                        </Disclosure.Panel>
                      </>
                    )}
                  </Disclosure>
                ))}
              </form>
            </Dialog.Panel>
          </div>
        </Dialog>
      </Transition.Root>

      {/* Desktop filter section */}
      <div className="border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center">
              <button
                type="button"
                className="inline-flex items-center lg:hidden"
                onClick={() => setMobileFiltersOpen(true)}
              >
                <span className="text-sm font-medium text-gray-700">Filtros</span>
                <FunnelIcon className="ml-1 h-5 w-5 text-gray-400" aria-hidden="true" />
              </button>
            </div>

            {/* Desktop filters */}
            <div className="hidden lg:flex lg:items-center lg:space-x-8">
              {Object.entries(filters).map(([sectionId, section]) => (
                <div key={sectionId} className="relative inline-block text-left">
                  <Disclosure>
                    {({ open }) => (
                      <>
                        <Disclosure.Button className="group inline-flex justify-center text-sm font-medium text-gray-700 hover:text-gray-900">
                          {sectionId.charAt(0).toUpperCase() + sectionId.slice(1)}
                          <ChevronDownIcon
                            className={`ml-2 h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-gray-500 ${
                              open ? '-rotate-180' : 'rotate-0'
                            }`}
                            aria-hidden="true"
                          />
                        </Disclosure.Button>

                        <Transition
                          enter="transition ease-out duration-100"
                          enterFrom="transform opacity-0 scale-95"
                          enterTo="transform opacity-100 scale-100"
                          leave="transition ease-in duration-75"
                          leaveFrom="transform opacity-100 scale-100"
                          leaveTo="transform opacity-0 scale-95"
                        >
                          <Disclosure.Panel className="absolute right-0 z-10 mt-2 w-40 origin-top-right rounded-md bg-white shadow-2xl ring-1 ring-black ring-opacity-5 focus:outline-none">
                            <div className="py-1">
                              {section.map((option, optionIdx) => (
                                <div
                                  key={option.value}
                                  className="flex items-center px-4 py-2 hover:bg-gray-50"
                                >
                                  <input
                                    id={`filter-${sectionId}-${optionIdx}`}
                                    name={`${sectionId}[]`}
                                    defaultValue={option.value}
                                    type="checkbox"
                                    defaultChecked={option.checked}
                                    onChange={() => handleFilterChange(sectionId, option.value)}
                                    className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                                  />
                                  <label
                                    htmlFor={`filter-${sectionId}-${optionIdx}`}
                                    className="ml-3 text-sm text-gray-500"
                                  >
                                    {option.label}
                                  </label>
                                </div>
                              ))}
                            </div>
                          </Disclosure.Panel>
                        </Transition>
                      </>
                    )}
                  </Disclosure>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
