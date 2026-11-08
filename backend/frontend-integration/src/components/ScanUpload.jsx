// New file: src/components/ScanUpload.jsx   (radiologist: upload an MRI and analyze it)
import { useEffect, useState } from 'react';
import { createStudy, getPatients, errorMessage } from '../api';
import StudyResult from './StudyResult';

export default function ScanUpload({ onCreated = () => {} }) {
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState('');
  const [file, setFile] = useState(null);
  const [maskFile, setMaskFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [formKey, setFormKey] = useState(0); // resets the file inputs

  useEffect(() => {
    let cancelled = false;
    getPatients()
      .then((p) => !cancelled && setPatients(p))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setBusy(true);
    setError('');
    setResult(null);
    try {
      const form = new FormData();
      form.append('file', file);
      if (patientId) form.append('patientId', patientId);
      if (maskFile) form.append('groundTruthMask', maskFile);
      const study = await createStudy(form);
      setResult(study);
      setFile(null);
      setMaskFile(null);
      setFormKey((k) => k + 1);
      onCreated();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border p-6 space-y-6">
      <h2 className="font-semibold text-lg">Analyze a brain MRI</h2>

      <form key={formKey} onSubmit={submit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">MRI image (.png, .jpg, .dcm)</label>
          <input
            type="file"
            accept=".png,.jpg,.jpeg,.dcm"
            required
            onChange={(e) => setFile(e.target.files[0] || null)}
            className="w-full text-sm border rounded-lg p-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Patient (optional)</label>
          <select
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            className="w-full border rounded-lg p-2.5 bg-white text-sm"
          >
            <option value="">— Not linked to a patient —</option>
            {patients.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.email})
              </option>
            ))}
          </select>
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium mb-2">Ground-truth mask (optional, to compute Dice / IoU)</label>
          <input
            type="file"
            accept=".png,.jpg,.jpeg"
            onChange={(e) => setMaskFile(e.target.files[0] || null)}
            className="w-full text-sm border rounded-lg p-2"
          />
        </div>

        <div className="md:col-span-2">
          <button
            type="submit"
            disabled={busy || !file}
            className="bg-teal-600 hover:bg-teal-700 disabled:opacity-60 text-white px-5 py-2.5 rounded-lg font-semibold"
          >
            {busy ? 'Analyzing…' : 'Analyze scan'}
          </button>
        </div>
      </form>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {result && (
        <div className="border-t pt-5">
          <StudyResult study={result} />
        </div>
      )}
    </div>
  );
}
