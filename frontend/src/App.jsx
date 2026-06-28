import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';

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
            <Route path="/login" element={<PlaceholderPage title="Login" />} />
            <Route path="/signup" element={<PlaceholderPage title="Sign Up" />} />
            <Route path="/dashboard" element={<PlaceholderPage title="Dashboard" />} />
            <Route path="/upload" element={<PlaceholderPage title="Upload Data" />} />
            <Route path="/datasets" element={<PlaceholderPage title="Datasets" />} />
            <Route path="/datasets/:id" element={<PlaceholderPage title="Dataset Detail" />} />
            <Route path="/ml/:datasetId" element={<PlaceholderPage title="ML Pipeline" />} />
            <Route path="/chat/:datasetId" element={<PlaceholderPage title="Ask Your Data" />} />
            <Route path="/reports" element={<PlaceholderPage title="Reports" />} />
            <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
