# Soccer Scout AI - Security Guide

## 🔒 Security Overview

This guide outlines the security measures implemented in the Soccer Scout AI system and provides best practices for maintaining a secure production environment.

## 🛡️ Security Architecture

### Defense in Depth Strategy
```
┌─────────────────────────────────────────────────────────┐
│                    CDN/Proxy Layer                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Application Security              │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │            API Security                │   │   │
│  │  │  ┌─────────────────────────────────┐   │   │   │
│  │  │  │        Data Security           │   │   │   │
│  │  │  └─────────────────────────────────┘   │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 🌐 Frontend Security (Next.js)

### Security Headers
```typescript
// Implemented in next.config.ts
{
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY", 
  "X-XSS-Protection": "1; mode=block",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}
```

### Content Security Policy (CSP)
```
default-src 'self';
script-src 'self' 'unsafe-inline';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
connect-src 'self' https:;
font-src 'self' https:;
object-src 'none';
media-src 'self';
frame-src 'none';
```

### Client-Side Security
- **Input Sanitization**: All user inputs are validated and sanitized
- **XSS Prevention**: React's built-in XSS protection + CSP
- **CSRF Protection**: SameSite cookies and CSRF tokens
- **Secure Storage**: No sensitive data stored in localStorage

## 🔧 Backend Security (Flask)

### Production Middleware
Located in `production_middleware.py`:

#### Rate Limiting
```python
# Per-IP rate limits
RATE_LIMITS = {
    "requests_per_minute": 60,    # Production: 60/min
    "requests_per_hour": 500      # Production: 500/hour
}
```

#### Request Validation
- **JSON Schema Validation**: All API requests validated
- **Content-Type Enforcement**: Only `application/json` accepted
- **Payload Size Limits**: Maximum 1MB request size
- **Query Length Limits**: Maximum 500 characters

#### Security Headers
```python
response.headers.update({
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
})
```

### API Security

#### Authentication & Authorization
- **API Key Protection**: OpenAI keys secured in environment variables
- **CORS Configuration**: Strict origin control
- **Endpoint Protection**: Debug endpoints disabled in production

#### Input Validation
```python
def validate_query_request(data):
    # Validate request structure
    # Check required fields
    # Sanitize input data
    # Prevent injection attacks
```

## 🔐 Environment Security

### Environment Variables
```bash
# Critical secrets (never commit to repo)
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Configuration
FLASK_ENV=production
NODE_ENV=production
CORS_ORIGINS=https://your-domain.com
```

### Secrets Management
- **Environment Variables**: All secrets stored as env vars
- **No Hardcoded Secrets**: Zero secrets in source code
- **Platform-Specific**: Use platform secret managers:
  - Vercel: Environment Variables
  - Railway: Environment Variables
  - Render: Environment Variables
  - Docker: Secrets or env files

## 🛠️ Infrastructure Security

### Container Security (Docker)
```dockerfile
# Non-root user
RUN useradd --create-home --shell /bin/bash --user-group soccer
USER soccer

# Minimal base image
FROM python:3.11-slim

# Security updates
RUN apt-get update && apt-get upgrade -y
```

### Network Security
- **HTTPS Only**: All production traffic encrypted
- **Secure Protocols**: TLS 1.2+ required
- **Port Restrictions**: Only necessary ports exposed

## 🔍 Monitoring & Logging

### Security Logging
```python
# Request logging with security context
logger.info(f"REQUEST: {method} {path} - IP: {client_ip}")
logger.warning(f"RATE_LIMIT: Client {client_ip} exceeded limit")
logger.error(f"SECURITY: Invalid request from {client_ip}")
```

### Health Monitoring
- **Health Checks**: `/api/health` endpoint
- **Error Tracking**: Comprehensive error logging
- **Performance Monitoring**: Request timing and metrics

## ⚠️ Security Best Practices

### Development
1. **Never commit secrets** to version control
2. **Use environment variables** for all configuration
3. **Validate all inputs** on both client and server
4. **Keep dependencies updated** regularly
5. **Use HTTPS** for all external communication

### Production
1. **Enable all security headers** in production
2. **Configure strict CORS** policies
3. **Use strong rate limiting** to prevent abuse
4. **Monitor logs** for security events
5. **Regular security audits** and updates

### API Key Security
1. **Rotate keys regularly** (monthly recommended)
2. **Use separate keys** for different environments
3. **Monitor API usage** for anomalies
4. **Set usage limits** on OpenAI dashboard
5. **Never expose keys** in client-side code

## 🚨 Incident Response

### Security Incident Checklist
1. **Identify the threat** and scope of impact
2. **Isolate affected systems** if necessary
3. **Preserve evidence** for investigation
4. **Notify stakeholders** according to policy
5. **Implement immediate fixes** to stop the incident
6. **Document the incident** and lessons learned
7. **Update security measures** to prevent recurrence

### Emergency Procedures
```bash
# Immediately rotate compromised API key
# 1. Generate new OpenAI API key
# 2. Update environment variables
# 3. Restart all services
railway restart
vercel redeploy

# Check for unauthorized access
grep "401\|403\|429" logs/app.log
```

## 🔧 Security Testing

### Automated Security Testing
```bash
# Dependency vulnerability scanning
npm audit                    # Frontend
pip-audit                   # Backend

# Security headers testing
curl -I https://your-app.com | grep -i security

# Rate limiting testing
for i in {1..100}; do curl https://your-api.com/api/health; done
```

### Manual Security Testing
1. **Input Validation**: Test with malicious inputs
2. **Authentication**: Test unauthorized access attempts
3. **Rate Limiting**: Verify limits are enforced
4. **CORS**: Test cross-origin requests
5. **Headers**: Verify all security headers present

## 📚 Security Resources

### Tools & Services
- **OWASP ZAP**: Web application security scanner
- **Snyk**: Dependency vulnerability scanning
- **Security Headers**: Test your security headers
- **SSL Labs**: SSL/TLS configuration testing

### Documentation
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Next.js Security](https://nextjs.org/docs/advanced-features/security-headers)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)
- [OpenAI Security Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)

## 🔒 Compliance Considerations

### Data Privacy
- **No PII Storage**: No personal information stored
- **Data Minimization**: Only necessary data processed
- **Anonymization**: All queries are anonymized
- **Retention Policies**: Log rotation and cleanup

### Regional Compliance
- **GDPR**: European data protection compliance
- **CCPA**: California privacy law compliance
- **SOX**: Financial compliance if applicable
- **HIPAA**: Healthcare compliance if handling health data

## ✅ Security Checklist

### Pre-Deployment
- [ ] All secrets stored in environment variables
- [ ] Security headers configured and tested
- [ ] Rate limiting enabled and configured
- [ ] Input validation implemented
- [ ] CORS properly configured
- [ ] Dependencies scanned for vulnerabilities
- [ ] SSL/TLS certificates configured

### Post-Deployment
- [ ] Security headers verified in production
- [ ] Rate limiting tested and working
- [ ] Monitoring and logging configured
- [ ] Incident response plan documented
- [ ] Regular security audits scheduled
- [ ] Team trained on security procedures

---

## 🛡️ Security Statement

The Soccer Scout AI system implements industry-standard security practices including:

- **Multi-layer security architecture**
- **Comprehensive input validation**
- **Production-grade rate limiting**
- **Secure environment management**
- **Continuous monitoring and logging**
- **Regular security updates and audits**

**Your data and queries are processed securely with enterprise-grade protection.**