# DevOps Portfolio Web

Professional portfolio web application with CI/CD pipeline, automated deployment and real-time monitoring.

![Build Status](https://github.com/nw4f2t4gqz-commits/devops-web/actions/workflows/docker-publish.yml/badge.svg)

## 🚀 Features

- **Portfolio & Contact Form** - Showcase skills and projects
- **LinkedIn Articles** - Published technical articles (Czech and English)
- **Real-time Deploy Status** - Live GitHub Actions workflow visualization
- **Admin Panel** - Lead management and traffic statistics
- **Automated Deployment** - CI/CD pipeline with GitHub Actions
- **SSL Certificates** - Automatic Let's Encrypt configuration
- **Multi-language** - Czech and English

## 🛠 Tech Stack

### Backend
- **Python 3.11** - Flask framework
- **SQLAlchemy** - Database ORM
- **Gunicorn** - WSGI server
- **SQLite** - Database

### Frontend
- **Tailwind CSS** - Styling
- **Vanilla JavaScript** - Interactivity
- **Anime.js** - Animations

### DevOps
- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD pipeline
- **GitHub Container Registry** - Docker image storage
- **Nginx Proxy Manager** - Reverse proxy and SSL
- **VPS Deployment** - Production deployment

## 📦 Project Structure

```
devops-web/
├── app.py                      # Main Flask application
├── models.py                   # SQLAlchemy models
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image configuration
├── docker-compose.yml          # Local development
├── docker-compose.prod.yml     # Production deployment
├── templates/                  # HTML templates
│   ├── index.html             # Homepage
│   ├── articles.html          # LinkedIn articles
│   ├── deploy.html            # Deploy monitoring
│   └── admin_*.html           # Admin panel
├── static/                     # Static files
│   ├── js/                    # JavaScript
│   └── images/                # Images
├── scripts/                    # Helper scripts
│   └── configure_nginx_proxy.sh
└── .github/workflows/         # CI/CD configuration
```

## 🏃 Quick Start

### Lokální Vývoj

1. **Clone Repository**
   ```bash
   git clone https://github.com/nw4f2t4gqz-commits/devops-web.git
   cd devops-web
   ```

2. **Create .env File**
   ```bash
   SECRET_KEY=your-secret-key-here
   ADMIN_USER=admin
   ADMIN_PASSWORD=your-password
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

3. **Run with Docker**
   ```bash
   docker-compose up -d
   ```

4. **Access Application**
   - Web: http://localhost:8000
   - Nginx Admin: http://localhost:81

### Manual Run (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Application runs on http://localhost:5001

## 🚢 Deployment

### GitHub Actions CI/CD

Automatic deployment triggers on push to `main` branch:

1. **Build & Push** - Multi-arch Docker image (amd64/arm64)
2. **Deploy** - SSH deployment to VPS
3. **Nginx Config** - Automatic SSL certificate configuration

### Required GitHub Secrets

```
VPS_HOST          - VPS IP address or hostname
VPS_USERNAME      - SSH user
VPS_SSH_KEY       - Private SSH key
VPS_PORT          - SSH port (usually 22)
GHCR_PAT          - GitHub Personal Access Token
SECRET_KEY        - Flask secret key
ADMIN_USER        - Admin username
ADMIN_PASSWORD    - Admin password
SMTP_SERVER       - SMTP server
SMTP_PORT         - SMTP port
SMTP_USERNAME     - Email for SMTP
SMTP_PASSWORD     - SMTP password/app password
NGINX_EMAIL       - (Optional) Email for Let's Encrypt notifications
```

### Manual VPS Deployment

Detailed guide in [DEPLOYMENT_SETUP.md](DEPLOYMENT_SETUP.md)

```bash
# On VPS
cd /root/devops-web

# Download configuration
wget https://raw.githubusercontent.com/nw4f2t4gqz-commits/devops-web/main/docker-compose.prod.yml

# Create .env file
nano .env

# Run
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

### GitHub Actions Status

Track deployment status in real-time on `/deploy` page:

- ✅ Successful builds
- ⏳ Running workflows
- ❌ Errors and failures
- 📦 Build details

### Admin Panel

Access `/admin` for:
- Contact lead management
- Traffic statistics
- Access location overview

## 🔧 Configuration

### Nginx Proxy Manager

Automatic configuration via API:
- Create Proxy Host for domain
- Request Let's Encrypt SSL certificate
- Configure Force SSL, HTTP/2, HSTS

Default access:
- Email: `admin@example.com`
- Password: `changeme`

⚠️ **Change default password after first login!**

### Flask Configuration

Main settings in [app.py](app.py):
- `DEBUG` - Development mode
- `DATABASE_URL` - Database path
- `UPLOAD_FOLDER` - Upload directory
- `MAX_CONTENT_LENGTH` - Max upload size

## 📝 API Endpoints

### Public
- `GET /` - Homepage
- `GET /about` - About me
- `GET /articles` - LinkedIn articles
- `GET /deploy` - Deploy monitoring
- `GET /contact` - Contact form
- `POST /contact` - Submit contact
- `GET /api/github-actions/status` - GitHub Actions status

### Admin (requires authentication)
- `GET /admin` - Leads overview
- `POST /admin/login` - Login
- `GET /admin/logout` - Logout
- `DELETE /admin/leads/<id>` - Delete lead

## 🎨 Customization

### Adding LinkedIn Article

Edit [templates/articles.html](templates/articles.html):

```html
<div class="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6">
    <div class="flex items-start justify-between mb-4">
        <h3 class="text-xl font-semibold text-gray-900">
            Article title
        </h3>
        <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
            Published
        </span>
    </div>
    <!-- ... more content ... -->
</div>
```

### Changing Colors

Tailwind CSS classes in templates:
- Primary: `text-blue-600`, `bg-blue-600`
- Success: `text-green-600`, `bg-green-600`
- Warning: `text-yellow-600`, `bg-yellow-600`

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs devops-web-web-1

# Restart services
docker-compose down --remove-orphans
docker-compose up -d
```

### Nginx not working
```bash
# Check nginx container
docker ps | grep nginx-proxy

# Manual configuration
cd /root/devops-web
chmod +x scripts/configure_nginx_proxy.sh
./scripts/configure_nginx_proxy.sh
```

### SSL certificate missing
- Check domain DNS records
- Verify ports 80 and 443 are open
- Check Nginx Proxy Manager admin panel

## 📄 License

This is a personal portfolio project.

## 👤 Contact

- 🌐 Web: [devops.itsvet.net](https://devops.itsvet.net)
- 💼 LinkedIn: [Your LinkedIn profile]
- 📧 Email: [Your email]

---

**Built with ❤️ using Flask, Docker, and GitHub Actions**
