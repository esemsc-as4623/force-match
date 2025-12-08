import React from 'react';

const SettingsPanel = ({ isOpen, onClose, groupBy, onGroupByChange }) => {
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  const handleGroupingChange = (value) => {
    onGroupByChange(value);
  };

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={onClose}
          role="button"
          aria-label="Close settings"
          tabIndex={0}
          onKeyDown={handleKeyDown}
        />
      )}

      {/* Settings Panel */}
      <div
        className={`fixed left-0 top-0 h-full w-80 bg-space-accent bg-opacity-95 backdrop-blur-md shadow-2xl transform transition-transform duration-300 z-50 overflow-y-auto ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{
          borderRight: '2px solid rgba(74, 158, 255, 0.3)',
        }}
      >
        <div className="p-6">
          {/* Close button */}
          <button
            onClick={onClose}
            onKeyDown={(e) => e.key === 'Enter' && onClose()}
            className="absolute top-4 right-4 text-white hover:text-lightsaber-blue transition-colors duration-200 text-2xl"
            aria-label="Close settings"
            tabIndex={0}
          >
            ✕
          </button>

          {/* Settings header */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-white mb-2" style={{ textShadow: '0 0 10px rgba(74, 158, 255, 0.8)' }}>
              Settings
            </h2>
            <div className="h-1 w-20 bg-gradient-to-r from-lightsaber-blue to-transparent rounded-full" />
          </div>

          {/* Grouping options */}
          <div className="space-y-4">
            <h3 className="text-lightsaber-blue font-semibold mb-4 text-sm uppercase tracking-wide">
              Group Characters By
            </h3>

            <div className="space-y-3">
              <label className="flex items-center space-x-3 cursor-pointer group">
                <input
                  type="radio"
                  name="groupBy"
                  value="none"
                  checked={groupBy === 'none'}
                  onChange={() => handleGroupingChange('none')}
                  className="w-5 h-5 text-lightsaber-blue focus:ring-lightsaber-blue focus:ring-2"
                />
                <span className="text-white group-hover:text-lightsaber-blue transition-colors duration-200">
                  No Grouping
                </span>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer group">
                <input
                  type="radio"
                  name="groupBy"
                  value="species"
                  checked={groupBy === 'species'}
                  onChange={() => handleGroupingChange('species')}
                  className="w-5 h-5 text-lightsaber-blue focus:ring-lightsaber-blue focus:ring-2"
                />
                <span className="text-white group-hover:text-lightsaber-blue transition-colors duration-200">
                  Species
                </span>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer group">
                <input
                  type="radio"
                  name="groupBy"
                  value="gender"
                  checked={groupBy === 'gender'}
                  onChange={() => handleGroupingChange('gender')}
                  className="w-5 h-5 text-lightsaber-blue focus:ring-lightsaber-blue focus:ring-2"
                />
                <span className="text-white group-hover:text-lightsaber-blue transition-colors duration-200">
                  Gender
                </span>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer group">
                <input
                  type="radio"
                  name="groupBy"
                  value="films"
                  checked={groupBy === 'films'}
                  onChange={() => handleGroupingChange('films')}
                  className="w-5 h-5 text-lightsaber-blue focus:ring-lightsaber-blue focus:ring-2"
                />
                <span className="text-white group-hover:text-lightsaber-blue transition-colors duration-200">
                  Film Appearances
                </span>
              </label>
            </div>

            <div className="mt-8 p-4 bg-space-dark bg-opacity-50 rounded-lg">
              <p className="text-gray-400 text-sm">
                Changing the grouping will reorganize the character nodes in the visualization.
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default SettingsPanel;
