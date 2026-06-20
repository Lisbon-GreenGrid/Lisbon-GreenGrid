# NCDC Tree Inventory - Quick Start Guide

Get the NCDC Tree Inventory System running locally in 15 minutes.

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Git

## Quick Setup (Linux/macOS)

### 1. Clone & Verify
```bash
git clone <repository-url>
cd NCDC_TREE_INVENTORY
bash verify-setup.sh  # Check system requirements
```

### 2. Database Setup (5 minutes)
```bash
# Connect to PostgreSQL
psql -U postgres

# In PostgreSQL console:
CREATE USER ncdc_admin WITH PASSWORD 'your_password';
CREATE DATABASE ncdc_greengrid OWNER ncdc_admin;
\c ncdc_greengrid
CREATE EXTENSION postgis;
\q

# Initialize schema
cd greengrid_db
psql -U ncdc_admin -d ncdc_greengrid -f 00-create_db.sql
psql -U ncdc_admin -d ncdc_greengrid -f 01-create_schemas.sql
psql -U ncdc_admin -d ncdc_greengrid -f 02-create_sa_tables.sql
psql -U ncdc_admin -d ncdc_greengrid -f 03-create_pa_tables.sql
psql -U ncdc_admin -d ncdc_greengrid -f 04-create_indexes.sql
psql -U ncdc_admin -d ncdc_greengrid -f 05-create_triggers.sql
```

### 3. ETL Setup (3 minutes)
```bash
cd ../greengrid_etl
cp .env.example .env
# Edit .env with your database password
nano .env

pip install -r etl_requirements.txt
python main.py  # Run data pipeline
```

### 4. API Setup (3 minutes)
```bash
cd ../api
cp .env.example .env
# Edit .env with your database password
nano .env

pip install -r requirements.txt
python api.py
```

API will be available at: `http://localhost:5000`

### 5. Web Interface (1 minute)
```bash
cd ../greengrid_web
# Option 1: Simple HTTP server
python3 -m http.server 8000

# Option 2: With Node.js
npm install
npm start
```

Open: `http://localhost:8000`

## Test It Works

```bash
# In another terminal
curl http://localhost:5000/trees | head -20
```

Should return JSON with tree data.

## Troubleshooting

**Database connection fails?**
```bash
psql -U ncdc_admin -h localhost -d ncdc_greengrid -c "SELECT 1;"
```

**ETL hangs?**
- Check internet connection (downloads from ArcGIS)
- Check PostgreSQL is running: `pg_isready`

**API won't start?**
- Verify port 5000 is available: `lsof -i :5000`
- Check database is running and credentials are correct

**Web shows "Cannot find module"?**
- Ensure API is running on port 5000
- Check browser console (F12) for errors
- Verify CORS is enabled in API .env

## Next Steps

- Read [INSTALLATION.md](INSTALLATION.md) for detailed setup
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production
- Review [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) before going live

## Docker Quick Start (Alternative)

```bash
# Copy env template
cp greengrid_etl/.env.example .env

# Start with Docker
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f api
```

Services will be available at:
- API: http://localhost:5000
- pgAdmin: http://localhost:5050 (admin@example.com / admin)
- Web: http://localhost:3000 (if enabled)

---

**Need help?** See the [README.md](README.md) or review individual module READMEs in each folder.
