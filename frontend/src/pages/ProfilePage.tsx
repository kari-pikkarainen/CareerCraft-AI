import React from 'react';

const ProfilePage: React.FC = () => {
  return (
    <div className="profile-page">
      <div className="page-header">
        <h1>👤 Profile Settings</h1>
        <p>Manage your account settings and preferences</p>
      </div>
      
      <div className="page-content">
        <div className="placeholder-card">
          <h2>Coming Soon</h2>
          <p>This page will feature:</p>
          <ul>
            <li>Account information management</li>
            <li>Password change functionality</li>
            <li>Analysis preferences</li>
            <li>Notification settings</li>
            <li>Data export/import options</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;