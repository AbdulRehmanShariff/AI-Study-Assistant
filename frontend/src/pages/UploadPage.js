import React, { useState, useEffect, useRef } from 'react';
import api from '../api/axios';

const UploadPage = () => {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await api.get('/documents/');
      setDocuments(res.data.data.documents || []);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFile = async (file) => {
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'txt'].includes(ext)) {
      setError('Only PDF and TXT files are supported.');
      return;
    }

    const maxMB = 50;
    if (file.size > maxMB * 1024 * 1024) {
      setError(`File too large. Maximum size is ${maxMB}MB.`);
      return;
    }

    setError('');
    setSuccess('');
    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          const pct = Math.round((e.loaded * 100) / e.total);
          setUploadProgress(pct);
        },
      });

      const newDoc = res.data.data.document;
      setDocuments((prev) => [newDoc, ...prev]);
      setSuccess(`"${newDoc.original_name}" uploaded successfully!`);
      setUploadProgress(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Upload failed. Please try again.');
      setUploadProgress(null);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) handleFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleDelete = async (docId, docName) => {
    if (!window.confirm(`Delete "${docName}"? This cannot be undone.`)) return;

    try {
      await api.delete(`/documents/${docId}`);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
      setSuccess(`"${docName}" deleted.`);
    } catch (err) {
      setError(err.response?.data?.message || 'Delete failed.');
    }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (iso) =>
    new Date(iso).toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric',
    });

  const statusBadge = (status) => {
    const map = {
      uploaded: { label: 'Uploaded', color: '#6c63ff' },
      processing: { label: 'Processing', color: '#f59e0b' },
      ready: { label: 'Ready', color: '#00d4aa' },
      error: { label: 'Error', color: '#ef4444' },
    };
    const s = map[status] || map.uploaded;
    return (
      <span
        className="doc-status-badge"
        style={{ background: `${s.color}22`, color: s.color, border: `1px solid ${s.color}44` }}
      >
        {s.label}
      </span>
    );
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">📂 Documents</h1>
        <p className="page-subtitle">Upload PDFs and text files to study with AI</p>
      </div>

      {/* Upload Zone */}
      <div
        id="upload-zone"
        className={`upload-zone ${dragOver ? 'upload-zone-active' : ''} ${uploading ? 'upload-zone-disabled' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !uploading && fileInputRef.current?.click()}
        style={{ cursor: uploading ? 'not-allowed' : 'pointer' }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileInput}
          style={{ display: 'none' }}
          id="file-input"
        />

        {uploading ? (
          <div className="upload-progress-area">
            <div className="upload-icon">⏳</div>
            <p className="upload-title">Uploading...</p>
            <div className="progress-bar-wrap">
              <div
                className="progress-bar-fill"
                style={{ width: `${uploadProgress ?? 0}%` }}
              />
            </div>
            <p className="upload-hint">{uploadProgress}% complete</p>
          </div>
        ) : (
          <>
            <div className="upload-icon">📄</div>
            <p className="upload-title">
              {dragOver ? 'Drop it here!' : 'Drag & drop your file here'}
            </p>
            <p className="upload-hint">or click to browse — PDF and TXT up to 50MB</p>
            <button className="btn btn-primary btn-sm" style={{ marginTop: '1rem', pointerEvents: 'none' }}>
              Choose File
            </button>
          </>
        )}
      </div>

      {/* Alerts */}
      {error && (
        <div className="auth-error" style={{ marginBottom: '1.5rem' }}>
          ⚠️ {error}
        </div>
      )}
      {success && (
        <div className="upload-success">
          ✅ {success}
        </div>
      )}

      {/* Documents List */}
      <div className="documents-section">
        <h2 className="section-title">
          Your Documents
          {documents.length > 0 && (
            <span className="doc-count"> ({documents.length})</span>
          )}
        </h2>

        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="empty-state glass-card">
            <div className="empty-icon">📭</div>
            <h3>No documents yet</h3>
            <p>Upload your first PDF or text file to get started</p>
          </div>
        ) : (
          <div className="documents-list">
            {documents.map((doc) => (
              <div key={doc.id} className="document-card glass-card">
                <div className="doc-icon">
                  {doc.file_type === 'pdf' ? '📕' : '📝'}
                </div>
                <div className="doc-info">
                  <p className="doc-name">{doc.original_name}</p>
                  <div className="doc-meta">
                    <span>{formatSize(doc.file_size)}</span>
                    {doc.page_count > 0 && <span>· {doc.page_count} pages</span>}
                    {doc.word_count > 0 && <span>· {doc.word_count.toLocaleString()} words</span>}
                    <span>· {formatDate(doc.uploaded_at)}</span>
                  </div>
                </div>
                <div className="doc-actions">
                  {statusBadge(doc.status)}
                  <button
                    id={`delete-${doc.id}`}
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(doc.id, doc.original_name)}
                    title="Delete document"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadPage;
