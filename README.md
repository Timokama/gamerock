# GameRock

GameRock is a **community management system** built with Flask. It provides role-based tools for managing members, financial contributions, budgets, meeting minutes, treasury records, family networks, and community events through a desktop-style web interface.

## Key Features

- **Role-Based Access Control**: DEVEL, ADMIN, SECRETARY, TREASURER, WELFARE_OFFICER, CHAIRPERSON, and USER roles with granular permissions.
- **Member Management**: Register, edit, and view member profiles with phone masking and family networks.
- **Deposits & Contributions**: Track member contributions against community events with payment type support (Cash, MPESA, Bank Deposit).
- **Budget Management**: Create, approve, and track community budgets with status workflows (Draft, Approved, Active, Closed).
- **Meeting Minutes**: Record, draft, approve, and archive meeting minutes.
- **Treasury**: Manage income and expense records with balance tracking.
- **Family Network**: Link spouses and children to member profiles.
- **Welfare Dashboard**: Monitor contributions, active members, and community events.
- **Reports & FAQs**: Generate reports and manage frequently asked questions.
- **Desktop Interface**: Uses Flask-WebGUI for a native application-like experience.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask 2.3.3 |
| Database ORM | SQLAlchemy 2.0.21 |
| Database Migrations | Flask-Migrate / Alembic |
| Authentication | Flask-Login |
| UI Framework | Flask-Bootstrap 3.3.7.1 |
| Desktop Runtime | Flask-WebGUI 1.0.6 |
| Database Drivers | PyMySQL 1.1.0, PostgreSQL (default), SQLite (alternative) |

## Prerequisites

- **Python**: 3.8+ (3.10+ recommended)
- **Database**: PostgreSQL (recommended) or MySQL/SQLite
- **Virtual Environment**: `venv` or equivalent

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Timokama/gamerock.git
   cd gamerock
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv

   # Windows (PowerShell)
   .\venv\Scripts\Activate.ps1

   # Windows (Command Prompt)
   venv\Scripts\activate.bat

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   # With PostgreSQL running and database created:
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

## Configuration

The application is configured via `app/__init__.py`. Update these settings before running:

| Variable | Purpose | Default / Example |
|----------|---------|-------------------|
| `SECRET_KEY` | Flask session signing | `'secret_key_goes_here'` |
| `SQLALCHEMY_DATABASE_URI` | Database connection | `postgresql://gamerock_user:gamerock_password@localhost/gamerock` |
| `DEBUG` | Debug mode | `False` |
| `TEMPLATES_AUTO_RELOAD` | Auto-reload templates | `True` |

### Database URI Examples

```python
# PostgreSQL (recommended)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/gamerock'

# MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:secret123@localhost/gamerock'

# SQLite (development only)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
```

## Usage

### Run the application
```bash
python main.py
```

This starts the Flask-WebGUI desktop interface on port `5000` by default. The window size is configured as `800x600`.

### Run with a custom port
```bash
# Windows PowerShell
$env:PORT = 8080; python main.py

# Command Prompt
set PORT=8080 && python main.py

# macOS / Linux
PORT=8080 python main.py
```

### Database migrations
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## Project Structure

```
gamerock/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── Gamerock.bat             # Windows launch script
├── app/
│   ├── __init__.py          # Application factory and configuration
│   ├── auth.py              # Authentication blueprint
│   ├── main.py              # Main routes blueprint
│   ├── user.py              # User model
│   ├── level.py             # Access level utilities
│   ├── image.py             # Image upload helpers
│   ├── account/             # Account management
│   ├── budget/              # Budget routes
│   ├── community/           # Community events and FAQs
│   ├── deposit/             # Contributions and deposits
│   ├── family/              # Family/spouse/child management
│   ├── home/                # Home routes
│   ├── minutes/             # Meeting minutes
│   ├── models/              # SQLAlchemy models
│   ├── register/            # Member registration and dashboards
│   ├── reports/             # Reporting routes
│   ├── static/              # CSS, JS, images
│   ├── templates/           # Jinja2 templates
│   └── treasurer/           # Treasury management
├── migrations/              # Alembic migration scripts
└── venv/                    # Virtual environment (gitignored)
```

## Role Overview

| Role | Access |
|------|--------|
| `DEVEL` / `ADMIN` | Full system access, user management, all modules |
| `SECRETARY` | Minutes, overviews, limited member access |
| `TREASURER` | Treasury, budgets, deposits, contributions |
| `WELFARE_OFFICER` | Contributions, deposits, welfare overview |
| `CHAIRPERSON` | Budgets, minutes, overviews |
| `USER` | Personal dashboard, own contributions, family view |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Coding Conventions

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Ensure database migrations are included for model changes

## Known Issues & Improvements Needed

- **Hardcoded secrets**: `SECRET_KEY` and database credentials are currently hardcoded in `app/__init__.py`. These should be moved to environment variables or a `.env` file.
- **No `.env` support**: The project lacks python-dotenv integration. Consider adding a `.env.example` and loading configuration from environment variables.
- **Debug configuration**: `DEBUG = False` is set but `TEMPLATES_AUTO_RELOAD = True`. Clarify intended development vs production settings.
- **Windows-only launch script**: `Gamerock.bat` assumes a Windows path. Add cross-platform launch instructions or scripts.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
