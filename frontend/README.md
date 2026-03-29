# TRIBE v2 Neural Persona Predictor - Frontend

A stunning, non-generic frontend for predicting neural reactions based on personality types.

## Design Philosophy

This interface uses a **Neural Interface** aesthetic inspired by neuroscience research and sci-fi control panels:

- **Bioluminescent accents** - Cyan and blue gradients mimicking neural activity
- **Dark atmospheric backgrounds** - Deep space-like environment
- **Organic flowing animations** - Synaptic firing patterns
- **Glass-morphism depth** - Layered translucent panels
- **Custom brain visualization** - Interactive cortical response mapping

## Tech Stack

- React 18
- Vite
- Tailwind CSS
- Framer Motion

## Getting Started

```bash
cd frontend
npm install
npm run dev
```

## Features

- **Persona Selection** - 6 pre-built personality types
- **Video Upload** - Drag & drop with file validation
- **Brain Visualization** - Real-time cortical activation map
- **Reaction Dashboard** - 9 reaction type predictions with confidence meters
- **Neural Insights** - AI-generated content optimization recommendations
- **Radar Chart** - Visual comparison of all reactions

## Architecture

```
src/
├── components/
│   ├── Header.jsx           # Navigation with animated logo
│   ├── HeroSection.jsx      # Landing with particle effects
│   ├── PersonaSelector.jsx  # Personality type cards
│   ├── UploadSection.jsx    # File upload with drag & drop
│   ├── ReactionDashboard.jsx # Reaction predictions display
│   ├── BrainVisualization.jsx # Interactive brain SVG
│   ├── InsightsPanel.jsx    # Recommendations & radar chart
│   ├── LoadingOverlay.jsx   # Analysis animation
│   ├── FloatingParticles.jsx # Background effects
│   └── Footer.jsx
├── App.jsx                  # Main application state
├── main.jsx                 # Entry point
└── index.css                # Custom styles & animations
```

## Customization

### Adding New Personas

Edit the `PERSONAS` object in `App.jsx`:

```javascript
const PERSONAS = {
  new_persona: {
    name: 'New Persona',
    icon: '🎯',
    description: 'Description here',
    traits: {
      openness: 0.7,
      conscientiousness: 0.8,
      // ...
    }
  }
}
```

### Modifying Brain Regions

Edit the `BRAIN_REGIONS` array in `App.jsx` to change which brain regions are visualized.

### API Integration

Replace the simulated analysis in `handleAnalyze` with actual TRIBE v2 API calls:

```javascript
const response = await fetch('/api/analyze', {
  method: 'POST',
  body: JSON.stringify({
    video: file,
    persona: selectedPersona
  })
})
```

## License

MIT - See main project LICENSE
