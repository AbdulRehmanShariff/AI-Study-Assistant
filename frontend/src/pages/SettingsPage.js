import React from 'react';

const SettingsPage = () => {
  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Configure your application preferences.</p>
      </div>
      <div className="settings-section glass-card">
        <h2 className="section-title">Account</h2>
        <div className="settings-item">
          <div className="settings-item-info">
            <h3>Change Password</h3>
            <p className="text-muted">Update your account password</p>
          </div>
          <button className="btn btn-outline" disabled>Change</button>
        </div>
        <div className="settings-item">
          <div className="settings-item-info">
            <h3>Delete Account</h3>
            <p className="text-muted">Permanently delete your account and data</p>
          </div>
          <button className="btn btn-danger" disabled>Delete</button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
