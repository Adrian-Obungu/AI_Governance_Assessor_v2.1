import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock the AuthContext for testing purposes
vi.mock('./context/AuthContext', () => ({
  useAuth: vi.fn(() => ({
    isAuthenticated: false,
    login: vi.fn(),
    logout: vi.fn(),
    user: null,
  })),
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
}));
