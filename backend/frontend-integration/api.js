// Copy to: src/api.js  (frontend)
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch { /* ignore */ }
    throw new Error(detail);
  }
  return res.json();
}

export async function analyzeScan(file) {
  const form = new FormData();
  form.append('file', file);
  return handle(await fetch(`${BASE}/api/analyze`, { method: 'POST', body: form }));
}

export async function sendChat(message, caseId, history) {
  return handle(
    await fetch(`${BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, caseId, history }),
    })
  );
}
