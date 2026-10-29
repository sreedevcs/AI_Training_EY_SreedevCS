import { useEffect, useState } from "react";
import {
  Users,
  UserCheck,
  UserX,
  ClipboardCheck,
  GraduationCap,
  FileBarChart,
  UserRound,
  CalendarDays,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../services/api";
import "../styles/global.css";

function TeacherDashboard() {
  const { user } = useAuth();
  const teacher = {
    name: user?.name || user?.username || "Teacher",
  };

  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadDashboardStats() {
      setLoading(true);
      setError("");

      try {
        const now = new Date();
        const attendanceDate = [
          now.getFullYear(),
          String(now.getMonth() + 1).padStart(2, "0"),
          String(now.getDate()).padStart(2, "0"),
        ].join("-");

        const [studentData, attendanceData] = await Promise.all([
          apiRequest("/students/"),
          apiRequest(`/attendance/?attendance_date=${attendanceDate}`),
        ]);

        if (
          !Array.isArray(studentData?.students) ||
          !Array.isArray(attendanceData?.records)
        ) {
          throw new Error("Unexpected response while loading dashboard data.");
        }

        if (!cancelled) {
          setStats({
            totalStudents: studentData.students.filter(
              (student) => student.is_active
            ).length,
            presentToday: attendanceData.records.filter(
              (record) => record.status === "Present"
            ).length,
            absentToday: attendanceData.records.filter(
              (record) => record.status === "Absent"
            ).length,
          });
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Unable to load dashboard statistics.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDashboardStats();

    return () => {
      cancelled = true;
    };
  }, []);

  const navigationItems = [
    {
      label: "Dashboard",
      icon: <ClipboardCheck size={20} />,
      active: true,
    },
    {
      label: "Students",
      icon: <Users size={20} />,
      active: false,
    },
    {
      label: "Mark Attendance",
      icon: <UserCheck size={20} />,
      active: false,
    },
    {
      label: "Reports",
      icon: <FileBarChart size={20} />,
      active: false,
    },
  ];

  return (
    <div className="teacher-dashboard">
      <aside className="teacher-sidebar">
        <div className="teacher-brand">
          <GraduationCap size={30} />
          <span>AttendEase</span>
        </div>

        <p className="sidebar-label">MAIN MENU</p>

        <nav className="sidebar-nav">
          {navigationItems.map((item) => (
            <button
              key={item.label}
              className={`sidebar-link ${
                item.active ? "active" : ""
              }`}
              type="button"
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="teacher-avatar">
            <UserRound size={22} />
          </div>

          <div>
            <strong>{teacher.name}</strong>
            <p>Teacher</p>
          </div>
        </div>
      </aside>

      <main className="teacher-main">
        <header className="teacher-topbar">
          <div>
            <h1>Teacher Dashboard</h1>
            <p>Manage students and track daily attendance.</p>
          </div>

          <div className="teacher-date">
            <CalendarDays size={18} />
            <span>Today's Overview</span>
          </div>
        </header>

        <section className="teacher-welcome">
          <h2>Welcome back, {teacher.name}!</h2>
          <p>
            Here's an overview of your class attendance.
          </p>
        </section>

        {error && (
          <p className="student-form-error" role="alert">
            {error}
          </p>
        )}

        <section className="teacher-stats">
          <div className="teacher-stat-card">
            <div className="teacher-stat-icon purple">
              <Users size={24} />
            </div>
            <p>Active Students</p>
            <h2>{loading ? "..." : stats?.totalStudents ?? "--"}</h2>
            <span>Students in your class</span>
          </div>

          <div className="teacher-stat-card">
            <div className="teacher-stat-icon green">
              <UserCheck size={24} />
            </div>
            <p>Present Today</p>
            <h2>{loading ? "..." : stats?.presentToday ?? "--"}</h2>
            <span>Students present</span>
          </div>

          <div className="teacher-stat-card">
            <div className="teacher-stat-icon red">
              <UserX size={24} />
            </div>
            <p>Absent Today</p>
            <h2>{loading ? "..." : stats?.absentToday ?? "--"}</h2>
            <span>Students absent</span>
          </div>
        </section>

        <section className="teacher-quick-actions">
          <div className="teacher-section-heading">
            <h2>Quick Actions</h2>
            <p>Access common tasks</p>
          </div>

          <div className="quick-action-grid">
            <div className="quick-action-card">
              <div className="quick-action-icon blue">
                <Users size={24} />
              </div>
              <h3>Manage Students</h3>
              <p>Add, edit, search, and deactivate student records.</p>
            </div>

            <div className="quick-action-card">
              <div className="quick-action-icon green">
                <ClipboardCheck size={24} />
              </div>
              <h3>Mark Attendance</h3>
              <p>Record and update daily student attendance.</p>
            </div>

            <div className="quick-action-card">
              <div className="quick-action-icon orange">
                <FileBarChart size={24} />
              </div>
              <h3>View Reports</h3>
              <p>Review attendance summaries for your class.</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default TeacherDashboard;