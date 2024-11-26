import { defineMiddleware } from 'astro/middleware';
import { useAuthStore } from '../services/authService';

export const onRequest = defineMiddleware(async (context, next) => {
  const publicPaths = ['/login', '/api/auth/login', '/api/auth/refresh'];
  const isPublicPath = publicPaths.some(path => context.url.pathname.startsWith(path));

  if (isPublicPath) {
    return next();
  }

  const authStore = useAuthStore.getState();
  const token = authStore.token;

  if (!token) {
    return Response.redirect(new URL('/login', context.url));
  }

  // Add token to request headers
  context.locals.token = token;

  const response = await next();

  // Check if the response is unauthorized
  if (response.status === 401) {
    return Response.redirect(new URL('/login', context.url));
  }

  return response;
});
