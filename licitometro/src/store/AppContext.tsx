import React, { createContext, useContext, useReducer, ReactNode } from 'react';

// Definir el tipo del estado
interface AppState {
  licitaciones: any[];
  currentLicitacion: any | null;
  loading: boolean;
  error: string | null;
}

// Definir el tipo de acción
type AppAction = 
  | { type: 'SET_LICITACIONES'; payload: any[] }
  | { type: 'SET_CURRENT_LICITACION'; payload: any }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null };

// Definir el tipo del contexto
interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
}

// Estado inicial
const initialState: AppState = {
  licitaciones: [],
  currentLicitacion: null,
  loading: false,
  error: null,
};

// Crear el contexto con un valor inicial
const AppContext = createContext<AppContextType>({
  state: initialState,
  dispatch: () => {
    console.warn('AppContext dispatch called before initialization');
  },
});

// Hook personalizado para usar el contexto
export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

// Reducer para manejar las acciones
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_LICITACIONES':
      return {
        ...state,
        licitaciones: action.payload,
        loading: false,
      };
    case 'SET_CURRENT_LICITACION':
      return {
        ...state,
        currentLicitacion: action.payload,
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };
    default:
      return state;
  }
};

// Propiedades del proveedor
interface AppProviderProps {
  children: ReactNode;
}

// Provider component
export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Memoizar el valor del contexto
  const value = React.useMemo(
    () => ({
      state,
      dispatch,
    }),
    [state]
  );

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

export default AppContext;
