# Force Match - Frontend Quick Start

## 🚀 Getting Started

### Option 1: Using the Quick Start Script
```bash
cd frontend
./start.sh
```

### Option 2: Manual Start
```bash
cd frontend
npm install
npm run dev
```

The application will be available at: **http://localhost:3000**

## 📋 What You'll See

- **Interactive Graph**: 83 Star Wars characters arranged in a circle
- **Lightsaber Colors**: Each species has its own lightsaber-themed color
- **Hover Effects**: Glowing effects on hover
- **Click to Explore**: Click any character to see detailed information
- **Settings Panel**: Group characters by species, gender, or film appearances

## 🎨 Features

1. **Character Nodes**: Each character is a circular node with their name
2. **Connections**: Lines connect characters in a circular graph pattern
3. **Sidebar**: Click a node to see character details (height, mass, species, etc.)
4. **Settings**: Toggle grouping to reorganize the layout
5. **Responsive**: Works on all screen sizes

## 🛠️ Tech Stack

- React 18 + Vite
- TailwindCSS
- N3 (RDF/Turtle parser)
- Custom animations and effects

## 📁 Data Files

- `public/data/data.ttl` - 83 Star Wars characters from SWAPI
- `public/data/connections.ttl` - Character connections in circular graph

## 🎮 Controls

- **Hover**: Highlight a character and their connections
- **Click**: Open character details sidebar
- **Settings Button**: Open settings to change grouping
- **Escape**: Close sidebar or settings panel

## 📝 Notes

The frontend automatically parses the TTL files and creates the visualization. The connections form a single circular graph where each character connects to exactly one other character.

For more details, see `frontend/README.md`
