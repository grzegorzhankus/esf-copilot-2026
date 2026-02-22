#!/bin/bash
# Status check script for esf-copilot-2026

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  e-SF Copilot 2026 Status${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if app is running
RUNNING=false

# Check PID file
if [ -f ".streamlit.pid" ]; then
    PID=$(cat .streamlit.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ App is RUNNING${NC}"
        echo -e "  ${BLUE}Process ID:${NC}    $PID"
        RUNNING=true

        # Get process info
        CPU=$(ps -p $PID -o %cpu= | xargs)
        MEM=$(ps -p $PID -o %mem= | xargs)
        UPTIME=$(ps -p $PID -o etime= | xargs)
        echo -e "  ${BLUE}CPU Usage:${NC}     ${CPU}%"
        echo -e "  ${BLUE}Memory:${NC}        ${MEM}%"
        echo -e "  ${BLUE}Uptime:${NC}        $UPTIME"
    else
        echo -e "${YELLOW}⚠️  App is NOT running (stale PID file)${NC}"
        rm -f .streamlit.pid
    fi
else
    # Check by port
    if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1; then
        PID=$(lsof -t -i:8501 | head -1)
        echo -e "${YELLOW}⚠️  App is running but PID file missing${NC}"
        echo -e "  ${BLUE}Process ID:${NC}    $PID"
        RUNNING=true
    else
        echo -e "${RED}✗ App is NOT running${NC}"
    fi
fi

echo ""

# Check URLs if running
if $RUNNING; then
    echo -e "${BLUE}Access URLs:${NC}"
    echo -e "  ${GREEN}Local:${NC}         http://localhost:8501"
    NETWORK_IP=$(hostname -I | awk '{print $1}')
    echo -e "  ${GREEN}Network:${NC}       http://${NETWORK_IP}:8501"
    echo ""
fi

# Check configuration
echo -e "${BLUE}Configuration:${NC}"

# Check virtual environment
if [ -d ".venv" ]; then
    echo -e "  ${GREEN}✓${NC} Virtual environment exists"
else
    echo -e "  ${RED}✗${NC} Virtual environment missing"
fi

# Check .env file
if [ -f ".env" ]; then
    echo -e "  ${GREEN}✓${NC} .env file exists"

    # Check NVIDIA NIM
    if grep -q "NVIDIA_API_KEY=nvapi-" .env 2>/dev/null; then
        if grep -q "NVIDIA_API_KEY=nvapi-your-api-key-here" .env; then
            echo -e "  ${YELLOW}⚠️${NC}  NVIDIA NIM: Not configured"
        else
            echo -e "  ${GREEN}✓${NC} NVIDIA NIM: Configured"
        fi
    else
        echo -e "  ${YELLOW}⚠️${NC}  NVIDIA NIM: Not configured"
    fi
else
    echo -e "  ${YELLOW}⚠️${NC}  .env file missing"
fi

# Check Ollama
if command -v ollama &> /dev/null; then
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        MODEL_COUNT=$(curl -s http://localhost:11434/api/tags | grep -o '"name"' | wc -l)
        echo -e "  ${GREEN}✓${NC} Ollama: Running (${MODEL_COUNT} models)"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Ollama: Installed but not running"
    fi
else
    echo -e "  ${YELLOW}⚠️${NC}  Ollama: Not installed"
fi

echo ""

# Check log file
if [ -f "streamlit.log" ]; then
    LOG_SIZE=$(du -h streamlit.log | cut -f1)
    LOG_LINES=$(wc -l < streamlit.log)
    echo -e "${BLUE}Logs:${NC}"
    echo -e "  ${BLUE}File:${NC}          streamlit.log"
    echo -e "  ${BLUE}Size:${NC}          $LOG_SIZE"
    echo -e "  ${BLUE}Lines:${NC}         $LOG_LINES"
    echo ""

    # Show last few lines if running
    if $RUNNING; then
        echo -e "${BLUE}Recent log entries:${NC}"
        tail -n 5 streamlit.log | sed 's/^/  /'
    fi
fi

echo ""
echo -e "${BLUE}================================================${NC}\n"

# Show available commands
if $RUNNING; then
    echo -e "${YELLOW}Commands:${NC}"
    echo -e "  ${GREEN}./stop.sh${NC}       - Stop the app"
    echo -e "  ${GREEN}tail -f streamlit.log${NC}  - View live logs"
else
    echo -e "${YELLOW}Commands:${NC}"
    echo -e "  ${GREEN}./start.sh${NC}      - Start the app"
fi

echo ""
