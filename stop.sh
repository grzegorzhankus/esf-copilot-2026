#!/bin/bash
# Stop script for esf-copilot-2026

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Stopping e-SF Copilot 2026${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

STOPPED=false

# Method 1: Check PID file
if [ -f ".streamlit.pid" ]; then
    PID=$(cat .streamlit.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping process (PID: $PID)...${NC}"
        kill $PID

        # Wait up to 10 seconds for graceful shutdown
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                echo -e "${GREEN}✓ Process stopped gracefully${NC}"
                STOPPED=true
                break
            fi
            sleep 1
        done

        # Force kill if still running
        if ! $STOPPED; then
            if ps -p $PID > /dev/null 2>&1; then
                echo -e "${YELLOW}Force killing process...${NC}"
                kill -9 $PID
                echo -e "${GREEN}✓ Process force killed${NC}"
                STOPPED=true
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Process $PID not running (stale PID file)${NC}"
    fi
    rm -f .streamlit.pid
fi

# Method 2: Kill by port
if ! $STOPPED; then
    if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}Finding process on port 8501...${NC}"
        PIDS=$(lsof -t -i:8501)
        for PID in $PIDS; do
            echo -e "${YELLOW}Stopping process (PID: $PID)...${NC}"
            kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
            STOPPED=true
        done
        echo -e "${GREEN}✓ Process(es) stopped${NC}"
    fi
fi

# Method 3: Kill by name (fallback)
if ! $STOPPED; then
    PIDS=$(pgrep -f "streamlit run app/app.py" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        echo -e "${YELLOW}Finding Streamlit processes...${NC}"
        for PID in $PIDS; do
            echo -e "${YELLOW}Stopping process (PID: $PID)...${NC}"
            kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
            STOPPED=true
        done
        echo -e "${GREEN}✓ Process(es) stopped${NC}"
    fi
fi

if ! $STOPPED; then
    echo -e "${GREEN}✓ No running instances found${NC}"
fi

# Clean up temporary files
if [ -f "streamlit.log" ]; then
    echo -e "${BLUE}Log saved to: streamlit.log${NC}"
fi

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}  e-SF Copilot 2026 stopped${NC}"
echo -e "${GREEN}================================================${NC}\n"
