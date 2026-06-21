# Local Installation - Quick Reference

## Quick Start (Automated)

```bash
cd /home/ghost58/Desktop/NCDC/tree\ inventory/NCDC_TREE_INVENTORY
bash local-install.sh
```

This script will:
- ✓ Verify Python, PostgreSQL, Git
- ✓ Create virtual environment
- ✓ Install dependencies
- ✓ Setup .env files
- ✓ Create database
- ✓ Initialize schema
- ✓ Run ETL pipeline

---

## Manual Setup (Step-by-Step)

### Prerequisites
- Python 3.8+ (you have 3.13.12 ✓)
- PostgreSQL 12+ (you have 18.4 ✓)
- Git (you have it ✓)

### 1. Setup Virtual Environment

```bash
cd "/home/ghost58/Desktop/NCDC/tree inventory/NCDC_TREE_INVENTORY"
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r api/requirements.txt
pip install -r greengrid_etl/etl_requirements.txt
```

### 3. Setup Environment Files

```bash
cp api/.env.example api/.env
cp greengrid_etl/.env.example greengrid_etl/.env
```

Edit both .env files with your PostgreSQL password.

### 4. Create Database

```bash
psql -U postgres -c "CREATE USER ncdc_local WITH PASSWORD 'ncdc_local_dev';"
psql -U postgres -c "CREATE DATABASE ncdc_greengrid OWNER ncdc_local;"
psql -U ncdc_local -d ncdc_greengrid -c "CREATE EXTENSION postgis;"
```

### 5. Initialize Schema

```bash
cd greengrid_db
for script in 00-create_db.sql 01-create_schemas.sql 02-create_sa_tables.sql 03-create_pa_tables.sql 04-create_indexes.sql 05-create_triggers.sql; do
  psql -U ncdc_local -d ncdc_greengrid -f "$script"
done
cd ..
```

### 6. Run ETL Pipeline

```bash
cd greengrid_etl
python main.py
```

### 7. Start API (Terminal 1)

```bash
cd api
python api.py
```

### 8. Start Web UI (Terminal 2)

```bash
cd greengrid_web
python3 -m http.server 8000
```

---

## Access Application

- **API**: http://localhost:5000
- **Web UI**: http://localhost:8000
- **API Test**: curl http://localhost:5000/trees

---

## Database Info

```
User: ncdc_local
Password: ncdc_local_dev
Database: ncdc_greengrid
Host: localhost
Port: 5432
```

---

## Troubleshooting

- **DB not running**: `pg_isready`
- **Port in use**: `lsof -i :5000` or use different port
- **Dependencies missing**: Re-run pip install commands
- **ETL fails**: Check internet connection and logs in etl_logs/

---

## Documentation

- Installation: INSTALLATION.md
- Deployment: DEPLOYMENT.md
- API Docs: api/API_DOCUMENTATION.md
- Security: SECURITY.md
