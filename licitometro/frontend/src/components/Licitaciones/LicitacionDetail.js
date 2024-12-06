import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import {
  Container,
  Paper,
  Typography,
  CircularProgress,
  Box,
  Grid,
  Divider,
  Chip
} from '@mui/material';
import { displayDate } from '../../utils/dateUtils';

const LicitacionDetail = () => {
  const { id } = useParams();
  const [licitacion, setLicitacion] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLicitacionDetail();
  }, [id]);

  const fetchLicitacionDetail = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/licitaciones/${id}`);
      setLicitacion(response.data);
    } catch (error) {
      console.error('Error fetching licitacion detail:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!licitacion) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h5" color="error">
          Licitación no encontrada
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          {licitacion.titulo}
        </Typography>
        <Divider sx={{ my: 2 }} />
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Detalles Generales
            </Typography>
            <Typography><strong>Expediente:</strong> {licitacion.numero_expediente}</Typography>
            <Typography><strong>Número:</strong> {licitacion.numero_licitacion}</Typography>
            <Typography><strong>Organismo:</strong> {licitacion.organismo}</Typography>
            <Typography><strong>Estado:</strong> {licitacion.estado}</Typography>
            <Typography><strong>Presupuesto:</strong> {licitacion.presupuesto} {licitacion.moneda}</Typography>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Fechas
            </Typography>
            <Typography><strong>Publicación:</strong> {displayDate(licitacion.fecha_publicacion)}</Typography>
            <Typography><strong>Apertura:</strong> {displayDate(licitacion.fecha_apertura)}</Typography>
          </Grid>

          {licitacion.extractos && licitacion.extractos.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                Extractos
              </Typography>
              <Box sx={{ mt: 2 }}>
                {licitacion.extractos.map((extracto, index) => (
                  <Paper key={extracto.id || index} sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="subtitle1" gutterBottom>
                      <strong>{extracto.tipo}</strong>
                    </Typography>
                    <Typography>{extracto.texto}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Fuente: {extracto.fuente}
                    </Typography>
                  </Paper>
                ))}
              </Box>
            </Grid>
          )}
        </Grid>
      </Paper>
    </Container>
  );
};

export default LicitacionDetail;
