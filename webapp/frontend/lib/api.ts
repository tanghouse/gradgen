import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface User {
  id: number;
  email: string;
  full_name?: string;
  credits: number;
  is_active: boolean;
  email_verified: boolean;
  email_verified_at?: string;
  oauth_provider?: string;
  created_at: string;
  last_login_at?: string;
}

export interface University {
  name: string;
  degree_levels: string[];
}

export interface GenerationJob {
  id: number;
  job_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  university: string;
  degree_level: string;
  prompt_id: string;
  total_images: number;
  completed_images: number;
  failed_images: number;
  error_message?: string;
  created_at: string;
  completed_at?: string;
  generated_images: GeneratedImage[];
}

export interface GeneratedImage {
  id: number;
  original_filename: string;
  output_image_path?: string;
  success: boolean;
  error_message?: string;
  created_at: string;
  processed_at?: string;
}

export interface JobStatus {
  job_id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  completed_images: number;
  total_images: number;
  message?: string;
}

// Auth API
export const authAPI = {
  register: async (email: string, password: string, fullName?: string) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  verifyEmail: async (token: string) => {
    const response = await api.post('/auth/verify-email', { token });
    return response.data;
  },

  resendVerification: async (email: string) => {
    const response = await api.post('/auth/resend-verification', { email });
    return response.data;
  },

  // OAuth URLs
  getGoogleAuthUrl: () => `${API_URL}/api/auth/oauth/google/authorize`,
  getMicrosoftAuthUrl: () => `${API_URL}/api/auth/oauth/microsoft/authorize`,
};

// User API
export const userAPI = {
  getMe: async (): Promise<User> => {
    const response = await api.get('/users/me');
    return response.data;
  },

  updateMe: async (data: Partial<User>) => {
    const response = await api.put('/users/me', data);
    return response.data;
  },
};

// Generation API
export const generationAPI = {
  listUniversities: async (): Promise<University[]> => {
    const response = await api.get('/generation/universities');
    return response.data.universities;
  },

  generateSingle: async (
    file: File,
    university: string,
    degreeLevel: string,
    promptId: string = 'P2'
  ): Promise<GenerationJob> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('university', university);
    formData.append('degree_level', degreeLevel);
    formData.append('prompt_id', promptId);

    const response = await api.post('/generation/single', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  generateBatch: async (
    files: File[],
    university: string,
    degreeLevel: string,
    promptId: string = 'P2'
  ): Promise<GenerationJob> => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    formData.append('university', university);
    formData.append('degree_level', degreeLevel);
    formData.append('prompt_id', promptId);

    const response = await api.post('/generation/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  listJobs: async (limit: number = 50): Promise<GenerationJob[]> => {
    const response = await api.get('/generation/jobs', { params: { limit } });
    return response.data;
  },

  getJob: async (jobId: number): Promise<GenerationJob> => {
    const response = await api.get(`/generation/jobs/${jobId}`);
    return response.data;
  },

  getJobStatus: async (jobId: number): Promise<JobStatus> => {
    const response = await api.get(`/generation/jobs/${jobId}/status`);
    return response.data;
  },

  downloadResult: async (imageId: number, filename: string): Promise<void> => {
    const response = await api.get(`/generation/results/${imageId}`, {
      responseType: 'blob',
    });

    // Create a download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};

// Payment API
export const paymentAPI = {
  getConfig: async () => {
    const response = await api.get('/payments/config');
    return response.data;
  },

  createPaymentIntent: async (credits: number) => {
    const response = await api.post('/payments/create-payment-intent', { credits });
    return response.data;
  },
};

export default api;
