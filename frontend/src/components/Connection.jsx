import React from 'react';

const Connection = ({ startPos, endPos, color, isHighlighted, centerX, centerY }) => {
  // AFFINITY_FACTOR: Controls how much the connection is pulled toward the center
  // Range: 0.0 (straight line) to 1.0 (passes directly through center)
  // Recommended: 0.7-0.95 for strong center affinity
  const AFFINITY_FACTOR = 0.85; // ← ADJUST THIS VALUE to control center affinity
  
  // Use cubic Bezier curve with two control points
  // Both control points are pulled toward the center based on AFFINITY_FACTOR
  
  // Control point 1: closer to start, pulled toward center
  const control1X = startPos.x + (centerX - startPos.x) * AFFINITY_FACTOR;
  const control1Y = startPos.y + (centerY - startPos.y) * AFFINITY_FACTOR;
  
  // Control point 2: closer to end, pulled toward center
  const control2X = endPos.x + (centerX - endPos.x) * AFFINITY_FACTOR;
  const control2Y = endPos.y + (centerY - endPos.y) * AFFINITY_FACTOR;

  const pathData = `M ${startPos.x} ${startPos.y} C ${control1X} ${control1Y}, ${control2X} ${control2Y}, ${endPos.x} ${endPos.y}`;
  
  // Calculate arrow direction at the end point
  const dx = endPos.x - control2X;
  const dy = endPos.y - control2Y;
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
  
  const arrowSize = 6;

  return (
    <svg
      className="absolute pointer-events-none transition-all duration-300"
      style={{
        left: 0,
        top: 0,
        width: '100%',
        height: '100%',
        overflow: 'visible',
      }}
    >
      <defs>
        <marker
          id={`arrowhead-${isHighlighted ? 'highlight' : 'normal'}`}
          markerWidth={arrowSize}
          markerHeight={arrowSize}
          refX={arrowSize - 1}
          refY={arrowSize / 2}
          orient="auto"
        >
          <polygon
            points={`0 0, ${arrowSize} ${arrowSize / 2}, 0 ${arrowSize}`}
            fill={color}
            opacity={isHighlighted ? 1 : 0.6}
          />
        </marker>
      </defs>
      <path
        d={pathData}
        stroke={color}
        strokeWidth={isHighlighted ? 3 : 2}
        fill="none"
        opacity={isHighlighted ? 1 : 0.6}
        markerEnd={`url(#arrowhead-${isHighlighted ? 'highlight' : 'normal'})`}
        style={{
          filter: isHighlighted ? `drop-shadow(0 0 15px ${color})` : `drop-shadow(0 0 8px ${color})`,
        }}
      />
    </svg>
  );
};

export default Connection;
