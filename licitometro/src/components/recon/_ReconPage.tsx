'use client';

import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Container, Paper, Tab, Tabs } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { ScrapingTemplate } from '@types/recon';
import MUIProvider from '@components/providers/MUIProvider';
import TemplateList from './_TemplateList';
import TemplateForm from './_TemplateForm';
import RunTemplates from './_RunTemplates';
import { apiClient } from '../../services/apiClient';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`recon-tabpanel-${index}`}
      aria-labelledby={`recon-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ReconPage: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [isCreating, setIsCreating] = useState(false);
  const [templates, setTemplates] = useState<ScrapingTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ScrapingTemplate | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await apiClient('/recon/templates');
      setTemplates(response);
      setError(null);
    } catch (err) {
      console.error('Error loading templates:', err);
      setError('Error al cargar las plantillas');
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleCreateClick = () => {
    setIsCreating(true);
    setSelectedTemplate(null);
  };

  const handleCancelCreate = () => {
    setIsCreating(false);
    setSelectedTemplate(null);
  };

  const handleTemplateSelect = (template: ScrapingTemplate) => {
    setSelectedTemplate(template);
    setIsCreating(true);
  };

  const handleTemplateSubmit = async (template: ScrapingTemplate) => {
    try {
      if (selectedTemplate) {
        await apiClient(`/recon/templates/${selectedTemplate.id}`, {
          method: 'PUT',
          body: template,
        });
      } else {
        await apiClient('/recon/templates', {
          method: 'POST',
          body: template,
        });
      }
      setIsCreating(false);
      setSelectedTemplate(null);
      loadTemplates();
    } catch (err) {
      console.error('Error saving template:', err);
      setError('Error al guardar la plantilla');
    }
  };

  const handleTemplateDelete = async (templateId: string) => {
    try {
      await apiClient(`/recon/templates/${templateId}`, {
        method: 'DELETE',
      });
      loadTemplates();
    } catch (err) {
      console.error('Error deleting template:', err);
      setError('Error al eliminar la plantilla');
    }
  };

  return (
    <MUIProvider>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 2 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs value={currentTab} onChange={handleTabChange}>
              <Tab label="Plantillas" />
              <Tab label="Ejecutar" />
            </Tabs>
          </Box>

          {error && (
            <Typography color="error" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}

          <TabPanel value={currentTab} index={0}>
            {!isCreating ? (
              <>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleCreateClick}
                  sx={{ mb: 2 }}
                >
                  Nueva Plantilla
                </Button>
                <TemplateList
                  templates={templates}
                  onSelect={handleTemplateSelect}
                  onDelete={handleTemplateDelete}
                />
              </>
            ) : (
              <TemplateForm
                template={selectedTemplate}
                onSubmit={handleTemplateSubmit}
                onCancel={handleCancelCreate}
              />
            )}
          </TabPanel>

          <TabPanel value={currentTab} index={1}>
            <RunTemplates templates={templates} />
          </TabPanel>
        </Paper>
      </Container>
    </MUIProvider>
  );
};

const WrappedReconPage = () => {
  return <ReconPage />;
};

export default WrappedReconPage;
