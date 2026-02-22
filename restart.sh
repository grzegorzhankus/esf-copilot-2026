#!/bin/bash
# Restart script for esf-copilot-2026

# Colors for output
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Restarting e-SF Copilot 2026${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Stop the app
./stop.sh

# Wait a moment
sleep 2

# Start the app
./start.sh
