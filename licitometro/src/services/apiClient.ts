import axios from 'axios';

const API_URL = import.meta.env.PUBLIC_API_URL || '/api';

export async function apiClient(endpoint: string, options: any = {}) {
  const {
    method = 'GET',
    body,
    headers = {},
  } = options;

  try {
    const response = await axios({
      method,
      url: `${API_URL}${endpoint}`,
      data: body,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    });

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('API Error:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || error.message);
    }
    throw error;
  }
}
