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
migrations or tests. Whenever new fields are added (for example `final_score`
in the recruitment module) make sure to apply migrations:

```
python manage.py migrate
```

Failing to run migrations can lead to errors such as
`ProgrammingError: column core_recruitmentemployee.final_score does not exist`.

Ensure `DJANGO_SECRET_KEY` is set to a unique value in production to avoid using
the default key from `settings.py`.
