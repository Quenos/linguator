#!/bin/bash

# Kill any existing Uvicorn processes
echo "Stopping any existing Uvicorn servers..."
pkill -f uvicorn || true

# Set the base directory to the project root
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Activate the virtual environment
echo "Activating virtual environment..."
source "${BASE_DIR}/venv/bin/activate"

# Run the Uvicorn server
echo "Starting Uvicorn server..."
cd "${BASE_DIR}"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Note: The server will continue running until you press CTRL+C
# When you're done, you can deactivate the virtual environment by typing 'deactivate' 