import React from 'react';

const Sidebar = ({ character, isOpen, onClose }) => {
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  if (!character) return null;

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={onClose}
          role="button"
          aria-label="Close sidebar"
          tabIndex={0}
          onKeyDown={handleKeyDown}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed right-0 top-0 h-full w-full md:w-96 bg-space-accent bg-opacity-95 backdrop-blur-md shadow-2xl transform transition-transform duration-300 z-50 overflow-y-auto ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        style={{
          borderLeft: '2px solid rgba(74, 158, 255, 0.3)',
        }}
      >
        <div className="p-6">
          {/* Close button */}
          <button
            onClick={onClose}
            onKeyDown={(e) => e.key === 'Enter' && onClose()}
            className="absolute top-4 right-4 text-white hover:text-lightsaber-blue transition-colors duration-200 text-2xl"
            aria-label="Close sidebar"
            tabIndex={0}
          >
            ✕
          </button>

          {/* Character header */}
          <div className="mb-6">
            <h2 className="text-3xl font-bold text-white mb-2" style={{ textShadow: '0 0 10px rgba(74, 158, 255, 0.8)' }}>
              {character.name}
            </h2>
            <div className="h-1 w-20 bg-gradient-to-r from-lightsaber-blue to-transparent rounded-full" />
          </div>

          {/* Character details */}
          <div className="space-y-4 text-gray-200">
            {character.species && (
              <div className="bg-space-dark bg-opacity-50 p-4 rounded-lg">
                <h3 className="text-lightsaber-blue font-semibold mb-1 text-sm uppercase tracking-wide">Species</h3>
                <p className="text-white text-lg">{character.species}</p>
              </div>
            )}

            {character.gender && (
              <div className="bg-space-dark bg-opacity-50 p-4 rounded-lg">
                <h3 className="text-lightsaber-green font-semibold mb-1 text-sm uppercase tracking-wide">Gender</h3>
                <p className="text-white text-lg">{character.gender}</p>
              </div>
            )}

            {character.height && (
              <div className="bg-space-dark bg-opacity-50 p-4 rounded-lg">
                <h3 className="text-lightsaber-purple font-semibold mb-1 text-sm uppercase tracking-wide">Height</h3>
                <p className="text-white text-lg">{character.height} cm</p>
              </div>
            )}

            {character.mass && (
              <div className="bg-space-dark bg-opacity-50 p-4 rounded-lg">
                <h3 className="text-lightsaber-yellow font-semibold mb-1 text-sm uppercase tracking-wide">Mass</h3>
                <p className="text-white text-lg">{character.mass} kg</p>
              </div>
            )}

            {character.hairColor && (
              <div className="bg-space-dark bg-opacity-50 p-4 rounded-lg">
                <h3 className="text-lightsaber-orange font-semibold mb-1 text-sm uppercase tracking-wide">Hair Color</h3>
                <p className="text-white text-lg">{character.hairColor}</p>
              </div>
            )}

            {character.skinColor && (
              <div className="bg-space-dark bg-opacity-50 p-4 rounded-lg">
                <h3 className="text-lightsaber-red font-semibold mb-1 text-sm uppercase tracking-wide">Skin Color</h3>
                <p className="text-white text-lg">{character.skinColor}</p>
              </div>
            )}

            {character.eyeColor && (
              <div className="bg-space-dark bg-opacity-50 p-4 rounded-lg">
                <h3 className="text-lightsaber-blue font-semibold mb-1 text-sm uppercase tracking-wide">Eye Color</h3>
                <p className="text-white text-lg">{character.eyeColor}</p>
              </div>
            )}

            {character.birthYear && (
              <div className="bg-space-dark bg-opacity-50 p-4 rounded-lg">
                <h3 className="text-lightsaber-green font-semibold mb-1 text-sm uppercase tracking-wide">Birth Year</h3>
                <p className="text-white text-lg">{character.birthYear}</p>
              </div>
            )}

            {character.films && character.films.length > 0 && (
              <div className="bg-space-dark bg-opacity-50 p-4 rounded-lg">
                <h3 className="text-lightsaber-purple font-semibold mb-2 text-sm uppercase tracking-wide">Films</h3>
                <p className="text-white text-sm">{character.films.length} film(s)</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
