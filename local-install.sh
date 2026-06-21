#!/bin/bash

# NCDC Tree Inventory - Local Installation Script

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=================================================="
echo "NCDC Tree Inventory - Local Installation"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo "▶ Checking Prerequisites..."
command -v python3 > /dev/null || { error "Python 3 not found"; exit 1; }
command -v psql > /dev/null || { error "PostgreSQL not found"; exit 1; }
success "All prerequisites installed"

# Setup virtual environment
echo ""
echo "▶ Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    success "Virtual environment created"
else
    success "Virtual environment exists"
fi

source venv/bin/activate
success "Virtual environment activated"

# Install dependencies
echo ""
echo "▶ Installing Python Dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r api/requirements.txt
pip install --quiet -r greengrid_etl/etl_requirements.txt
success "Dependencies installed"

# Setup environment files
echo ""
echo "▶ Setting up Environment Files..."
if [ ! -f "api/.env" ]; then
    cp api/.env.example api/.env
    sed -i 's/your_secure_password_here/ncdc_local_dev/g' api/.env
    success "api/.env created"
else
    success "api/.env already exists"
fi

if [ ! -f "greengrid_etl/.env" ]; then
    cp greengrid_etl/.env.example greengrid_etl/.env
    sed -i 's/your_secure_password_here/ncdc_local_dev/g' greengrid_etl/.env
    success "greengrid_etl/.env created"
else
    success "greengrid_etl/.env already exists"
fi

# Database setup
echo ""
echo "▶ Setting up PostgreSQL Database..."
psql -U postgres << DBEOF 2>/dev/null || warn "Database setup skipped (may already exist)"
CREATE USER ncdc_local WITH PASSWORD 'ncdc_local_dev';
CREATE DATABASE ncdc_greengrid OWNER ncdc_local;
\c ncdc_greengrid
CREATE EXTENSION IF NOT EXISTS postgis;
DBEOF
success "Database configured"

# Initialize schema
echo ""
echo "▶ Initializing Database Schema..."
cd greengrid_db
for script in 00-create_db.sql 01-create_schemas.sql 02-create_sa_tables.sql 03-create_pa_tables.sql 04-create_indexes.sql 05-create_triggers.sql; do
    psql -U ncdc_local -d ncdc_greengrid -f "$script" > /dev/null 2>&1 || true
done
cd ..
success "Database schema initialized"

# ETL pipeline
echo ""
echo "▶ Running ETL Pipeline (this may take 2-5 minutes)..."
cd greengrid_etl
python main.py
cd ..
success "ETL pipeline completed"

# Summary
echo ""
echo "=================================================="
echo "✅ Installation Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start API (Terminal 1):"
echo "   cd api && python api.py"
echo ""
echo "2. Start Web (Terminal 2):"
echo "   cd greengrid_web && python3 -m http.server 8000"
echo ""
echo "3. Access:"
echo "   API: http://localhost:5000"
echo "   Web: http://localhost:8000"
echo ""
