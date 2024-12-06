import React, { useState } from 'react';
import { TemplateEditor } from './TemplateEditor';
import { ScrapingStatus } from './ScrapingStatus';
import { DocumentAnalysis } from './DocumentAnalysis';

export const ReconDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('templates');

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <nav className="flex border-b mb-6">
        <button
          className={`mr-6 py-2 ${activeTab === 'templates' ? 'border-b-2 border-blue-500' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          Plantillas
        </button>
        <button
          className={`mr-6 py-2 ${activeTab === 'scraping' ? 'border-b-2 border-blue-500' : ''}`}
          onClick={() => setActiveTab('scraping')}
        >
          Estado del Scraping
        </button>
        <button
          className={`py-2 ${activeTab === 'analysis' ? 'border-b-2 border-blue-500' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          Análisis de Documentos
        </button>
      </nav>

      <div className="mt-6">
        {activeTab === 'templates' && <TemplateEditor />}
        {activeTab === 'scraping' && <ScrapingStatus />}
        {activeTab === 'analysis' && <DocumentAnalysis />}
      </div>
    </div>
  );
};
