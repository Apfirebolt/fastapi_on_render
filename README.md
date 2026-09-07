# Deploying FastAPI / Python Service to Render with DigitalOcean PostgreSQL

A step-by-step guide to deploying a Python web service (FastAPI/Uvicorn) to Render connected to an external DigitalOcean Managed PostgreSQL database.

---

## Prerequisites

- A [Render](https://render.com) account.
- A [DigitalOcean](https://digitalocean.com) Managed PostgreSQL database.
- Your project pushed to a GitHub or GitLab repository.
- A `requirements.txt` file in your repository root specifying all dependencies (including `uvicorn`, database drivers, etc.).

---

## Step 1: Configure DigitalOcean Managed Database Access

Because Render uses dynamic outbound IP addresses, you must configure network access on DigitalOcean.

1. Log in to the **DigitalOcean Cloud Console**.
2. Go to **Databases** and select your PostgreSQL cluster.
3. Under the **Overview** tab:
   - In the **Connection details** box, switch the dropdown to **Connection string**.
   - Copy the complete connection URI (ensure `sslmode=require` is appended).
4. Go to the **Settings** tab and scroll to **Trusted Sources**:
   - If enabled, ensure traffic from your local IP address (for migrations) and Render's outgoing traffic is allowed.
   - For simple external access, you can add `0.0.0.0/0` (traffic remains secured via credentials and mandatory SSL).

---

## Step 2: Apply Migrations from Your Local Machine

Run and apply your database migrations locally so tables and schemas exist on DigitalOcean prior to launching your web service.

```bash
# 1. Point DATABASE_URL to your DigitalOcean PostgreSQL connection string
export DATABASE_URL="postgresql://doadmin:your_password@your-db-host.ondigitalocean.com:25060/defaultdb?sslmode=require"

# 2. Generate new migration files if needed
# For Alembic / FastAPI:
alembic revision --autogenerate -m "initial schema"
# For Django:
# python manage.py makemigrations

# 3. Apply migrations to the remote database
# For Alembic / FastAPI:
alembic upgrade head
# For Django:
# python manage.py migrate

# 4. Commit and push the generated migration scripts to your repository
git add .
git commit -m "Add database migrations"
git push origin main

### Command to run on local

`uvicorn main:app --reload`

## Vercel deployment

The same configuration with no changes at all also worked in vercel, the project for the time being is deployed here

https://fastapionrender.vercel.app