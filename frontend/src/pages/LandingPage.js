import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="landing-page">
      <div className="landing-hero">
        <div className="landing-hero-content">
          <h1 className="landing-title">
            Study Smarter with <span className="gradient-text">AI</span>
          </h1>
          <p className="landing-subtitle">
            Upload your study materials, ask questions, generate flashcards, quizzes, and summaries — all powered by AI.
          </p>
          <div className="landing-cta">
            <Link to="/register" className="btn btn-primary btn-lg">Get Started Free</Link>
            <Link to="/login" className="btn btn-outline btn-lg">Sign In</Link>
          </div>
        </div>
        <div className="landing-features">
          <div className="feature-card glass-card">
            <div className="feature-icon">📄</div>
            <h3>Smart Documents</h3>
            <p>Upload PDFs and notes. Our AI processes and understands your content.</p>
          </div>
          <div className="feature-card glass-card">
            <div className="feature-icon">💬</div>
            <h3>AI Chat</h3>
            <p>Ask questions about your documents and get accurate, sourced answers.</p>
          </div>
          <div className="feature-card glass-card">
            <div className="feature-icon">🧠</div>
            <h3>Flashcards & Quizzes</h3>
            <p>Auto-generate study materials to test your knowledge.</p>
          </div>
          <div className="feature-card glass-card">
            <div className="feature-icon">📊</div>
            <h3>Summaries</h3>
            <p>Get concise summaries of your documents in seconds.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
