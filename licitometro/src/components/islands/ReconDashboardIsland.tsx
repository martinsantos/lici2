import { useState, useEffect } from 'react';

interface Template {
  id: string;
  name: string;
  base_url: string;
  selector_config: Record<string, any>;
  auth_config?: Record<string, any>;
}

interface Job {
  id: string;
  template_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export default function ReconDashboardIsland() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [currentTemplate, setCurrentTemplate] = useState<Template | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [templatesRes, jobsRes] = await Promise.all([
        fetch('/api/recon/templates'),
        fetch('/api/recon/jobs')
      ]);

      if (templatesRes.ok && jobsRes.ok) {
        const templatesData = await templatesRes.json();
        const jobsData = await jobsRes.json();
        setTemplates(templatesData);
        setJobs(jobsData.jobs);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async (templateData: Partial<Template>) => {
    try {
      const response = await fetch('/api/recon/templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData),
      });

      if (response.ok) {
        await fetchData();
        setIsDialogOpen(false);
      }
    } catch (error) {
      console.error('Error creating template:', error);
    }
  };

  const handleRunJob = async (templateId: string) => {
    try {
      const response = await fetch('/api/recon/jobs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ template_id: templateId }),
      });

      if (response.ok) {
        await fetchData();
      }
    } catch (error) {
      console.error('Error running job:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Templates Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Plantillas de Scraping</h2>
          <button
            onClick={() => {
              setCurrentTemplate(null);
              setIsDialogOpen(true);
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
          >
            Nueva Plantilla
          </button>
        </div>

        <div className="space-y-4">
          {templates.map((template) => (
            <div key={template.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium text-gray-900">{template.name}</h3>
                  <p className="text-sm text-gray-500">{template.base_url}</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleRunJob(template.id)}
                    className="text-blue-500 hover:text-blue-700"
                  >
                    Ejecutar
                  </button>
                  <button
                    onClick={() => {
                      setCurrentTemplate(template);
                      setIsDialogOpen(true);
                    }}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    Editar
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Jobs Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Trabajos Recientes</h2>
        <div className="space-y-4">
          {jobs.map((job) => (
            <div key={job.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-medium text-gray-900">Job #{job.id}</h3>
                  <p className="text-sm text-gray-500">
                    Estado: {job.status} | {new Date(job.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Template Dialog */}
      {isDialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full">
            <h2 className="text-xl font-semibold mb-4">
              {currentTemplate ? 'Editar Plantilla' : 'Nueva Plantilla'}
            </h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                const templateData = {
                  name: formData.get('name') as string,
                  base_url: formData.get('base_url') as string,
                  selector_config: JSON.parse(formData.get('selector_config') as string),
                  auth_config: formData.get('auth_config')
                    ? JSON.parse(formData.get('auth_config') as string)
                    : undefined,
                };
                handleCreateTemplate(templateData);
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700">Nombre</label>
                <input
                  type="text"
                  name="name"
                  defaultValue={currentTemplate?.name}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">URL Base</label>
                <input
                  type="url"
                  name="base_url"
                  defaultValue={currentTemplate?.base_url}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Configuración de Selectores (JSON)
                </label>
                <textarea
                  name="selector_config"
                  defaultValue={
                    currentTemplate
                      ? JSON.stringify(currentTemplate.selector_config, null, 2)
                      : ''
                  }
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  rows={4}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Configuración de Autenticación (JSON, opcional)
                </label>
                <textarea
                  name="auth_config"
                  defaultValue={
                    currentTemplate?.auth_config
                      ? JSON.stringify(currentTemplate.auth_config, null, 2)
                      : ''
                  }
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  rows={4}
                />
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setIsDialogOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-500"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-500 rounded-md hover:bg-blue-600"
                >
                  {currentTemplate ? 'Guardar' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
