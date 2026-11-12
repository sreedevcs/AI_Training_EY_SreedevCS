
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function ProtectedRoute({ allowedRole }) {
  const { user, loading } = useAuth();

  // Wait for session restoration before checking authentication.
  if (loading) {
    return <p>Checking your session...</p>;
  }

  // Redirect users who are not logged in.
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Prevent students and teachers from accessing each other's pages.
  if (allowedRole && user.role !== allowedRole) {
    return (
      <Navigate
        to={user.role === "teacher" ? "/teacher" : "/student"}
        replace
      />
    );
  }

  return <Outlet />;
}

export default ProtectedRoute;
