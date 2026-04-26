#!/bin/bash

# Setup script for Multimodal Graph RAG (Ubuntu/Linux Version)

# Colors for output
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${CYAN}Checking Docker status...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "Error: Docker is not running or you don't have permissions (try 'sudo')."
    exit 1
fi

echo -e "${CYAN}Starting E-Commerce Intelligence services...${NC}"
# Use 'docker-compose' as the primary tool for this environment
docker-compose up -d --build

echo -e "${GREEN}Waiting for services to initialize (Weaviate & Neo4j)...${NC}"
# Wait for healthchecks to pass
sleep 20

echo -e "${CYAN}Seeding Multimodal E-Commerce Data...${NC}"
# Check for python3
if command -v python3 &>/dev/null; then
    python3 backend/ingest_data.py
elif command -v python &>/dev/null; then
    python backend/ingest_data.py
else
    echo -e "Error: Python is not installed. Please install python3 to run the ingestion script."
fi

echo -e "------------------------------------------------"
echo -e "${GREEN}System is ready!${NC}"
echo -e "Frontend Dashboard: http://localhost:3000"
echo -e "Backend API Docs:   http://localhost:8000/docs"
echo -e "Neo4j Explorer:     http://localhost:7474 (Login: neo4j/password)"
echo -e "------------------------------------------------"
