import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  LinearProgress,
  Box,
  List,
  ListItem,
  ListItemText,
  Alert,
  Chip,
  Stack,
  Grid
} from '@mui/material';
import axios from 'axios';

const ScrapingProgress = ({ jobId }) => {
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_API_URL}/scrape/status/${jobId}`
        );
        setProgress(response.data);
        setError(null);
      } catch (err) {
        setError('Error al obtener el progreso del scraping');
        console.error('Error fetching scraping progress:', err);
      }
    };

    // Fetch immediately
    fetchProgress();

    // Then fetch every 3 seconds
    const interval = setInterval(fetchProgress, 3000);

    return () => clearInterval(interval);
  }, [jobId]);

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!progress) {
    return <LinearProgress />;
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Progreso de Scraping: {progress.template_name}
      </Typography>

      <Box sx={{ mb: 3 }}>
        <LinearProgress 
          variant="determinate" 
          value={progress.percent_complete} 
          sx={{ height: 10, borderRadius: 5 }}
        />
        <Typography variant="body2" color="text.secondary" align="right" sx={{ mt: 1 }}>
          {progress.percent_complete}% Completado
        </Typography>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Stack spacing={1}>
            <Typography variant="subtitle2">Estadísticas</Typography>
            <Box>
              <Chip 
                label={`Total: ${progress.total_found}`} 
                size="small" 
                sx={{ mr: 1 }}
              />
              <Chip 
                label={`Procesadas: ${progress.processed}`} 
                size="small" 
                sx={{ mr: 1 }}
              />
              <Chip 
                label={`Guardadas: ${progress.saved}`} 
                size="small" 
                color="success"
              />
            </Box>
            <Box>
              <Chip 
                label={`Errores: ${progress.errors}`} 
                size="small" 
                color="error" 
                sx={{ mr: 1 }}
              />
              <Chip 
                label={`Omitidas: ${progress.skipped}`} 
                size="small" 
                color="warning"
              />
            </Box>
          </Stack>
        </Grid>
        <Grid item xs={12} md={6}>
          <Stack spacing={1}>
            <Typography variant="subtitle2">Métricas</Typography>
            <Typography variant="body2">
              Tasa de éxito: {progress.success_rate}%
            </Typography>
            <Typography variant="body2">
              Velocidad: {progress.items_per_minute} items/min
            </Typography>
            <Typography variant="body2">
              Tiempo transcurrido: {progress.elapsed_time}
            </Typography>
          </Stack>
        </Grid>
      </Grid>

      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Estado Actual
        </Typography>
        <Alert severity="info">
          {progress.current_status}
        </Alert>
      </Box>

      {progress.last_saved && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Última Licitación Guardada
          </Typography>
          <Alert severity="success">
            {progress.last_saved}
          </Alert>
        </Box>
      )}

      {progress.error_details && progress.error_details.length > 0 && (
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Últimos Errores
          </Typography>
          <List dense>
            {progress.error_details.map((error, index) => (
              <ListItem key={index}>
                <ListItemText 
                  primary={error}
                  primaryTypographyProps={{ color: 'error' }}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Paper>
  );
};

export default ScrapingProgress;
