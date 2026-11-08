// Replaces: src/context/AuthContext.jsx
import { createContext, useContext, useState } from 'react';
import { loginRequest } from '../api';

const AuthContext = createContext(null);

function readStoredUser() {
  try {
    const user = JSON.parse(sessionStorage.getItem('user'));
    return user && sessionStorage.getItem('token') ? user : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser); // survives a page refresh (same tab)

  // Now async: talks to the backend. Throws on wrong email / password / role.
  const login = async (email, password, role) => {
    const data = await loginRequest(email, password, role);
    sessionStorage.setItem('token', data.accessToken);
    sessionStorage.setItem('user', JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
