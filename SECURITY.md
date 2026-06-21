# NCDC Tree Inventory - Security Guide

## Overview

This guide covers security best practices for the NCDC Tree Inventory system in development and production environments.

---

## 1. Authentication & Authorization

### Current State (Development)
- No authentication required currently
- All endpoints are publicly accessible

### Production Requirements

#### 1.1 Implement JWT Authentication

Add JWT token-based authentication to protect endpoints in production.

#### 1.2 Role-Based Access Control (RBAC)

Implement role-based access with ADMIN, EDITOR, and VIEWER roles.

---

## 2. Data Protection

### 2.1 Encryption

**In Transit:**
- Always use HTTPS in production
- Minimum TLS 1.2
- Strong cipher suites only

**At Rest:**
- Encrypt sensitive database columns
- Use industry-standard encryption algorithms

### 2.2 Database Security

**User Permissions:**
```sql
-- API user: read-only
CREATE USER ncdc_api WITH PASSWORD 'strong_password';
GRANT SELECT ON ALL TABLES IN SCHEMA pa TO ncdc_api;

-- Admin user: full access
CREATE USER ncdc_admin WITH PASSWORD 'another_strong_password';
GRANT ALL PRIVILEGES ON DATABASE ncdc_greengrid TO ncdc_admin;
```

---

## 3. Input Validation & Sanitization

### 3.1 SQL Injection Prevention

✓ **Already implemented** - Using parameterized queries

### 3.2 File Upload Security

- Validate file types (MIME type checking)
- Enforce file size limits (5MB default)
- Store uploads outside web root
- Use secure_filename for validation

### 3.3 Request Validation

Validate all inputs against expected schema and data types.

---

## 4. API Security

### 4.1 Rate Limiting

Implement rate limiting to prevent abuse:
- 200 requests per day per IP
- 50 requests per hour per IP

### 4.2 CORS Configuration

Restrict CORS to specific origins in production.

### 4.3 Security Headers

Configure security headers in responses:
- Strict-Transport-Security
- X-Content-Type-Options
- X-Frame-Options
- Content-Security-Policy

---

## 5. Environment Security

### 5.1 Environment Variables

✓ **Already implemented** - Using .env files (excluded from git)

Never commit to git:
- .env files
- Private keys
- Certificates
- API credentials

### 5.2 Secrets Management

For production, use proper secrets management:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault

---

## 6. Logging & Monitoring

### 6.1 Security Logging

- Log all authentication attempts
- Log failed database operations
- Log admin actions
- Preserve logs for forensics

### 6.2 Failed Login Attempts

Implement lockout after 5 failed attempts in 15 minutes.

---

## 7. Database Security

### 7.1 Regular Backups

- Daily automated backups
- Monthly backup restoration tests
- Off-site backup storage

### 7.2 Connection Security

- SSL/TLS for database connections
- IP whitelisting when possible
- Non-standard ports

---

## 8. Infrastructure Security

### 8.1 Firewall Rules

- Allow SSH (22), HTTP (80), HTTPS (443) only
- Restrict PostgreSQL access to API servers

### 8.2 SSH Hardening

- Use key-based authentication only
- Disable root login
- Non-standard port (optional)
- Automatic logout after idle time

### 8.3 System Updates

- Enable automatic security updates
- Regular OS patching
- Dependency updates

---

## 9. Vulnerability Scanning

### 9.1 Dependency Audit

```bash
pip-audit
npm audit
```

### 9.2 OWASP Scanning

Run OWASP ZAP regularly against production.

### 9.3 Static Code Analysis

```bash
bandit -r api/
```

---

## 10. Incident Response

### 10.1 Security Incident Plan

1. Detect - Monitor logs and alerts
2. Contain - Isolate affected systems
3. Eradicate - Remove the threat
4. Recover - Restore operations
5. Learn - Post-incident review

### 10.2 Emergency Contacts

Document and maintain contact list for:
- Security team lead
- Database administrator
- System administrator
- Incident response team

---

## 11. Compliance

### 11.1 GDPR Compliance (if applicable)

- Obtain user consent for data collection
- Implement data export functionality
- Implement data deletion ("right to be forgotten")
- Document data processing

---

## 12. Security Checklist

- [ ] HTTPS/SSL enabled
- [ ] JWT authentication implemented
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] CORS properly configured
- [ ] Security headers configured
- [ ] Logging and monitoring active
- [ ] Database backups verified
- [ ] Firewall configured
- [ ] SSH hardening applied
- [ ] Dependency vulnerabilities scanned
- [ ] Code security analysis completed
- [ ] Incident response plan documented

---

**Last Updated**: 2026-06-20
**Version**: 1.0
