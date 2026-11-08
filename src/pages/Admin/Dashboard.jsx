import React from 'react';
import { Users, UserCheck, Scan, Activity } from 'lucide-react';
import StatCard from '../../components/StatCard';

function AdminDashboard() {
  const stats = [
    {
      title: 'Registered Doctors',
      value: '—',
      description: 'Doctor accounts',
      icon: UserCheck
    },
    {
      title: 'Registered Patients',
      value: '—',
      description: 'Patient accounts',
      icon: Users
    },
    {
      title: 'MRI Studies',
      value: '—',
      description: 'Total scan records',
      icon: Scan
    },
    {
      title: 'System Activity',
      value: '—',
      description: 'Activity records',
      icon: Activity
    }
  ];

  return (
    <div className="space-y-8">

      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Admin Dashboard
        </h1>
        <p className="text-slate-500 mt-2">
          Manage users and monitor the NeuroAI platform.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
        {stats.map((item) => (
          <StatCard key={item.title} {...item} />
        ))}
      </div>

      <div className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold text-lg">System Overview</h2>
        <p className="text-slate-500 text-sm mt-2">
          User management, system monitoring and application
          administration will be available in this workspace.
        </p>
      </div>

    </div>
  );
}

export default AdminDashboard;