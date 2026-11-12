
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";

import {
  loginUser,
  getCurrentUser,
  logoutUser,
} from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore the login session when the page is refreshed.
  useEffect(() => {
    let cancelled = false;

    async function restoreSession() {
      if (!sessionStorage.getItem("access_token")) {
        setLoading(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser();

        if (!cancelled) {
          setUser({
            ...currentUser,
            role: currentUser.role.toLowerCase(),
          });
        }
      } catch (error) {
        sessionStorage.removeItem("access_token");

        if (!cancelled) {
          setUser(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    restoreSession();

    return () => {
      cancelled = true;
    };
  }, []);

  // Authenticate using the FastAPI backend.
  const login = useCallback(async (username, password) => {
    try {
      const authenticatedUser = await loginUser(username, password);

      const safeUser = {
        ...authenticatedUser,
        role: authenticatedUser.role.toLowerCase(),
      };

      setUser(safeUser);

      return {
        success: true,
        user: safeUser,
      };
    } catch (error) {
      return {
        success: false,
        message: error.message || "Login failed. Please try again.",
      };
    }
  }, []);

  // End the backend session and clear the local session.
  const logout = useCallback(async () => {
    try {
      await logoutUser();
    } finally {
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
