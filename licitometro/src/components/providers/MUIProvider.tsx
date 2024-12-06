import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#3b82f6', // Tailwind blue-500
    },
    secondary: {
      main: '#2563eb', // Tailwind blue-600
    },
  },
});

interface Props {
  children: React.ReactNode;
}

export default function MUIProvider({ children }: Props) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
