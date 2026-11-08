import React from 'react';

function StatCard({ title, value, description, icon: Icon }) {
  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">

      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <h2 className="text-3xl font-bold text-slate-900 mt-3">
            {value}
          </h2>
        </div>

        <div className="bg-teal-50 p-3 rounded-xl">
          <Icon size={23} className="text-teal-600" />
        </div>
      </div>

      <p className="text-xs text-slate-400 mt-4">
        {description}
      </p>

    </div>
  );
}

export default StatCard;