# NCDC Tree Inventory - Pre-Deployment Checklist

## Code Quality & Version Control

- [ ] All code committed to main branch
- [ ] No hardcoded passwords or credentials in code
- [ ] All `.env.example` files created for configuration reference
- [ ] `.gitignore` properly configured to exclude sensitive files
- [ ] Code reviewed by at least one team member
- [ ] No `console.log()` statements in production code
- [ ] All TODO/FIXME comments addressed or documented
- [ ] API error responses don't leak system information

## Dependencies & Requirements

- [ ] `api/requirements.txt` has version pinned (e.g., `flask==2.3.0`)
- [ ] `greengrid_etl/etl_requirements.txt` has version pinned
- [ ] `package.json` (if using npm) has all dependencies listed
- [ ] Tested with Python 3.8+ compatibility
- [ ] No deprecated dependencies
- [ ] All major dependencies have been tested together
- [ ] Security audit run on dependencies (using `pip-audit` or similar)

## Database Preparation

- [ ] PostgreSQL 12+ installed and running
- [ ] PostGIS extension installed and verified
- [ ] Database schema scripts exist and tested (`00-07-*.sql`)
- [ ] Database user created with appropriate permissions
- [ ] Read-only user created for API connections
- [ ] Admin user created for maintenance operations
- [ ] Backup location determined and configured
- [ ] Database credentials stored in `.env`, not in code
- [ ] Connection string tested with target database
- [ ] Initial data loaded and verified

## ETL Pipeline

- [ ] ETL requirements installed and tested
- [ ] ETL configuration file (config/00.yml) created with correct credentials
- [ ] `.env` created for ETL module
- [ ] ETL runs successfully in test environment
- [ ] ETL logs are generated and viewable
- [ ] ETL can be scheduled via cron or scheduler
- [ ] Data source URL verified and accessible
- [ ] Sample output data reviewed for quality
- [ ] ETL error handling tested with bad data

## API Configuration & Security

- [ ] `api/.env.example` created with all required variables
- [ ] `api/.env` created with production values
- [ ] Database connection pooling configured
- [ ] CORS origins properly set (not `*`)
- [ ] API listens on secure port with HTTPS capability
- [ ] Request validation implemented
- [ ] Error responses are generic (don't leak details)
- [ ] Rate limiting configured (optional but recommended)
- [ ] API endpoints documented
- [ ] SQL injection prevention verified (using parameterized queries)
- [ ] File upload validation implemented
- [ ] Maximum file size limits enforced

## Web Application

- [ ] Frontend environment configuration created (.env or config file)
- [ ] API URL configured to point to correct backend
- [ ] Map tiles URL verified and working
- [ ] All assets optimized (images compressed, CSS/JS minified)
- [ ] No console errors in browser (check all features)
- [ ] Responsive design tested on target devices
- [ ] Loading states and error messages display correctly
- [ ] CORS errors resolved between frontend and API

## Security Hardening

- [ ] SSL/TLS certificates obtained (Let's Encrypt recommended)
- [ ] Private keys not committed to repository
- [ ] Environment-specific configs separated (.env, .env.production)
- [ ] Database passwords at least 12 characters, random
- [ ] API secret key generated (use `openssl rand -hex 32`)
- [ ] Firewall rules configured (allow 22, 80, 443 only)
- [ ] SSH key-based authentication configured
- [ ] Root login disabled on servers
- [ ] Automatic security updates enabled
- [ ] Web server headers configured (CSP, X-Frame-Options, etc.)

## Documentation

- [ ] INSTALLATION.md created and tested
- [ ] DEPLOYMENT.md created with production steps
- [ ] README.md updated with version info
- [ ] API endpoints documented (Swagger/OpenAPI optional)
- [ ] Database schema documented
- [ ] Deployment troubleshooting guide created
- [ ] Emergency contact information documented
- [ ] Runbook for common operations created

## Infrastructure Setup

- [ ] Web server OS selected and provisioned
- [ ] Database server prepared (separate from API if possible)
- [ ] Reverse proxy (Nginx/Apache) configured
- [ ] SSL certificate installed
- [ ] DNS records created and verified
- [ ] Domain name configured and tested
- [ ] Port forwarding configured (if behind NAT)
- [ ] Static IP assigned to servers
- [ ] Backup storage location provisioned

## Testing & Validation

- [ ] Manual end-to-end testing completed
- [ ] All CRUD operations tested on production-like data
- [ ] Search functionality tested (by parish, species, ID)
- [ ] Spatial queries tested (nearby trees)
- [ ] File uploads tested (images for trees)
- [ ] Comments and maintenance records tested
- [ ] Database queries reviewed for performance
- [ ] API response times measured (should be < 500ms)
- [ ] Load testing performed (simulate expected traffic)
- [ ] Failover/recovery tested (database reconnection)

## Monitoring & Logging

- [ ] Application logging configured
- [ ] Log files have rotation configured (don't fill disk)
- [ ] Error logging monitored for issues
- [ ] Database logs reviewed for slow queries
- [ ] Health check endpoint created (`/health`)
- [ ] Uptime monitoring service configured
- [ ] Alert thresholds set for critical metrics
- [ ] Log aggregation considered (ELK, Splunk, etc.)
- [ ] Database connection pool monitoring
- [ ] Disk space monitoring configured

## Backup & Disaster Recovery

- [ ] Database backup script created
- [ ] Backup schedule configured (daily at minimum)
- [ ] Backup location verified (not on same disk)
- [ ] Backup restoration tested monthly
- [ ] Disaster recovery plan documented
- [ ] RTO (Recovery Time Objective) defined
- [ ] RPO (Recovery Point Objective) defined
- [ ] Off-site backup copy available
- [ ] Database consistency checks scheduled (VACUUM, ANALYZE)

## Performance Optimization

- [ ] Database indexes created for common queries
- [ ] Query performance tested and optimized
- [ ] API response caching considered
- [ ] Static file caching headers configured
- [ ] Image compression applied
- [ ] Frontend bundle size analyzed
- [ ] Database connection pooling optimized
- [ ] Server resources (RAM, CPU) appropriately sized

## Post-Deployment

- [ ] Date/time of deployment recorded
- [ ] Deployment notes added to documentation
- [ ] Team notified of deployment
- [ ] Smoke tests performed (basic functionality)
- [ ] Production logs reviewed for errors
- [ ] User feedback collected for first week
- [ ] Performance metrics baseline established
- [ ] Rollback plan documented (just in case)

## Maintenance Schedule

Set reminders for:
- [ ] Weekly: Review error logs and performance metrics
- [ ] Monthly: Test backup restoration
- [ ] Quarterly: Security update review
- [ ] Yearly: Disaster recovery drill

---

**Deployment Date**: __________
**Deployed By**: __________
**Version**: __________

**Post-Deployment Verification Date**: __________
**Verified By**: __________

---

## Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| System Administrator | | | |
| Database Administrator | | | |
| Development Lead | | | |
| Infrastructure Lead | | | |

## Rollback Procedure

If critical issues occur after deployment:

1. Document the issue and time
2. Review recent logs for errors
3. Check database connectivity
4. For code issues: Revert to previous version
   ```bash
   git revert <commit_hash>
   systemctl restart ncdc-api
   ```
5. For database issues: Restore from latest good backup
6. Notify team and stakeholders
7. Post-mortem after 24 hours

---

**Last Updated**: 2026-06-20
