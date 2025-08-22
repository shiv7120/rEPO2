# Bank Management System (Flask + React)

## Backend (Flask)

### Setup

1. Create venv and install deps:

```bash
cd backend
python3 -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment:
- Copy `.env.example` to `.env` and set `JWT_SECRET_KEY`.
- To use PostgreSQL, set `DATABASE_URL` like `postgresql+psycopg://postgres:postgres@localhost:5432/bankdb`.
- If `DATABASE_URL` is unset, SQLite file `bank.db` is used.

3. Initialize DB:

```bash
FLASK_APP=wsgi.py flask db upgrade
```

4. Run server:

```bash
FLASK_APP=wsgi.py flask run --port 5000
```

### API
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/accounts`
- `POST /api/accounts` (create)
- `POST /api/accounts/{id}/deposit`
- `POST /api/accounts/{id}/withdraw`
- `POST /api/accounts/transfer`
- `GET /api/accounts/{id}/transactions`

## Database (PostgreSQL optional)

With Docker installed:

```bash
cd workspace
docker compose up -d db
```

Then set `DATABASE_URL` in `backend/.env`.

## Frontend (React + Vite)

### Setup & Run

```bash
cd frontend
npm install
npm run dev
```

Vite dev server proxies `/api` to the Flask backend at `http://localhost:5000`.

### Build

```bash
npm run build
npm run preview
```