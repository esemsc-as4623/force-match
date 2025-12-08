# Force Match - Quick Reference

## Start the App
```bash
cd frontend
npm run dev
```
**URL**: http://localhost:3000

## Project Overview
- **83 Star Wars characters** in a circular graph
- **Lightsaber-themed colors** by species
- **Interactive hover effects** with glowing animations
- **Click nodes** to see character details
- **Dynamic grouping** by species, gender, or films

## File Locations

### Main Components
- `src/App.jsx` - Main application
- `src/components/Dashboard.jsx` - Graph visualization
- `src/components/CharacterNode.jsx` - Individual nodes
- `src/components/Connection.jsx` - Graph edges
- `src/components/Sidebar.jsx` - Character details
- `src/components/SettingsPanel.jsx` - Grouping controls

### Data Files
- `public/data/data.ttl` - Character data (83 characters)
- `public/data/connections.ttl` - Graph connections

### Utilities
- `src/utils/dataParser.js` - TTL file parser

## Key Features Checklist
✅ Circular graph layout  
✅ Lightsaber color scheme  
✅ Hover glow effects  
✅ Click for character details  
✅ Sidebar with full info  
✅ Settings panel for grouping  
✅ Space-themed background  
✅ Responsive design  
✅ Keyboard navigation  
✅ Accessibility features  

## Color Palette
- Blue: #4A9EFF (Human, Mon Calamari, etc.)
- Green: #7FFF00 (Rodian, Yoda's species, etc.)
- Red: #FF3B3B (Zabrak, Trandoshan, etc.)
- Purple: #B270FF (Droid, Twi'lek, etc.)
- Yellow: #FFE66D (Wookiee, Ewok, etc.)
- Orange: #FF8C42 (Hutt, Aleena, etc.)

## User Controls
- **Hover**: Highlight character + connections
- **Click node**: Open sidebar
- **Click Settings**: Open grouping panel
- **ESC key**: Close panels
- **Tab**: Navigate with keyboard

## Build for Production
```bash
npm run build
npm run preview
```

## Dependencies
React 18, Vite, TailwindCSS, N3 (RDF parser)
Total: 144 packages installed

---
For detailed documentation, see:
- `frontend/README.md` - Full frontend docs
- `frontend/IMPLEMENTATION_SUMMARY.md` - Complete feature list
- `FRONTEND_GUIDE.md` - Quick start guide
