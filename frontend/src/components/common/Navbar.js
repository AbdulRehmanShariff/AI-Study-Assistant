import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isLanding = location.pathname === '/';
  const isAuth = ['/login', '/register'].includes(location.pathname);

  return (
    <nav className={`navbar ${isLanding ? 'navbar-transparent' : ''}`}>
      <div className="navbar-container">
        <Link to={user ? '/dashboard' : '/'} className="navbar-brand">
          <span className="brand-icon">🎓</span>
          <span className="brand-text">StudyAI</span>
        </Link>

        <button
          className="navbar-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <span className={`hamburger ${mobileMenuOpen ? 'active' : ''}`}></span>
        </button>

        <div className={`navbar-menu ${mobileMenuOpen ? 'navbar-menu-open' : ''}`}>
          {user ? (
            <>
              <div className="navbar-user">
                <span className="user-avatar">👤</span>
                <span className="user-name">{user.name || 'User'}</span>
              </div>
              <button className="btn btn-outline btn-sm" onClick={logout}>
                Logout
              </button>
            </>
          ) : (
            !isAuth && (
              <>
                <Link to="/login" className="btn btn-outline btn-sm">Sign In</Link>
                <Link to="/register" className="btn btn-primary btn-sm">Get Started</Link>
              </>
            )
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
