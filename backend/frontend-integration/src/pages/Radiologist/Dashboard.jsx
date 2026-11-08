// Replaces: src/pages/Radiologist/Dashboard.jsx
import { useState } from 'react';
import { Upload, Scan, Brain, FileText } from 'lucide-react';
import StatCard from '../../components/StatCard';
import ScanUpload from '../../components/ScanUpload';
import StudyBrowser from '../../components/StudyBrowser';
import useDashboardStats from '../../hooks/useDashboardStats';

function RadiologistDashboard() {
  const [version, setVersion] = useState(0);
  const { stats, error } = useDashboardStats(version);
  const v = (key) => (stats ? stats[key] : '—');
  const refresh = () => setVersion((x) => x + 1);

  const cards = [
    { title: 'MRI Scans', value: v('mriScans'), description: 'Uploaded scans', icon: Upload },
    { title: 'Classification', value: v('classifications'), description: 'Analysis records', icon: Scan },
    { title: 'Segmentation', value: v('segmentations'), description: 'Segmentation results', icon: Brain },
    { title: 'Reports', value: v('reports'), description: 'Generated reports', icon: FileText },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Radiologist Dashboard</h1>
        <p className="text-slate-500 mt-2">Brain MRI classification and segmentation workspace.</p>
        {error && <p className="text-sm text-red-600 mt-2">{error}</p>}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
        {cards.map((item) => (
          <StatCard key={item.title} {...item} />
        ))}
      </div>

      <ScanUpload onCreated={refresh} />
      <StudyBrowser role="radiologist" reloadKey={version} onChanged={refresh} />
    </div>
  );
}

export default RadiologistDashboard;
