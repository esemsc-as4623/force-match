import React, { useState, useEffect, useMemo } from 'react';
import CharacterNode from './CharacterNode';
import Connection from './Connection';
import Sidebar from './Sidebar';
import SettingsPanel from './SettingsPanel';
import { getColorForSpecies } from '../utils/dataParser';

const Dashboard = ({ characters, connections }) => {
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [hoveredCharacterId, setHoveredCharacterId] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [groupBy, setGroupBy] = useState('none');
  const [dimensions, setDimensions] = useState({ width: window.innerWidth, height: window.innerHeight });

  useEffect(() => {
    const handleResize = () => {
      setDimensions({ width: window.innerWidth, height: window.innerHeight });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Get color for a group
  const getColorForGroup = (groupKey, groupIndex, totalGroups) => {
    const colors = [
      '#4A9EFF', // Blue
      '#7FFF00', // Green
      '#FF3B3B', // Red
      '#B270FF', // Purple
      '#FFE66D', // Yellow
      '#FF8C42', // Orange
      '#00D9FF', // Cyan
      '#FF69B4', // Pink
      '#32CD32', // Lime
      '#FF1493', // Deep Pink
    ];
    return colors[groupIndex % colors.length];
  };

  const { positions, groupInfo, characterGroups } = useMemo(() => {
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    const radius = Math.min(dimensions.width, dimensions.height) * 0.35;

    if (groupBy === 'none') {
      // Simple circular layout
      const angleStep = (2 * Math.PI) / characters.length;
      const positions = characters.reduce((acc, char, index) => {
        const angle = index * angleStep - Math.PI / 2;
        acc[char.id] = {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
        };
        return acc;
      }, {});
      const characterGroups = characters.reduce((acc, char) => {
        acc[char.id] = { groupKey: 'default', groupIndex: 0 };
        return acc;
      }, {});
      return { positions, groupInfo: null, characterGroups };
    } else {
      // Grouped layout - nodes in same group are consecutive around the circle
      const groups = characters.reduce((acc, char) => {
        let key = 'Unknown';
        if (groupBy === 'species' && char.species) {
          key = char.species;
        } else if (groupBy === 'gender' && char.gender) {
          key = char.gender;
        } else if (groupBy === 'films' && char.films && char.films.length > 0) {
          key = `${char.films.length} films`;
        }
        if (!acc[key]) acc[key] = [];
        acc[key].push(char);
        return acc;
      }, {});

      const groupKeys = Object.keys(groups).sort();
      const totalCharacters = characters.length;
      const gapAngle = 0.05; // Small gap between groups
      const totalGapAngle = gapAngle * groupKeys.length;
      const usableAngle = (2 * Math.PI) - totalGapAngle;
      
      const positions = {};
      const groupInfoArray = [];
      const characterGroups = {};
      let currentAngle = -Math.PI / 2;

      groupKeys.forEach((groupKey, groupIndex) => {
        const groupMembers = groups[groupKey];
        const groupSize = groupMembers.length;
        const groupAngleSpan = (groupSize / totalCharacters) * usableAngle;
        const angleStep = groupAngleSpan / groupSize;
        
        const startAngle = currentAngle;

        groupMembers.forEach((char, index) => {
          const angle = currentAngle + (index + 0.5) * angleStep;
          positions[char.id] = {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle),
          };
          characterGroups[char.id] = { groupKey, groupIndex };
        });

        const endAngle = currentAngle + groupAngleSpan;
        
        groupInfoArray.push({
          name: groupKey,
          startAngle,
          endAngle,
          centerX,
          centerY,
          radius,
        });

        currentAngle += groupAngleSpan + gapAngle;
      });

      return { positions, groupInfo: groupInfoArray, characterGroups };
    }
  }, [characters, dimensions, groupBy]);

  const handleNodeClick = (character) => {
    setSelectedCharacter(character);
    setIsSidebarOpen(true);
  };

  const handleSidebarClose = () => {
    setIsSidebarOpen(false);
  };

  const handleSettingsToggle = () => {
    setIsSettingsOpen(!isSettingsOpen);
  };

  const handleGroupByChange = (value) => {
    setGroupBy(value);
  };

  const connectedCharacters = useMemo(() => {
    if (!hoveredCharacterId) return new Set();
    const connected = new Set();
    connections.forEach(conn => {
      if (conn.source === hoveredCharacterId) {
        connected.add(conn.target);
      }
      if (conn.target === hoveredCharacterId) {
        connected.add(conn.source);
      }
    });
    return connected;
  }, [hoveredCharacterId, connections]);

  const centerX = dimensions.width / 2;
  const centerY = dimensions.height / 2;

  return (
    <div className="relative w-full h-screen space-bg overflow-hidden">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-10 p-4 md:p-6 flex justify-between items-center">
        <h1
          className="text-2xl md:text-4xl font-bold text-white"
          style={{ textShadow: '0 0 20px rgba(74, 158, 255, 0.8)' }}
        >
          Force Match
        </h1>
        <button
          onClick={handleSettingsToggle}
          onKeyDown={(e) => e.key === 'Enter' && handleSettingsToggle()}
          className="px-4 py-2 bg-lightsaber-blue text-white rounded-lg hover:bg-opacity-80 transition-all duration-200 shadow-lg"
          style={{ boxShadow: '0 0 15px rgba(74, 158, 255, 0.6)' }}
          aria-label="Open settings"
          tabIndex={0}
        >
          ⚙️ Settings
        </button>
      </div>

      {/* Character count */}
      <div className="absolute bottom-4 left-4 z-10 text-gray-400 text-sm">
        {characters.length} characters • {connections.length} connections
      </div>

      {/* Group brackets and labels */}
      {groupInfo && (
        <svg
          className="absolute inset-0 pointer-events-none"
          style={{ width: '100%', height: '100%' }}
        >
          {groupInfo.map((group, index) => {
            const { name, startAngle, endAngle, centerX, centerY, radius } = group;
            const bracketRadius = radius + 50;
            
            // Create arc path for bracket
            const startX = centerX + bracketRadius * Math.cos(startAngle);
            const startY = centerY + bracketRadius * Math.sin(startAngle);
            const endX = centerX + bracketRadius * Math.cos(endAngle);
            const endY = centerY + bracketRadius * Math.sin(endAngle);
            
            const largeArcFlag = (endAngle - startAngle) > Math.PI ? 1 : 0;
            const arcPath = `M ${startX} ${startY} A ${bracketRadius} ${bracketRadius} 0 ${largeArcFlag} 1 ${endX} ${endY}`;
            
            // Label position at midpoint of arc - positioned radially outside
            const midAngle = (startAngle + endAngle) / 2;
            const midAngleDeg = midAngle * 180 / Math.PI;
            const labelRadius = bracketRadius + 15;
            const labelX = centerX + labelRadius * Math.cos(midAngle);
            const labelY = centerY + labelRadius * Math.sin(midAngle);
            
            // Make text read left-to-right like character names
            let labelRotation = midAngleDeg;
            let anchor = 'start';
            
            if (midAngleDeg > 90 && midAngleDeg < 270) {
              labelRotation = midAngleDeg + 180;
              anchor = 'end';
            }
            
            return (
              <g key={`group-${index}`}>
                <path
                  d={arcPath}
                  stroke="#9CA3AF"
                  strokeWidth="1.5"
                  fill="none"
                  opacity="0.4"
                  strokeDasharray="4 2"
                />
                <text
                  x={labelX}
                  y={labelY}
                  fill="#9CA3AF"
                  fontSize="9"
                  fontWeight="600"
                  textAnchor={anchor}
                  opacity="0.6"
                  transform={`rotate(${labelRotation}, ${labelX}, ${labelY})`}
                  letterSpacing="1.5"
                >
                  {name.toUpperCase()}
                </text>
              </g>
            );
          })}
        </svg>
      )}

      {/* Connections */}
      <div className="absolute inset-0">
        {connections.map((conn, index) => {
          const startPos = positions[conn.source];
          const endPos = positions[conn.target];
          if (!startPos || !endPos) return null;

          const isHighlighted =
            hoveredCharacterId === conn.source || hoveredCharacterId === conn.target;

          return (
            <Connection
              key={`conn-${index}`}
              startPos={startPos}
              endPos={endPos}
              color="#E5E7EB"
              isHighlighted={isHighlighted}
              centerX={centerX}
              centerY={centerY}
            />
          );
        })}
      </div>

      {/* Character nodes */}
      <div className="absolute inset-0">
        {characters.map((character) => {
          const position = positions[character.id];
          if (!position) return null;

          const groupData = characterGroups[character.id];
          const groupKeys = groupInfo ? groupInfo.map(g => g.name).sort() : [];
          const totalGroups = groupKeys.length;
          const groupIndex = groupKeys.indexOf(groupData.groupKey);
          
          const color = groupBy === 'none' 
            ? getColorForSpecies(character.species)
            : getColorForGroup(groupData.groupKey, groupIndex >= 0 ? groupIndex : 0, totalGroups);
          
          const isHovered = hoveredCharacterId === character.id;
          const isConnectedToHovered = connectedCharacters.has(character.id);

          return (
            <CharacterNode
              key={character.id}
              character={character}
              position={position}
              isHovered={isHovered}
              isConnectedToHovered={isConnectedToHovered}
              onClick={handleNodeClick}
              onMouseEnter={() => setHoveredCharacterId(character.id)}
              onMouseLeave={() => setHoveredCharacterId(null)}
              color={color}
              centerX={centerX}
              centerY={centerY}
            />
          );
        })}
      </div>

      {/* Sidebar */}
      <Sidebar
        character={selectedCharacter}
        isOpen={isSidebarOpen}
        onClose={handleSidebarClose}
      />

      {/* Settings Panel */}
      <SettingsPanel
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        groupBy={groupBy}
        onGroupByChange={handleGroupByChange}
      />
    </div>
  );
};

export default Dashboard;
