import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import { useNavigate } from 'react-router-dom';

interface LoginData {
  user_email: string;
  user_password: string;
}

interface RegisterData {
  first_name: string;
  last_name: string;
  user_email: string;
  user_password: string;
  role: number;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

const API_URL = 'http://localhost:8000/api';

export const useAuthActions = () => {
  const [loading, setLoading] = useState(false);
  const { login: setUser, logout: clearUser } = useAuth();
  const { show } = useNotification();
  const navigate = useNavigate();

  const refreshAccessToken = async (): Promise<string | null> => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      return null;
    }

    try {
      const response = await fetch(`${API_URL}/authentication/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }

      const data: TokenResponse = await response.json();
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      return data.access_token;
    } catch (error) {
      console.error('Error refreshing token:', error);
      clearUser();
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      navigate('/login');
      return null;
    }
  };

  const fetchWithToken = async (url: string, options: RequestInit = {}) => {
    let token = localStorage.getItem('token');

    if (!token) {
      token = await refreshAccessToken();
      if (!token) {
        throw new Error('No authentication token available');
      }
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
      },
    });

    if (response.status === 401) {
      // Token might be expired, try to refresh
      token = await refreshAccessToken();
      if (!token) {
        throw new Error('Failed to refresh authentication token');
      }

      // Retry the request with the new token
      return fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${token}`,
        },
      });
    }

    return response;
  };

  const login = async (data: LoginData) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/authentication/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        mode: 'cors',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const tokenData: TokenResponse = await response.json();
      
      // Store both tokens
      localStorage.setItem('token', tokenData.access_token);
      localStorage.setItem('refresh_token', tokenData.refresh_token);
      
      // Get user profile using the new fetchWithToken utility
      const userResponse = await fetchWithToken(`${API_URL}/authentication/me`);

      if (!userResponse.ok) {
        throw new Error('Failed to get user profile');
      }

      const userData = await userResponse.json();
      
      // Update auth context
      setUser(userData);
      
      // Set login flag for enhanced notification
      localStorage.setItem('justLoggedIn', 'true');
      show(`Welcome back, ${userData.first_name}! You're now logged into Reservelt.`, 'success');
      navigate('/');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Invalid email or password';
      show(message, 'error');
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: RegisterData) => {
    setLoading(true);
    try {
      const registerData = {
        ...data,
        role: 0
      };

      const response = await fetch(`${API_URL}/authentication/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
        mode: 'cors',
      });

      if (!response.ok) {
        if (response.status === 500) {
          throw new Error('Server error. Please try again later.');
        }
        const errorData = await response.json();
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            throw new Error(errorData.detail[0].msg);
          } else {
            throw new Error(errorData.detail);
          }
        }
        throw new Error('Registration failed');
      }

      const tokenData: TokenResponse = await response.json();
      
      // Store both tokens
      localStorage.setItem('token', tokenData.access_token);
      localStorage.setItem('refresh_token', tokenData.refresh_token);
      
      // Get user profile using the new fetchWithToken utility
      const userResponse = await fetchWithToken(`${API_URL}/authentication/me`);

      if (!userResponse.ok) {
        throw new Error('Failed to get user profile');
      }

      const userData = await userResponse.json();
      
      // Update auth context
      setUser(userData);
      
      show('Registration successful!', 'success');
      navigate('/');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Registration failed. Please try again.';
      show(message, 'error');
      console.error('Registration error:', error);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    clearUser();
    navigate('/login');
  };

  return {
    login,
    register,
    logout,
    loading,
  };
}; 