import React from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from 'react-router-dom';

import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './routes/ProtectedRoute';
import DashboardLayout from './layouts/DashboardLayout';

import Login from './pages/Auth/Login';

import AdminDashboard from './pages/Admin/Dashboard';
import DoctorDashboard from './pages/Doctor/Dashboard';
import RadiologistDashboard from './pages/Radiologist/Dashboard';
import PatientDashboard from './pages/Patient/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>

        <Routes>

          <Route
            path="/"
            element={<Navigate to="/login" replace />}
          />

          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRole="admin">
                <DashboardLayout>
                  <AdminDashboard />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/doctor"
            element={
              <ProtectedRoute allowedRole="doctor">
                <DashboardLayout>
                  <DoctorDashboard />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/radiologist"
            element={
              <ProtectedRoute allowedRole="radiologist">
                <DashboardLayout>
                  <RadiologistDashboard />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/patient"
            element={
              <ProtectedRoute allowedRole="patient">
                <DashboardLayout>
                  <PatientDashboard />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="*"
            element={<Navigate to="/" replace />}
          />

        </Routes>

      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;