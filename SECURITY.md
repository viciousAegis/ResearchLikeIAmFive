# 🔒 Security Guide & Deployment Checklist

## 🚨 Critical Security Measures Implemented

### ✅ Backend Security Features

#### **1. Authentication & Authorization**
- API key validation system (optional, configurable)
- Rate limiting (10 requests/minute by default)
- Request size limits (1MB max)
- Environment-based configuration

#### **2. Input Validation & Sanitization**
- Strict arXiv URL validation with regex patterns
- URL length limits (2KB max)
- Explanation style validation
- JSON response validation

#### **3. CORS & Network Security**
- Restrictive CORS policy (no wildcard origins in production)
- Trusted host middleware for production
- Security headers (CSP, HSTS, XSS protection, etc.)
- No credentials allowed in CORS

#### **4. Resource Protection**
- PDF file size limits (50MB max)
- Text extraction limits (500KB max)
- Page count limits (100 pages max)
- Automatic temporary file cleanup

#### **5. Error Handling & Logging**
- Comprehensive security event logging
- No sensitive data in error messages
- Rate limit violation logging
- Client IP tracking for security events

#### **6. Production Hardening**
- API documentation disabled in production
- Environment-based security configuration
- Secure headers middleware
- Request timeout enforcement

### ✅ Frontend Security Features

#### **1. Input Validation**
- Client-side arXiv URL validation
- Input sanitization to prevent XSS
- Explanation style validation

#### **2. API Communication**
- Request timeouts (60 seconds)
- No credentials sent with requests
- Comprehensive error handling
- Response validation

#### **3. Error Handling**
- Safe error message display
- No sensitive data exposure
- User-friendly error messages

## 🚀 Deployment Checklist

### **Pre-Deployment Security Steps**

#### **1. Environment Variables** ⚠️ CRITICAL
```bash
# Backend .env file
GOOGLE_API_KEY=your_actual_api_key_here
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
RATE_LIMIT_REQUESTS=10
API_KEY_REQUIRED=false
```

#### **2. Frontend Environment**
```bash
# Frontend .env file
VITE_API_URL=https://your-api-domain.com
```

#### **3. Git Security**
```bash
# Remove sensitive data from git history if needed
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch backend/.env' \
--prune-empty --tag-name-filter cat -- --all
```

### **Deployment Options**

#### **Option 1: Traditional VPS/Server Deployment**

**Backend Deployment:**
```bash
# Install dependencies
cd backend
uv install

# Set environment variables
export GOOGLE_API_KEY="your_key_here"
export ENVIRONMENT="production"
export ALLOWED_ORIGINS="https://yourdomain.com"

# Run with production settings
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend Deployment:**
```bash
# Build for production
cd frontend
npm install
npm run build

# Serve with nginx, Apache, or any static file server
# Point to the dist/ directory
```

#### **Option 2: Cloud Platform Deployment**

**Render.com:**
- Backend: Python service with `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Frontend: Static site pointing to `dist` folder
- Environment variables in dashboard

**Vercel:**
- Frontend: Connect GitHub repo, auto-deploy
- Backend: Deploy as Vercel Functions or separate service

**Heroku:**
- Create `Procfile`: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
- Set environment variables in dashboard

### **Production Security Configuration**

#### **1. Web Server Configuration (Nginx)**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    
    location / {
        # Frontend static files
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        # Backend API
        limit_req zone=api burst=5 nodelay;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### **2. Firewall Configuration**
```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### **Monitoring & Alerts**

#### **1. Log Monitoring**
- Monitor security events in application logs
- Set up alerts for rate limit violations
- Track failed API key attempts

#### **2. Performance Monitoring**
- Monitor API response times
- Track memory usage for PDF processing
- Set up alerts for high resource usage

#### **3. Security Monitoring**
- Monitor for unusual traffic patterns
- Track error rates
- Set up alerts for repeated failed requests

### **Maintenance Tasks**

#### **Weekly:**
- Review security logs
- Check for dependency updates
- Monitor resource usage

#### **Monthly:**
- Update dependencies
- Review and rotate API keys
- Check SSL certificate expiration

#### **Quarterly:**
- Security audit
- Penetration testing
- Review and update security policies

## 🔧 Additional Security Recommendations

### **1. Enhanced Security (Optional)**
- Enable API key authentication in production
- Add Redis for distributed rate limiting
- Implement request signing
- Add input content filtering

### **2. Infrastructure Security**
- Use HTTPS everywhere
- Implement proper SSL/TLS configuration
- Use a Web Application Firewall (WAF)
- Regular security updates

### **3. Compliance**
- GDPR compliance (no personal data stored)
- Data retention policies
- Privacy policy for your application
- Terms of service

## 🚫 Security Don'ts

❌ Never commit API keys to git  
❌ Don't use wildcard CORS origins in production  
❌ Don't expose detailed error messages to users  
❌ Don't run as root user  
❌ Don't disable HTTPS in production  
❌ Don't skip input validation  
❌ Don't ignore security updates  

## 📞 Emergency Response

If you suspect a security breach:
1. **Immediately** revoke and regenerate API keys
2. Check logs for suspicious activity
3. Update and restart services
4. Monitor for ongoing attacks
5. Consider temporarily disabling the service

---

**Remember**: Security is an ongoing process, not a one-time setup. Regularly review and update your security measures!
