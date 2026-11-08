// New file: src/components/UserManagement.jsx   (admin: list / create / activate users)
import { useEffect, useState } from 'react';
import { adminListUsers, adminCreateUser, adminUpdateUser, errorMessage } from '../api';

const EMPTY = { name: '', email: '', password: '', role: 'doctor', assignedDoctorId: '' };

export default function UserManagement({ onChanged = () => {} }) {
  const [users, setUsers] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let cancelled = false;
    adminListUsers()
      .then((u) => !cancelled && setUsers(u))
      .catch((e) => !cancelled && setError(errorMessage(e)));
    return () => {
      cancelled = true;
    };
  }, [version]);

  const doctors = (users || []).filter((u) => u.role === 'doctor' && u.isActive);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const create = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      const body = { name: form.name, email: form.email, password: form.password, role: form.role };
      if (form.role === 'patient' && form.assignedDoctorId) body.assignedDoctorId = Number(form.assignedDoctorId);
      await adminCreateUser(body);
      setForm(EMPTY);
      setVersion((v) => v + 1);
      onChanged();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const toggleActive = async (u) => {
    setError('');
    try {
      await adminUpdateUser(u.id, { isActive: !u.isActive });
      setVersion((v) => v + 1);
      onChanged();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const assignDoctor = async (u, doctorId) => {
    setError('');
    try {
      await adminUpdateUser(u.id, { assignedDoctorId: doctorId ? Number(doctorId) : null });
      setVersion((v) => v + 1);
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  return (
    <div className="bg-white rounded-xl border p-6 space-y-6">
      <h2 className="font-semibold text-lg">User Management</h2>

      <form onSubmit={create} className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <input required placeholder="Full name" value={form.name} onChange={set('name')} className="border rounded-lg p-2.5 text-sm" />
        <input required type="email" placeholder="Email" value={form.email} onChange={set('email')} className="border rounded-lg p-2.5 text-sm" />
        <input required type="password" minLength={8} placeholder="Password (min 8)" value={form.password} onChange={set('password')} className="border rounded-lg p-2.5 text-sm" autoComplete="new-password" />
        <select value={form.role} onChange={set('role')} className="border rounded-lg p-2.5 text-sm bg-white">
          <option value="doctor">Doctor</option>
          <option value="radiologist">Radiologist</option>
          <option value="patient">Patient</option>
          <option value="admin">Admin</option>
        </select>
        {form.role === 'patient' ? (
          <select value={form.assignedDoctorId} onChange={set('assignedDoctorId')} className="border rounded-lg p-2.5 text-sm bg-white">
            <option value="">No doctor assigned</option>
            {doctors.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
        ) : (
          <div />
        )}
        <button type="submit" disabled={busy} className="bg-slate-700 hover:bg-slate-800 disabled:opacity-60 text-white rounded-lg font-semibold p-2.5 text-sm">
          {busy ? 'Creating…' : 'Create user'}
        </button>
      </form>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {users === null && !error && <p className="text-sm text-slate-500">Loading…</p>}

      {users && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b">
                <th className="py-2 pr-4">Name</th>
                <th className="py-2 pr-4">Email</th>
                <th className="py-2 pr-4">Role</th>
                <th className="py-2 pr-4">Doctor (patients)</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2" />
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b last:border-0">
                  <td className="py-2 pr-4">{u.name}</td>
                  <td className="py-2 pr-4">{u.email}</td>
                  <td className="py-2 pr-4 capitalize">{u.role}</td>
                  <td className="py-2 pr-4">
                    {u.role === 'patient' ? (
                      <select
                        value={u.assignedDoctorId ?? ''}
                        onChange={(e) => assignDoctor(u, e.target.value)}
                        className="border rounded p-1 bg-white"
                      >
                        <option value="">—</option>
                        {doctors.map((d) => (
                          <option key={d.id} value={d.id}>{d.name}</option>
                        ))}
                      </select>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td className="py-2 pr-4">{u.isActive ? 'Active' : 'Inactive'}</td>
                  <td className="py-2">
                    <button onClick={() => toggleActive(u)} className="text-slate-700 hover:underline">
                      {u.isActive ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
