// Replaces: src/pages/Patient/Dashboard.jsx
import { Scan, FileText, UserRound } from 'lucide-react';
import StatCard from '../../components/StatCard';
import StudyBrowser from '../../components/StudyBrowser';
import useDashboardStats from '../../hooks/useDashboardStats';

function PatientDashboard() {
  const { stats, error } = useDashboardStats();
  const v = (key) => (stats ? stats[key] : '—');

  const cards = [
    { title: 'My MRI Scans', value: v('myScans'), description: 'Your scan records', icon: Scan },
    { title: 'Medical Reports', value: v('medicalReports'), description: 'Doctor-approved reports', icon: FileText },
    { title: 'Profile Status', value: v('profileStatus'), description: 'Account information', icon: UserRound },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Patient Dashboard</h1>
        <p className="text-slate-500 mt-2">View your MRI scan records and approved medical reports.</p>
        {error && <p className="text-sm text-red-600 mt-2">{error}</p>}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
        {cards.map((item) => (
          <StatCard key={item.title} {...item} />
        ))}
      </div>

      <StudyBrowser role="patient" />
    </div>
  );
}

export default PatientDashboard;
