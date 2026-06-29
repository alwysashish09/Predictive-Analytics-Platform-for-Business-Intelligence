import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import UploadPage from './pages/Upload';
import DatasetsList from './pages/DatasetsList';
import DatasetDetail from './pages/DatasetDetail';

// Placeholder pages — will be built in later phases
function PlaceholderPage({ title }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-50 dark:bg-dark-950">
      <div className="glass-card p-8 text-center animate-fade-in">
        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl gradient-primary flex items-center justify-center">
          <span className="text-2xl text-white">📊</span>
        </div>
        <h1 className="text-2xl font-bold gradient-text mb-2">{title}</h1>
        <p className="text-dark-500 dark:text-dark-400">Coming soon...</p>
      </div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* Protected routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute><DatasetsList /></ProtectedRoute>
            } />
            <Route path="/upload" element={
              <ProtectedRoute><UploadPage /></ProtectedRoute>
            } />
            <Route path="/datasets" element={
              <ProtectedRoute><DatasetsList /></ProtectedRoute>
            } />
            <Route path="/datasets/:id" element={
              <ProtectedRoute><DatasetDetail /></ProtectedRoute>
            } />
            <Route path="/ml/:datasetId" element={
              <ProtectedRoute><PlaceholderPage title="ML Pipeline" /></ProtectedRoute>
            } />
            <Route path="/chat/:datasetId" element={
              <ProtectedRoute><PlaceholderPage title="Ask Your Data" /></ProtectedRoute>
            } />
            <Route path="/reports" element={
              <ProtectedRoute><PlaceholderPage title="Reports" /></ProtectedRoute>
            } />
            <Route path="/settings" element={
              <ProtectedRoute><PlaceholderPage title="Settings" /></ProtectedRoute>
            } />

            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
