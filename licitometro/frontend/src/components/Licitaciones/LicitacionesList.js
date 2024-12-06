import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Container,
  CircularProgress,
  Box,
  Pagination
} from '@mui/material';
import { displayDate } from '../../utils/dateUtils';

const LicitacionesList = () => {
  const [licitaciones, setLicitaciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchLicitaciones();
  }, [page]);

  const fetchLicitaciones = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/licitaciones`, {
        params: {
          skip: (page - 1) * itemsPerPage,
          limit: itemsPerPage
        }
      });
      setLicitaciones(response.data);
      setTotalPages(Math.ceil(response.data.length / itemsPerPage));
    } catch (error) {
      console.error('Error fetching licitaciones:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (event, value) => {
    setPage(value);
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
      <Typography variant="h4" component="h1" gutterBottom>
        Licitaciones
      </Typography>
      <Grid container spacing={3}>
        {licitaciones.map((licitacion) => (
          <Grid item xs={12} key={licitacion.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" component={Link} to={`/licitaciones/${licitacion.id}`} sx={{ textDecoration: 'none', color: 'inherit' }}>
                  {licitacion.titulo}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  ID: {licitacion.id}
                </Typography>
                <Typography variant="body1" paragraph>
                  {licitacion.extracto}
                </Typography>
                <Typography color="textSecondary">
                  Fecha de publicación: {displayDate(licitacion.fecha_publicacion)}
                </Typography>
                <Typography color="textSecondary">
                  Estado: {licitacion.estado}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Box display="flex" justifyContent="center" mt={4}>
        <Pagination
          count={totalPages}
          page={page}
          onChange={handlePageChange}
          color="primary"
        />
      </Box>
    </Container>
  );
};

export default LicitacionesList;
