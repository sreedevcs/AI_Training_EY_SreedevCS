
import { useEffect, useState } from "react";
import {
  CalendarDays,
  ClipboardCheck,
  CheckCircle2,
  AlertCircle,
  Save,
} from "lucide-react";
import { apiRequest } from "../services/api";
import "../styles/global.css";

// Returns today's date in local YYYY-MM-DD format.
function getLocalDate() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function MarkAttendance() {
  const today = getLocalDate();

  const [selectedDate, setSelectedDate] = useState(today);
  const [students, setStudents] = useState([]);
  const [statuses, setStatuses] = useState({});
  const [savedRegisters, setSavedRegisters] = useState({});
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadAttendance() {
      setLoading(true);
      setError("");
      setSuccess("");

      try {
        const data = await apiRequest(
          `/attendance/?attendance_date=${selectedDate}`
        );

        if (cancelled) return;

        if (!Array.isArray(data?.records)) {
          throw new Error("Unexpected response while loading attendance.");
        }

        const nextStudents = data.records.map((record) => ({
          id: record.student_id ?? record.id,
          name: record.name,
          registerNumber:
            record.register_number ?? record.registerNumber,
          status: record.status ?? null,
        }));

        const nextStatuses = {};

        nextStudents.forEach((student) => {
          if (student.status) {
            nextStatuses[student.id] = student.status;
          }
        });

        setStudents(nextStudents);
        setStatuses(nextStatuses);

        const allMarked =
          nextStudents.length > 0 &&
          nextStudents.every((student) => student.status);

        if (allMarked) {
          setSavedRegisters((previous) => ({
            ...previous,
            [selectedDate]: true,
          }));
        } else {
          setSavedRegisters((previous) => ({
            ...previous,
            [selectedDate]: false,
          }));
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Unable to load attendance.");
          setStudents([]);
          setStatuses({});
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadAttendance();

    return () => {
      cancelled = true;
    };
  }, [selectedDate]);

  const presentCount = students.filter(
    (student) => statuses[student.id] === "Present"
  ).length;

  const absentCount = students.filter(
    (student) => statuses[student.id] === "Absent"
  ).length;

  const markedCount = presentCount + absentCount;

  function handleDateChange(event) {
    setSelectedDate(event.target.value);
    setError("");
    setSuccess("");
  }

  function handleStatusChange(studentId, status) {
    setStatuses((previous) => ({
      ...previous,
      [studentId]: status,
    }));

    setSavedRegisters((previous) => ({
      ...previous,
      [selectedDate]: false,
    }));

    setError("");
    setSuccess("");
  }

  async function handleSave() {
    if (!selectedDate) {
      setError("Please select an attendance date.");
      return;
    }

    if (selectedDate > today) {
      setError("Future attendance dates are not allowed.");
      return;
    }

    const incomplete = students.filter(
      (student) => !statuses[student.id]
    );

    if (incomplete.length > 0) {
      setError(
        `Please mark attendance for all students. ${incomplete.length} student(s) remain unmarked.`
      );
      return;
    }

    setSaving(true);
    setError("");
    setSuccess("");

    try {
      await apiRequest("/attendance/bulk", {
        method: "POST",
        body: JSON.stringify({
          attendance_date: selectedDate,
          records: students.map((student) => ({
            student_id: student.id,
            status: statuses[student.id],
          })),
        }),
      });

      setSavedRegisters((previous) => ({
        ...previous,
        [selectedDate]: true,
      }));

      setSuccess("Attendance saved successfully.");
    } catch (err) {
      setError(err.message || "Unable to save attendance.");
    } finally {
      setSaving(false);
    }
  }

  const isSaved = Boolean(savedRegisters[selectedDate]);

  return (
    <div className="mark-attendance-page">
      <header className="attendance-page-header">
        <div>
          <h1>Mark Attendance</h1>
          <p>Record and manage daily student attendance.</p>
        </div>

        <div className="attendance-date-picker">
          <CalendarDays size={20} />

          <input
            type="date"
            aria-label="Attendance date"
            value={selectedDate}
            max={today}
            onChange={handleDateChange}
          />
        </div>
      </header>

      <section className="attendance-overview">
        <div className="attendance-overview-card">
          <span>Total Students</span>
          <strong>{students.length}</strong>
        </div>

        <div className="attendance-overview-card">
          <span>Present</span>
          <strong className="overview-present">{presentCount}</strong>
        </div>

        <div className="attendance-overview-card">
          <span>Absent</span>
          <strong className="overview-absent">{absentCount}</strong>
        </div>

        <div className="attendance-overview-card">
          <span>Unmarked</span>
          <strong>{students.length - markedCount}</strong>
        </div>
      </section>

      <section className="attendance-register">
        <div className="attendance-register-header">
          <div>
            <h2>
              <ClipboardCheck size={22} />
              Daily Register
            </h2>
            <p>
              Select Present or Absent for every active student.
            </p>
          </div>

          {isSaved && (
            <span className="register-saved-label">
              <CheckCircle2 size={16} />
              Saved
            </span>
          )}
        </div>

        <div className="register-table-wrapper">
          <table className="register-table">
            <thead>
              <tr>
                <th>Register No.</th>
                <th>Student Name</th>
                <th>Attendance Status</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="3">Loading attendance...</td>
                </tr>
              ) : students.length > 0 ? (
                students.map((student) => (
                  <tr key={student.id}>
                    <td>{student.registerNumber}</td>
                    <td>{student.name}</td>
                    <td>
                      <div
                        className="attendance-status-controls"
                        role="group"
                        aria-label={`Attendance for ${student.name}`}
                      >
                        <button
                          type="button"
                          className={`attendance-choice present-choice ${
                            statuses[student.id] === "Present"
                              ? "selected"
                              : ""
                          }`}
                          aria-pressed={
                            statuses[student.id] === "Present"
                          }
                          disabled={saving}
                          onClick={() =>
                            handleStatusChange(student.id, "Present")
                          }
                        >
                          Present
                        </button>

                        <button
                          type="button"
                          className={`attendance-choice absent-choice ${
                            statuses[student.id] === "Absent"
                              ? "selected"
                              : ""
                          }`}
                          aria-pressed={
                            statuses[student.id] === "Absent"
                          }
                          disabled={saving}
                          onClick={() =>
                            handleStatusChange(student.id, "Absent")
                          }
                        >
                          Absent
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="3">
                    {error
                      ? "Could not load students. Check the error below."
                      : "No active students found."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {error && (
          <div className="attendance-message error-message" role="alert">
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        {success && (
          <div
            className="attendance-message success-message"
            role="status"
          >
            <CheckCircle2 size={18} />
            {success}
          </div>
        )}

        <div className="attendance-register-footer">
          <p>
            {markedCount} of {students.length} students marked
          </p>

          <button
            type="button"
            className="save-attendance-button"
            onClick={handleSave}
            disabled={loading || saving || students.length === 0}
          >
            <Save size={18} />
            {saving ? "Saving..." : "Save Attendance"}
          </button>
        </div>
      </section>
    </div>
  );
}

export default MarkAttendance;
