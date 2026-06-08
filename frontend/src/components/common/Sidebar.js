import React from 'react';
import { NavLink } from 'react-router-dom';

const sidebarItems = [
  { path: '/dashboard', icon: '📊', label: 'Dashboard' },
  { path: '/upload', icon: '📤', label: 'Upload' },
  { path: '/chat', icon: '💬', label: 'AI Chat' },
  { path: '/summary', icon: '📋', label: 'Summaries' },
  { path: '/flashcards', icon: '🧠', label: 'Flashcards' },
  { path: '/quiz', icon: '📝', label: 'Quizzes' },
  { path: '/profile', icon: '👤', label: 'Profile' },
  { path: '/settings', icon: '⚙️', label: 'Settings' },
];

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {sidebarItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `sidebar-item ${isActive ? 'sidebar-item-active' : ''}`
            }
          >
            <span className="sidebar-icon">{item.icon}</span>
            <span className="sidebar-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
