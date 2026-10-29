
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  GraduationCap,
  LogOut,
  LayoutDashboard,
  Users,
  ClipboardCheck,
  FileBarChart,
} from "lucide-react";
import "../styles/global.css";

function TeacherLayout() {
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
          <span>Teacher</span>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/teacher" end className="nav-link">
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </NavLink>

          <NavLink to="/teacher/students" className="nav-link">
            <Users size={18} />
            <span>Students</span>
          </NavLink>

          <NavLink to="/teacher/attendance" className="nav-link">
            <ClipboardCheck size={18} />
            <span>Mark Attendance</span>
          </NavLink>

          <NavLink to="/teacher/reports" className="nav-link">
            <FileBarChart size={18} />
            <span>Reports</span>
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

export default TeacherLayout;
