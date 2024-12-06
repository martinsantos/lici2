import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Box
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  PlayArrow as PlayArrowIcon
} from '@mui/icons-material';
import axios from 'axios';

const ReconDashboard = () => {
  const [templates, setTemplates] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentTemplate, setCurrentTemplate] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [templatesResponse, jobsResponse] = await Promise.all([
        axios.get(`${process.env.REACT_APP_API_URL}/recon/templates/`),
        axios.get(`${process.env.REACT_APP_API_URL}/recon/jobs/`)
      ]);
      setTemplates(templatesResponse.data);
      setJobs(jobsResponse.data.jobs);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async (templateData) => {
    try {
      await axios.post(`${process.env.REACT_APP_API_URL}/recon/templates/`, templateData);
      fetchData();
      setOpenDialog(false);
    } catch (error) {
      console.error('Error creating template:', error);
    }
  };

  const handleRunJob = async (templateId) => {
    try {
      await axios.post(`${process.env.REACT_APP_API_URL}/recon/jobs/`, {
        template_id: templateId
      });
      fetchData();
    } catch (error) {
      console.error('Error running job:', error);
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    try {
      await axios.delete(`${process.env.REACT_APP_API_URL}/recon/templates/${templateId}`);
      fetchData();
    } catch (error) {
      console.error('Error deleting template:', error);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h4">RECON Dashboard</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => {
                setCurrentTemplate(null);
                setOpenDialog(true);
              }}
            >
              Nueva Plantilla
            </Button>
          </Box>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Plantillas de Scraping
            </Typography>
            <List>
              {templates.map((template) => (
                <ListItem key={template.id}>
                  <ListItemText
                    primary={template.name}
                    secondary={`URL Base: ${template.base_url}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      aria-label="run"
                      onClick={() => handleRunJob(template.id)}
                      sx={{ mr: 1 }}
                    >
                      <PlayArrowIcon />
                    </IconButton>
                    <IconButton
                      edge="end"
                      aria-label="edit"
                      onClick={() => {
                        setCurrentTemplate(template);
                        setOpenDialog(true);
                      }}
                      sx={{ mr: 1 }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleDeleteTemplate(template.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Trabajos Recientes
            </Typography>
            <List>
              {jobs.map((job) => (
                <ListItem key={job.id}>
                  <ListItemText
                    primary={`Job #${job.id}`}
                    secondary={`Estado: ${job.status} | Fecha: ${new Date(
                      job.created_at
                    ).toLocaleString()}`}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      <TemplateDialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        onSubmit={handleCreateTemplate}
        template={currentTemplate}
      />
    </Container>
  );
};

const TemplateDialog = ({ open, onClose, onSubmit, template }) => {
  const [formData, setFormData] = useState({
    name: '',
    base_url: '',
    selector_config: '',
    auth_config: ''
  });

  useEffect(() => {
    if (template) {
      setFormData({
        name: template.name,
        base_url: template.base_url,
        selector_config: JSON.stringify(template.selector_config, null, 2),
        auth_config: JSON.stringify(template.auth_config, null, 2)
      });
    } else {
      setFormData({
        name: '',
        base_url: '',
        selector_config: '',
        auth_config: ''
      });
    }
  }, [template]);

  const handleSubmit = () => {
    try {
      const data = {
        ...formData,
        selector_config: JSON.parse(formData.selector_config),
        auth_config: formData.auth_config ? JSON.parse(formData.auth_config) : null
      };
      onSubmit(data);
    } catch (error) {
      console.error('Error parsing JSON:', error);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {template ? 'Editar Plantilla' : 'Nueva Plantilla'}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Nombre"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="URL Base"
              value={formData.base_url}
              onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Configuración de Selectores (JSON)"
              value={formData.selector_config}
              onChange={(e) => setFormData({ ...formData, selector_config: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Configuración de Autenticación (JSON, opcional)"
              value={formData.auth_config}
              onChange={(e) => setFormData({ ...formData, auth_config: e.target.value })}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={handleSubmit} variant="contained">
          {template ? 'Guardar' : 'Crear'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ReconDashboard;
