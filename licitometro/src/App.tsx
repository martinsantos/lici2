import React from 'react';
import { Routes, Route } from 'react-router-dom';
import LicitacionForm from './components/LicitacionForm';
import LicitacionesList from './components/LicitacionesList';

// Providers
import { AppProvider } from './store/AppContext';
import { NotificationProvider } from './store/NotificationContext';

function App() {
  return (
    <AppProvider>
      <NotificationProvider>
        <div className="min-h-screen">
          <Routes>
            <Route path="/" element={<LicitacionesList />} />
            <Route path="/licitaciones" element={<LicitacionesList />} />
            <Route path="/licitaciones/new" element={<LicitacionForm />} />
            <Route path="/licitaciones/:id" element={<LicitacionForm isEditing={true} />} />
          </Routes>
        </div>
      </NotificationProvider>
    </AppProvider>
  );
}

export default App;
