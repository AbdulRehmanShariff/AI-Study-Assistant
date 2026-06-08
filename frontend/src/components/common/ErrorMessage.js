import React from 'react';

const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className="error-container glass-card">
      <div className="error-icon">⚠️</div>
      <p className="error-text">{message || 'Something went wrong.'}</p>
      {onRetry && (
        <button className="btn btn-outline" onClick={onRetry}>Try Again</button>
      )}
    </div>
  );
};

export default ErrorMessage;
