#!/bin/bash

# Car Sales and Servicing Portal - Quick Start Guide

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Car Sales & Servicing Portal${NC}"
echo -e "${BLUE}Quick Start Setup${NC}"
echo -e "${BLUE}================================${NC}"

# Backend Setup
echo -e "\n${YELLOW}Setting up Backend...${NC}"
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/Scripts/activate 2>/dev/null || . venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

echo -e "${GREEN}✓ Backend setup complete!${NC}"
echo -e "${YELLOW}Backend command: python run.py${NC}"

# Frontend Setup
echo -e "\n${YELLOW}Setting up Frontend...${NC}"
cd ../frontend

echo -e "${GREEN}✓ Frontend setup complete!${NC}"
echo -e "${YELLOW}Frontend command: python -m http.server 8000${NC}"

# Summary
echo -e "\n${BLUE}================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "1. Open two terminal windows"
echo -e "2. ${GREEN}Terminal 1:${NC} cd backend && python run.py"
echo -e "3. ${GREEN}Terminal 2:${NC} cd frontend && python -m http.server 8000"
echo -e "4. Open browser: ${GREEN}http://localhost:8000${NC}"
echo -e "\n${YELLOW}Database Setup:${NC}"
echo -e "- See DATABASE_SETUP.md for SQL Server configuration"
echo -e "- Update .env with your database credentials"
echo -e "\n${YELLOW}Documentation:${NC}"
echo -e "- See README.md for full documentation"
echo -e "- See API_TESTING.md for API testing guide"
