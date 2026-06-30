/**
 * useAuth — JWT auth state stored in localStorage.
 */
import { useState, useCallback } from "react";

const TOKEN_KEY = "vs_token";
const USER_KEY  = "vs_user";

export default function useAuth(apiUrl) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser]   = useState(() => {
    try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; }
  });

  const _save = (token, user) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    setToken(token);
    setUser(user);
  };

  const register = useCallback(async (username, email, password) => {
    const res = await fetch(`${apiUrl}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Registration failed.");
    _save(data.token, data.user);
    return data.user;
  }, [apiUrl]);

  const login = useCallback(async (email, password) => {
    const res = await fetch(`${apiUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Login failed.");
    _save(data.token, data.user);
    return data.user;
  }, [apiUrl]);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const authHeader = token ? { Authorization: `Bearer ${token}` } : {};

  return { token, user, authHeader, register, login, logout };
}
