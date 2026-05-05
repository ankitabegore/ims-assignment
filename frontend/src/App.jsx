import { useState } from 'react';
import LiveFeed from './components/LiveFeed';
import IncidentDetail from './components/IncidentDetail';

function App() {
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <header className="mb-8 border-b border-gray-700 pb-4">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
          IMS Dashboard
        </h1>
      </header>
      <div className="flex gap-6 h-[calc(100vh-8rem)]">
        <div className="w-1/3 bg-gray-800 rounded-lg p-4 flex flex-col border border-gray-700">
          <h2 className="text-xl font-semibold mb-4 text-gray-300">Live Feed</h2>
          <div className="flex-1 overflow-y-auto pr-2">
             <LiveFeed onSelect={setSelectedIncidentId} selectedId={selectedIncidentId} />
          </div>
        </div>
        <div className="w-2/3 bg-gray-800 rounded-lg p-6 overflow-y-auto border border-gray-700 shadow-xl">
          {selectedIncidentId ? (
            <IncidentDetail incidentId={selectedIncidentId} />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400 text-lg">
              Select an incident from the live feed to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
