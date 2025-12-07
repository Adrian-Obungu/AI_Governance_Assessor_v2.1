import { render, screen } from '@testing-library/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { vi } from 'vitest';
import App from '../App';
import { useAuth } from '../context/AuthContext';

// Mock the actual page components to simplify testing
vi.mock('../pages/DashboardPage', () => ({ default: () => <div>Dashboard Content</div> }));
vi.mock('../pages/LoginPage', () => ({ default: () => <div>Login Content</div> }));

const mockUseAuth = useAuth as unknown as ReturnType<typeof vi.fn>;

const renderApp = (initialEntries: string[] = ['/dashboard']) => {
  return render(
    <BrowserRouter>
      <Routes>
        <Route path="*" element={<App />} />
      </Routes>
    </BrowserRouter>,
    { wrapper: ({ children }) => children }
  );
};

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the protected content when authenticated', () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true, login: vi.fn(), logout: vi.fn(), user: { username: 'test' } });
    renderApp();

    // The App component redirects '/' to '/dashboard'
    expect(screen.getByText('Dashboard Content')).toBeInTheDocument();
    expect(screen.queryByText('Login Content')).not.toBeInTheDocument();
  });

  it('should redirect to login page when not authenticated', () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false, login: vi.fn(), logout: vi.fn(), user: null });
    renderApp(['/dashboard']);

    // The ProtectedRoute should redirect to /login
    expect(screen.getByText('Login Content')).toBeInTheDocument();
    expect(screen.queryByText('Dashboard Content')).not.toBeInTheDocument();
  });

  it('should render login page directly for the /login route', () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true, login: vi.fn(), logout: vi.fn(), user: { username: 'test' } });
    renderApp(['/login']);

    // Should render login content regardless of auth status
    expect(screen.getByText('Login Content')).toBeInTheDocument();
    expect(screen.queryByText('Dashboard Content')).not.toBeInTheDocument();
  });
});
