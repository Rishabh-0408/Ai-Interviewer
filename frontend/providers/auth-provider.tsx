"use client";

/**
 * Firebase Authentication context provider.
 *
 * Wraps the app with auth state, providing user info,
 * login/register/logout functions, and ID token access.
 */

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  updateProfile,
  type User,
} from "firebase/auth";
import { auth } from "@/lib/firebase";
import { api } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => Promise<void>;
  getIdToken: () => Promise<string | null>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!auth) {
      setLoading(false);
      return;
    }
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const login = async (email: string, password: string) => {
    if (!auth) {
      setError("Firebase Auth is not configured yet. Please check environment variables.");
      return;
    }
    setError(null);
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Login failed";
      setError(friendlyAuthError(message));
      throw err;
    }
  };

  const register = async (
    email: string,
    password: string,
    name?: string
  ) => {
    if (!auth) {
      setError("Firebase Auth is not configured yet. Please check environment variables.");
      return;
    }
    setError(null);
    try {
      const credential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
      );

      if (name) {
        await updateProfile(credential.user, { displayName: name });
      }

      // Sync user to PostgreSQL backend
      try {
        await api.post("/api/v1/auth/register");
      } catch {
        // Backend sync can fail silently — will retry on next request
        console.warn("Backend user sync deferred");
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Registration failed";
      setError(friendlyAuthError(message));
      throw err;
    }
  };

  const logout = async () => {
    if (!auth) return;
    setError(null);
    await signOut(auth);
  };

  const getIdToken = async (): Promise<string | null> => {
    if (!auth?.currentUser) return null;
    return auth.currentUser.getIdToken();
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider
      value={{ user, loading, error, login, register, logout, getIdToken, clearError }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

/** Map Firebase error codes to user-friendly messages. */
function friendlyAuthError(message: string): string {
  if (message.includes("user-not-found") || message.includes("wrong-password")) {
    return "Invalid email or password.";
  }
  if (message.includes("email-already-in-use")) {
    return "An account with this email already exists.";
  }
  if (message.includes("weak-password")) {
    return "Password must be at least 6 characters.";
  }
  if (message.includes("invalid-email")) {
    return "Please enter a valid email address.";
  }
  if (message.includes("too-many-requests")) {
    return "Too many attempts. Please try again later.";
  }
  return "Authentication failed. Please try again.";
}
