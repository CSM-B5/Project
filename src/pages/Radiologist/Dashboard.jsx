import React from 'react';
import { Upload, Scan, Brain, FileText } from 'lucide-react';
import StatCard from '../../components/StatCard';

function RadiologistDashboard() {
  const stats = [
    {
      title: 'MRI Scans',
      value: '—',
      description: 'Uploaded scans',
      icon: Upload
    },
    {
      title: 'Classification',
      value: '—',
      description: 'Analysis records',
      icon: Scan
    },
    {
      title: 'Segmentation',
      value: '—',
      description: 'Segmentation results',
      icon: Brain
    },
    {
      title: 'Reports',
      value: '—',
      description: 'Generated reports',
      icon: FileText
    }
  ];

  return (
    <div className="space-y-8">

      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Radiologist Dashboard
        </h1>
        <p className="text-slate-500 mt-2">
          Brain MRI classification and segmentation workspace.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
        {stats.map((item) => (
          <StatCard key={item.title} {...item} />
        ))}
      </div>

      <div className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold text-lg">
          Medical Imaging Analysis
        </h2>

        <p className="text-slate-500 text-sm mt-2">
          Upload brain MRI images, review CNN/VGG classification
          predictions and inspect U-Net++ segmentation results.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">

          <div className="bg-teal-50 rounded-lg p-5">
            <Scan className="text-teal-600 mb-3" size={28} />
            <h3 className="font-semibold">Image Classification</h3>
            <p className="text-sm text-slate-600 mt-2">
              Glioma, Meningioma, Pituitary and No Tumor.
            </p>
          </div>

          <div className="bg-blue-50 rounded-lg p-5">
            <Brain className="text-blue-600 mb-3" size={28} />
            <h3 className="font-semibold">Tumor Segmentation</h3>
            <p className="text-sm text-slate-600 mt-2">
              U-Net++ based tumor boundary visualization.
            </p>
          </div>

        </div>
      </div>

    </div>
  );
}

export default RadiologistDashboard;