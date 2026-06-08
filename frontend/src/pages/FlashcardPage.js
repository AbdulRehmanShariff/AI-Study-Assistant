import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const FlashcardPage = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [deck, setDeck] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch available documents on load
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const res = await api.get('/documents/');
        const ready = (res.data.data.documents || []).filter(d => d.status === 'ready');
        setDocuments(ready);
      } catch { /* silent */ }
    };
    fetchDocuments();
  }, []);

  // When a document is selected, try to load existing flashcards
  useEffect(() => {
    if (selectedDoc) {
      loadFlashcards(selectedDoc);
    } else {
      setDeck(null);
    }
  }, [selectedDoc]);

  const loadFlashcards = async (docId) => {
    setLoading(true);
    setError('');
    setDeck(null);
    setIsFlipped(false);
    setCurrentIndex(0);

    try {
      const res = await api.get(`/flashcards/${docId}`);
      if (res.data.data.deck) {
        setDeck(res.data.data.deck);
      }
    } catch (err) {
      if (err.response?.status !== 404) {
        setError('Error loading flashcards. ' + (err.response?.data?.message || ''));
      }
    } finally {
      setLoading(false);
    }
  };

  const generateFlashcards = async () => {
    if (!selectedDoc) return;
    
    setLoading(true);
    setError('');
    setDeck(null);
    setIsFlipped(false);
    setCurrentIndex(0);

    try {
      const res = await api.post('/flashcards/generate', {
        document_id: selectedDoc,
        count: 10
      });
      setDeck(res.data.data.deck);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to generate flashcards.');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (deck && currentIndex < deck.cards.length - 1) {
      setIsFlipped(false);
      setTimeout(() => setCurrentIndex(prev => prev + 1), 150); // wait for flip to hide
    }
  };

  const handlePrev = () => {
    if (deck && currentIndex > 0) {
      setIsFlipped(false);
      setTimeout(() => setCurrentIndex(prev => prev - 1), 150);
    }
  };

  const flipCard = () => {
    setIsFlipped(!isFlipped);
  };

  return (
    <div className="page-content">
      <div className="glass-card" style={{ padding: 'var(--spacing-xl)', maxWidth: '900px', margin: '0 auto', width: '100%' }}>
        <h1 className="page-title">🧠 AI Flashcards</h1>
        <p className="page-subtitle" style={{ marginBottom: 'var(--spacing-xl)' }}>
          Review interactive AI-generated flashcards from your study materials.
        </p>

        <div className="form-group" style={{ maxWidth: '400px', marginBottom: 'var(--spacing-2xl)' }}>
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

        {error && (
          <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-lg)' }}>
            {error}
          </div>
        )}

        <div style={{ minHeight: '450px', position: 'relative' }}>
          {loading && (
            <div className="loading-state" style={{ position: 'absolute', inset: 0 }}>
              <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
              <p>{deck ? 'Loading...' : 'Generating 10 AI Flashcards...'}</p>
              {!deck && <small style={{ color: 'var(--text-muted)' }}>This takes about 10 seconds.</small>}
            </div>
          )}

          {!loading && !deck && selectedDoc && (
            <div className="flashcard-empty-state">
              <h3>No flashcards found</h3>
              <p style={{ marginBottom: 'var(--spacing-lg)' }}>You haven't generated any flashcards for this document yet.</p>
              <button className="btn btn-primary" onClick={generateFlashcards}>
                Generate 10 Flashcards
              </button>
            </div>
          )}

          {!loading && !selectedDoc && (
             <div className="flashcard-empty-state">
               <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🗂️</div>
               <h3>Select a document</h3>
               <p>Pick a document from the dropdown to start studying.</p>
             </div>
          )}

          {!loading && deck && deck.cards && deck.cards.length > 0 && (
            <>
              <h3 style={{ textAlign: 'center', marginBottom: 'var(--spacing-md)', color: 'var(--text-secondary)' }}>
                {deck.title}
              </h3>
              
              <div className="flashcard-container" onClick={flipCard}>
                <div className={`flashcard ${isFlipped ? 'flipped' : ''}`}>
                  
                  {/* Front Side */}
                  <div className="flashcard-front">
                    <span className="flashcard-label">Question</span>
                    <p className="flashcard-text">{deck.cards[currentIndex].question || deck.cards[currentIndex].q}</p>
                    <span className="flashcard-hint">Click to reveal answer</span>
                  </div>

                  {/* Back Side */}
                  <div className="flashcard-back">
                    <span className="flashcard-label">Answer</span>
                    <p className="flashcard-text">{deck.cards[currentIndex].answer || deck.cards[currentIndex].a}</p>
                    <span className="flashcard-hint">Click to flip back</span>
                  </div>

                </div>
              </div>

              <div className="flashcard-controls">
                <button 
                  className="btn btn-outline" 
                  onClick={handlePrev} 
                  disabled={currentIndex === 0}
                >
                  &larr; Previous
                </button>
                <div className="flashcard-progress">
                  {currentIndex + 1} / {deck.cards.length}
                </div>
                <button 
                  className="btn btn-outline" 
                  onClick={handleNext} 
                  disabled={currentIndex === deck.cards.length - 1}
                >
                  Next &rarr;
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default FlashcardPage;
