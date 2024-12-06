import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container
} from '@mui/material';

const Navigation = () => {
  return (
    <AppBar position="static">
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              mr: 4,
              textDecoration: 'none',
              color: 'inherit',
              flexGrow: 0
            }}
          >
            Licitómetro
          </Typography>
          <Button
            component={RouterLink}
            to="/licitaciones"
            color="inherit"
            sx={{ mr: 2 }}
          >
            Licitaciones
          </Button>
          <Button
            component={RouterLink}
            to="/recon"
            color="inherit"
          >
            RECON
          </Button>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navigation;
