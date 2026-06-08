import React from 'react';

const LoadingSpinner = ({ size = 'md', text = 'Loading...' }) => {
  return (
    <div className="spinner-container">
      <div className={`spinner spinner-${size}`}></div>
      {text && <p className="spinner-text">{text}</p>}
    </div>
  );
};

export default LoadingSpinner;
