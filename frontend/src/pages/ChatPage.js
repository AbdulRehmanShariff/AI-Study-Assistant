import React, { useState, useEffect, useRef } from 'react';
import api from '../api/axios';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput]       = useState('');
  const [loading, setLoading]   = useState(false);
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [llmStatus, setLlmStatus] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
    fetchHistory();
    checkLlmStatus();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const checkLlmStatus = async () => {
    try {
      const res = await api.get('/chat/status');
      setLlmStatus(res.data.data);
    } catch { /* silent */ }
  };

  const fetchDocuments = async () => {
    try {
      const res = await api.get('/documents/');
      const ready = (res.data.data.documents || []).filter(d => d.status === 'ready');
      setDocuments(ready);
    } catch { /* silent */ }
  };

  const fetchHistory = async () => {
    try {
      const res = await api.get('/chat/history');
      const history = res.data.data.messages || [];
      if (history.length > 0) {
        const formatted = history.flatMap(m => [
          { role: 'user', text: m.question, id: m.id + '_q' },
          { role: 'assistant', text: m.answer, sources: m.sources, id: m.id + '_a' },
        ]);
        setMessages(formatted);
      }
    } catch { /* silent */ }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: question, id: Date.now() }]);
    setLoading(true);

    try {
      const payload = { question };
      if (selectedDoc) payload.document_id = selectedDoc;

      const res = await api.post('/chat/ask', payload);
      const { answer, sources } = res.data.data;

      setMessages(prev => [
        ...prev,
        { role: 'assistant', text: answer, sources, id: Date.now() + 1 }
      ]);
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to get answer. Please try again.';
      setMessages(prev => [
        ...prev,
        { role: 'assistant', text: msg, isError: true, id: Date.now() + 1 }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearHistory = async () => {
    if (!window.confirm('Clear all chat history?')) return;
    try {
      await api.delete('/chat/history');
      setMessages([]);
    } catch { /* silent */ }
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
    <div className="page-content chat-page">
      {/* Header */}
      <div className="chat-header glass-card">
        <div className="chat-header-left">
          <h1 className="page-title" style={{ margin: 0, fontSize: '1.3rem' }}>
            🤖 AI Study Assistant
          </h1>

        </div>
        <div className="chat-header-right">
          {documents.length > 0 && (
            <select
              id="doc-selector"
              className="doc-selector"
              value={selectedDoc}
              onChange={e => setSelectedDoc(e.target.value)}
            >
              <option value="">All documents</option>
              {documents.map(d => (
                <option key={d.id} value={d.id}>{d.original_name}</option>
              ))}
            </select>
          )}
          {messages.length > 0 && (
            <button id="clear-chat-btn" className="btn btn-outline btn-sm" onClick={clearHistory}>
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages glass-card">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">💬</div>
            <h3>Ask me anything about your study materials</h3>
            <p>Upload a PDF or text file, then ask questions about it.</p>
            <div className="chat-suggestions">
              {['Summarize the key points', 'Explain the main concepts', 'What are the important topics?'].map(s => (
                <button key={s} className="suggestion-chip" onClick={() => setInput(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map(msg => (
            <div
              key={msg.id}
              className={`chat-message ${msg.role === 'user' ? 'chat-message-user' : 'chat-message-assistant'} ${msg.isError ? 'chat-message-error' : ''}`}
            >
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-bubble">
                {msg.role === 'assistant' ? (
                  <div
                    className="message-text"
                    dangerouslySetInnerHTML={{ __html: formatMarkdown(msg.text) }}
                  />
                ) : (
                  <p className="message-text">{msg.text}</p>
                )}
                {/* Sources */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="message-sources">
                    <p className="sources-label">Sources used:</p>
                    {msg.sources.slice(0, 3).map((s, i) => (
                      <div key={i} className="source-chip">
                        <span className="source-score">{(s.score * 100).toFixed(0)}%</span>
                        <span className="source-text">{s.text.substring(0, 80)}...</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="chat-message chat-message-assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-bubble">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-area glass-card">
        <textarea
          id="chat-input"
          className="chat-textarea"
          placeholder="Ask a question about your study materials... (Enter to send)"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={loading}
        />
        <button
          id="send-btn"
          className="btn btn-primary chat-send-btn"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
        >
          {loading ? <span className="spinner spinner-sm" /> : '➤'}
        </button>
      </div>
    </div>
  );
};

export default ChatPage;
