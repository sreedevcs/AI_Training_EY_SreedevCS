
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/Login";
import StudentDashboard from "./pages/StudentDashboard";
import TeacherDashboard from "./pages/TeacherDashboard";
import Students from "./pages/Students";
import MarkAttendance from "./pages/MarkAttendance";
import Reports from "./pages/Reports";

import StudentLayout from "./layouts/StudentLayout";
import TeacherLayout from "./layouts/TeacherLayout";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Default route */}
          <Route path="/" element={<Navigate to="/login" replace />} />

          {/* Public route */}
          <Route path="/login" element={<Login />} />

          {/* Student routes */}
          <Route element={<ProtectedRoute allowedRole="student" />}>
            <Route element={<StudentLayout />}>
              <Route
                path="/student"
                element={<StudentDashboard />}
              />
            </Route>
          </Route>

          {/* Teacher routes */}
          <Route element={<ProtectedRoute allowedRole="teacher" />}>
            <Route element={<TeacherLayout />}>
              <Route
                path="/teacher"
                element={<TeacherDashboard />}
              />
              <Route
                path="/teacher/students"
                element={<Students />}
              />
              <Route
                path="/teacher/attendance"
                element={<MarkAttendance />}
              />
              <Route
                path="/teacher/reports"
                element={<Reports />}
              />
            </Route>
          </Route>

          {/* Unknown routes */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
