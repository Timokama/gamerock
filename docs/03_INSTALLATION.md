# GameRock - Installation & Setup Guide

## 3.1 Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.8+ | 3.10+ |
| **Database** | SQLite (dev) | PostgreSQL 14+ / MySQL 8+ |
| **Memory** | 512 MB | 2 GB+ |
| **Disk** | 1 GB | 5 GB+ |
| **OS** | Windows 10+, macOS 11+, Linux | Any modern OS |

### Required Software

- **Python 3.8+** with `venv` module
- **Git** for version control
- **Database Server** (PostgreSQL recommended for production)
- **Virtual Environment** tool (`venv`, `virtualenv`, or `conda`)

## 3.2 Quick Start (Development)

### 1. Clone Repository

```bash
git clone https://github.com/Timokama/gamerock.git
cd gamerock
```

### 2. Create Virtual Environment

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
python -m venv venv
venv\Scripts\activate.bat

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

**Option A: SQLite (Development Only - Zero Config)**
```bash
# No additional setup required
# Database file: instance/db.sqlite
```

**Option B: PostgreSQL (Recommended)**
```bash
# 1. Install PostgreSQL
# 2. Create database and user
psql -U postgres
CREATE DATABASE gamerock;
CREATE USER gamerock_user WITH ENCRYPTED PASSWORD 'gamerock_password';
GRANT ALL PRIVILEGES ON DATABASE gamerock TO gamerock_user;
\q
```

**Option C: MySQL**
```bash
# 1. Install MySQL
# 2. Create database and user
mysql -u root -p
CREATE DATABASE gamerock CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gamerock_user'@'localhost' IDENTIFIED BY 'gamerock_password';
GRANT ALL PRIVILEGES ON gamerock.* TO 'gamerock_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Update Configuration

Edit `app/__init__.py` with your database settings:

```python
# PostgreSQL (Production)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gamerock_user:gamerock_password@localhost/gamerock'

# MySQL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://gamerock_user:gamerock_password@localhost/gamerock'

# SQLite (Development)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

# IMPORTANT: Change SECRET_KEY in production!
app.config['SECRET_KEY'] = 'your-secure-random-secret-key-here'
```

### 6. Initialize Database

```bash
# Initialize migration repository
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

### 7. Run Application

```bash
# Desktop mode (default)
python main.py

# Web server mode
flask run --host=0.0.0.0 --port=5000
```

### 8. Access Application

- **Desktop**: Application window opens automatically (1024x768)
- **Web**: Open http://localhost:5000 in browser

## 3.3 Production Deployment

### Environment Variables

Create a `.env` file (not committed to git):

```bash
# .env
SECRET_KEY=your-very-long-random-secret-key-min-32-chars
SQLALCHEMY_DATABASE_URI=postgresql://user:pass@host/gamerock
DEBUG=False
TEMPLATES_AUTO_RELOAD=False
PORT=5000
HOST=0.0.0.0
```

Update `app/__init__.py` to load from environment:

```python
import os
from dotenv import load_dotenv

load_dotenv()

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
app.config['TEMPLATES_AUTO_RELOAD'] = os.environ.get('TEMPLATES_AUTO_RELOAD', 'False').lower() == 'true'
```

Add `python-dotenv` to requirements:
```bash
pip install python-dotenv
echo "python-dotenv==1.0.0" >> requirements.txt
```

### Windows Service (NSSM)

```bash
# Install NSSM (Non-Sucking Service Manager)
# Download from https://nssm.cc/download

# Install as service
nssm install GameRock "C:\path\to\gamerock\venv\Scripts\python.exe" "C:\path\to\gamerock\main.py"
nssm set GameRock AppDirectory "C:\path\to\gamerock"
nssm set GameRock AppEnvironmentExtra "SECRET_KEY=your-secret;SQLALCHEMY_DATABASE_URI=postgresql://..."
nssm start GameRock
```

### Linux systemd Service

```ini
# /etc/systemd/system/gamerock.service
[Unit]
Description=GameRock Community Management System
After=network.target postgresql.service

[Service]
Type=simple
User=gamerock
WorkingDirectory=/opt/gamerock
Environment=PATH=/opt/gamerock/venv/bin
Environment=SECRET_KEY=your-secret
Environment=SQLALCHEMY_DATABASE_URI=postgresql://user:pass@localhost/gamerock
ExecStart=/opt/gamerock/venv/bin/python main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable gamerock
sudo systemctl start gamerock
sudo systemctl status gamerock
```

### Reverse Proxy (Nginx) - Web Mode Only

```nginx
# /etc/nginx/sites-available/gamerock
server {
    listen 80;
    server_name gamerock.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static {
        alias /opt/gamerock/app/static;
        expires 30d;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/gamerock /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 3.4 Database Migrations

### Common Commands

```bash
# Create new migration after model changes
flask db migrate -m "Description of changes"

# Apply pending migrations
flask db upgrade

# Rollback last migration
flask db downgrade

# Show migration history
flask db history

# Show current revision
flask db current

# Stamp database with specific revision (without running migrations)
flask db stamp head
```

### Migration Best Practices

1. **Always review generated migrations** before applying
2. **Test migrations on staging** before production
3. **Backup database** before running migrations in production
4. **Use descriptive migration messages**
5. **Never edit applied migrations** - create new ones instead

## 3.5 Configuration Reference

### Application Configuration (`app/__init__.py`)

| Setting | Description | Default | Production Value |
|---------|-------------|---------|------------------|
| `SECRET_KEY` | Flask session signing key | `'secret_key_goes_here'` | **Required: Strong random string** |
| `SQLALCHEMY_DATABASE_URI` | Database connection string | PostgreSQL URI | Your production DB URI |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | Track object modifications | `False` | `False` |
| `DEBUG` | Enable debug mode | `False` | `False` |
| `TEMPLATES_AUTO_RELOAD` | Auto-reload templates | `False` | `False` |
| `USE_RELOADER` | Use Werkzeug reloader | `False` | `False` |
| `SEND_FILE_MAX_AGE_DEFAULT` | Static file cache max age | `0` | `31536000` (1 year) |
| `EXPLAIN_TEMPLATE_LOADING` | Debug template loading | `False` | `False` |

### File Upload Configuration

```python
PEOPLE_FOLDER = os.path.join('static', 'photos')
EVENTS_FOLDER = os.path.join('static', 'photos', 'events')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
```

### Logging Configuration

```python
# Current setup suppresses INFO logs
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('jinja2').setLevel(logging.WARNING)
logging.getLogger('flask').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('alembic').setLevel(logging.WARNING)

app.logger.setLevel(logging.WARNING)
```

For production, consider:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/gamerock.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('GameRock startup')
```

## 3.6 Default Accounts & Initial Setup

### Creating First Admin User

After first run, register a new user through the web interface at `/signup`. Then promote to admin via database:

```sql
-- Option 1: Direct database update
UPDATE "user" SET role = 'DEVEL', status = 'active' WHERE email = 'admin@example.com';

-- Option 2: Use the application (login as dev/admin if exists)
-- The first user can be promoted via UI: Register > Pending Users > Approve > Assign Admin
```

### Default Roles Available

- **DEVEL** / **ADMIN**: Full system access
- **CHAIRPERSON**: Leadership oversight
- **TREASURER**: Financial management
- **SECRETARY**: Minutes & records
- **WELFARE_OFFICER**: Member welfare
- **USER**: Basic member access

## 3.7 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure virtual environment is activated and `pip install -r requirements.txt` completed |
| `sqlalchemy.exc.OperationalError` | Check database connection string, ensure DB server is running |
| `flask.db` commands not found | Install Flask-Migrate: `pip install Flask-Migrate` |
| `Permission denied` on Windows | Run PowerShell as Administrator, or check execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Port 5000 in use | Change port: `set PORT=8080 && python main.py` (Windows) or `PORT=8080 python main.py` (Unix) |
| Template not found | Ensure `TEMPLATES_AUTO_RELOAD=True` in development, check template paths |
| Image upload fails | Check `UPLOAD_FOLDER` exists and is writable, verify `ALLOWED_EXTENSIONS` |

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql postgresql://gamerock_user:gamerock_password@localhost/gamerock -c "SELECT version();"

# Test MySQL connection
mysql -u gamerock_user -p -h localhost gamerock -e "SELECT VERSION();"

# Test SQLite
ls -la instance/db.sqlite
```

### Migration Issues

```bash
# If migration fails, check current state
flask db current

# If database is out of sync, stamp to head and recreate
flask db stamp head
flask db migrate -m "Resync after manual changes"
flask db upgrade
```

## 3.8 Verification Checklist

After installation, verify:

- [ ] Application starts without errors
- [ ] Login page accessible at `/`
- [ ] User registration works at `/signup`
- [ ] Database tables created (check with `flask db current`)
- [ ] Static files served (CSS, JS, images)
- [ ] File uploads work (profile photos, event images)
- [ ] CSV exports functional
- [ ] Role-based redirects work correctly
- [ ] Desktop window opens (if using `python main.py`)

## 3.9 Uninstallation

```bash
# Stop application
# Remove virtual environment
rm -rf venv  # Unix
rmdir /s venv  # Windows

# Remove database (if SQLite)
rm instance/db.sqlite

# Remove project directory
cd ..
rm -rf gamerock  # Unix
rmdir /s gamerock  # Windows
```