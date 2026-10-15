import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserResponse, UserLogin } from '../types';
import { authService } from '../services/apiServices';
import { safeStorage } from '../utils/safeStorage';

interface AuthContextType {
  user: UserResponse | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: UserLogin) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [token, setToken] = useState<string | null>(() => safeStorage.getItem('access_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    const timeout = setTimeout(() => {
      if (isMounted) setIsLoading(false);
    }, 4000); // 4-second safety guard: never leave user hanging on loading screen

    const initAuth = async () => {
      try {
        const storedToken = safeStorage.getItem('access_token');
        if (storedToken) {
          try {
            const profile = await authService.getCurrentUser();
            if (isMounted) {
              setUser(profile);
              setToken(storedToken);
            }
          } catch (err) {
            console.warn('Failed to verify existing session:', err);
            safeStorage.removeItem('access_token');
            safeStorage.removeItem('refresh_token');
            if (isMounted) {
              setUser(null);
              setToken(null);
            }
          }
        }
      } catch (e) {
        console.warn('Storage initialization error:', e);
      } finally {
        clearTimeout(timeout);
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    initAuth();

    return () => {
      isMounted = false;
      clearTimeout(timeout);
    };
  }, []);

  const login = async (credentials: UserLogin) => {
    setIsLoading(true);
    try {
      const data = await authService.login(credentials);
      safeStorage.setItem('access_token', data.access_token);
      safeStorage.setItem('refresh_token', data.refresh_token);
      setToken(data.access_token);

      if (data.user) {
        setUser(data.user);
      } else {
        const profile = await authService.getCurrentUser();
        setUser(profile);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    const refreshToken = safeStorage.getItem('refresh_token');
    try {
      await authService.logout(refreshToken || undefined);
    } catch (e) {
      console.warn('Logout request failed or expired token');
    } finally {
      safeStorage.removeItem('access_token');
      safeStorage.removeItem('refresh_token');
      setUser(null);
      setToken(null);
    }
  };


  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
