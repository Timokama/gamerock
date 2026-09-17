# GameRock - Contribution Guidelines

## 5.1 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive criticism
- Respect differing viewpoints and experiences
- Gracefully accept constructive feedback

## 5.2 Getting Started

### Development Environment Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/gamerock.git
cd gamerock

# 3. Add upstream remote
git remote add upstream https://github.com/Timokama/gamerock.git

# 4. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1

# 5. Install dependencies
pip install -r requirements.txt

# 6. Install development dependencies
pip install pytest pytest-cov black flake8 mypy pre-commit

# 7. Set up pre-commit hooks
pre-commit install

# 8. Configure development database
cp app/__init__.py app/__init__.py.dev
# Edit app/__init__.py.dev to use SQLite
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_family_member_redirect.py -v

# Run with specific markers
pytest -m "not slow"
```

## 5.3 Development Workflow

### Branch Strategy

```
main (protected)
  ├── develop (integration branch)
  │     ├── feature/xxx (feature branches)
  │     ├── bugfix/xxx (bug fix branches)
  │     └── hotfix/xxx (urgent production fixes)
  └── release/x.x.x (release branches)
```

### Creating a Feature Branch

```bash
# Sync with upstream
git fetch upstream
git checkout develop
git merge upstream/develop

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit frequently
git add .
git commit -m "feat: add member search with multiple filters"

# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### Commit Message Convention

Follow **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Formatting, missing semicolons, etc.
- `refactor` - Code restructuring without behavior change
- `perf` - Performance improvement
- `test` - Adding tests
- `chore` - Maintenance tasks

**Examples:**
```
feat(register): add bulk member import from CSV

fix(deposit): resolve decimal precision issue in contribution totals

docs(api): update JSON endpoint documentation

refactor(models): extract base model class for timestamps

test(family): add unit tests for spouse/child creation

chore(deps): update Flask to 2.3.3
```

## 5.4 Code Standards

### Python Style Guide

Follow **PEP 8** with these project-specific conventions:

```python
# Line length: 100 characters (not 79)
# Use double quotes for strings
# Type hints for all new functions

# Good
def get_member_contributions(member_id: int, event_id: int | None = None) -> list[Contribution]:
    """Get contributions for a member, optionally filtered by event."""
    query = Contribution.query.filter_by(member_id=member_id)
    if event_id:
        query = query.filter_by(propose=event_id)
    return query.order_by(Contribution.trans_date.desc()).all()

# Avoid
def get_member_contributions(member_id, event_id=None):
    query = Contribution.query.filter_by(member_id=member_id)
    if event_id:
        query = query.filter_by(propose=event_id)
    return query.order_by(Contribution.trans_date.desc()).all()
```

### Import Organization

```python
# 1. Standard library imports
import os
from datetime import datetime
from typing import Optional

# 2. Third-party imports
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import select, func
from werkzeug.security import generate_password_hash

# 3. Local imports
from app import db
from app.user import User
from app.level import AccessLevel
from app.models.register import Member
from app.models.contribute import Contribution
```

### Blueprint Structure

Each blueprint follows this structure:

```
app/<module>/
├── __init__.py          # Blueprint registration
├── routes.py            # Route definitions
└── templates/<module>/  # Module-specific templates
```

```python
# app/<module>/__init__.py
from flask import Blueprint

bp = Blueprint('<module>', __name__, url_prefix='/<prefix>')

from app.<module> import routes  # noqa: E402,F401
```

### Database Model Conventions

```python
class NewModel(db.Model):
    __tablename__ = 'new_model'  # snake_case table name
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign keys use singular table name
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships use backref
    user = db.relationship('User', backref='new_models')
    
    def __repr__(self):
        return f'<NewModel {self.name}>'
```

### Migration Guidelines

```bash
# 1. Make model changes
# 2. Generate migration
flask db migrate -m "Add phone_number to Member model"

# 3. Review generated migration file in migrations/versions/
# 4. Apply migration
flask db upgrade

# 5. Test rollback
flask db downgrade
flask db upgrade
```

**Never:**
- Edit applied migration files
- Delete migration files from history
- Commit migration files with syntax errors

### Template Conventions

```jinja2
{# Use consistent naming #}
{# Templates: lowercase_with_underscores.html #}
{# Variables: snake_case #}

{# Base template extends #}
{% extends "base.html" %}

{# Block structure #}
{% block title %}Page Title{% endblock %}

{% block content %}
<div class="container">
    {% include "partials/header.html" %}
    
    {% for item in items %}
        {% include "partials/item_card.html" with context %}
    {% endfor %}
</div>
{% endblock %}

{% block scripts %}
{{ super() }}
<script src="{{ static_version('js/module.js') }}"></script>
{% endblock %}
```

### CSS/JS Organization

```
app/static/
├── css/
│   ├── main.css           # Main stylesheet
│   ├── components/        # Component-specific styles
│   └── pages/             # Page-specific styles
├── js/
│   ├── main.js            # Main JavaScript
│   ├── components/        # Component scripts
│   └── pages/             # Page-specific scripts
└── images/
    ├── events/            # Event images
    └── photos/            # Member photos
```

## 5.5 Testing Standards

### Test Structure

```
tests/
├── __init__.py
├── conftest.py            # Pytest fixtures
├── unit/                  # Unit tests
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_level.py
├── integration/           # Integration tests
│   ├── test_auth.py
│   ├── test_deposit.py
│   └── test_family.py
└── fixtures/              # Test data
    └── sample_data.json
```

### Writing Tests

```python
# tests/unit/test_level.py
import pytest
from app.level import AccessLevel

class TestAccessLevel:
    def test_devel_is_admin(self):
        assert AccessLevel.DEVEL.is_admin is True
    
    def test_user_is_not_admin(self):
        assert AccessLevel.USER.is_admin is False
    
    def test_hierarchy_levels(self):
        assert AccessLevel.DEVEL.level == 5
        assert AccessLevel.USER.level == 1
        assert AccessLevel.DEVEL.level > AccessLevel.ADMIN.level

# tests/integration/test_deposit.py
def test_create_contribution(client, auth_user, member, event):
    response = client.post(
        f'/contribution/{member.id}/amount',
        data={
            'amount': '1000',
            'payment': 'MPESA',
            'propose': str(event.id),
            'transaction_ref': 'TEST123'
        }
    )
    assert response.status_code == 302
    
    contribution = Contribution.query.filter_by(
        member_id=member.id,
        propose=event.id
    ).first()
    assert contribution is not None
    assert contribution.amount == 1000
```

### Fixtures (conftest.py)

```python
import pytest
from app import create_app, db
from app.user import User
from app.level import AccessLevel
from app.models.register import Member

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_user(app):
    with app.app_context():
        user = User(
            first_name='Test',
            surname='User',
            email='test@example.com',
            passwords='password123',
            role=AccessLevel.ADMIN,
            status='active'
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def member(app, auth_user):
    with app.app_context():
        member = Member(
            firstname='John',
            lastname='Doe',
            surname='Smith',
            email='john@example.com',
            phone_num='0712345678',
            user_id=auth_user.id
        )
        db.session.add(member)
        db.session.commit()
        return member
```

## 5.6 Pull Request Process

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guide (run `black .` and `flake8`)
- [ ] Type hints added for new functions
- [ ] Tests added/updated for new functionality
- [ ] All tests pass (`pytest`)
- [ ] Database migrations included for model changes
- [ ] Documentation updated (README, API docs, etc.)
- [ ] Commit messages follow convention
- [ ] Branch is rebased on latest `develop`
- [ ] No merge conflicts

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactor

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code formatted with black
- [ ] Linting passes (flake8)
- [ ] Type checking passes (mypy)
- [ ] Migrations included
- [ ] Documentation updated

## Screenshots (if UI changes)
[Add screenshots]

## Related Issues
Closes #XXX
```

### Review Process

1. **Automated Checks**: CI runs tests, linting, type checking
2. **Code Review**: At least one maintainer reviews
3. **Approval**: Required from maintainer
4. **Merge**: Squash and merge to `develop`

## 5.7 Release Process

### Versioning

Follow **Semantic Versioning** (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

```bash
# 1. Create release branch
git checkout develop
git checkout -b release/1.2.0

# 2. Update version
# Edit version in relevant files (if any)

# 3. Update CHANGELOG.md
# 4. Run full test suite
pytest --cov=app

# 5. Build and test production image
# 6. Create PR to main
# 7. After merge, tag release
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0

# 8. Deploy to production
# 9. Merge back to develop
git checkout develop
git merge main
```

## 5.8 Security Guidelines

### Reporting Vulnerabilities

**DO NOT** create public issues for security vulnerabilities. Instead:
1. Email security@gamerock.example.com (or maintainers directly)
2. Include detailed description and reproduction steps
3. Allow time for fix before disclosure

### Secure Coding Practices

- **Never** commit secrets, API keys, or passwords
- **Always** use parameterized queries (SQLAlchemy ORM handles this)
- **Validate** all user inputs server-side
- **Hash** passwords with PBKDF2-SHA256 (already implemented)
- **Use** HTTPS in production
- **Set** secure session cookies: `SESSION_COOKIE_SECURE=True`
- **Implement** CSRF protection for forms (Flask-WTF recommended)

### Current Security Gaps (To Address)

- [ ] Add `python-dotenv` for environment configuration
- [ ] Move `SECRET_KEY` to environment variable
- [ ] Add CSRF protection (Flask-WTF)
- [ ] Implement rate limiting on auth endpoints
- [ ] Add security headers (CSP, HSTS, etc.)
- [ ] Enable SQL query logging in development only
- [ ] Add audit logging for sensitive operations

## 5.9 Documentation Standards

### Writing Documentation

- Use **Markdown** with GitHub-flavored extensions
- Include **code examples** for all APIs
- Keep **diagrams** in Mermaid format (renderable on GitHub)
- Update **API reference** when endpoints change
- Document **migration steps** for breaking changes

### Documentation Structure

```
docs/
├── 01_PROJECT_OVERVIEW.md
├── 02_ARCHITECTURE.md
├── 03_INSTALLATION.md
├── 04_API_REFERENCE.md
├── 05_CONTRIBUTING.md
├── 06_DIRECTORY_STRUCTURE.md
├── CHANGELOG.md
└── ROADMAP.md
```

## 5.10 Useful Commands

### Development Commands

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type check
mypy app/

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Database operations
flask db migrate -m "message"
flask db upgrade
flask db downgrade

# Run development server
python main.py          # Desktop mode
flask run --debug       # Web mode with debug

# Shell context
flask shell
```

### Git Helpers

```bash
# Amend last commit
git commit --amend --no-edit

# Interactive rebase
git rebase -i develop

# Squash commits
git reset --soft develop
git commit -m "feat: combined feature"

# Clean up merged branches
git branch --merged | grep -v "\*\|main\|develop" | xargs -n 1 git branch -d
```