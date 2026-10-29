
import { useEffect, useMemo, useState } from "react";
import {
  Search,
  FileBarChart,
  Users,
  ArrowUpDown,
  Download,
} from "lucide-react";
import { apiRequest } from "../services/api";
import "../styles/global.css";

function Reports() {
  const [sampleReports, setSampleReports] = useState([]);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const [sortDirection, setSortDirection] = useState("asc");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadReports() {
      setLoading(true);
      setError("");

      try {
        const data = await apiRequest("/reports/attendance");

        // Support either an array response or an object containing reports.
        const records = Array.isArray(data)
          ? data
          : data.reports ?? data.students ?? data.records;

        if (!Array.isArray(records)) {
          throw new Error(
            "Unexpected reports response. Check the backend response format."
          );
        }

        const normalized = records.map((student) => ({
          id: student.id ?? student.student_id,
          name: student.name,
          registerNumber:
            student.register_number ?? student.registerNumber,
          present: Number(student.present ?? student.present_count ?? 0),
          absent: Number(student.absent ?? student.absent_count ?? 0),
          percentage:
            student.percentage ??
            student.attendance_percentage ??
            null,
        }));

        if (!cancelled) {
          setSampleReports(normalized);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Unable to load attendance reports.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadReports();

    return () => {
      cancelled = true;
    };
  }, []);

  const reports = useMemo(() => {
    return sampleReports
      .map((student) => {
        const recorded = student.present + student.absent;

        // Calculate percentage from counts when the API does not supply it.
        const percentage =
          recorded > 0
            ? (student.present / recorded) * 100
            : null;

        return {
          ...student,
          recorded,
          percentage,
        };
      })
      .filter((student) => {
        const query = search.trim().toLowerCase();

        return (
          student.name.toLowerCase().includes(query) ||
          student.registerNumber.toLowerCase().includes(query)
        );
      })
      .sort((a, b) => {
        let comparison;

        if (sortBy === "percentage") {
          comparison =
            (a.percentage ?? -1) - (b.percentage ?? -1);
        } else if (sortBy === "recorded") {
          comparison = a.recorded - b.recorded;
        } else {
          comparison = a[sortBy].localeCompare(b[sortBy]);
        }

        return sortDirection === "asc" ? comparison : -comparison;
      });
  }, [sampleReports, search, sortBy, sortDirection]);

  const totalPresent = sampleReports.reduce(
    (sum, student) => sum + student.present,
    0
  );

  const totalAbsent = sampleReports.reduce(
    (sum, student) => sum + student.absent,
    0
  );

  const totalRecorded = totalPresent + totalAbsent;

  const classPercentage =
    totalRecorded > 0
      ? ((totalPresent / totalRecorded) * 100).toFixed(1)
      : "N/A";

  function handleSortChange(event) {
    setSortBy(event.target.value);
    setSortDirection("asc");
  }

  function toggleSortDirection() {
    setSortDirection((previous) =>
      previous === "asc" ? "desc" : "asc"
    );
  }

  function handleExport() {
    const headers = [
      "Register Number",
      "Student Name",
      "Present",
      "Absent",
      "Recorded",
      "Attendance Percentage",
    ];

    const rows = reports.map((student) => [
      student.registerNumber,
      student.name,
      student.present,
      student.absent,
      student.recorded,
      student.percentage === null
        ? "N/A"
        : `${student.percentage.toFixed(1)}%`,
    ]);

    const escapeCsv = (value) =>
      `"${String(value).replace(/"/g, '""')}"`;

    const csvContent = [headers, ...rows]
      .map((row) => row.map(escapeCsv).join(","))
      .join("\r\n");

    const blob = new Blob(["\uFEFF", csvContent], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "attendance-report.csv";
    link.click();

    URL.revokeObjectURL(url);
  }

  return (
    <div className="reports-page">
      <header className="reports-header">
        <div>
          <h1>Attendance Reports</h1>
          <p>
            Review attendance summaries and student performance.
          </p>
        </div>

        <button
          type="button"
          className="report-export-button"
          onClick={handleExport}
          disabled={loading || reports.length === 0}
        >
          <Download size={18} />
          Export CSV
        </button>
      </header>

      {error && (
        <p className="student-form-error" role="alert">
          {error}
        </p>
      )}

      <section className="report-summary">
        <div className="report-summary-card">
          <div className="report-summary-icon purple">
            <Users size={23} />
          </div>
          <p>Total Students</p>
          <h2>{loading ? "..." : sampleReports.length}</h2>
        </div>

        <div className="report-summary-card">
          <div className="report-summary-icon green">
            <FileBarChart size={23} />
          </div>
          <p>Present Records</p>
          <h2>{loading ? "..." : totalPresent}</h2>
        </div>

        <div className="report-summary-card">
          <div className="report-summary-icon red">
            <FileBarChart size={23} />
          </div>
          <p>Absent Records</p>
          <h2>{loading ? "..." : totalAbsent}</h2>
        </div>

        <div className="report-summary-card">
          <div className="report-summary-icon blue">
            <ArrowUpDown size={23} />
          </div>
          <p>Class Attendance</p>
          <h2>
            {loading
              ? "..."
              : classPercentage === "N/A"
                ? "N/A"
                : `${classPercentage}%`}
          </h2>
        </div>
      </section>

      <section className="reports-panel">
        <div className="reports-toolbar">
          <div>
            <h2>Student Attendance Summary</h2>
            <p>Attendance counts and percentages for each student.</p>
          </div>

          <div className="reports-filters">
            <label className="report-search">
              <Search size={18} />
              <input
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search students..."
                aria-label="Search by student name or register number"
              />
            </label>

            <label className="report-sort">
              <span>Sort by</span>
              <select value={sortBy} onChange={handleSortChange}>
                <option value="name">Student Name</option>
                <option value="registerNumber">Register Number</option>
                <option value="recorded">Recorded Days</option>
                <option value="percentage">Attendance %</option>
              </select>
            </label>

            <button
              type="button"
              className="report-sort-direction"
              onClick={toggleSortDirection}
              aria-label={`Sort ${
                sortDirection === "asc" ? "descending" : "ascending"
              }`}
              title={`Currently ${
                sortDirection === "asc" ? "ascending" : "descending"
              }`}
            >
              <ArrowUpDown size={18} />
              {sortDirection === "asc" ? "Ascending" : "Descending"}
            </button>
          </div>
        </div>

        <div className="reports-table-wrapper">
          <table className="reports-table">
            <thead>
              <tr>
                <th>Register No.</th>
                <th>Student Name</th>
                <th>Present</th>
                <th>Absent</th>
                <th>Recorded</th>
                <th>Attendance %</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" className="report-empty">
                    Loading reports...
                  </td>
                </tr>
              ) : reports.length > 0 ? (
                reports.map((student) => (
                  <tr key={student.id}>
                    <td>{student.registerNumber}</td>
                    <td>{student.name}</td>
                    <td className="report-present">{student.present}</td>
                    <td className="report-absent">{student.absent}</td>
                    <td>{student.recorded}</td>
                    <td>
                      {student.percentage === null ? (
                        <span className="report-na">N/A</span>
                      ) : (
                        <div className="report-percentage">
                          <span>
                            {student.percentage.toFixed(1)}%
                          </span>
                          <div
                            className="report-progress-track"
                            role="progressbar"
                            aria-label={`${student.name} attendance`}
                            aria-valuenow={student.percentage}
                            aria-valuemin={0}
                            aria-valuemax={100}
                          >
                            <div
                              className="report-progress-fill"
                              style={{
                                width: `${student.percentage}%`,
                              }}
                            />
                          </div>
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="report-empty">
                    {error
                      ? "Unable to display reports."
                      : "No matching students found."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="reports-footer">
          Showing {reports.length} of {sampleReports.length} students
        </div>
      </section>
    </div>
  );
}

export default Reports;
