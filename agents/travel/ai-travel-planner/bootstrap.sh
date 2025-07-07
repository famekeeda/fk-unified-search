#!/bin/bash

# AI Travel Planner Bootstrap Script (Poetry Version)
# This script starts both backend and frontend services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE} AI Travel Planner Bootstrap${NC}"
    echo -e "${PURPLE}================================${NC}"
    echo
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to cleanup background processes on exit
cleanup() {
    print_status "Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend stopped"
    fi
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

print_header

# Pre-flight checks
print_status "Running pre-flight checks..."

# Check if Poetry is available
if ! command_exists poetry; then
    print_error "Poetry is not installed. Please install it first:"
    echo -e "${CYAN}curl -sSL https://install.python-poetry.org | python3 -${NC}"
    exit 1
fi

# Check if npm is available
if ! command_exists npm; then
    print_error "npm is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the project root directory."
    exit 1
fi

if [ ! -f "backend/main.py" ]; then
    print_error "backend/main.py not found. Please run this script from the project root directory."
    exit 1
fi

if [ ! -d "frontend/trip-planner" ]; then
    print_error "frontend/trip-planner directory not found. Please run this script from the project root directory."
    exit 1
fi

# Check ports availability
if ! check_port 8000; then
    print_error "Port 8000 is already in use. Please stop the service using this port."
    exit 1
fi

if ! check_port 5173; then
    print_warning "Port 5173 is in use. Vite will try to use the next available port."
fi

print_success "Pre-flight checks completed"
echo

# Install dependencies if needed
print_status "Checking Python dependencies..."
if ! poetry check >/dev/null 2>&1; then
    print_warning "Dependencies need to be installed"
    print_status "Installing Python dependencies with Poetry..."
    poetry install
    print_success "Python dependencies installed"
else
    print_success "Python dependencies are up to date"
fi

# Check and install npm dependencies
print_status "Checking frontend dependencies..."
cd frontend/trip-planner
if [ ! -d "node_modules" ]; then
    print_status "Installing npm dependencies..."
    npm install
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies are installed"
fi
cd ../..

# Environment reminders
print_warning "IMPORTANT REMINDERS:"
echo -e "${YELLOW}1. Make sure all required environment variables are set:${NC}"
echo -e "   ${CYAN}- API keys for travel services${NC}"
echo -e "   ${CYAN}- Email configuration${NC}"
echo -e "   ${CYAN}- Any other service credentials${NC}"
echo -e "${YELLOW}2. Create a .env file in the project root if needed${NC}"
echo

read -p "Press Enter to continue or Ctrl+C to abort..."
echo

# Start Backend using Poetry
print_status "Starting backend server on port 8000..."
cd "$(dirname "$0")"  # Go to script directory (project root)

poetry run python -m backend.main &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend failed to start"
    exit 1
fi

print_success "Backend started successfully (PID: $BACKEND_PID)"

# Start Frontend
print_status "Starting frontend development server..."
cd frontend/trip-planner

npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Frontend failed to start"
    exit 1
fi

print_success "Frontend started successfully (PID: $FRONTEND_PID)"
echo

# Success message
print_success "🚀 AI Travel Planner is now running!"
echo
echo -e "${GREEN}Backend API:${NC} http://localhost:8000"
echo -e "${GREEN}Frontend App:${NC} http://localhost:5173"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo
print_status "Press Ctrl+C to stop both services"
echo

# Keep the script running and wait for user interruption
wait