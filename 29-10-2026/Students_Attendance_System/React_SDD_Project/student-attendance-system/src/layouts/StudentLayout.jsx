
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { GraduationCap, LogOut, LayoutDashboard } from "lucide-react";
import "../styles/global.css";

function StudentLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <GraduationCap size={28} />
          <span>Attendance</span>
        </div>

        <div className="sidebar-user">
          <strong>{user?.name}</strong>
          <span>Student</span>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/student" end className="nav-link">
            <LayoutDashboard size={18} />
            <span>My Attendance</span>
          </NavLink>
        </nav>

        <button className="logout-button" onClick={handleLogout}>
          <LogOut size={18} />
          <span>Logout</span>
        </button>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

export default StudentLayout;
