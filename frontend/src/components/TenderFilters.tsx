import React, { useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';

interface FilterState {
  status: string[];
  budget: {
    min: string;
    max: string;
  };
  deadline: {
    from: string;
    to: string;
  };
  organization: string[];
}

interface TenderFiltersProps {
  isOpen: boolean;
  onClose: () => void;
  onApplyFilters: (filters: FilterState) => void;
}

const TenderFilters: React.FC<TenderFiltersProps> = ({
  isOpen,
  onClose,
  onApplyFilters,
}) => {
  const [filters, setFilters] = useState<FilterState>({
    status: [],
    budget: { min: '', max: '' },
    deadline: { from: '', to: '' },
    organization: [],
  });

  const statusOptions = [
    { id: 'active', label: 'Activa' },
    { id: 'closed', label: 'Cerrada' },
    { id: 'draft', label: 'Borrador' },
  ];

  const handleStatusChange = (statusId: string) => {
    setFilters((prev) => ({
      ...prev,
      status: prev.status.includes(statusId)
        ? prev.status.filter((id) => id !== statusId)
        : [...prev.status, statusId],
    }));
  };

  const handleBudgetChange = (field: 'min' | 'max', value: string) => {
    setFilters((prev) => ({
      ...prev,
      budget: {
        ...prev.budget,
        [field]: value,
      },
    }));
  };

  const handleDeadlineChange = (field: 'from' | 'to', value: string) => {
    setFilters((prev) => ({
      ...prev,
      deadline: {
        ...prev.deadline,
        [field]: value,
      },
    }));
  };

  const handleApply = () => {
    onApplyFilters(filters);
    onClose();
  };

  const handleReset = () => {
    setFilters({
      status: [],
      budget: { min: '', max: '' },
      deadline: { from: '', to: '' },
      organization: [],
    });
  };

  return (
    <Transition show={isOpen} as={React.Fragment}>
      <Dialog
        as="div"
        className="fixed inset-0 z-10 overflow-y-auto"
        onClose={onClose}
      >
        <div className="min-h-screen px-4 text-center">
          <Transition.Child
            as={React.Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <Dialog.Overlay className="fixed inset-0 bg-black opacity-30" />
          </Transition.Child>

          <span
            className="inline-block h-screen align-middle"
            aria-hidden="true"
          >
            &#8203;
          </span>

          <Transition.Child
            as={React.Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <div className="inline-block w-full max-w-md p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-2xl">
              <Dialog.Title
                as="h3"
                className="text-lg font-medium leading-6 text-gray-900"
              >
                Filtros de Licitaciones
              </Dialog.Title>

              <div className="mt-4 space-y-6">
                {/* Estado */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Estado
                  </h4>
                  <div className="space-y-2">
                    {statusOptions.map((option) => (
                      <label
                        key={option.id}
                        className="flex items-center space-x-2"
                      >
                        <input
                          type="checkbox"
                          checked={filters.status.includes(option.id)}
                          onChange={() => handleStatusChange(option.id)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700">
                          {option.label}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Presupuesto */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Presupuesto
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs text-gray-500">Mínimo</label>
                      <input
                        type="number"
                        value={filters.budget.min}
                        onChange={(e) =>
                          handleBudgetChange('min', e.target.value)
                        }
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">Máximo</label>
                      <input
                        type="number"
                        value={filters.budget.max}
                        onChange={(e) =>
                          handleBudgetChange('max', e.target.value)
                        }
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                  </div>
                </div>

                {/* Fecha límite */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Fecha límite
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs text-gray-500">Desde</label>
                      <input
                        type="date"
                        value={filters.deadline.from}
                        onChange={(e) =>
                          handleDeadlineChange('from', e.target.value)
                        }
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">Hasta</label>
                      <input
                        type="date"
                        value={filters.deadline.to}
                        onChange={(e) =>
                          handleDeadlineChange('to', e.target.value)
                        }
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={handleReset}
                  className="inline-flex justify-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Limpiar
                </button>
                <button
                  type="button"
                  onClick={handleApply}
                  className="inline-flex justify-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Aplicar
                </button>
              </div>
            </div>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition>
  );
};

export default TenderFilters;
