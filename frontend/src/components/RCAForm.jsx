import { useState } from 'react';
import { apiClient } from '../api/client';

export default function RCAForm({ incidentId, onComplete }) {
  const [category, setCategory] = useState('UNKNOWN');
  const [description, setDescription] = useState('');
  const [action, setAction] = useState('');
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [suggesting, setSuggesting] = useState(false);

  const addAction = () => {
    if (action.trim()) {
      setActions([...actions, action.trim()]);
      setAction('');
    }
  };

  const submitRCA = async (e) => {
    e.preventDefault();
    if (!description || actions.length === 0) {
      alert("Description and at least one preventative action are required.");
      return;
    }
    
    setLoading(true);
    try {
      await apiClient.post(`/incidents/${incidentId}/rca`, {
        category,
        description,
        preventative_actions: actions
      });
      onComplete();
    } catch (e) {
      alert("Failed to submit RCA");
    } finally {
      setLoading(false);
    }
  };

  const getSuggestion = async () => {
    setSuggesting(true);
    try {
      const res = await apiClient.get(`/incidents/${incidentId}/rca-suggestion`);
      setCategory(res.data.category);
      setDescription(res.data.description);
      setActions(res.data.preventative_actions);
    } catch (e) {
      alert("Failed to get suggestion");
    } finally {
      setSuggesting(false);
    }
  };

  return (
    <form onSubmit={submitRCA} className="bg-gray-800 border border-gray-700 rounded-lg p-5 space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-200">Submit Root Cause Analysis</h3>
        <button
          type="button"
          onClick={getSuggestion}
          disabled={suggesting}
          className="text-sm bg-purple-600 hover:bg-purple-700 text-white px-3 py-1.5 rounded-md transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          {suggesting ? 'Analyzing...' : '✨ AI Suggestion'}
        </button>
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-1">Category</label>
        <select 
          value={category} 
          onChange={(e) => setCategory(e.target.value)}
          className="w-full bg-gray-900 border border-gray-700 rounded-md p-2 text-white focus:border-blue-500 focus:outline-none"
        >
          <option value="HARDWARE">Hardware</option>
          <option value="SOFTWARE">Software</option>
          <option value="NETWORK">Network</option>
          <option value="HUMAN_ERROR">Human Error</option>
          <option value="UNKNOWN">Unknown</option>
        </select>
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-1">Description</label>
        <textarea 
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows="3"
          className="w-full bg-gray-900 border border-gray-700 rounded-md p-2 text-white focus:border-blue-500 focus:outline-none"
          placeholder="Detailed explanation of the root cause..."
        />
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-1">Preventative Actions</label>
        <div className="flex gap-2 mb-2">
          <input 
            type="text"
            value={action}
            onChange={(e) => setAction(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAction())}
            className="flex-1 bg-gray-900 border border-gray-700 rounded-md p-2 text-white focus:border-blue-500 focus:outline-none"
            placeholder="Action item..."
          />
          <button 
            type="button" 
            onClick={addAction}
            className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-md transition-colors"
          >
            Add
          </button>
        </div>
        <ul className="space-y-1">
          {actions.map((act, i) => (
            <li key={i} className="flex justify-between items-center bg-gray-900 px-3 py-2 rounded border border-gray-800">
              <span className="text-sm">{act}</span>
              <button 
                type="button"
                onClick={() => setActions(actions.filter((_, idx) => idx !== i))}
                className="text-red-400 hover:text-red-300 px-2"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="pt-4 flex justify-end">
        <button 
          type="submit"
          disabled={loading}
          className="bg-green-600 hover:bg-green-500 text-white px-6 py-2 rounded-md transition-colors disabled:opacity-50"
        >
          {loading ? 'Submitting...' : 'Submit RCA & Enable Close'}
        </button>
      </div>
    </form>
  );
}
