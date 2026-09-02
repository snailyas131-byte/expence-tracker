# Smart Expense Tracker

A production-style Flask web application for recording personal income and expenses, planning budgets, tracking savings goals, and understanding spending patterns.

## Overview

Smart Expense Tracker gives each account a private financial workspace. Users can record transactions in PKR, organize them by income or expense category, monitor monthly budgets, set savings targets, inspect Chart.js analytics, and export their own records as CSV.

## Features

- Secure registration, login, logout, and password hashing
- CSRF-protected forms and authenticated sessions
- User-isolated transaction CRUD
- Search, type filtering, and sorting for transaction history
- Default and custom income/expense categories
- Monthly overall and category budgets with progress alerts
- Savings goals with deadlines, contributions, progress, and completion states
- Dashboard balance, income, expense, savings, recent activity, and analytics
- Expenses by category, monthly comparisons, spending trends, and category analysis
- CSV export limited to the signed-in user's transactions
- Profile name and theme preferences
- Responsive interface with light and dark themes

## Screenshots

Real screenshots are not included yet. Follow [docs/SCREENSHOT_GUIDE.md](docs/SCREENSHOT_GUIDE.md) to capture the ten recommended views with fictional data.

## Technology Stack

- Python 3.14+
- Flask 3
- Flask-SQLAlchemy and SQLAlchemy
- SQLite for local development
- Flask-Login
- Flask-WTF
- Jinja2, HTML5, CSS3, and JavaScript
- Bootstrap 5 utilities
- Chart.js via CDN
- pytest

## Project Structure

```text
app/
  models/       SQLAlchemy models and relationships
  routes/       Flask blueprints by feature
  templates/    Jinja templates grouped by feature
  static/       CSS and JavaScript assets
config.py       Environment-aware configuration
run.py          Local application entry point
tests/          Automated workflow tests
docs/           Release and screenshot documentation
screenshots/    Destination for real portfolio screenshots
```

## Database Design

- `User` owns transactions, custom categories, budgets, and savings goals.
- `Category` supports global defaults and user-owned custom categories for income or expenses.
- `Transaction` references its owner and category and stores amount, type, date, payment method, description, and notes.
- `Budget` belongs to a user and optionally a category for a specific month and year.
- `SavingsGoal` belongs to a user and stores target amount, saved amount, and optional deadline.

Every protected record query is scoped to the authenticated user's ID.

## Installation

From the repository root on Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/). The SQLite database is created under `instance/` on first startup, and default categories are seeded automatically.

For production, set `FLASK_CONFIG=production`, provide a strong `SECRET_KEY`, and provide an appropriate `DATABASE_URL` through the environment.

## Usage

Create an account, sign in, and add income or expense transactions. Use the sidebar to review activity, create budgets and savings goals, inspect reports, manage categories, or update settings. The dashboard recalculates totals and analytics from stored transactions.

## Security

Passwords are hashed with Werkzeug. Flask-Login protects private routes, Flask-WTF provides CSRF protection, and SQLAlchemy handles database access. Transaction, budget, category, savings-goal, and report access is scoped to the current user. Secrets belong in environment variables; `.env`, local databases, and virtual environments are ignored by Git.

## Testing

```powershell
python -m compileall -q app
python -m pytest -q
```

The tests cover registration, login, protected routes, transaction creation, dashboard access, CSV export, savings-goal progress, and cross-user goal isolation.

## Known Limitations

- Chart.js is loaded through a CDN and requires network access.
- PDF report generation is not implemented.
- Transaction pagination is not implemented.
- Browser-level automated visual testing is not included.
- Portfolio screenshots must be captured manually; see the screenshot guide.

## Future Improvements

PostgreSQL deployment, a REST API, a React frontend, PDF reports, pagination, receipt uploads, recurring transactions, email notifications, multi-currency support, and AI-assisted categorization are possible future additions.

## License

Released under the [MIT License](LICENSE).
