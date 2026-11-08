// Replaces: src/pages/Admin/Dashboard.jsx
import { useState } from 'react';
import { Users, UserCheck, Scan, Activity } from 'lucide-react';
import StatCard from '../../components/StatCard';
import UserManagement from '../../components/UserManagement';
import useDashboardStats from '../../hooks/useDashboardStats';

function AdminDashboard() {
  const [version, setVersion] = useState(0);
  const { stats, error } = useDashboardStats(version);
  const v = (key) => (stats ? stats[key] : '—');

  const cards = [
    { title: 'Registered Doctors', value: v('registeredDoctors'), description: 'Doctor accounts', icon: UserCheck },
    { title: 'Registered Patients', value: v('registeredPatients'), description: 'Patient accounts', icon: Users },
    { title: 'MRI Studies', value: v('mriStudies'), description: 'Total scan records', icon: Scan },
    { title: 'System Activity', value: v('systemActivity'), description: 'Activity records', icon: Activity },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Admin Dashboard</h1>
        <p className="text-slate-500 mt-2">Manage users and monitor the NeuroAI platform.</p>
        {error && <p className="text-sm text-red-600 mt-2">{error}</p>}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
        {cards.map((item) => (
          <StatCard key={item.title} {...item} />
        ))}
      </div>

      <UserManagement onChanged={() => setVersion((x) => x + 1)} />
    </div>
  );
}

export default AdminDashboard;
