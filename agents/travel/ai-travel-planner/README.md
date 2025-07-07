# AI Travel Planner

AI-powered travel planning assistant that helps you find flights and hotels with intelligent recommendations.

## Quick Start (Recommended)

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- Poetry (Python dependency manager)

### 1. Install Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Clone and Setup
```bash
git clone https://github.com/MeirKaD/ai-travel-planner.git
cd ai-travel-planner
chmod +x bootstrap.sh
./bootstrap.sh
```

That's it! The bootstrap script will:
- Install all Python dependencies using Poetry
- Install all frontend dependencies using npm
- Start both backend and frontend services
- Open the application at http://localhost:5173

## Manual Setup

### Backend Setup
```bash
# Install Python dependencies
poetry install

# Start backend server
poetry run python -m backend.main
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend/trip-planner

# Install dependencies
npm install

# Start development server
npm run dev
```

## Environment Configuration

Create a `.env` file in the project root with your API keys:

```env
BRIGHT_DATA_API_TOKEN=""
GOOGLE_API_KEY=""
GOOGLE_GENAI_USE_VERTEXAI="False"
SENDGRID_API_KEY=""
FROM_EMAIL=""
TO_EMAIL=""
```

## Available Commands

### Poetry Commands
```bash
# Install dependencies
poetry install

# Add new dependency
poetry add package_name

# Add development dependency
poetry add --group dev package_name

# Run backend
poetry run python -m backend.main

# Run tests
poetry run pytest

# Format code
poetry run black .

# Check code quality
poetry run flake8 .
```

### npm Commands
```bash
cd frontend/trip-planner

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure
```
ai-travel-planner/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── graph.py             # Travel planning workflow
│   └── state.py             # Application state management
├── frontend/
│   └── trip-planner/        # React application
├── pyproject.toml           # Poetry configuration
├── bootstrap.sh             # Quick start script
└── README.md
```

## API Endpoints

- `POST /travel` - Plan travel with flights and hotels
- `GET /` - Simple web interface
- `WS /ws/{thread_id}` - WebSocket for real-time updates
- `GET /docs` - Interactive API documentation

## Features

- 🎯 Intelligent travel planning
- ✈️ Flight search and recommendations
- 🏨 Hotel search with star ratings
- 📧 Automated email reports
- 🔄 Real-time updates via WebSocket
- 📱 Responsive web interface
- 🎨 Modern UI with animations

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

**Poetry not found:**
```bash
# Add Poetry to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

**Dependencies not installing:**
```bash
# Clear Poetry cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install --no-cache
```

## Development

### Adding New Dependencies

**Python packages:**
```bash
poetry add package_name
```

**Development tools:**
```bash
poetry add --group dev package_name
```

**Frontend packages:**
```bash
cd frontend/trip-planner
npm install package_name
```

### Code Quality

Run code formatting and linting:
```bash
poetry run black .
poetry run flake8 .
poetry run mypy .
```

### Testing

```bash
poetry run pytest
```

## Production Deployment

### Backend
```bash
# Build and run with Poetry
poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend/trip-planner
npm run build
# Serve the dist/ folder with your preferred web server
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please create an issue in the repository.