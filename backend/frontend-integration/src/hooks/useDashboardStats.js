// New file: src/hooks/useDashboardStats.js
import { useEffect, useState } from 'react';
import { getStats, errorMessage } from '../api';

/** Loads the numbers for the StatCards. Pass a changing `reloadKey` to refresh. */
export default function useDashboardStats(reloadKey = 0) {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    getStats()
      .then((d) => !cancelled && setStats(d.stats))
      .catch((e) => !cancelled && setError(errorMessage(e)));
    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  return { stats, error };
}
