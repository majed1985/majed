# Majed Learning Platform

This project is a Django-based training management application. The database
configuration uses PostgreSQL by default. Adjust the following environment
variables to match your local setup:

```
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
DJANGO_SECRET_KEY
```

A local `db.sqlite3` file was previously tracked but is now removed. Ensure your
PostgreSQL server is running and the variables above are set when running
migrations or tests.

Ensure `DJANGO_SECRET_KEY` is set to a unique value in production to avoid using
the default key from `settings.py`.
