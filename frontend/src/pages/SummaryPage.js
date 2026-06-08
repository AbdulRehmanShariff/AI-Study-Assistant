import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const SummaryPage = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [style, setStyle] = useState('concise');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await api.get('/documents/');
      const ready = (res.data.data.documents || []).filter(d => d.status === 'ready');
      setDocuments(ready);
    } catch { /* silent */ }
  };

  const generateSummary = async () => {
    if (!selectedDoc) {
      setError('Please select a document first.');
      return;
    }

    setLoading(true);
    setError('');
    setSummary('');

    try {
      const res = await api.post('/summaries/generate', {
        document_id: selectedDoc,
        style: style
      });
      setSummary(res.data.data.summary);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to generate summary.');
    } finally {
      setLoading(false);
    }
  };

  const formatMarkdown = (text) => {
    if (!text) return '';
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^- (.*$)/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <div className="page-content summary-page">
      <div className="glass-card" style={{ padding: 'var(--spacing-xl)', maxWidth: '900px', margin: '0 auto', width: '100%' }}>
        <h1 className="page-title">📝 AI Document Summaries</h1>
        <p className="page-subtitle" style={{ marginBottom: 'var(--spacing-xl)' }}>
          Generate beautiful, structured summaries of your uploaded study materials.
        </p>

        <div className="summary-controls" style={{ display: 'flex', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-xl)', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '250px' }}>
            <label className="form-label">Select Document</label>
            <select 
              className="form-input" 
              value={selectedDoc} 
              onChange={e => setSelectedDoc(e.target.value)}
            >
              <option value="">-- Choose a document --</option>
              {documents.map(d => (
                <option key={d.id} value={d.id}>{d.original_name}</option>
              ))}
            </select>
          </div>

          <div style={{ flex: 1, minWidth: '200px' }}>
            <label className="form-label">Summary Style</label>
            <select 
              className="form-input" 
              value={style} 
              onChange={e => setStyle(e.target.value)}
            >
              <option value="concise">Concise Bullet Points</option>
              <option value="detailed">Detailed Overview</option>
              <option value="actionable">Actionable Takeaways</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button 
              className="btn btn-primary" 
              onClick={generateSummary}
              disabled={loading || !selectedDoc}
              style={{ height: '44px' }}
            >
              {loading ? <span className="spinner spinner-sm" style={{ margin: '0 auto' }}></span> : 'Generate Summary'}
            </button>
          </div>
        </div>

        {error && (
          <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-lg)' }}>
            {error}
          </div>
        )}

        <div className="summary-result-container" style={{ 
          background: 'var(--bg-tertiary)', 
          border: '1px solid var(--glass-border)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--spacing-lg)',
          minHeight: '300px'
        }}>
          {loading ? (
            <div className="loading-state">
              <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
              <p>Reading document and generating summary...</p>
              <small style={{ color: 'var(--text-muted)' }}>This can take 5-15 seconds depending on document length.</small>
            </div>
          ) : summary ? (
            <div 
              className="markdown-body" 
              style={{ lineHeight: 1.6, color: 'var(--text-primary)' }}
              dangerouslySetInnerHTML={{ __html: formatMarkdown(summary) }}
            />
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <h3>No summary generated yet</h3>
              <p>Select a document and click generate to get started.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SummaryPage;
