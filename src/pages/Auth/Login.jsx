import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Brain, Lock, Mail } from 'lucide-react';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('doctor');

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    login(email, role);
    navigate(`/${role}`);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">

      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">

        <div className="text-center mb-8">
          <Brain className="mx-auto text-teal-600 w-12 h-12 mb-3" />

          <h1 className="text-3xl font-bold text-slate-900">
            NeuroAI
          </h1>

          <p className="text-slate-500 mt-2">
            Deep Learning Based Medical Imaging
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-5">

          <div>
            <label className="block text-sm font-medium mb-2">
              Email Address
            </label>

            <div className="flex items-center border rounded-lg px-3">
              <Mail className="w-4 h-4 text-slate-400" />

              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter email"
                autoComplete="email"
                className="w-full p-3 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Password
            </label>

            <div className="flex items-center border rounded-lg px-3">
              <Lock className="w-4 h-4 text-slate-400" />

              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                autoComplete="current-password"
                className="w-full p-3 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Login As
            </label>

            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full border rounded-lg p-3 bg-white"
            >
              <option value="admin">Admin</option>
              <option value="doctor">Doctor</option>
              <option value="radiologist">Radiologist</option>
              <option value="patient">Patient</option>
            </select>
          </div>

          <button
            type="submit"
            className="w-full bg-teal-600 hover:bg-teal-700 text-white p-3 rounded-lg font-semibold transition-colors"
          >
            Sign In
          </button>

        </form>

        <p className="text-center text-xs text-slate-400 mt-6">
          NeuroAI Medical Imaging Platform
        </p>

      </div>
    </div>
  );
}

export default Login;