#!/bin/bash

# NCDC Tree Inventory - Setup Verification Script
# This script verifies all components are properly configured for local installation

set -e

echo "======================================"
echo "NCDC Tree Inventory Setup Verification"
echo "======================================"
echo ""

ERRORS=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Helper functions
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        ((ERRORS++))
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Found: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Missing: $1"
        ((ERRORS++))
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} Found directory: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Missing directory: $1"
        ((ERRORS++))
        return 1
    fi
}

warn() {
    echo -e "${YELLOW}⚠${NC} WARNING: $1"
    ((WARNINGS++))
}

# 1. Check System Requirements
echo "1. System Requirements"
echo "---------------------"
check_command "python3"
check_command "psql"
check_command "git"

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $PYTHON_VERSION"

PG_VERSION=$(psql --version | awk '{print $3}')
echo "  PostgreSQL version: $PG_VERSION"

echo ""

# 2. Check Project Structure
echo "2. Project Structure"
echo "-------------------"
check_dir "api"
check_dir "greengrid_db"
check_dir "greengrid_etl"
check_dir "greengrid_web"

echo ""

# 3. Check Configuration Files
echo "3. Configuration Files"
echo "----------------------"
check_file ".env.example" || warn "Missing .env.example (or it should be in subdirectories)"
check_file "api/.env.example"
check_file "greengrid_etl/.env.example"
check_file ".gitignore"

echo ""

# 4. Check Documentation
echo "4. Documentation"
echo "----------------"
check_file "README.md"
check_file "INSTALLATION.md"
check_file "DEPLOYMENT.md"
check_file "DEPLOYMENT_CHECKLIST.md"

echo ""

# 5. Check Requirements Files
echo "5. Dependencies"
echo "---------------"
check_file "api/requirements.txt"
check_file "greengrid_etl/etl_requirements.txt"

# Check for version pinning
if grep -q "==" "api/requirements.txt"; then
    echo -e "${GREEN}✓${NC} API requirements have pinned versions"
else
    warn "API requirements.txt should have pinned versions (use ==)"
fi

echo ""

# 6. Check Database Setup Scripts
echo "6. Database Setup"
echo "----------------"
check_file "greengrid_db/00-create_db.sql"
check_file "greengrid_db/01-create_schemas.sql"
check_file "greengrid_db/02-create_sa_tables.sql"
check_file "greengrid_db/03-create_pa_tables.sql"
check_file "greengrid_db/04-create_indexes.sql"
check_file "greengrid_db/05-create_triggers.sql"
check_file "greengrid_db/06-data.sql"

echo ""

# 7. Check API Files
echo "7. API Module"
echo "-------------"
check_file "api/api.py"
check_file "api/README.md"

# Check if API uses environment variables
if grep -q "os.getenv" "api/api.py"; then
    echo -e "${GREEN}✓${NC} API uses environment variables for configuration"
else
    warn "API should use environment variables (os.getenv) instead of hardcoded values"
fi

# Check for python-dotenv
if grep -q "python-dotenv\|python_dotenv\|dotenv" "api/requirements.txt"; then
    echo -e "${GREEN}✓${NC} python-dotenv is in requirements"
else
    warn "python-dotenv should be in api/requirements.txt"
fi

echo ""

# 8. Check ETL Module
echo "8. ETL Module"
echo "-------------"
check_file "greengrid_etl/main.py"
check_file "greengrid_etl/etl/__init__.py"
check_file "greengrid_etl/config/00.yml"
check_file "greengrid_etl/README.md"

echo ""

# 9. Check Web Application
echo "9. Web Application"
echo "------------------"
check_file "greengrid_web/index.html"

if [ -f "greengrid_web/package.json" ]; then
    echo -e "${GREEN}✓${NC} Node.js project detected"
else
    echo -e "${YELLOW}ℹ${NC} Static HTML project (no package.json)"
fi

echo ""

# 10. Check Docker Files
echo "10. Containerization"
echo "--------------------"
if [ -f "Dockerfile" ] && [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}✓${NC} Docker files present"
else
    warn "Docker files missing (optional but recommended)"
fi

echo ""

# 11. Check Git Configuration
echo "11. Git Configuration"
echo "---------------------"
if [ -d ".git" ]; then
    echo -e "${GREEN}✓${NC} Git repository initialized"
    LAST_COMMIT=$(git log -1 --pretty=format:"%h - %s")
    echo "  Last commit: $LAST_COMMIT"
else
    warn "Not a git repository"
fi

echo ""

# 12. Summary
echo "======================================"
echo "Verification Summary"
echo "======================================"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
else
    echo -e "${RED}✗ $ERRORS error(s) found${NC}"
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s)${NC}"
fi

echo ""

# 13. Next Steps
echo "Next Steps:"
echo "-----------"
echo "1. Create .env file in api/ directory:"
echo "   cp api/.env.example api/.env"
echo "   # Edit api/.env with your database credentials"
echo ""
echo "2. Create .env file in greengrid_etl/ directory:"
echo "   cp greengrid_etl/.env.example greengrid_etl/.env"
echo "   # Edit greengrid_etl/.env with your database credentials"
echo ""
echo "3. Follow INSTALLATION.md for complete setup steps"
echo ""
echo "4. For Docker deployment:"
echo "   docker-compose up -d"
echo ""

exit $ERRORS
