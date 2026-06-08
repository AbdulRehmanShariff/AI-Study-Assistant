import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import ProtectedRoute from './components/common/ProtectedRoute';
import { useAuth } from './context/AuthContext';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import ChatPage from './pages/ChatPage';
import SummaryPage from './pages/SummaryPage';
import FlashcardPage from './pages/FlashcardPage';
import QuizPage from './pages/QuizPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';

// Styles
import './App.css';

// Layout wrapper that handles sidebar visibility
const AppLayout = () => {
  const { user } = useAuth();
  const location = useLocation();

  // Public pages don't show sidebar
  const publicPaths = ['/', '/login', '/register'];
  const isPublicPage = publicPaths.includes(location.pathname);
  const showSidebar = user && !isPublicPage;

  return (
    <>
      <Navbar />
      <div className="app-layout">
        {showSidebar && <Sidebar />}
        <main className={`main-content ${!showSidebar ? 'main-content-full' : ''}`}>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected Routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute><DashboardPage /></ProtectedRoute>
            } />
            <Route path="/upload" element={
              <ProtectedRoute><UploadPage /></ProtectedRoute>
            } />
            <Route path="/chat" element={
              <ProtectedRoute><ChatPage /></ProtectedRoute>
            } />
            <Route path="/summary" element={
              <ProtectedRoute><SummaryPage /></ProtectedRoute>
            } />
            <Route path="/flashcards" element={
              <ProtectedRoute><FlashcardPage /></ProtectedRoute>
            } />
            <Route path="/quiz" element={
              <ProtectedRoute><QuizPage /></ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute><ProfilePage /></ProtectedRoute>
            } />
            <Route path="/settings" element={
              <ProtectedRoute><SettingsPage /></ProtectedRoute>
            } />
          </Routes>
        </main>
      </div>
    </>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppLayout />
      </AuthProvider>
    </Router>
  );
}

export default App;
