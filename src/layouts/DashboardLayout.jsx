
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

// Individual medical color themes
const roleThemes = {
  admin: {
    sidebar: 'bg-slate-700',
    active: 'bg-slate-500',
    logo: 'text-slate-200',
    page: 'bg-slate-50',
    accent: 'text-slate-600',
    label: 'text-slate-300',
    border: 'border-slate-600',
    hover: 'hover:bg-slate-600'
  },

  doctor: {
    sidebar: 'bg-blue-900',
    active: 'bg-blue-500',
    logo: 'text-blue-200',
    page: 'bg-blue-50',
    accent: 'text-blue-700',
    label: 'text-blue-200',
    border: 'border-blue-800',
    hover: 'hover:bg-blue-800'
  },

  radiologist: {
    sidebar: 'bg-teal-900',
    active: 'bg-teal-600',
    logo: 'text-teal-200',
    page: 'bg-teal-50',
    accent: 'text-teal-700',
    label: 'text-teal-200',
    border: 'border-teal-800',
    hover: 'hover:bg-teal-800'
  },

  patient: {
    sidebar: 'bg-purple-900',
    active: 'bg-purple-600',
    logo: 'text-purple-200',
    page: 'bg-purple-50',
    accent: 'text-purple-700',
    label: 'text-purple-200',
    border: 'border-purple-800',
    hover: 'hover:bg-purple-800'
  }
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

  const theme = roleThemes[user.role];
  console.log("ROLE:", user.role);
console.log("THEME:", roleThemes[user.role]);
  const roleMenu = menus[user.role] || [];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className={`flex min-h-screen ${theme.page}`}>

      {/* Sidebar */}
      <aside className={`w-64 ${theme.sidebar} text-white flex flex-col shrink-0`}>

        {/* Logo */}
        <div className={`p-6 flex items-center gap-3 border-b ${theme.border}`}>
          <Brain className={`${theme.logo} w-8 h-8`} />

          <div>
            <h1 className="font-bold text-xl">NeuroAI</h1>
            <p className="text-xs text-white/60">
              Medical Imaging Platform
            </p>
          </div>
        </div>

        {/* Workspace name */}
        <div className="px-5 py-5">
          <p className={`text-xs uppercase tracking-wider ${theme.label}`}>
            {roleNames[user.role]} Workspace
          </p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 space-y-2">

          {roleMenu.map((item) => {
            const Icon = item.icon;

            return item.active ? (
              <NavLink
                key={item.name}
                to={`/${user.role}`}
                end
                className={`flex items-center gap-3 p-3 rounded-lg ${theme.active} text-white shadow-sm`}
              >
                <Icon size={19} />
                {item.name}
              </NavLink>
            ) : (
              <div
                key={item.name}
                title="This section will be implemented next"
                className={`flex items-center gap-3 p-3 rounded-lg text-white/60 opacity-70 cursor-not-allowed ${theme.hover}`}
              >
                <Icon size={19} />
                {item.name}
              </div>
            );
          })}

        </nav>

        {/* User information and logout */}
        <div className={`p-4 border-t ${theme.border}`}>

          <p className="text-sm text-white truncate">
            {user.email}
          </p>

          <p className="text-xs text-white/60 mb-4">
            {roleNames[user.role]}
          </p>

          <button
            onClick={handleLogout}
            className="flex items-center gap-3 text-red-300 hover:text-red-200 transition-colors"
          >
            <LogOut size={18} />
            Logout
          </button>

        </div>

      </aside>

      {/* Main workspace */}
      <main className="flex-1 min-w-0">

        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 md:px-8">

          <h2 className={`font-semibold ${theme.accent}`}>
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
