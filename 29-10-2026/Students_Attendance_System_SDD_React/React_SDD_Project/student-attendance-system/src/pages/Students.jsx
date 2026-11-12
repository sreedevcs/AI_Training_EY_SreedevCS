
import { useEffect, useState } from "react";
import {
  Search,
  Plus,
  Pencil,
  UserX,
  Users,
  X,
  Trash2,
} from "lucide-react";
import { apiRequest } from "../services/api";
import "../styles/global.css";

const emptyForm = {
  name: "",
  registerNumber: "",
  className: "CSE - A",
};

function Students() {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [createdCredentials, setCreatedCredentials] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  async function loadStudents() {
    setLoading(true);
    setError("");

    try {
      const data = await apiRequest("/students/");
      if (!Array.isArray(data?.students)) {
        throw new Error("Unexpected response while loading students.");
      }
      setStudents(data.students);
    } catch (err) {
      setError(err.message || "Unable to load students.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadStudents();
  }, []);

  const filteredStudents = students.filter((student) => {
    const query = search.trim().toLowerCase();

    return (
      student.name.toLowerCase().includes(query) ||
      student.register_number.toLowerCase().includes(query)
    );
  });

  const activeCount = students.filter(
    (student) => student.is_active
  ).length;

  function openAddForm() {
    setEditingId(null);
    setForm(emptyForm);
    setError("");
    setShowForm(true);
  }

  function openEditForm(student) {
    setEditingId(student.id);
    setForm({
      name: student.name,
      registerNumber: student.register_number,
      className: student.class_name,
    });
    setError("");
    setShowForm(true);
  }

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    const name = form.name.trim();
    const registerNumber = form.registerNumber.trim();
    const className = form.className.trim();

    if (name.length < 2 || name.length > 100) {
      setError("Name must contain 2–100 characters.");
      return;
    }

    if (
      registerNumber.length < 1 ||
      registerNumber.length > 30
    ) {
      setError("Register number must contain 1–30 characters.");
      return;
    }

    if (!className || className.length > 50) {
      setError("Please enter a valid class or section.");
      return;
    }

    const duplicate = students.some(
      (student) =>
        student.register_number.toLowerCase() ===
          registerNumber.toLowerCase() &&
        student.id !== editingId
    );

    if (duplicate) {
      setError("This register number already exists.");
      return;
    }

    const payload = {
      name,
      register_number: registerNumber,
      class_name: className,
    };

    setSubmitting(true);

    try {
      if (editingId !== null) {
        await apiRequest(`/students/${editingId}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      } else {
        const result = await apiRequest("/students/", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        setCreatedCredentials({
          studentName: name,
          username: result.credentials.username,
          password: result.credentials.password,
        });
      }

      setShowForm(false);
      setForm(emptyForm);
      setEditingId(null);
      await loadStudents();
    } catch (err) {
      setError(err.message || "Unable to save student.");
    } finally {
      setSubmitting(false);
    }
  }

  async function toggleActive(student) {
    const action = student.is_active ? "deactivate" : "reactivate";

    if (
      !window.confirm(
        `Are you sure you want to ${action} ${student.name}?`
      )
    ) {
      return;
    }

    setError("");

    try {
      await apiRequest(`/students/${student.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          is_active: !student.is_active,
        }),
      });

      await loadStudents();
    } catch (err) {
      setError(err.message || "Unable to update student status.");
    }
  }

  async function deleteStudent(student) {
    if (
      !window.confirm(
        `Permanently delete ${student.name}? They cannot be restored. Their login will be deactivated, and attendance history will be preserved.`
      )
    ) {
      return;
    }

    setError("");
    setDeletingId(student.id);

    try {
      await apiRequest(`/students/${student.id}`, {
        method: "DELETE",
      });
      await loadStudents();
    } catch (err) {
      setError(err.message || "Unable to delete student.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="students-page">
      <header className="students-header">
        <div>
          <h1>Student Management</h1>
          <p>Manage student records and class information.</p>
        </div>

        <button className="primary-button" onClick={openAddForm}>
          <Plus size={18} />
          Add Student
        </button>
      </header>

      <section className="student-count-card">
        <div className="student-count-icon">
          <Users size={24} />
        </div>

        <div>
          <p>Active Students</p>
          <h2>{activeCount}</h2>
        </div>
      </section>

      <section className="students-panel">
        <div className="students-toolbar">
          <div>
            <h2>All Students</h2>
            <p>{filteredStudents.length} records found</p>
          </div>

          <div className="student-search">
            <Search size={19} />
            <input
              type="search"
              placeholder="Search name or register number"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              aria-label="Search students"
            />
          </div>
        </div>

        {error && !showForm && (
          <p className="student-form-error" role="alert">
            {error}
          </p>
        )}

        <div className="students-table-wrapper">
          <table className="students-table">
            <thead>
              <tr>
                <th>Register No.</th>
                <th>Student Name</th>
                <th>Class / Section</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="5" className="empty-students">
                    Loading students...
                  </td>
                </tr>
              ) : filteredStudents.length > 0 ? (
                filteredStudents.map((student) => (
                  <tr key={student.id}>
                    <td>{student.register_number}</td>
                    <td>
                      <span
                        className={
                          student.is_deleted ? "student-name-deleted" : ""
                        }
                      >
                        {student.name}
                      </span>
                    </td>
                    <td>{student.class_name}</td>
                    <td>
                      <span
                        className={`student-status ${
                          student.is_deleted
                            ? "deleted"
                            : student.is_active
                              ? "active"
                              : "inactive"
                        }`}
                      >
                        {student.is_deleted
                          ? "Deleted"
                          : student.is_active
                            ? "Active"
                            : "Inactive"}
                      </span>
                    </td>
                    <td>
                      <div className="student-actions">
                        {!student.is_deleted && (
                          <>
                            <button
                              className="icon-button edit-button"
                              title="Edit student"
                              aria-label={`Edit ${student.name}`}
                              onClick={() => openEditForm(student)}
                            >
                              <Pencil size={17} />
                            </button>

                            <button
                              className="icon-button deactivate-button"
                              title={
                                student.is_active
                                  ? "Deactivate student"
                                  : "Reactivate student"
                              }
                              aria-label={`${
                                student.is_active
                                  ? "Deactivate"
                                  : "Reactivate"
                              } ${student.name}`}
                              onClick={() => toggleActive(student)}
                            >
                              <UserX size={17} />
                            </button>

                            <button
                              className="icon-button deactivate-button"
                              title="Permanently delete student"
                              aria-label={`Delete ${student.name}`}
                              disabled={deletingId === student.id}
                              onClick={() => deleteStudent(student)}
                            >
                              <Trash2 size={17} />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="empty-students">
                    {error
                      ? "Students could not be loaded."
                      : "No students match your search."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {showForm && (
        <div className="student-modal-backdrop">
          <section
            className="student-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="student-form-title"
          >
            <div className="student-modal-header">
              <div>
                <h2 id="student-form-title">
                  {editingId !== null ? "Edit Student" : "Add Student"}
                </h2>
                <p>Enter the student's details below.</p>
              </div>

              <button
                className="icon-button"
                onClick={() => setShowForm(false)}
                aria-label="Close form"
                disabled={submitting}
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="student-form-field">
                <label htmlFor="student-name">Full Name</label>
                <input
                  id="student-name"
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  minLength={2}
                  maxLength={100}
                  required
                />
              </div>

              <div className="student-form-field">
                <label htmlFor="register-number">Register Number</label>
                <input
                  id="register-number"
                  name="registerNumber"
                  value={form.registerNumber}
                  onChange={handleChange}
                  maxLength={30}
                  required
                />
              </div>

              <div className="student-form-field">
                <label htmlFor="class-name">Class / Section</label>
                <input
                  id="class-name"
                  name="className"
                  value={form.className}
                  onChange={handleChange}
                  maxLength={50}
                  required
                />
              </div>

              {error && (
                <p className="student-form-error" role="alert">
                  {error}
                </p>
              )}

              <div className="student-form-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowForm(false)}
                  disabled={submitting}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={submitting}
                >
                  {submitting
                    ? "Saving..."
                    : editingId !== null
                      ? "Save Changes"
                      : "Add Student"}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}

      {createdCredentials && (
        <div className="student-modal-backdrop">
          <section
            className="student-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="student-credentials-title"
          >
            <div className="student-modal-header">
              <div>
                <h2 id="student-credentials-title">
                  Student login created
                </h2>
                <p>
                  Share these credentials with {createdCredentials.studentName}.
                </p>
              </div>
            </div>

            <div className="student-form-field">
              <label>Username</label>
              <input value={createdCredentials.username} readOnly />
            </div>

            <div className="student-form-field">
              <label>Temporary password</label>
              <input value={createdCredentials.password} readOnly />
            </div>

            <p>
              Save these credentials now. The password is generated from the
              username and should be changed before using this system with
              sensitive data.
            </p>

            <div className="student-form-actions">
              <button
                type="button"
                className="primary-button"
                onClick={() => setCreatedCredentials(null)}
              >
                Done
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

export default Students;
