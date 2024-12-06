import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Components
import LicitacionesList from './components/Licitaciones/LicitacionesList';
import LicitacionDetail from './components/Licitaciones/LicitacionDetail';
import ReconDashboard from './components/Recon/ReconDashboard';
import Navigation from './components/Navigation';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navigation />
        <Routes>
          <Route path="/" element={<LicitacionesList />} />
          <Route path="/licitaciones" element={<LicitacionesList />} />
          <Route path="/licitaciones/:id" element={<LicitacionDetail />} />
          <Route path="/recon" element={<ReconDashboard />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
