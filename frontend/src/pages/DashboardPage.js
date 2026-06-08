import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const DashboardPage = () => {
  const [stats, setStats] = useState({
    documents: 0,
    chats: 0,
    flashcards: 0,
    quizzes: 0,
    recent_documents: [],
    recent_chats: []
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/dashboard/stats');
        if (res.data.data) {
          setStats(res.data.data);
        }
      } catch (err) {
        console.error("Failed to load dashboard stats", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Welcome back! Here's your study overview.</p>
      </div>

      {loading ? (
        <div style={{ padding: 'var(--spacing-2xl)', textAlign: 'center' }}>
           <div className="spinner" style={{ margin: '0 auto' }}></div>
           <p style={{ marginTop: 'var(--spacing-md)' }}>Loading your dashboard...</p>
        </div>
      ) : (
        <>
          <div className="dashboard-stats">
            <div className="stat-card glass-card">
              <div className="stat-icon">📄</div>
              <div className="stat-info">
                <span className="stat-value">{stats.documents}</span>
                <span className="stat-label">Documents</span>
              </div>
            </div>
            <div className="stat-card glass-card">
              <div className="stat-icon">💬</div>
              <div className="stat-info">
                <span className="stat-value">{stats.chats}</span>
                <span className="stat-label">Chats</span>
              </div>
            </div>
            <div className="stat-card glass-card">
              <div className="stat-icon">🧠</div>
              <div className="stat-info">
                <span className="stat-value">{stats.flashcards}</span>
                <span className="stat-label">Flashcards</span>
              </div>
            </div>
            <div className="stat-card glass-card">
              <div className="stat-icon">📝</div>
              <div className="stat-info">
                <span className="stat-value">{stats.quizzes}</span>
                <span className="stat-label">Quizzes</span>
              </div>
            </div>
          </div>

          <div className="dashboard-grid">
            <div className="dashboard-section glass-card">
              <h2 className="section-title">Recent Documents</h2>
              {stats.recent_documents.length === 0 ? (
                <div className="empty-state">
                  <span className="empty-icon">📁</span>
                  <p>No documents uploaded yet.</p>
                </div>
              ) : (
                <div className="documents-list">
                  {stats.recent_documents.map(doc => (
                    <div key={doc._id} className="document-card" style={{ padding: 'var(--spacing-md)', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
                      <div className="doc-icon">📄</div>
                      <div className="doc-info">
                        <div className="doc-name">{doc.original_name}</div>
                        <div className="doc-meta">Status: {doc.status} • {new Date(doc.uploaded_at).toLocaleDateString()}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="dashboard-section glass-card">
              <h2 className="section-title">Recent Chats</h2>
              {stats.recent_chats.length === 0 ? (
                <div className="empty-state">
                  <span className="empty-icon">💭</span>
                  <p>No conversations yet.</p>
                </div>
              ) : (
                <div className="documents-list">
                  {stats.recent_chats.map(chat => (
                    <div key={chat._id} className="document-card" style={{ padding: 'var(--spacing-md)', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
                      <div className="doc-icon">💬</div>
                      <div className="doc-info">
                        <div className="doc-name">{chat.question}</div>
                        <div className="doc-meta">{new Date(chat.created_at || chat.timestamp).toLocaleDateString()}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DashboardPage;
