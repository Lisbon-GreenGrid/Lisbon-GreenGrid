# NCDC Tree Inventory - Production Deployment Guide

## Overview

This guide covers deploying the NCDC Tree Inventory System to a production environment with:
- Security hardening
- Performance optimization
- High availability considerations
- Monitoring and logging
- Database backups

## Pre-Deployment Checklist

- [ ] All code is committed to git
- [ ] All dependencies are pinned with versions
- [ ] Environment configuration is externalized
- [ ] Sensitive credentials are not in version control
- [ ] SSL/TLS certificates are obtained
- [ ] Database backups are configured
- [ ] Monitoring and alerting are set up
- [ ] Disaster recovery plan is documented

## Production Environment Setup

### 1. Server Infrastructure

#### Recommended Setup
- **Web Server**: Ubuntu 20.04 LTS or newer
- **Database Server**: Separate PostgreSQL instance (12+)
- **Load Balancer**: Nginx or HAProxy (if multiple API instances)
- **Storage**: Separate volume for database backups
- **Monitoring**: Prometheus + Grafana (optional but recommended)

### 2. PostgreSQL Production Configuration

#### 2.1 Security Hardening

```bash
# Create dedicated database user for API (read-heavy)
sudo -u postgres psql

CREATE USER ncdc_api WITH PASSWORD 'strong_random_password';
CREATE USER ncdc_admin WITH PASSWORD 'another_strong_password';

-- Grant read-only permissions to API user
GRANT CONNECT ON DATABASE ncdc_greengrid TO ncdc_api;
GRANT USAGE ON SCHEMA pa TO ncdc_api;
GRANT SELECT ON ALL TABLES IN SCHEMA pa TO ncdc_api;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA pa TO ncdc_api;

-- Grant admin permissions (for maintenance)
GRANT ALL PRIVILEGES ON DATABASE ncdc_greengrid TO ncdc_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA pa TO ncdc_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA pa TO ncdc_admin;

-- Prevent public access
REVOKE ALL ON DATABASE ncdc_greengrid FROM PUBLIC;
REVOKE ALL ON SCHEMA pa FROM PUBLIC;

\q
```

#### 2.2 PostgreSQL Configuration (`postgresql.conf`)

```ini
# Performance tuning for production
max_connections = 200
shared_buffers = 256MB          # 25% of system RAM for typical servers
effective_cache_size = 1GB      # 50-75% of system RAM
work_mem = 16MB                 # RAM available per operation
maintenance_work_mem = 64MB

# Logging
log_statement = 'all'           # Log all statements (review logs regularly)
log_duration = on               # Log query duration
log_min_duration_statement = 1000  # Log slow queries (> 1 second)
log_directory = '/var/log/postgresql'

# SSL/TLS
ssl = on
ssl_cert_file = '/etc/postgresql/server.crt'
ssl_key_file = '/etc/postgresql/server.key'

# Connection limits
max_idle_in_transaction_session_timeout = 600000  # 10 minutes
statement_timeout = 300000                        # 5 minutes
```

#### 2.3 PostgreSQL Backup Strategy

```bash
# Create backup directory
sudo mkdir -p /var/backups/postgresql
sudo chown postgres:postgres /var/backups/postgresql
sudo chmod 700 /var/backups/postgresql

# Daily backup script (/usr/local/bin/pg-backup.sh)
#!/bin/bash
BACKUP_DIR="/var/backups/postgresql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATABASE="ncdc_greengrid"

pg_dump -U ncdc_admin -d $DATABASE | gzip > $BACKUP_DIR/ncdc_greengrid_$TIMESTAMP.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "ncdc_greengrid_*.sql.gz" -mtime +30 -delete

# Add to crontab for daily execution
# 0 2 * * * /usr/local/bin/pg-backup.sh
```

### 3. Flask API Production Deployment

#### 3.1 Production Requirements File

```bash
# Ensure wsgi server is in requirements
pip install gunicorn
```

Update `api/requirements.txt`:
```
flask>=2.3.0
psycopg2-binary>=2.9.0
requests>=2.31.0
flask-cors>=4.0.0
python-dotenv>=1.0.0
werkzeug>=2.3.0
gunicorn>=21.0.0
```

#### 3.2 Systemd Service File

Create `/etc/systemd/system/ncdc-api.service`:

```ini
[Unit]
Description=NCDC Tree Inventory API
After=network.target postgresql.service

[Service]
Type=notify
User=ncdc
WorkingDirectory=/opt/ncdc-tree-inventory/api
ExecStart=/opt/ncdc-tree-inventory/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --bind 127.0.0.1:5000 \
    --access-logfile /var/log/ncdc-api/access.log \
    --error-logfile /var/log/ncdc-api/error.log \
    api:app

Restart=on-failure
RestartSec=10
Environment="PATH=/opt/ncdc-tree-inventory/venv/bin"
EnvironmentFile=/etc/ncdc/api.env

[Install]
WantedBy=multi-user.target
```

#### 3.3 Production Environment File

Create `/etc/ncdc/api.env`:
```bash
DB_NAME=ncdc_greengrid
DB_USER=ncdc_api
DB_PASSWORD=<STRONG_PASSWORD>
DB_HOST=<DATABASE_SERVER_IP>
DB_PORT=5432
FLASK_ENV=production
API_CORS_ORIGINS=https://your-domain.com
SECRET_KEY=<STRONG_RANDOM_KEY>
```

#### 3.4 Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable ncdc-api
sudo systemctl start ncdc-api
sudo systemctl status ncdc-api
```

### 4. Nginx Reverse Proxy Configuration

Create `/etc/nginx/sites-available/ncdc-api`:

```nginx
upstream ncdc_api {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;  # Force HTTPS
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    client_max_body_size 50M;

    location /api/ {
        proxy_pass http://ncdc_api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location / {
        root /opt/ncdc-web/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/ncdc-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. ETL Scheduled Execution

Create cron job for periodic data updates:

```bash
# Edit crontab
sudo crontab -e

# Schedule ETL to run daily at 2 AM
0 2 * * * cd /opt/ncdc-tree-inventory/greengrid_etl && /opt/ncdc-tree-inventory/venv/bin/python main.py >> /var/log/ncdc-etl/execution.log 2>&1
```

Create log directory:
```bash
sudo mkdir -p /var/log/ncdc-etl
sudo chown root:root /var/log/ncdc-etl
sudo chmod 755 /var/log/ncdc-etl
```

### 6. Web Application Deployment

#### 6.1 Build Frontend

```bash
cd greengrid_web
npm install
npm run build
# Output goes to dist/ directory
```

#### 6.2 Configure Web Server

Update `greengrid_web/config/api.config.js`:
```javascript
export const API_BASE_URL = 'https://your-domain.com/api';
export const MAP_TILES = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
```

#### 6.3 Serve from Nginx

See Nginx configuration above - `/` location serves static files from `/opt/ncdc-web/dist`

## Security Hardening

### 1. Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS only
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. SSL/TLS Certificates

```bash
# Use Let's Encrypt with Certbot
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
```

### 3. Remove Sensitive Files from Version Control

Ensure `.gitignore` contains:
```
.env
.env.local
.env.*.local
*.key
*.crt
.DS_Store
__pycache__/
*.pyc
node_modules/
dist/
venv/
uploaded_images/
```

### 4. API Security Hardening

Update `api.py`:
```python
from flask import Flask, request
from werkzeug.security import generate_password_hash

# Add rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Add request validation
@app.before_request
def validate_request():
    if request.method == 'POST' or request.method == 'PUT':
        if request.is_json is False:
            return {"error": "Content-Type must be application/json"}, 400
```

## Monitoring & Logging

### 1. Application Logging

Configure centralized logging:

```python
# In api.py
import logging
from logging.handlers import RotatingFileHandler

log_handler = RotatingFileHandler(
    '/var/log/ncdc-api/application.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
log_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(log_handler)
```

### 2. Database Monitoring

```sql
-- Monitor slow queries
SELECT query, calls, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Monitor table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 3. Health Check Endpoint

Add to `api.py`:
```python
@app.route('/health', methods=['GET'])
def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500
```

## Performance Optimization

### 1. Database Query Optimization

Add indexes for common queries:
```sql
CREATE INDEX idx_trees_freguesia ON pa.trees(freguesia);
CREATE INDEX idx_trees_especie ON pa.trees(especie);
CREATE INDEX idx_trees_geometry ON pa.trees USING gist(geometry);
CREATE INDEX idx_maintenance_tree_id ON pa.maintenance(tree_id);
```

### 2. API Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedResponse:
    def __init__(self, ttl_minutes=5):
        self.ttl = timedelta(minutes=ttl_minutes)
        self.cache = {}
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())
```

### 3. Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

## Disaster Recovery

### 1. Backup Verification

```bash
# Test backup restoration monthly
sudo -u postgres psql -d test_restore -f /var/backups/postgresql/latest_backup.sql
psql -U ncdc_admin -d test_restore -c "SELECT COUNT(*) FROM pa.trees;"
```

### 2. Database Replication (Optional)

For high-availability PostgreSQL:
```bash
# Configure streaming replication
# Edit postgresql.conf on primary:
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3
```

### 3. Runbook Documentation

Document procedures for:
- Database failover
- API restart procedures
- Web application rollback
- Data recovery from backups

## Post-Deployment Testing

1. **Load Testing**:
   ```bash
   # Using Apache Bench
   ab -n 1000 -c 10 https://your-domain.com/api/trees
   ```

2. **Security Testing**:
   ```bash
   # OWASP ZAP scanning
   # SSL Labs test: https://www.ssllabs.com/ssltest/
   ```

3. **Uptime Monitoring**:
   - Set up monitoring with Uptime Robot or similar
   - Test health check endpoint regularly
   - Monitor database performance

## Maintenance Schedule

| Task | Frequency |
|------|-----------|
| Database backups | Daily |
| Backup verification | Weekly |
| Security updates | As released |
| PostgreSQL maintenance (VACUUM, ANALYZE) | Weekly |
| Log rotation | Daily |
| Performance monitoring review | Weekly |
| SSL certificate renewal | 30 days before expiry |

## Support & Documentation

- API Documentation: See `api/README.md`
- Database Schema: See `greengrid_db/README.md`
- ETL Documentation: See `greengrid_etl/README.md`
- Emergency contacts: [Document in separate file]

---

**Last Updated**: 2026-06-20
**Version**: 1.0
