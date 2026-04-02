# TRIBE v2 Persona Predictor

![Made by Richansh](https://img.shields.io/badge/Made%20by-Richansh-00e6c3?style=for-the-badge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-blue.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite)](https://vitejs.dev/)
[![GitHub Stars](https://img.shields.io/github/stars/Richaansh-bot/tribe-persona-predictor?style=social)](https://github.com/Richaansh-bot/tribe-persona-predictor)

> Predict how different personalities react to content using brain-encoded AI

TRIBE v2 Persona Predictor combines Meta's TRIBE v2 brain encoding model with personality-based prediction to forecast how users with different traits will respond to video, audio, and text content.

## Quick Start (Windows)

1. **Double-click `SETUP.bat`** - Installs all dependencies automatically
2. **Double-click `START.bat`** - Launches the application
3. **Open http://localhost:5173** in your browser

That's it! The application runs in CPU mode by default (fast and reliable).

## Features

## Features

### Core Capabilities
- **9 Reaction Types**: Attention, Engagement, Valence, Arousal, Memory, Aesthetics, Novelty, Social, Curiosity
- **6 Pre-built Personas**: Analytical, Creative, Emotional, Social, Pragmatic, Tech-Savvy
- **Custom Personas**: Create from Big5 traits or MBTI types
- **Brain Visualization**: Interactive cortical activation maps
- **Content Recommendations**: AI-generated optimization tips

### Technical
- Built on Meta's TRIBE v2 foundation model
- Cross-attention fusion for brain + persona
- Works with or without TRIBE v2 installed (demo mode)
- Python backend + React frontend
- Responsive neural interface design

## Installation

### Option 1: One-Click Setup (Recommended)

1. Download the project
2. Double-click `SETUP.bat` - Automatically installs all dependencies
3. Double-click `START.bat` - Launches the application
4. Open http://localhost:5173

### Option 2: Manual Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install frontend dependencies
cd frontend
npm install
cd ..

# 3. Start the application
START.bat
```

### GPU Mode (Optional - Requires NVIDIA GPU with 10GB+ VRAM)

For GPU acceleration with TRIBE v2:
1. Install WSL: `wsl --install` (in PowerShell as Admin)
2. Run `SETUP_WSL.bat`
3. Start WSL and run: `bash tribev2_wsl.sh`

Note: GPU mode requires an NVIDIA GPU with at least 10GB VRAM.

## Usage

### Python API

```python
from tribev2_persona import PersonaReactionPipeline
from tribev2_persona.models import PersonaLibrary

# Initialize pipeline
pipeline = PersonaReactionPipeline()
pipeline.load_models(load_tribe=False)  # Demo mode

# Predict reactions for a persona
result = pipeline.predict(
    video_path="content.mp4",
    persona="creative"
)

# Print reaction summary
print(pipeline.summarize_reactions(result["reactions"]))

# Generate insights
insights = pipeline.generate_insights(
    result["reactions"],
    result["persona"]
)
```

### Custom Personas

```python
from tribev2_persona.models import PersonaTraits, PersonaLibrary

# From Big5 traits
persona = PersonaLibrary.create_custom(
    openness=0.85,
    conscientiousness=0.6,
    extraversion=0.4,
    learning_style="visual",
    emotional_range="high"
)

# From MBTI
persona = PersonaTraits.from_mbti("INTJ")
```

### Compare Personas

```python
comparisons = pipeline.compare_personas(
    video_path="video.mp4",
    personas=["analytical", "creative", "emotional"]
)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT                                     │
│              (Video / Audio / Text)                              │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       TRIBE v2                                    │
│            (Brain Response Predictions)                           │
│        Pretrained on 500+ hours fMRI data                        │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PERSONA ENCODER                                 │
│              (Big5 Traits → Embedding)                           │
│         Converts personality traits to vectors                    │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FUSION MODULE                                  │
│           (Cross-Attention + Gating)                             │
│         Combines brain + persona info                            │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                REACTION PREDICTOR                                 │
│        (9 Reaction Types with Confidence)                        │
│  Attention | Engagement | Valence | Arousal | Memory             │
│  Aesthetics | Novelty | Social | Curiosity                       │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
tribe-persona-predictor/
├── tribev2_persona/           # Python package
│   └── models/
│       ├── tribe_wrapper.py    # TRIBE v2 integration
│       ├── persona_encoder.py  # Persona encoding
│       ├── fusion_module.py    # Brain + persona fusion
│       ├── reaction_predictor.py # Reaction predictions
│       └── pipeline.py         # Main API
├── frontend/                   # React frontend
│   └── src/
│       ├── components/         # UI components
│       ├── App.jsx             # Main app
│       └── index.css           # Neural interface styles
├── demo.py                     # Python demo
├── notebooks/
│   └── demo.ipynb             # Jupyter notebook
├── docs/                       # Documentation
├── .github/                    # GitHub templates
├── CONTRIBUTING.md             # Contribution guide
├── CHANGELOG.md               # Version history
├── LICENSE                    # MIT + CC BY-NC 4.0
└── README.md                  # This file
```

## API Reference

### PersonaReactionPipeline

| Method | Description |
|--------|-------------|
| `load_models(load_tribe)` | Load all model components |
| `predict(video/audio/text, persona)` | Predict reactions |
| `compare_personas(personas)` | Compare reactions across personas |
| `generate_insights(reactions, persona)` | Generate human-readable insights |

### PersonaLibrary

| Method | Description |
|--------|-------------|
| `get_persona(name)` | Get pre-built persona |
| `list_personas()` | List available personas |
| `create_custom(...)` | Create custom persona |

### Reaction Types

| Type | Description | Range |
|------|-------------|-------|
| Attention | Focus/concentration level | 0-1 |
| Engagement | Overall interest | 0-1 |
| Valence | Positive vs negative | 0-1 |
| Arousal | Emotional intensity | 0-1 |
| Memory | Memory encoding strength | 0-1 |
| Aesthetics | Beauty appreciation | 0-1 |
| Novelty | Response to new stimuli | 0-1 |
| Social | Response to social cues | 0-1 |
| Curiosity | Desire to continue | 0-1 |

## Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/Richaansh-bot/tribe-persona-predictor.git
cd tribe-persona-predictor

# Python setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev,plotting]"

# Frontend setup
cd frontend
npm install
```

### Run Tests

```bash
# Python
pytest tests/

# Frontend
cd frontend
npm run build
```

### Build for Production

```bash
# Frontend
cd frontend
npm run build
```

## Resources

- [TRIE v2 Paper](https://ai.meta.com/research/publications/a-foundation-model-of-vision-audition-and-language-for-in-silico-neuroscience/)
- [HuggingFace Model](https://huggingface.co/facebook/tribev2)
- [GitHub Repository](https://github.com/facebookresearch/tribev2)
- [Meta AI Blog](https://ai.meta.com/blog/tribe-v2-brain-predictive-foundation-model/)

## Citation

```bibtex
@article{tribePersona2026,
  title={TRIBE v2 Persona Predictor: Brain-Encoded Personality Reactions},
  author={Richansh},
  year={2026}
}

@article{dAscoli2026TribeV2,
  title={A foundation model of vision, audition, and language for in-silico neuroscience},
  author={d'Ascoli, Stephane and Rapin, Jeremy and others},
  year={2026}
}
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

- **TRIE v2 Model**: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) (Meta AI Research)
- **This Project**: [MIT](LICENSE)

---

**Made with ❤️ by [Richansh](https://github.com/Richaansh-bot)**

Built with [Meta AI Research](https://ai.meta.com/research/) | Powered by TRIBE v2
