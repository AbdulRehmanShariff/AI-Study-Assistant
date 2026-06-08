import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';

const ProfilePage = () => {
  const { user, logout, setUser } = useAuth();
  const navigate = useNavigate();
  
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  useEffect(() => {
    if (user) {
      setName(user.name || '');
      setEmail(user.email || '');
    }
  }, [user]);

  const handleUpdate = async () => {
    setLoading(true);
    setMessage({ text: '', type: '' });
    try {
      const res = await api.put('/auth/profile', { name, email });
      setUser(res.data.data.user);
      setMessage({ text: 'Profile updated successfully!', type: 'success' });
    } catch (err) {
      setMessage({ text: err.response?.data?.message || 'Failed to update profile.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you absolutely sure you want to delete your account? This will permanently delete all your documents, summaries, flashcards, and chat history. This action cannot be undone.')) {
      return;
    }
    setLoading(true);
    try {
      await api.delete('/auth/account');
      logout();
      navigate('/login');
    } catch (err) {
      setMessage({ text: err.response?.data?.message || 'Failed to delete account.', type: 'error' });
      setLoading(false);
    }
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Profile</h1>
        <p className="page-subtitle">Manage your account information.</p>
      </div>
      <div className="profile-card glass-card" style={{ maxWidth: '600px', margin: '0 auto' }}>
        <div className="profile-avatar" style={{ textAlign: 'center', marginBottom: 'var(--spacing-xl)' }}>
          <span className="avatar-placeholder" style={{ fontSize: '4rem' }}>👤</span>
        </div>
        
        {message.text && (
          <div className={`alert ${message.type === 'error' ? 'alert-error auth-error' : 'upload-success'}`} style={{ marginBottom: 'var(--spacing-lg)' }}>
            {message.text}
          </div>
        )}

        <div className="profile-info">
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input 
              type="text" 
              className="form-input" 
              placeholder="Your name" 
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input 
              type="email" 
              className="form-input" 
              placeholder="your@email.com" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            />
          </div>
          
          <div style={{ display: 'flex', gap: 'var(--spacing-md)', marginTop: 'var(--spacing-xl)' }}>
            <button 
              className="btn btn-primary" 
              onClick={handleUpdate}
              disabled={loading}
              style={{ flex: 1 }}
            >
              {loading ? 'Updating...' : 'Update Profile'}
            </button>
            <button 
              className="btn btn-danger" 
              onClick={handleDelete}
              disabled={loading}
            >
              Delete Account
            </button>
          </div>
        </div>
      </div>
      <div style={{ marginTop: '60px', fontSize: '0.6rem', textAlign: 'center', opacity: 0.08, userSelect: 'none' }}>
        <a href="https://github.com/AbdulRehmanShariff" target="_blank" rel="noopener noreferrer" style={{ color: 'inherit', textDecoration: 'none', display: 'inline-block' }}>
          Developed By Rehman Shariff
        </a>
      </div>
    </div>
  );
};

export default ProfilePage;
