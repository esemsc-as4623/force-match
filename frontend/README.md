# Force Match Frontend

An interactive Star Wars character visualization dashboard built with React, Vite, and TailwindCSS.

## Features

- **Interactive Circular Graph**: Each Star Wars character is represented as a node in a circular graph
- **Lightsaber-Themed Colors**: Nodes and connections use vibrant lightsaber colors (blue, green, red, purple, yellow, orange)
- **Hover Effects**: Nodes and their connections glow when hovered
- **Character Details**: Click any node to view detailed character information in a sidebar
- **Dynamic Grouping**: Group characters by species, gender, or film appearances
- **Space-Themed Background**: Dark space background with twinkling stars
- **Fully Responsive**: Works on desktop, tablet, and mobile devices

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Building for Production

To create a production build:
```bash
npm run build
```

To preview the production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/
│   └── data/
│       ├── data.ttl           # Character data from SWAPI
│       └── connections.ttl    # Character connections
├── src/
│   ├── components/
│   │   ├── CharacterNode.jsx  # Individual character node
│   │   ├── Connection.jsx     # Connection line between nodes
│   │   ├── Dashboard.jsx      # Main dashboard layout
│   │   ├── Sidebar.jsx        # Character details sidebar
│   │   └── SettingsPanel.jsx  # Settings panel
│   ├── utils/
│   │   └── dataParser.js      # TTL file parser
│   ├── App.jsx                # Main app component
│   ├── main.jsx               # Entry point
│   └── index.css              # Global styles
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── vite.config.js
```

## Data Format

The application uses RDF/Turtle (TTL) format for data:

- **data.ttl**: Contains Star Wars character information from SWAPI
- **connections.ttl**: Defines connections between characters in a circular graph

## Technologies Used

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **N3**: RDF/Turtle parser for JavaScript
- **Custom animations**: Glow effects and transitions

## Customization

### Changing Colors

Edit `tailwind.config.js` to customize the lightsaber colors:

```javascript
colors: {
  lightsaber: {
    blue: '#4A9EFF',
    green: '#7FFF00',
    red: '#FF3B3B',
    purple: '#B270FF',
    yellow: '#FFE66D',
    orange: '#FF8C42',
  }
}
```

### Adding New Grouping Options

Edit `src/components/SettingsPanel.jsx` and `src/components/Dashboard.jsx` to add new grouping criteria.

## Accessibility

The application includes:
- Keyboard navigation support
- ARIA labels for interactive elements
- Focus indicators
- Screen reader friendly structure

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ JavaScript support required
