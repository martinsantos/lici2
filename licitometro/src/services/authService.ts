import { apiClient } from './apiClient';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  nombre: string;
  rol: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setToken: (token) => set({ token }),
      logout: () => set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
);

export async function getAuthToken(): Promise<string | null> {
  return useAuthStore.getState().token;
}

export async function login(email: string, password: string) {
  try {
    const response = await apiClient('/api/auth/login', {
      method: 'POST',
      body: { email, password },
      requiresAuth: false,
    });

    useAuthStore.getState().setToken(response.token);
    useAuthStore.getState().setUser(response.user);

    return response;
  } catch (error) {
    console.error('Error en login:', error);
    throw error;
  }
}

export async function logout() {
  try {
    await apiClient('/api/auth/logout', { method: 'POST' });
  } catch (error) {
    console.error('Error en logout:', error);
  } finally {
    useAuthStore.getState().logout();
    window.location.href = '/login';
  }
}

export async function refreshToken() {
  try {
    const response = await apiClient('/api/auth/refresh', {
      method: 'POST',
      requiresAuth: true,
    });

    useAuthStore.getState().setToken(response.token);
    return response.token;
  } catch (error) {
    console.error('Error al refrescar token:', error);
    useAuthStore.getState().logout();
    throw error;
  }
}

export async function getCurrentUser(): Promise<User | null> {
  try {
    const response = await apiClient('/api/auth/me');
    useAuthStore.getState().setUser(response);
    return response;
  } catch (error) {
    console.error('Error al obtener usuario actual:', error);
    return null;
  }
}
