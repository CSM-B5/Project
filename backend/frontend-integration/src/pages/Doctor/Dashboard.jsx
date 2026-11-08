// Replaces: src/pages/Doctor/Dashboard.jsx
import { useState } from 'react';
import { Users, Scan, FileText, Clock } from 'lucide-react';
import StatCard from '../../components/StatCard';
import StudyBrowser from '../../components/StudyBrowser';
import useDashboardStats from '../../hooks/useDashboardStats';

function DoctorDashboard() {
  const [version, setVersion] = useState(0);
  const { stats, error } = useDashboardStats(version);
  const v = (key) => (stats ? stats[key] : '—');

  const cards = [
    { title: 'My Patients', value: v('myPatients'), description: 'Assigned patients', icon: Users },
    { title: 'MRI Studies', value: v('mriStudies'), description: 'Available scan records', icon: Scan },
    { title: 'Medical Reports', value: v('medicalReports'), description: 'Approved reports', icon: FileText },
    { title: 'Pending Reviews', value: v('pendingReviews'), description: 'Studies awaiting review', icon: Clock },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Doctor Dashboard</h1>
        <p className="text-slate-500 mt-2">Review patient MRI studies and AI-assisted findings.</p>
        {error && <p className="text-sm text-red-600 mt-2">{error}</p>}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
        {cards.map((item) => (
          <StatCard key={item.title} {...item} />
        ))}
      </div>

      <StudyBrowser role="doctor" reloadKey={version} onChanged={() => setVersion((x) => x + 1)} />
    </div>
  );
}

export default DoctorDashboard;
