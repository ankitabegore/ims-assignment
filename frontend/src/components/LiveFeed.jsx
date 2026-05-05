import { useState, useEffect } from 'react';
import { apiClient, setupSSE } from '../api/client';

export default function LiveFeed({ onSelect, selectedId }) {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchIncidents = async () => {
    try {
      const res = await apiClient.get('/incidents');
      setIncidents(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
    const eventSource = setupSSE((data) => {
      if (data.type === 'new_incident' || data.type === 'update_incident') {
        fetchIncidents(); // Refresh list. Optimization: could just update the specific item
      }
    });
    return () => eventSource.close();
  }, []);

  if (loading) return <div className="text-gray-400">Loading incidents...</div>;

  const getStatusColor = (status) => {
    switch (status) {
      case 'OPEN': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'INVESTIGATING': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 'RESOLVED': return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      case 'CLOSED': return 'text-green-400 bg-green-400/10 border-green-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  return (
    <div className="flex flex-col gap-3">
      {incidents.map((incident) => (
        <button
          key={incident.id}
          onClick={() => onSelect(incident.id)}
          className={`text-left p-3 rounded-md border transition-all duration-200 ${
            selectedId === incident.id
              ? 'border-blue-500 bg-gray-700 shadow-[0_0_15px_rgba(59,130,246,0.15)]'
              : 'border-gray-700 hover:border-gray-500 bg-gray-800 hover:bg-gray-750'
          }`}
        >
          <div className="flex justify-between items-start mb-2">
            <span className="font-semibold text-gray-200">{incident.component_id}</span>
            <span className={`text-xs px-2 py-1 rounded-full border ${getStatusColor(incident.status)}`}>
              {incident.status}
            </span>
          </div>
          <div className="text-sm text-gray-400 truncate">{incident.title}</div>
          <div className="text-xs text-gray-500 mt-2">
            {new Date(incident.updated_at).toLocaleString()}
          </div>
        </button>
      ))}
      {incidents.length === 0 && <div className="text-gray-500">No active incidents</div>}
    </div>
  );
}
