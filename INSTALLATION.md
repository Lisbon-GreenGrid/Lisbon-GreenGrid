# NCDC Tree Inventory - Local Installation Guide

## Overview
The NCDC Tree Inventory System is a comprehensive urban tree management platform with:
- PostgreSQL/PostGIS spatial database
- Python ETL pipeline for data processing
- Flask REST API
- Interactive web interface with Leaflet maps

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (with WSL2)
- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher
- **PostGIS**: 3.0 or higher
- **Node.js**: 14+ (for web development, optional)

### Required Software Installation

#### 1. PostgreSQL & PostGIS

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis postgresql-12-postgis
```

**macOS (with Homebrew):**
```bash
brew install postgresql postgis
brew services start postgresql
```

**Windows:**
Download PostgreSQL installer from https://www.postgresql.org/download/windows/ and include PostGIS extension during installation.

#### 2. Python Setup

```bash
# Check Python version
python3 --version

# Create a virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

## Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-repo/NCDC_TREE_INVENTORY.git
cd NCDC_TREE_INVENTORY
```

### Step 2: Database Setup

**2.1 Create PostgreSQL User and Database:**
```bash
sudo -u postgres psql
```

Inside psql:
```sql
-- Create a new user (change password as needed)
CREATE USER ncdc_admin WITH PASSWORD 'your_secure_password';

-- Create the database
CREATE DATABASE ncdc_greengrid OWNER ncdc_admin;

-- Connect to the new database
\c ncdc_greengrid

-- Enable PostGIS extension
CREATE EXTENSION postgis;

-- Exit psql
\q
```

**2.2 Initialize Database Schema:**

Navigate to `greengrid_db` folder:
```bash
cd greengrid_db

# Run initialization scripts in order:
# Note: Update connection strings in scripts as needed
psql -U ncdc_admin -d ncdc_greengrid -f 00-create_db.sql
psql -U ncdc_admin -d ncdc_greengrid -f 01-create_schemas.sql
psql -U ncdc_admin -d ncdc_greengrid -f 02-create_sa_tables.sql
psql -U ncdc_admin -d ncdc_greengrid -f 03-create_pa_tables.sql
psql -U ncdc_admin -d ncdc_greengrid -f 04-create_indexes.sql
psql -U ncdc_admin -d ncdc_greengrid -f 05-create_triggers.sql

# Run initial data (after ETL completes):
# psql -U ncdc_admin -d ncdc_greengrid -f 06-data.sql
```

**Alternative: Using Python Setup Script:**
```bash
python create_db.py
# Follow prompts to enter database credentials
```

### Step 3: ETL Configuration

Navigate to `greengrid_etl` folder:

**3.1 Setup Python Environment:**
```bash
cd ../greengrid_etl
pip install -r etl_requirements.txt
```

**3.2 Configure Environment:**
```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your database credentials
nano .env  # or use your preferred editor
```

Update the following in `.env`:
```
DB_PASSWORD=your_secure_password
DB_USER=ncdc_admin
DB_HOST=localhost
DB_NAME=ncdc_greengrid
```

**3.3 Update YAML Configuration (Optional):**
```bash
# Edit config/00.yml
nano config/00.yml

# Update database credentials:
database:
  database: ncdc_greengrid
  host: localhost
  port: 5432
  username: ncdc_admin
  password: your_secure_password
```

**3.4 Run ETL Pipeline:**
```bash
python main.py
```

The ETL will:
- Download tree data from the ArcGIS service
- Transform and validate the data
- Load it into the PostGIS database
- Generate logs in `etl_logs/` directory

### Step 4: API Setup

Navigate to `api` folder:

**4.1 Setup Python Environment:**
```bash
cd ../api
pip install -r requirements.txt
```

**4.2 Configure Environment:**
```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

Update the following in `.env`:
```
DB_NAME=ncdc_greengrid
DB_USER=ncdc_admin
DB_PASSWORD=your_secure_password
DB_HOST=localhost
API_ENV=development
```

**4.3 Start the API Server:**
```bash
python api.py
```

The API will be available at: `http://localhost:5000`

### Step 5: Web Application Setup

Navigate to `greengrid_web` folder:

**5.1 Option A: Direct HTML (Simplest)**
```bash
cd ../greengrid_web

# Open in default browser or use a local server:
python3 -m http.server 8000
```

Then visit: `http://localhost:8000`

**5.2 Option B: With Node.js Development Server (Recommended)**
```bash
# Install dependencies (if package.json exists)
npm install

# Start development server
npm start
# or
npm run dev
```

## Verification Checklist

- [ ] PostgreSQL is running: `psql --version`
- [ ] PostGIS installed: `psql -c "CREATE EXTENSION postgis;"`
- [ ] Database created: `psql -l | grep ncdc_greengrid`
- [ ] ETL ran successfully: Check `etl_logs/` for completion messages
- [ ] API server started: Visit `http://localhost:5000/trees` (should return JSON)
- [ ] Web UI loads: Visit `http://localhost:8000` and check browser console for errors

## Testing the System

### Test API Endpoints

```bash
# Get all trees
curl http://localhost:5000/trees

# Get trees by parish
curl "http://localhost:5000/trees/freguesia/Lisboa"

# Get trees by species
curl "http://localhost:5000/trees/species/oak"

# Find nearby trees (within 500m of coordinates)
curl "http://localhost:5000/trees/near?lat=38.7223&lon=-9.1393&radius=500"
```

### Test Web Interface
1. Open http://localhost:8000 in browser
2. Check if map loads with tree data
3. Test search functionality
4. Test CRUD operations (add, update, delete trees)
5. Check console for any JavaScript errors

## Troubleshooting

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -U ncdc_admin -h localhost -d ncdc_greengrid -c "SELECT 1;"

# Check PostGIS
psql -U ncdc_admin -d ncdc_greengrid -c "SELECT postgis_version();"
```

### ETL Fails
- Check database credentials in `.env`
- Verify database and schema exist
- Check internet connection (downloads data from ArcGIS)
- Review logs in `etl_logs/` directory

### API Won't Start
- Check port 5000 is available: `lsof -i :5000`
- Verify database is running
- Check `.env` file has correct credentials
- Review Python error messages

### Web Interface Issues
- Open browser developer console (F12)
- Check for CORS errors (configure API_CORS_ORIGINS in `.env`)
- Verify API is running on correct port
- Check network requests in browser

## Next Steps

- Review [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Implement authentication and authorization
- Configure HTTPS/SSL for production
- Set up database backups
- Implement monitoring and logging
