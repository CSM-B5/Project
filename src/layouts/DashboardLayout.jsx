import React from 'react';
import { useNavigate, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

import {
  Brain,
  LayoutDashboard,
  Users,
  Scan,
  FileText,
  Settings,
  LogOut,
  UserRound,
  Activity
} from 'lucide-react';

const menus = {
  admin: [
    { name: 'Dashboard', icon: LayoutDashboard, active: true },
    { name: 'User Management', icon: Users },
    { name: 'Doctors & Patients', icon: UserRound },
    { name: 'System Activity', icon: Activity },
    { name: 'Settings', icon: Settings }
  ],

  doctor: [
    { name: 'Dashboard', icon: LayoutDashboard, active: true },
    { name: 'Patients', icon: Users },
    { name: 'MRI Review', icon: Scan },
    { name: 'Reports', icon: FileText }
  ],

  radiologist: [
    { name: 'Dashboard', icon: LayoutDashboard, active: true },
    { name: 'MRI Analysis', icon: Scan },
    { name: 'Segmentation Lab', icon: Brain },
    { name: 'Reports', icon: FileText }
  ],

  patient: [
    { name: 'Dashboard', icon: LayoutDashboard, active: true },
    { name: 'My Scans', icon: Scan },
    { name: 'Medical Reports', icon: FileText }
  ]
};

function DashboardLayout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const roleNames = {
    admin: 'Administrator',
    doctor: 'Doctor',
    radiologist: 'Radiologist',
    patient: 'Patient'
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex min-h-screen bg-slate-100">

      {/* Sidebar */}
      <aside className="w-64 bg-slate-950 text-white flex flex-col shrink-0">

        <div className="p-6 flex items-center gap-3 border-b border-slate-800">
          <Brain className="text-teal-400 w-8 h-8" />

          <div>
            <h1 className="font-bold text-xl">NeuroAI</h1>
            <p className="text-xs text-slate-400">
              Medical Imaging Platform
            </p>
          </div>
        </div>

        <div className="px-5 py-5">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            {roleNames[user.role]} Workspace
          </p>
        </div>

        <nav className="flex-1 px-3 space-y-2">

          {menus[user.role].map((item) => {
            const Icon = item.icon;

            return item.active ? (
              <NavLink
                key={item.name}
                to={`/${user.role}`}
                end
                className="flex items-center gap-3 p-3 rounded-lg bg-teal-600 text-white"
              >
                <Icon size={19} />
                {item.name}
              </NavLink>
            ) : (
              <div
                key={item.name}
                title="This section will be implemented next"
                className="flex items-center gap-3 p-3 rounded-lg text-slate-400 opacity-60 cursor-not-allowed"
              >
                <Icon size={19} />
                {item.name}
              </div>
            );
          })}

        </nav>

        <div className="p-4 border-t border-slate-800">

          <p className="text-sm text-white truncate">
            {user.email}
          </p>

          <p className="text-xs text-slate-400 mb-4">
            {roleNames[user.role]}
          </p>

          <button
            onClick={handleLogout}
            className="flex items-center gap-3 text-red-400 hover:text-red-300"
          >
            <LogOut size={18} />
            Logout
          </button>

        </div>

      </aside>

      {/* Main workspace */}
      <main className="flex-1 min-w-0">

        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 md:px-8">

          <h2 className="font-semibold text-slate-800">
            {roleNames[user.role]} Dashboard
          </h2>

          <div className="flex items-center gap-2 text-slate-600">
            <UserRound size={20} />
            <span className="text-sm">
              {user.email}
            </span>
          </div>

        </header>

        <div className="p-6 md:p-8">
          {children}
        </div>

      </main>

    </div>
  );
}

export default DashboardLayout;