# GameRock - Technical Documentation Suite

> **Version**: 1.0.0 | **Last Updated**: September 17, 2026

## Welcome

This documentation suite provides comprehensive technical information for the **GameRock** project — a Flask-based Community Management System designed for desktop deployment with Flask-WebGUI while maintaining full web application compatibility.

## Documentation Index

| # | Document | Description |
|---|----------|-------------|
| [01. Project Overview](01_PROJECT_OVERVIEW.md) | High-level project description, key features, technology stack, role hierarchy, and access control matrix. |
| [02. Architecture](02_ARCHITECTURE.md) | Architectural diagrams including high-level architecture, request flow, database schema (ERD), RBAC flow, module dependencies, data flow, security model, deployment architecture, and design patterns. |
| [03. Installation & Setup](03_INSTALLATION.md) | Prerequisites, quick start guide, production deployment, database setup, migration workflow, environment variables, troubleshooting, and configuration reference. |
| [04. API Reference](04_API_REFERENCE.md) | JSON endpoints reference, template global functions, template filters, complete model reference, blueprint route tables, error responses, and CSV export formats. |
| [05. Contributing](05_CONTRIBUTING.md) | Code of conduct, development setup, workflow guidelines, coding standards, testing standards, pull request process, release process, security guidelines, and useful commands. |
| [06. Directory Structure](06_DIRECTORY_STRUCTURE.md) | Complete project directory tree, blueprint registration order, module import dependencies, template hierarchy, static asset organization, and testing structure. |

## Quick Navigation

### Getting Started
1. Read [Installation Guide](03_INSTALLATION.md) for setup instructions
2. Review [Project Overview](01_PROJECT_OVERVIEW.md) for feature overview
3. Understand [Architecture](02_ARCHITECTURE.md) for technical context

### Development
1. Follow [Contributing Guidelines](05_CONTRIBUTING.md) for coding standards
2. Check [API Reference](04_API_REFERENCE.md) for endpoint details
3. Review [Directory Structure](06_DIRECTORY_STRUCTURE.md) for navigation

### Deployment
1. Follow [Installation Guide](03_INSTALLATION.md#section-34-production-deployment) for production deployment
2. Reference [Architecture](02_ARCHITECTURE.md#section-27-security-architecture) for security considerations

## Key Components

### Core Application
- **Entry Point**: `main.py` — Application launcher with Flask-WebGUI
- **Factory**: `app/__init__.py` — Application factory, blueprint registration, context processors
- **Models**: `app/models/` — 15 SQLAlchemy models covering all domain entities
- **Blueprints**: 14 Flask blueprints for modular route organization

### Role-Based Access Control
| Role | Level | Description |
|------|-------|-------------|
| `DEVEL` | 5 | Developer - full system access |
| `ADMIN` | 4 | Administrator - full system access |
| `CHAIRPERSON` | 4 | Leadership oversight |
| `TREASURER` | 3 | Financial management |
| `SECRETARY` | 3 | Minutes & records |
| `WELFARE_OFFICER` | 3 | Member welfare |
| `USER` | 1 | Basic member access |

### Major Features
- Member Management with family networks
- Contribution tracking with multi-payment support
- Budget creation, approval, and tracking workflows
- Meeting minutes with draft/approve workflow
- Treasury income/expense management
- Community events with contribution tracking
- FAQ knowledge base
- Item requisition system
- Sponsor relationship management
- Reports with Chart.js visualizations

## Technology Stack Summary

| Category | Technology |
|----------|------------|
| Framework | Flask 2.3.3 |
| ORM | SQLAlchemy 2.0.21 |
| Auth | Flask-Login 0.6.2 |
| UI | Flask-Bootstrap 3.3.7.1 |
| Desktop | Flask-WebGUI 1.0.6 |
| Database | PostgreSQL (recommended) |
| Migrations | Flask-Migrate / Alembic |

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: This directory (`docs/`)
- **Project README**: [README.md](README.md)
- **Report Issues**: https://github.com/Timokama/gamerock/issues
- **Kilo Help**: `/help` command in CLI