import React from 'react';
import { Users, Scan, FileText, Clock } from 'lucide-react';
import StatCard from '../../components/StatCard';

function DoctorDashboard() {
  const stats = [
    {
      title: 'My Patients',
      value: '—',
      description: 'Assigned patients',
      icon: Users
    },
    {
      title: 'MRI Studies',
      value: '—',
      description: 'Available scan records',
      icon: Scan
    },
    {
      title: 'Medical Reports',
      value: '—',
      description: 'Approved reports',
      icon: FileText
    },
    {
      title: 'Pending Reviews',
      value: '—',
      description: 'Studies awaiting review',
      icon: Clock
    }
  ];

  return (
    <div className="space-y-8">

      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Doctor Dashboard
        </h1>
        <p className="text-slate-500 mt-2">
          Review patient MRI studies and AI-assisted findings.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
        {stats.map((item) => (
          <StatCard key={item.title} {...item} />
        ))}
      </div>

      <div className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold text-lg">Clinical Workspace</h2>
        <p className="text-slate-500 text-sm mt-2">
          Patient records, MRI review and diagnostic reports
          will be managed here.
        </p>
      </div>

    </div>
  );
}

export default DoctorDashboard;