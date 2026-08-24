# Gamerock Welfare Association

<p align="center">
  <img src="https://img.shields.io/badge/Flask-2.3.3-black?style=flat-square" alt="Flask Version">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
</p>

A modern, secure web application for managing welfare association operations — including member registration, contribution tracking, family records, community events, and transparent reporting.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Mission Statement](#mission-statement)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [User Roles & Permissions](#user-roles--permissions)
- [Contributing](#contributing)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [License](#license)
- [Contact](#contact)

---

## Project Overview

Gamerock Welfare Association is a community-focused platform designed to streamline the management of welfare associations. It provides a centralized system for:

- **Member Management** — Register, update, and maintain member profiles with verified details
- **Contribution Tracking** — Record and track financial contributions against specific community events
- **Family Records** — Manage spouse and child records linked to primary members
- **Community Events** — Create and manage events with contribution goals and participant tracking
- **Reporting & Analytics** — Generate insights on contributions, member engagement, and community impact
- **Role-Based Access** — Secure access controls for administrators, developers, and regular users

The application prioritizes data privacy with built-in masking of sensitive identifiers (ID numbers and phone numbers) for non-administrator accounts.

---

## Mission Statement

To empower communities through sustainable development programs, financial support, and social welfare initiatives that uplift every member of our community. We are committed to creating lasting positive change by fostering collaboration, transparency, and collective responsibility among all members.

---

## Features

### Member Management
- Secure registration and authentication
- Profile management with avatar support
- Member search and filtering by multiple criteria
- Data masking for sensitive fields (phone, ID number)

### Contribution System
- Record contributions against specific events
- Multiple payment methods: Cash, MPESA, Bank Deposit, Cheque
- Contribution history and receipts
- Pending contribution tracking

### Family Management
- Link spouses to primary members
- Track children with birth dates and details
- Family-level reporting and summaries

### Community & Events
- Create and manage community events
- Track event contributions and participation
- Community announcements and engagement

### Reporting & Insights
- Contribution summaries by member and event
- Payment method analytics
- Member engagement tracking
- Exportable reports

### Security & Privacy
- Role-based access control (Admin, Developer, User)
- Password hashing and secure authentication
- Sensitive data masking for non-admin users
- CSRF protection on all forms

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Flask 2.3.3 |
| **Database ORM** | SQLAlchemy 2.0.21 |
| **Database** | MySQL / PyMySQL |
| **Authentication** | Flask-Login |
| **Migrations** | Flask-Migrate |
| **Frontend** | Jinja2 Templates, Bootstrap Icons |
| **Styling** | Custom CSS with CSS Variables |
| **Desktop Wrapper** | FlaskWebGUI |

---

## Installation

### Prerequisites

- Python 3.10 or higher
- MySQL Server (or compatible database)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/Timokama/gamerock.git
cd gamerock
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure the Application

Create a `.env` file in the project root with your database and secret key configuration:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URI=mysql+pymysql://username:password@localhost/gamerock_db
```

### Step 5: Initialize the Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Step 6: Create an Admin User

```bash
python create_dev_user.py
```

### Step 7: Run the Application

```bash
python main.py
```

Or for desktop mode:

```bash
python main.py --desktop
```

The application will be available at `http://localhost:5000`.

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for session encryption | Yes |
| `DATABASE_URI` | SQLAlchemy database connection string | Yes |
| `FLASK_ENV` | Environment mode (`development` or `production`) | No |

### Database Schema

The application uses SQLAlchemy ORM with the following core models:

- **Member** — Primary member records
- **User** — Authentication and role management
- **Spouse** — Spouse records linked to members
- **Child** — Child records linked to members
- **Contribution** — Financial contribution records
- **Event** — Community events

---

## Usage

### Getting Started

1. **Register** — New members can register with verified details
2. **Login** — Authenticated access based on user role
3. **Dashboard** — Overview of contributions, family, and community activity
4. **Profile** — Manage personal information and settings

### For Administrators

- Manage all member records
- Assign roles to users
- Review and approve contributions
- Generate reports and analytics
- Manage community events

### For Members

- View and update personal profile
- Make contributions to events
- View contribution history
- Manage family records
- Participate in community events

---

## User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **ADMIN** | Full access to all features, user management, reporting |
| **DEVEL** | Developer access with extended permissions, user role assignment |
| **USER** | Standard member access to profile, contributions, and family records |

---

## Contributing

We welcome contributions from the community. To contribute:

### Reporting Issues

1. Search existing issues to avoid duplicates
2. Create a new issue with a clear title and description
3. Include steps to reproduce, expected behavior, and actual behavior

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit:
   ```bash
   git add -A
   git commit -m "feat: add your feature description"
   ```
4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a Pull Request against the `main` branch

### Code Standards

- Follow PEP 8 style guidelines for Python code
- Write descriptive commit messages
- Update documentation for new features
- Ensure all tests pass before submitting

---

## Development

### Project Structure

```
gamerock/
├── app/
│   ├── __init__.py          # Application factory and configuration
│   ├── main.py              # Route definitions and application logic
│   ├── models/              # SQLAlchemy database models
│   ├── templates/           # Jinja2 HTML templates
│   ├── static/              # CSS, JavaScript, images
│   ├── home/                # Home page routes
│   ├── auth/                # Authentication routes
│   ├── register/            # Member registration routes
│   ├── deposit/             # Contribution management routes
│   ├── family/              # Family management routes
│   ├── community/           # Community and events routes
│   ├── reports/             # Reporting and analytics routes
│   └── admin/               # Admin dashboard routes
├── migrations/              # Database migration scripts
├── requirements.txt         # Python dependencies
├── main.py                  # Application entry point
└── README.md                # Project documentation
```

### Running Tests

```bash
python -m pytest
```

### Database Migrations

Create a new migration after model changes:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

---

## Deployment

### Production Setup

1. Set `FLASK_ENV=production`
2. Configure a production-grade WSGI server (Gunicorn, uWSGI)
3. Set up a reverse proxy (Nginx, Apache)
4. Enable HTTPS with SSL certificates
5. Configure database backups

### Environment Checklist

- [ ] Strong `SECRET_KEY` configured
- [ ] Database credentials secured
- [ ] Debug mode disabled
- [ ] HTTPS enabled
- [ ] Regular database backups scheduled

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

**Gamerock Welfare Association**

- 📧 Email: [gamerock2026@gmail.com](mailto:gamerock2026@gmail.com)
- 📞 Phone: [0745908682](tel:0745908682)
- 🌐 Repository: [https://github.com/Timokama/gamerock](https://github.com/Timokama/gamerock)

---

<p align="center">
  Built with ❤️ for the Gamerock Welfare Association community
</p>
