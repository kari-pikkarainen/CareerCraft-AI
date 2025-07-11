import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Layout.css';

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const isActiveRoute = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  return (
    <div className="layout">
      {/* Header */}
      <header className="layout-header">
        <div className="container">
          <div className="header-content">
            {/* Logo */}
            <Link to="/" className="logo">
              <span className="logo-icon">🎯</span>
              <span className="logo-text">CareerCraft AI</span>
            </Link>

            {/* Navigation */}
            <nav className="main-nav">
              <Link 
                to="/" 
                className={`nav-link ${isActiveRoute('/') && location.pathname === '/' ? 'active' : ''}`}
              >
                Dashboard
              </Link>
              <Link 
                to="/analyze" 
                className={`nav-link ${isActiveRoute('/analyze') ? 'active' : ''}`}
              >
                New Analysis
              </Link>
              <Link 
                to="/history" 
                className={`nav-link ${isActiveRoute('/history') ? 'active' : ''}`}
              >
                History
              </Link>
            </nav>

            {/* User Menu */}
            <div className="user-menu">
              <div className="user-info">
                <span className="user-name">
                  {user?.email || 'User'}
                </span>
              </div>
              <div className="user-actions">
                <Link to="/profile" className="btn btn-secondary btn-sm">
                  Profile
                </Link>
                <button onClick={handleLogout} className="btn btn-secondary btn-sm">
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="layout-main">
        <div className="container">
          <div className="main-content">
            <Outlet />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="layout-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-info">
              <p>&copy; 2024 Kari Pikkarainen. All rights reserved. CareerCraft AI - Proprietary Software.</p>
            </div>
            <div className="footer-links">
              <button className="footer-link">Privacy</button>
              <button className="footer-link">Terms</button>
              <button className="footer-link">Support</button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;