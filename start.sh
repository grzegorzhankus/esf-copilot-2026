#!/bin/bash
# Start script for esf-copilot-2026

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Starting e-SF Copilot 2026${NC}"
echo -e "${BLUE}================================================${NC}"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if requirements are installed
if [ ! -f ".venv/requirements_installed" ] || [ "requirements.txt" -nt ".venv/requirements_installed" ]; then
    echo -e "${YELLOW}Installing/updating dependencies...${NC}"
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    touch .venv/requirements_installed
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies up to date${NC}"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file to configure LLM settings${NC}"
fi

# Check if Ollama is running (optional)
if command -v ollama &> /dev/null; then
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${GREEN}✓ Ollama is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Ollama is installed but not running${NC}"
        echo -e "${YELLOW}   Start with: ollama serve${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Ollama not found. Install from https://ollama.ai${NC}"
fi

# Check for NVIDIA NIM configuration
if grep -q "NVIDIA_API_KEY=nvapi-" .env 2>/dev/null; then
    if grep -q "NVIDIA_API_KEY=nvapi-your-api-key-here" .env; then
        echo -e "${YELLOW}⚠️  NVIDIA NIM not configured (using placeholder key)${NC}"
        echo -e "${YELLOW}   Get API key from: https://build.nvidia.com/${NC}"
    else
        echo -e "${GREEN}✓ NVIDIA NIM configured${NC}"
    fi
fi

# Create necessary directories
mkdir -p outputs
mkdir -p data/demo_xml

# Check if port 8501 is already in use
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}✗ Port 8501 is already in use${NC}"
    echo -e "${YELLOW}  Stop the existing instance with: ./stop.sh${NC}"
    echo -e "${YELLOW}  Or kill manually: kill \$(lsof -t -i:8501)${NC}"
    exit 1
fi

echo -e "\n${BLUE}================================================${NC}"
echo -e "${GREEN}🚀 Starting Streamlit app...${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Start Streamlit in background and save PID
nohup streamlit run app/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    > streamlit.log 2>&1 &

STREAMLIT_PID=$!
echo $STREAMLIT_PID > .streamlit.pid

# Wait a moment for startup
sleep 3

# Check if process is still running
if ps -p $STREAMLIT_PID > /dev/null; then
    echo -e "${GREEN}✓ App started successfully!${NC}\n"
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}  📊 e-SF Copilot 2026 is running!${NC}"
    echo -e "${GREEN}================================================${NC}\n"
    echo -e "  ${BLUE}Local URL:${NC}     http://localhost:8501"
    echo -e "  ${BLUE}Network URL:${NC}   http://$(hostname -I | awk '{print $1}'):8501"
    echo -e "  ${BLUE}Process ID:${NC}    $STREAMLIT_PID"
    echo -e "  ${BLUE}Log file:${NC}      streamlit.log"
    echo -e "\n${YELLOW}To stop the app:${NC}   ./stop.sh"
    echo -e "${YELLOW}To view logs:${NC}      tail -f streamlit.log\n"
else
    echo -e "${RED}✗ Failed to start app${NC}"
    echo -e "${YELLOW}Check streamlit.log for details${NC}"
    exit 1
fi
