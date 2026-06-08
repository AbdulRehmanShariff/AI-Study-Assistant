import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const QuizPage = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  
  const [quiz, setQuiz] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState(null);
  const [score, setScore] = useState(0);
  const [showResult, setShowResult] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch available documents
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

  // When doc changes, fetch existing quiz if any
  useEffect(() => {
    if (selectedDoc) {
      loadQuiz(selectedDoc);
    } else {
      setQuiz(null);
    }
  }, [selectedDoc]);

  const loadQuiz = async (docId) => {
    resetState();
    setLoading(true);
    try {
      const res = await api.get(`/quiz/${docId}`);
      if (res.data.data.quiz) {
        setQuiz(res.data.data.quiz);
      }
    } catch (err) {
      if (err.response?.status !== 404) {
        setError('Error loading quiz. ' + (err.response?.data?.message || ''));
      }
    } finally {
      setLoading(false);
    }
  };

  const generateQuiz = async () => {
    if (!selectedDoc) return;
    
    resetState();
    setLoading(true);
    try {
      const res = await api.post('/quiz/generate', {
        document_id: selectedDoc,
        count: 5
      });
      setQuiz(res.data.data.quiz);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to generate quiz.');
    } finally {
      setLoading(false);
    }
  };

  const resetState = () => {
    setQuiz(null);
    setCurrentIndex(0);
    setSelectedOption(null);
    setScore(0);
    setShowResult(false);
    setError('');
  };

  const handleOptionSelect = (index) => {
    // Only allow selection if an option hasn't been picked yet for this question
    if (selectedOption !== null) return;
    
    setSelectedOption(index);
    const q = quiz.questions[currentIndex];
    if (index === q.correct_index) {
      setScore(s => s + 1);
    }
  };

  const handleNextQuestion = () => {
    if (currentIndex < quiz.questions.length - 1) {
      setCurrentIndex(c => c + 1);
      setSelectedOption(null);
    } else {
      setShowResult(true);
    }
  };

  const restartQuiz = () => {
    setCurrentIndex(0);
    setSelectedOption(null);
    setScore(0);
    setShowResult(false);
  };

  return (
    <div className="page-content">
      <div className="glass-card" style={{ padding: 'var(--spacing-xl)', maxWidth: '900px', margin: '0 auto', width: '100%' }}>
        <h1 className="page-title">📝 AI Quiz Evaluator</h1>
        <p className="page-subtitle" style={{ marginBottom: 'var(--spacing-xl)' }}>
          Test your knowledge with multiple-choice questions generated from your document.
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

        <div style={{ minHeight: '400px', position: 'relative' }}>
          {loading && (
            <div className="loading-state" style={{ position: 'absolute', inset: 0 }}>
              <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
              <p>{quiz ? 'Loading...' : 'Generating AI Quiz...'}</p>
              {!quiz && <small style={{ color: 'var(--text-muted)' }}>This takes about 10 seconds.</small>}
            </div>
          )}

          {!loading && !quiz && selectedDoc && (
            <div className="flashcard-empty-state">
              <h3>No quiz found</h3>
              <p style={{ marginBottom: 'var(--spacing-lg)' }}>Generate a quiz to test your knowledge.</p>
              <button className="btn btn-primary" onClick={generateQuiz}>
                Generate Quiz
              </button>
            </div>
          )}

          {!loading && !selectedDoc && (
             <div className="flashcard-empty-state">
               <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎓</div>
               <h3>Select a document</h3>
               <p>Pick a document from the dropdown to start the quiz.</p>
             </div>
          )}

          {!loading && quiz && !showResult && (
            <div className="quiz-container">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ color: 'var(--text-secondary)' }}>Question {currentIndex + 1} of {quiz.questions.length}</h3>
                <span style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>Score: {score}</span>
              </div>

              <div className="quiz-question" style={{ fontSize: '1.25rem', fontWeight: 500, marginBottom: 'var(--spacing-xl)' }}>
                {quiz.questions[currentIndex].question}
              </div>

              <div className="quiz-options" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                {quiz.questions[currentIndex].options.map((opt, idx) => {
                  const isSelected = selectedOption === idx;
                  const isCorrect = quiz.questions[currentIndex].correct_index === idx;
                  const hasAnswered = selectedOption !== null;
                  
                  let optStyle = {
                    padding: 'var(--spacing-md) var(--spacing-lg)',
                    border: '1px solid var(--glass-border)',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-tertiary)',
                    cursor: hasAnswered ? 'default' : 'pointer',
                    transition: 'var(--transition-fast)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-md)',
                    fontSize: '1rem'
                  };

                  if (hasAnswered) {
                    if (isCorrect) {
                      optStyle.background = 'rgba(0, 212, 170, 0.15)';
                      optStyle.borderColor = 'rgba(0, 212, 170, 0.5)';
                      optStyle.color = '#6ee7d4';
                    } else if (isSelected) {
                      optStyle.background = 'rgba(239, 68, 68, 0.15)';
                      optStyle.borderColor = 'rgba(239, 68, 68, 0.5)';
                      optStyle.color = '#fca5a5';
                    } else {
                      optStyle.opacity = 0.5;
                    }
                  }

                  return (
                    <div 
                      key={idx} 
                      style={optStyle}
                      onClick={() => handleOptionSelect(idx)}
                      onMouseEnter={e => {
                        if (!hasAnswered) {
                          e.currentTarget.style.background = 'var(--glass-hover)';
                          e.currentTarget.style.borderColor = 'var(--accent-primary)';
                        }
                      }}
                      onMouseLeave={e => {
                        if (!hasAnswered) {
                          e.currentTarget.style.background = 'var(--bg-tertiary)';
                          e.currentTarget.style.borderColor = 'var(--glass-border)';
                        }
                      }}
                    >
                      <div style={{ 
                        width: '24px', height: '24px', borderRadius: '50%', 
                        border: hasAnswered && isCorrect ? '2px solid #6ee7d4' : (hasAnswered && isSelected ? '2px solid #fca5a5' : '2px solid var(--text-muted)'),
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '0.8rem', fontWeight: 'bold'
                      }}>
                        {['A', 'B', 'C', 'D'][idx]}
                      </div>
                      <div style={{ flex: 1 }}>{opt}</div>
                      {hasAnswered && isCorrect && <span>✅</span>}
                      {hasAnswered && isSelected && !isCorrect && <span>❌</span>}
                    </div>
                  );
                })}
              </div>

              {selectedOption !== null && (
                <div style={{ marginTop: 'var(--spacing-xl)', animation: 'slideUp 0.3s ease' }}>
                  <div style={{ 
                    padding: 'var(--spacing-lg)', 
                    background: 'var(--bg-secondary)', 
                    borderRadius: 'var(--radius-md)',
                    borderLeft: `4px solid ${selectedOption === quiz.questions[currentIndex].correct_index ? '#6ee7d4' : '#fca5a5'}`
                  }}>
                    <h4 style={{ marginBottom: 'var(--spacing-sm)', color: selectedOption === quiz.questions[currentIndex].correct_index ? '#6ee7d4' : '#fca5a5' }}>
                      {selectedOption === quiz.questions[currentIndex].correct_index ? 'Correct!' : 'Incorrect'}
                    </h4>
                    <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                      {quiz.questions[currentIndex].explanation}
                    </p>
                  </div>
                  
                  <div style={{ marginTop: 'var(--spacing-xl)', textAlign: 'right' }}>
                    <button className="btn btn-primary" onClick={handleNextQuestion}>
                      {currentIndex < quiz.questions.length - 1 ? 'Next Question &rarr;' : 'View Results'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {showResult && (
            <div className="quiz-result" style={{ textAlign: 'center', padding: 'var(--spacing-2xl) 0' }}>
              <div style={{ fontSize: '4rem', marginBottom: 'var(--spacing-md)' }}>
                {score === quiz.questions.length ? '🏆' : (score > quiz.questions.length / 2 ? '👍' : '📚')}
              </div>
              <h2 style={{ fontSize: '2rem', marginBottom: 'var(--spacing-sm)' }}>Quiz Complete!</h2>
              <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', marginBottom: 'var(--spacing-2xl)' }}>
                You scored <span style={{ fontWeight: 700, color: 'var(--accent-primary)', fontSize: '1.5rem' }}>{score}</span> out of {quiz.questions.length}
              </p>
              
              <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--spacing-md)' }}>
                <button className="btn btn-outline" onClick={restartQuiz}>
                  Retake Quiz
                </button>
                <button className="btn btn-primary" onClick={generateQuiz}>
                  Generate New Quiz
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuizPage;
