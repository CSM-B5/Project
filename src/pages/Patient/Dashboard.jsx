import React from 'react';
import { Scan, FileText, UserRound } from 'lucide-react';
import StatCard from '../../components/StatCard';

function PatientDashboard() {
  const stats = [
    {
      title: 'My MRI Scans',
      value: '—',
      description: 'Your scan records',
      icon: Scan
    },
    {
      title: 'Medical Reports',
      value: '—',
      description: 'Doctor-approved reports',
      icon: FileText
    },
    {
      title: 'Profile Status',
      value: '—',
      description: 'Account information',
      icon: UserRound
    }
  ];

  return (
    <div className="space-y-8">

      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Patient Dashboard
        </h1>
        <p className="text-slate-500 mt-2">
          View your MRI scan records and approved medical reports.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
        {stats.map((item) => (
          <StatCard key={item.title} {...item} />
        ))}
      </div>

      <div className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold text-lg">My Medical Records</h2>
        <p className="text-slate-500 text-sm mt-2">
          Your authorized scan history and doctor-approved
          diagnostic reports will appear here.
        </p>
      </div>

    </div>
  );
}

export default PatientDashboard;