// New file: src/components/StudyBrowser.jsx
// List of studies for the logged-in role + detail view. Doctors can approve reports.
import { useEffect, useState } from 'react';
import { getStudies, getStudy, approveReport, errorMessage } from '../api';
import StudyResult from './StudyResult';

export default function StudyBrowser({ role, reloadKey = 0, onChanged = () => {} }) {
  const [studies, setStudies] = useState(null);
  const [error, setError] = useState('');
  const [detail, setDetail] = useState(null);
  const [draft, setDraft] = useState('');
  const [busy, setBusy] = useState(false);
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let cancelled = false;
    getStudies()
      .then((rows) => !cancelled && setStudies(rows))
      .catch((e) => !cancelled && setError(errorMessage(e)));
    return () => {
      cancelled = true;
    };
  }, [reloadKey, version]);

  const open = async (id) => {
    setError('');
    try {
      const s = await getStudy(id);
      setDetail(s);
      setDraft(s.report.summary || '');
    } catch (e) {
      setError(errorMessage(e));
    }
  };

  const approve = async () => {
    setBusy(true);
    setError('');
    try {
      const s = await approveReport(detail.id, draft.trim() || undefined);
      setDetail(s);
      setVersion((v) => v + 1);
      onChanged();
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border p-6 space-y-5">
      <h2 className="font-semibold text-lg">{role === 'patient' ? 'My Scans' : 'MRI Studies'}</h2>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {studies === null && !error && <p className="text-sm text-slate-500">Loading…</p>}
      {studies && studies.length === 0 && <p className="text-sm text-slate-500">No studies yet.</p>}

      {studies && studies.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b">
                <th className="py-2 pr-4">Case</th>
                <th className="py-2 pr-4">Patient</th>
                <th className="py-2 pr-4">Date</th>
                <th className="py-2 pr-4">Prediction</th>
                <th className="py-2 pr-4">Report</th>
                <th className="py-2" />
              </tr>
            </thead>
            <tbody>
              {studies.map((s) => (
                <tr key={s.id} className="border-b last:border-0">
                  <td className="py-2 pr-4 font-mono">{s.caseId}</td>
                  <td className="py-2 pr-4">{s.patientName}</td>
                  <td className="py-2 pr-4">{new Date(s.createdAt + 'Z').toLocaleDateString()}</td>
                  <td className="py-2 pr-4">{s.predictedClass || '—'}</td>
                  <td className="py-2 pr-4">{s.reportStatus}</td>
                  <td className="py-2">
                    <button onClick={() => open(s.id)} className="text-teal-700 hover:underline">
                      {role === 'doctor' && s.reportStatus === 'Pending' ? 'Review' : 'View'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {detail && (
        <div className="border-t pt-5 space-y-4">
          <StudyResult study={detail} />

          {role === 'doctor' && detail.report.status === 'Pending' && (
            <div className="space-y-3">
              <label className="block text-sm font-medium">Edit the report if needed, then approve</label>
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                rows={5}
                maxLength={5000}
                className="w-full border rounded-lg p-3 text-sm"
              />
              <button
                onClick={approve}
                disabled={busy}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white px-4 py-2 rounded-lg font-semibold"
              >
                {busy ? 'Approving…' : 'Approve report'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
