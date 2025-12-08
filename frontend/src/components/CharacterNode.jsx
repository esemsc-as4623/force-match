import React from 'react';

const CharacterNode = ({ character, position, isHovered, isConnectedToHovered, onClick, onMouseEnter, onMouseLeave, color, centerX, centerY }) => {
  const handleClick = () => {
    onClick(character);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick(character);
    }
  };

  const glowClass = isHovered || isConnectedToHovered ? 'animate-pulse-glow' : '';
  const scaleClass = isHovered ? 'scale-125' : 'scale-100';

  // Calculate angle from center to position for radial label orientation
  const dx = position.x - centerX;
  const dy = position.y - centerY;
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
  const angleRad = Math.atan2(dy, dx);
  
  // Calculate label position with proper distance and orientation
  const labelDistance = 35; // Increased to ensure labels are outside circle
  const labelX = labelDistance * Math.cos(angleRad);
  const labelY = labelDistance * Math.sin(angleRad);
  
  // Normalize angle to 0-360 range
  const normalizedAngle = ((angle % 360) + 360) % 360;
  
  // Left side (91° to 270°): left-justified, reads left-to-right
  // Right side (271° to 90°): right-justified, rotated
  const isLeftSide = normalizedAngle > 90 && normalizedAngle <= 270;
  
  let textRotation, textAnchor;
  
  if (isLeftSide) {
    // Left side: flip 180° so text reads left-to-right, left-justified
    textRotation = angle + 180;
    textAnchor = 'start'; // Left-justified
  } else {
    // Right side: normal rotation, right-justified
    textRotation = angle;
    textAnchor = 'end'; // Right-justified
  }
  
  // Character name with fallback for missing data
  const displayName = character.name || character.id || 'Unknown';

  return (
    <div
      className={`absolute cursor-pointer transition-all duration-300 ${scaleClass} ${glowClass}`}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        transform: 'translate(-50%, -50%)',
        color: color,
      }}
      onClick={handleClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="button"
      aria-label={`Character node: ${character.name}`}
    >
      <div className="relative flex items-center justify-center">
        {/* Node circle - no text inside */}
        <div
          className="w-3 h-3 md:w-4 md:h-4 rounded-full shadow-lg transition-all duration-300"
          style={{
            backgroundColor: color,
            boxShadow: `0 0 ${isHovered || isConnectedToHovered ? '30px' : '15px'} ${color}`,
          }}
        />
        {/* Text label positioned outside radially */}
        <div
          className="absolute text-xs font-medium text-white whitespace-nowrap pointer-events-none"
          style={{
            textShadow: `0 0 10px ${color}`,
            transform: `rotate(${textRotation}deg)`,
            transformOrigin: 'center center',
            left: `${labelX}px`,
            top: `${labelY}px`,
            textAlign: textAnchor === 'end' ? 'right' : 'left',
          }}
        >
          {displayName}
        </div>
      </div>
    </div>
  );
};

export default CharacterNode;
