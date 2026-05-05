import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import RCAForm from './RCAForm';

export default function IncidentDetail({ incidentId }) {
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDetail = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get(`/incidents/${incidentId}`);
      setIncident(res.data);
      setError(null);
    } catch (e) {
      setError("Failed to load incident");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [incidentId]);

  const updateStatus = async (newStatus) => {
    try {
      await apiClient.patch(`/incidents/${incidentId}/status?status=${newStatus}`);
      fetchDetail();
    } catch (e) {
      alert(e.response?.data?.detail || "Failed to update status");
    }
  };

  if (loading) return <div className="text-gray-400">Loading details...</div>;
  if (error) return <div className="text-red-400">{error}</div>;
  if (!incident) return null;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start border-b border-gray-700 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-100">{incident.component_id}</h2>
          <p className="text-gray-400">{incident.title}</p>
        </div>
        <div className="flex gap-2">
          {['OPEN', 'INVESTIGATING', 'RESOLVED', 'CLOSED'].map((s) => (
            <button
              key={s}
              disabled={incident.status === s}
              onClick={() => updateStatus(s)}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                incident.status === s 
                ? 'bg-blue-600 text-white cursor-default' 
                : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-700/50 p-4 rounded-lg">
          <div className="text-sm text-gray-400 mb-1">Priority</div>
          <div className="text-lg font-semibold">{incident.priority}</div>
        </div>
        <div className="bg-gray-700/50 p-4 rounded-lg">
          <div className="text-sm text-gray-400 mb-1">Created</div>
          <div className="text-lg font-semibold">{new Date(incident.created_at).toLocaleString()}</div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Signals ({incident.signals.length})</h3>
        <div className="bg-gray-900 rounded-lg p-3 max-h-40 overflow-y-auto text-sm font-mono text-gray-400">
          {incident.signals.join(', ')}
        </div>
      </div>

      {incident.status === 'RESOLVED' && !incident.rca && (
        <RCAForm incidentId={incident.id} onComplete={fetchDetail} />
      )}

      {incident.rca && (
        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-5">
          <h3 className="text-lg font-semibold mb-4 text-blue-300">Root Cause Analysis</h3>
          <div className="space-y-3">
            <div>
              <span className="text-gray-400 text-sm block">Category</span>
              <span className="font-medium">{incident.rca.category}</span>
            </div>
            <div>
              <span className="text-gray-400 text-sm block">Description</span>
              <p className="text-gray-300">{incident.rca.description}</p>
            </div>
            <div>
              <span className="text-gray-400 text-sm block">Preventative Actions</span>
              <ul className="list-disc list-inside text-gray-300">
                {incident.rca.preventative_actions.map((act, i) => <li key={i}>{act}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
