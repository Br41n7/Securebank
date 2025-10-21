# Deployment Guide - SecureBank

This guide covers deploying SecureBank to production environments.

## 🚀 Quick Deploy to Render

### Prerequisites
- GitHub account
- Render account
- Paystack account (for payments)

### Step 1: Prepare Repository
1. Push your code to GitHub
2. Ensure all environment variables are set in `.env.example`

### Step 2: Create Render Web Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: securebank
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn securebank.wsgi:application`
   - **Instance Type**: Free (to start)

### Step 3: Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. **Name**: securebank-db
3. **Database Name**: securebank
4. **User**: securebank

### Step 4: Configure Environment Variables
Add these environment variables in Render:

```env
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=postgresql://securebank:password@host:5432/securebank

# Paystack (get from Paystack dashboard)
PAYSTACK_PUBLIC_KEY=pk_test_xxxx
PAYSTACK_SECRET_KEY=sk_test_xxxx

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Access your app at `https://securebank.onrender.com`

### Step 6: Post-Deployment Setup
1. Create superuser:
   ```bash
   # Connect to service shell in Render dashboard
   python manage.py createsuperuser
   ```
2. Configure Paystack webhooks in Paystack dashboard
3. Set up custom domain (optional)

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "securebank.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:password@db:5432/securebank
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=securebank
      - POSTGRES_USER=securebank
      - POSTGRES_PASSWORD=your-password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Deploy with Docker
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## 🖥️ Manual Server Deployment

### System Requirements
- Ubuntu 20.04+ or CentOS 8+
- Python 3.11+
- PostgreSQL 13+
- Nginx
- SSL certificate

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3-pip postgresql nginx -y

# Create project user
sudo useradd -m -s /bin/bash securebank
sudo usermod -aG sudo securebank
```

### Step 2: Application Setup
```bash
# Switch to project user
sudo su - securebank

# Clone repository
git clone <your-repo-url> securebank
cd securebank

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Environment configuration
cp .env.example .env
nano .env  # Edit with your values
```

### Step 3: Database Setup
```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createdb securebank
createuser securebank
psql -c "ALTER USER securebank PASSWORD 'your-password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE securebank TO securebank;"

exit

# Run migrations
cd /home/securebank/securebank
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### Step 4: Gunicorn Service
Create `/etc/systemd/system/securebank.service`:
```ini
[Unit]
Description=SecureBank Django Application
After=network.target

[Service]
User=securebank
Group=securebank
WorkingDirectory=/home/securebank/securebank
Environment="PATH=/home/securebank/securebank/venv/bin"
ExecStart=/home/securebank/securebank/venv/bin/gunicorn securebank.wsgi:application --workers 3 --bind unix:/run/securebank.sock

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable securebank
sudo systemctl start securebank
```

### Step 5: Nginx Configuration
Create `/etc/nginx/sites-available/securebank`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/securebank/securebank;
    }

    location /media/ {
        root /home/securebank/securebank;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/securebank.sock;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/securebank /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: SSL Certificate
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔒 Security Considerations

### Production Security Checklist
- [ ] Set strong SECRET_KEY
- [ ] Disable DEBUG mode
- [ ] Configure ALLOWED_HOSTS
- [ ] Use HTTPS everywhere
- [ ] Set up firewall
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitoring and logging
- [ ] Rate limiting
- [ ] Input validation

### Firewall Setup
```bash
# UFW firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Database Security
```bash
# PostgreSQL security
sudo nano /etc/postgresql/13/main/postgresql.conf
# Set: listen_addresses = 'localhost'

sudo nano /etc/postgresql/13/main/pg_hba.conf
# Require password for all connections
```

## 📊 Monitoring

### Application Monitoring
- Use Sentry for error tracking
- Set up logs with Papertrail or similar
- Monitor server resources with New Relic or DataDog

### Database Monitoring
- Monitor query performance
- Set up connection pooling
- Regular backups

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Render
      uses: johnbeynon/render-deploy-action@v0.0.8
      with:
        service-id: ${{ secrets.RENDER_SERVICE_ID }}
        api-key: ${{ secrets.RENDER_API_KEY }}
```

## 🚨 Troubleshooting

### Common Issues

1. **Static files not loading**
   - Run `python manage.py collectstatic --noinput`
   - Check Nginx configuration

2. **Database connection errors**
   - Verify DATABASE_URL
   - Check PostgreSQL status

3. **502 Bad Gateway**
   - Check Gunicorn service status
   - Review application logs

4. **Permission errors**
   - Check file permissions
   - Verify user ownership

### Logs
```bash
# Application logs
sudo journalctl -u securebank

# Nginx logs
sudo tail -f /var/log/nginx/error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

## 📞 Support

For deployment issues:
- Check the [GitHub Issues](#)
- Email: iyanuolalegan@gmail.com
- Documentation: [Wiki](#)