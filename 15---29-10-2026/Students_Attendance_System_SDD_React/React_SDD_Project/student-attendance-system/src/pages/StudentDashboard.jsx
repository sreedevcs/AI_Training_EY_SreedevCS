
import { useEffect, useState } from "react";
import {
  CalendarCheck,
  CalendarX,
  Percent,
  GraduationCap,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../services/api";
import AttendanceCard from "../components/AttendanceCard";
import AttendanceTable from "../components/AttendanceTable";
import "../styles/global.css";

function StudentDashboard() {
  const { user } = useAuth();

  const [student, setStudent] = useState({
    name: user?.name || user?.username || "Student",
    registerNumber: "",
    className: "",
  });

  const [records, setRecords] = useState([]);
  const [summary, setSummary] = useState({
    presentCount: 0,
    absentCount: 0,
    recordedCount: 0,
    percentage: null,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadAttendance() {
      setLoading(true);
      setError("");

      try {
        const data = await apiRequest("/attendance/me");

        if (cancelled) return;

        const studentDetails = data.student || {};

        setStudent({
          name:
            studentDetails.name ||
            data.student_name ||
            user?.name ||
            user?.username ||
            "Student",
          registerNumber:
            studentDetails.register_number ||
            data.register_number ||
            "",
          className:
            studentDetails.class_name ||
            data.class_name ||
            "",
        });

        const history = Array.isArray(data.history) ? data.history : [];

        const normalizedRecords = history.map((record, index) => ({
          id: record.id ?? index + 1,
          date: record.attendance_date ?? record.date,
          status: record.status,
        }));

        setRecords(normalizedRecords);

        const presentCount =
          data.present_count ??
          normalizedRecords.filter((record) => record.status === "Present")
            .length;

        const absentCount =
          data.absent_count ??
          normalizedRecords.filter((record) => record.status === "Absent")
            .length;

        const recordedCount =
          data.recorded_count ?? presentCount + absentCount;

        const percentage =
          data.attendance_percentage ??
          (recordedCount > 0
            ? (presentCount / recordedCount) * 100
            : null);

        setSummary({
          presentCount,
          absentCount,
          recordedCount,
          percentage:
            percentage === null ? null : Number(percentage),
        });
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message || "Unable to load your attendance. Please try again."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadAttendance();

    return () => {
      cancelled = true;
    };
  }, [user]);

  const formattedPercentage =
    summary.percentage === null
      ? "N/A"
      : `${summary.percentage.toFixed(1)}%`;

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="brand">
          <GraduationCap size={30} />
          <span>AttendEase</span>
        </div>

        <div className="student-profile">
          <div className="profile-avatar">
            {student.name.charAt(0).toUpperCase()}
          </div>

          <div>
            <strong>{student.name}</strong>
            <p>{student.registerNumber || "Student Account"}</p>
          </div>
        </div>
      </header>

      <main className="dashboard-content">
        <section className="welcome-section">
          <div>
            <h1>My Attendance</h1>
            <p>
              Welcome back, {student.name}. Here's your attendance overview.
            </p>
          </div>

          {student.className && (
            <span className="class-label">{student.className}</span>
          )}
        </section>

        {loading ? (
          <p>Loading your attendance...</p>
        ) : error ? (
          <div role="alert">
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>
              Try Again
            </button>
          </div>
        ) : (
          <>
            <section className="attendance-summary">
              <AttendanceCard
                title="Present"
                value={summary.presentCount}
                subtitle="Days attended"
                icon={<CalendarCheck size={21} />}
                color="green"
              />

              <AttendanceCard
                title="Absent"
                value={summary.absentCount}
                subtitle="Days missed"
                icon={<CalendarX size={21} />}
                color="red"
              />

              <AttendanceCard
                title="Attendance"
                value={formattedPercentage}
                subtitle={`${summary.recordedCount} recorded days`}
                icon={<Percent size={21} />}
                color="blue"
              />
            </section>

            <section className="history-section">
              <div className="section-heading">
                <div>
                  <h2>Attendance History</h2>
                  <p>Your recorded attendance by date</p>
                </div>
              </div>

              <AttendanceTable records={records} />
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default StudentDashboard;
