# GameRock - Project Overview

## 1.1 Project Description

GameRock is a comprehensive **Community Management System** built with Flask that provides role-based tools for managing members, financial contributions, budgets, meeting minutes, treasury records, family networks, and community events through a desktop-style web interface. The application is designed to run as a native desktop application using Flask-WebGUI while maintaining full web compatibility.

## 1.2 Key Features

### Core Functional Modules

| Module | Description | Key Capabilities |
|--------|-------------|------------------|
| **Member Management** | Register, edit, and view member profiles | Phone masking, ID validation, family networks, role assignment |
| **Deposits & Contributions** | Track member contributions against community events | Multi-payment support (Cash, MPESA, Bank), CSV export, filtering |
| **Budget Management** | Create, approve, and track community budgets | Status workflows (Draft→Approved→Active→Closed), line items |
| **Meeting Minutes** | Record, draft, approve, and archive meeting minutes | Agenda, discussion, decisions, action items, attendees |
| **Treasury** | Manage income and expense records | Balance tracking, category classification, date filtering |
| **Family Network** | Link spouses and children to member profiles | Spouse/child management with user accounts, age tracking |
| **Welfare Dashboard** | Monitor contributions, active members, community events | Role-specific views, pending contributions, statistics |
| **Reports & Analytics** | Generate reports and visualizations | Chart.js integration, monthly trends, payment breakdowns |
| **FAQs & Knowledge Base** | Manage frequently asked questions | Category grouping, search, admin management |
| **Requisitions** | Track item requests and returns | Multi-item requisitions, status workflow |
| **Sponsors** | Manage sponsor relationships and items | Sponsorship types, amounts, items, status tracking |

### Cross-Cutting Features

- **Role-Based Access Control (RBAC)**: 7 distinct roles with granular permissions
- **Desktop Interface**: Flask-WebGUI for native application experience
- **Image Management**: Profile photos and event images with MIME type detection
- **Data Export**: CSV export across multiple modules
- **Audit Trail**: Created/updated timestamps, user tracking
- **Responsive UI**: Bootstrap 3 with custom CSS

## 1.3 Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Backend Framework** | Flask | 2.3.3 |
| **Database ORM** | SQLAlchemy | 2.0.21 |
| **Database Migrations** | Flask-Migrate / Alembic | 4.0.5 |
| **Authentication** | Flask-Login | 0.6.2 |
| **UI Framework** | Flask-Bootstrap | 3.3.7.1 |
| **Desktop Runtime** | Flask-WebGUI | 1.0.6 |
| **Database Drivers** | PyMySQL, psycopg2 (PostgreSQL), SQLite | 1.1.0+ |
| **Template Engine** | Jinja2 | 3.1.2 |
| **WSGI Server** | Werkzeug | 2.3.7 |

## 1.4 Supported Databases

| Database | Connection URI Format | Status |
|----------|----------------------|--------|
| PostgreSQL (Recommended) | `postgresql://user:pass@host/db` | ✅ Production Ready |
| MySQL | `mysql+pymysql://user:pass@host/db` | ✅ Supported |
| SQLite | `sqlite:///db.sqlite` | ✅ Development Only |

## 1.5 Role Hierarchy and Permissions

### Role Definitions

```python
class AccessLevel(Enum):
    DEVEL = 'Developer'           # Level 5 - Full system access
    CHAIRPERSON = 'Chairperson'   # Level 4 - Leadership oversight
    ADMIN = 'Administrator'       # Level 4 - System administration
    TREASURER = 'Treasurer'       # Level 3 - Financial management
    SECRETARY = 'Secretary'       # Level 3 - Minutes & records
    WELFARE_OFFICER = 'Welfare Officer'  # Level 3 - Member welfare
    USER = 'User'                 # Level 1 - Basic member access
```

### Permission Matrix

| Feature | DEVEL | ADMIN | CHAIRPERSON | TREASURER | SECRETARY | WELFARE | USER |
|---------|-------|-------|-------------|-----------|-----------|---------|------|
| User Management | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Member CRUD | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Own |
| Contributions | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | View |
| Budgets | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Minutes | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | View |
| Treasury | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Family Management | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | Own |
| Events | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | View |
| FAQs | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | View |
| Requisitions | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | Own |
| Sponsors | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Reports | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | View |

## 1.6 Application Entry Points

### Desktop Mode (Default)
```bash
python main.py
```
Launches Flask-WebGUI desktop window (1024x768) on port 5000.

### Web Server Mode
```bash
flask run --host=0.0.0.0 --port=5000
```
Runs as standard Flask web application.

## 1.7 Project Status

- **Current Version**: Active development
- **Architecture**: Flask Blueprint-based modular monolith
- **Database**: SQLAlchemy models with Alembic migrations
- **Testing**: Basic pytest structure in place
- **Deployment**: Desktop-focused with web capability