# Mini ERP

Mini ERP is a small FastAPI web application for managing project-scoped users and inventory. It provides account creation, login, an authenticated dashboard, inventory object tracking, manual stock movements, project history, and basic admin approval for users who join an existing project.

> **Development note:** this project is intended as a local/demo application. User passwords are currently stored in plain text and the session secret is hard-coded for development, so do not deploy it as-is for production use.

## Features

- **Project-based access**: users belong to a project, and dashboard data is filtered to that project.
- **Account creation flow**:
  - Create a new project and become its `admin`.
  - Join an existing project as `unvalidated` until an admin accepts the account.
- **Authentication**: session-based login/logout flow using Starlette sessions.
- **Dashboard metrics**: per-user movement counts, distinct impacted inventory objects, total project inventory objects, and total project movements.
- **User administration**: project admins can accept pending users.
- **Inventory management**:
  - Create inventory object types with an initial quantity and unit price.
  - Add or remove stock through manual movements.
  - Prevent stock removals that would make quantity negative.
- **Project history**: audit-style list of inventory movements for the current project.
- **Optional fixture data**: seed two example projects with users, inventory items, and movement history.

## Tech stack

- Python 3.10+
- FastAPI
- Uvicorn
- Jinja2 templates
- SQLAlchemy ORM
- SQLite local database
- Alembic scaffold for future migrations

## Repository layout

```text
.
├── main.py                         # FastAPI app setup, router registration, DB initialization
├── models/                         # SQLAlchemy database models and session setup
│   ├── db.py
│   ├── inventory_items.py
│   ├── projects.py
│   └── users.py
├── routes/                         # FastAPI routers for auth, dashboard, and inventory actions
│   ├── auth.py
│   ├── common.py
│   ├── dashboard.py
│   └── inventory.py
├── templates/                      # Jinja2 HTML templates
├── static/                         # CSS and JavaScript assets
├── fixtures/sqlalchemy_fixtures.py  # Optional demo data loader
├── alembic/                        # Alembic migration scaffold
├── alembic.ini
├── requirements.txt
└── README.md
```

## Quick start

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000> in your browser.

On startup, the app creates a local SQLite database file named `erp.db` in the project root if it does not already exist.

## Optional: load demo data

To reset the local database tables and load example projects, users, inventory items, and movement history, run:

```bash
python fixtures/sqlalchemy_fixtures.py
```

Then start the app and sign in with one of these fixture accounts:

| Project | Role | Username | Password |
| --- | --- | --- | --- |
| computer shop | admin | `leroy_jenkin` | `lj123` |
| computer shop | member | `jeffanie_jefferson` | `jj1234` |
| computer shop | member | `johnny_johnson` | `19` |
| computer shop | member | `bob` | `12bob` |
| garage | admin | `jeremy_hammond` | `jh199` |
| garage | member | `richard_may` | `rm001` |
| garage | member | `james_clarkson` | `jc` |

## Using the app

1. Visit <http://127.0.0.1:8000>.
2. Log in with an existing account, or create a new account.
3. To create a new project, choose **Create new project** in the account creation form. The first user for that project becomes an admin.
4. To join an existing project, choose **Join existing project**. The new account starts as `unvalidated` and cannot log in until a project admin accepts it.
5. In the dashboard:
   - Use **Inventory** to create inventory objects or record stock additions/removals.
   - Use **Project history** to review inventory movement records.
   - Use **Users list** as an admin to accept pending users.
   - Use **Settings** to toggle dark mode in the UI.

## Database notes

- The SQLite database URL is configured in `models/db.py` as `sqlite:///./erp.db`.
- Tables are created automatically when `main.py` imports the models and runs `Base.metadata.create_all(bind=engine)`.
- Alembic files are present as a scaffold, but this repository does not currently include generated migration revisions.
- The app includes a small startup compatibility check that adds `inventory_items.current_quantity` for older local databases that only have `initial_quantity`.

