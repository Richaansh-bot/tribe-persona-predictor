# Contributing to TRIBE v2 Persona Predictor

Thank you for your interest in contributing to this project!

## How to Contribute

### Reporting Bugs

Before creating a bug report:
- Search existing issues to avoid duplicates
- Use the bug report template
- Include your environment details (Python version, OS, etc.)
- Provide minimal reproducible examples

### Suggesting Features

We welcome feature suggestions! Please:
- Search existing issues first
- Describe the feature clearly
- Explain the use case
- Consider backward compatibility

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Install dev dependencies**
   ```bash
   # Python
   pip install -e ".[dev]"
   
   # Frontend
   cd frontend && npm install
   ```
4. **Make your changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation
5. **Run tests**
   ```bash
   # Python tests
   pytest tests/
   
   # Frontend build
   cd frontend && npm run build
   ```
6. **Commit your changes**
   ```bash
   git commit -m "feat: add amazing feature"
   ```
7. **Push and create PR**

## Code Style

### Python
- Follow PEP 8
- Use type hints where possible
- Write docstrings for public functions
- Maximum line length: 100 characters

### JavaScript/React
- Use functional components with hooks
- Follow React best practices
- Use meaningful variable names
- Add comments for complex logic

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/tribe-persona-predictor.git
cd tribe-persona-predictor

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/tribe-persona-predictor.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"
pip install -e ".[plotting]"

# Run the demo
python demo.py
```

## Project Structure

```
tribe-persona-predictor/
├── tribev2_persona/      # Python package
├── frontend/              # React frontend
├── tests/                # Test files
├── docs/                 # Documentation
└── scripts/              # Utility scripts
```

## Questions?

Feel free to:
- Open an issue for questions
- Join discussions in PRs
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
