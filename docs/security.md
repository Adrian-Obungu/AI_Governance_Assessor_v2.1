# Security Guide

## Overview

The AI Governance Assessor implements multiple layers of security to protect user data and ensure system integrity.

## Authentication & Authorization

### Password Security
- **Bcrypt Hashing**: All passwords are hashed using bcrypt with configurable rounds (default: 12)
- **Minimum Length**: Passwords must be at least 8 characters
- **No Plain Text Storage**: Passwords are never stored in plain text

### JWT Tokens
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: Configurable (default: 30 minutes)
- **Secret Key**: Must be changed in production (set via `SECRET_KEY` environment variable)

### Account Protection
- **Failed Login Tracking**: All failed login attempts are logged with timestamps and IP addresses
- **Account Lockout**: Accounts are locked after configurable failed attempts (default: 5)
- **Lockout Duration**: Configurable lockout period (default: 15 minutes)
- **Automatic Unlock**: Accounts automatically unlock after the lockout period expires

### Password Reset
- **Single-Use Tokens**: Reset tokens can only be used once
- **Time-Limited**: Tokens expire after 1 hour
- **Secure Generation**: Tokens are generated using cryptographically secure random functions
- **Email Verification**: Reset links are sent to verified email addresses only

## API Security

### Rate Limiting
- **Per-IP Limiting**: 60 requests per minute per IP address
- **Automatic Blocking**: Exceeding limits results in 429 Too Many Requests
- **Configurable**: Adjust via `RATE_LIMIT_PER_MINUTE` environment variable

### CORS Configuration
- **Whitelist Origins**: Only configured origins are allowed
- **Credentials Support**: Allows credentials for authenticated requests
- **Configurable**: Set via `CORS_ORIGINS` environment variable (comma-separated)

### Input Validation
- **Pydantic Models**: All inputs are validated using Pydantic schemas
- **Type Checking**: Strict type validation for all fields
- **Length Limits**: Maximum lengths enforced on string fields
- **Email Validation**: Email addresses are validated for correct format

## Data Security

### Database
- **SQLite**: Local database with file-based storage
- **Migrations**: Schema changes managed through Alembic
- **Backups**: Regular backups recommended (see runbook.md)

### Sensitive Data
- **Environment Variables**: All secrets stored in environment variables
- **No Hardcoding**: No secrets in source code
- **.env.example**: Template provided without real secrets
- **.gitignore**: Ensures .env files are not committed

### Assessment Data
- **User Isolation**: Users can only access their own assessments
- **Authorization Checks**: All endpoints verify user ownership
- **Versioned Results**: Assessment results are versioned and immutable

## Deployment Security

### Environment Variables
Required security-related environment variables:

```bash
# CRITICAL: Change in production
SECRET_KEY=your-secret-key-here-change-in-production

# Password hashing
BCRYPT_ROUNDS=12

# Account lockout
MAX_FAILED_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# Rate limiting
RATE_LIMIT_PER_MINUTE=60

# CORS
CORS_ORIGINS=https://your-frontend-domain.com
```

### Docker Security
- **Non-Root User**: Consider running containers as non-root user
- **Network Isolation**: Services communicate via internal network
- **Volume Permissions**: Ensure proper file permissions on volumes
- **Image Scanning**: Scan images for vulnerabilities before deployment

### HTTPS/TLS
- **Production Requirement**: Always use HTTPS in production
- **Reverse Proxy**: Use nginx or similar with TLS termination
- **Certificate Management**: Use Let's Encrypt or similar for certificates

## Security Best Practices

### For Administrators
1. **Change Default Secrets**: Update `SECRET_KEY` before deployment
2. **Regular Updates**: Keep dependencies updated
3. **Monitor Logs**: Review logs for suspicious activity
4. **Backup Data**: Regular database backups
5. **Limit Access**: Restrict database and server access

### For Developers
1. **Code Review**: Review all code changes for security issues
2. **Dependency Scanning**: Use tools like `safety` to scan dependencies
3. **No Secrets in Code**: Never commit secrets to version control
4. **Input Validation**: Always validate and sanitize user inputs
5. **Error Handling**: Don't expose sensitive information in error messages

## Incident Response

### Failed Login Attempts
- Monitor `failed_logins` table for patterns
- Investigate repeated failures from same IP
- Consider IP blocking for persistent attacks

### Data Breach
1. Immediately rotate `SECRET_KEY`
2. Force password reset for all users
3. Review access logs
4. Notify affected users
5. Document incident

### Vulnerability Discovery
1. Assess severity and impact
2. Develop and test patch
3. Deploy fix as soon as possible
4. Document vulnerability and fix
5. Consider disclosure timeline

## Compliance Considerations

### Data Privacy
- **GDPR**: Implement data deletion on request
- **Data Minimization**: Collect only necessary data
- **Consent**: Obtain user consent for data processing
- **Transparency**: Provide clear privacy policy

### Audit Trail
- **Request Logging**: All API requests are logged
- **Security Events**: Failed logins and lockouts are logged
- **Assessment History**: All assessment changes are tracked
- **Retention**: Configure log retention policies

## Security Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong, random value
- [ ] Configure CORS to only allow your frontend domain
- [ ] Enable HTTPS/TLS
- [ ] Set up regular database backups
- [ ] Configure monitoring and alerting
- [ ] Review and adjust rate limits
- [ ] Scan Docker images for vulnerabilities
- [ ] Set up log aggregation and monitoring
- [ ] Document incident response procedures
- [ ] Conduct security testing (penetration testing, vulnerability scanning)
