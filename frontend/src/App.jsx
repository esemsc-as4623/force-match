import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import { parseCharactersFromTTL, parseConnectionsFromTTL } from './utils/dataParser';

const App = () => {
  const [characters, setCharacters] = useState([]);
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);

        // Load character data
        const dataTtlResponse = await fetch('/data/data.ttl');
        const dataTtlText = await dataTtlResponse.text();
        const parsedCharacters = await parseCharactersFromTTL(dataTtlText);

        // Load connections data
        const connectionsTtlResponse = await fetch('/data/connections.ttl');
        const connectionsTtlText = await connectionsTtlResponse.text();
        const parsedConnections = await parseConnectionsFromTTL(connectionsTtlText);

        setCharacters(parsedCharacters);
        setConnections(parsedConnections);
        setLoading(false);
      } catch (err) {
        console.error('Error loading data:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="w-full h-screen space-bg flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-lightsaber-blue mb-4"></div>
          <p className="text-white text-xl" style={{ textShadow: '0 0 10px rgba(74, 158, 255, 0.8)' }}>
            Loading the Force...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-screen space-bg flex items-center justify-center">
        <div className="text-center bg-space-accent bg-opacity-90 p-8 rounded-lg max-w-md">
          <h2 className="text-2xl font-bold text-red-500 mb-4">Error</h2>
          <p className="text-white mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-lightsaber-blue text-white rounded-lg hover:bg-opacity-80 transition-all duration-200"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (characters.length === 0) {
    return (
      <div className="w-full h-screen space-bg flex items-center justify-center">
        <div className="text-center bg-space-accent bg-opacity-90 p-8 rounded-lg max-w-md">
          <h2 className="text-2xl font-bold text-white mb-4">No Characters Found</h2>
          <p className="text-gray-300">
            Please ensure the data.ttl file is available in the public/data directory.
          </p>
        </div>
      </div>
    );
  }

  return <Dashboard characters={characters} connections={connections} />;
};

export default App;
