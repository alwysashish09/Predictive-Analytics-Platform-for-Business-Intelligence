import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Will be connected to Supabase in Phase 03
    setLoading(false);
  }, []);

  const signIn = async (email, password) => {
    // Placeholder — implemented in Phase 03
    console.log('signIn called', email);
  };

  const signUp = async (email, password, fullName) => {
    // Placeholder — implemented in Phase 03
    console.log('signUp called', email, fullName);
  };

  const signOut = async () => {
    // Placeholder — implemented in Phase 03
    setUser(null);
    setSession(null);
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
}
