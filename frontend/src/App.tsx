import { BrowserRouter as Router, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TicketPortal from './pages/TicketPortal';
import AdminDashboard from './pages/AdminDashboard';
import AdminLogin from './pages/AdminLogin';
import RepairAssistantPage from './pages/RepairAssistantPage';
import { Activity, LogOut } from 'lucide-react';

const queryClient = new QueryClient();

// Protected Route Wrapper
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const token = localStorage.getItem('adminToken');
  const location = useLocation();

  if (!token) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  return children;
};

function App() {
  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    window.location.href = '/admin/login';
  };
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen flex flex-col font-sans text-slate-900 bg-slate-50">
          <header className="glass sticky top-0 z-50 px-8 py-4 flex justify-between items-center">
            <Link to="/" className="flex items-center space-x-2 text-accent font-black text-2xl tracking-tighter">
              <Activity size={32} />
              <span>UniBike</span>
            </Link>
            <nav className="flex items-center space-x-6 font-semibold text-sm">
              <Link to="/" className="hover:text-accent transition-colors">Report Issue</Link>
              <Link to="/repair" className="hover:text-accent transition-colors">Repair Assistant</Link>
              <Link to="/admin" className="hover:text-accent transition-colors flex items-center space-x-1">
                <span>Admin Dashboard</span>
              </Link>
              {localStorage.getItem('adminToken') && (
                <button onClick={handleLogout} className="text-slate-500 hover:text-rose-500 transition-colors" title="Logout">
                  <LogOut size={18} />
                </button>
              )}
            </nav>
          </header>

          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<TicketPortal />} />
              <Route path="/repair" element={<RepairAssistantPage />} />
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route path="/admin/*" element={
                <ProtectedRoute>
                  <AdminDashboard />
                </ProtectedRoute>
              } />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
