# Majed Learning Platform

This project is a Django-based training management application. The database
configuration uses PostgreSQL by default. Adjust the following environment
variables to match your local setup:
A `.env.example` file lists these variables; copy it to `.env` and adjust as needed.
The sample file sets `POSTGRES_PASSWORD=postgres`; you can change this value if you prefer a different password.

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

## Local Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Install and build Tailwind CSS assets (requires `npm`):

```bash
npm install
npm run build:css &
```

3. Apply database migrations and start the development server:

```bash
python manage.py migrate
python manage.py runserver
```

## Importing Legacy Data from Excel

Old recruitment spreadsheets can be imported directly using a custom Django
management command. This avoids indentation issues that may occur when pasting
code into the interactive shell.

```bash
python manage.py import_legacy_excel path/to/legacy.xlsx
```

Replace `path/to/legacy.xlsx` with the Excel file you wish to import. The
command cleans the column names and bulk creates
`LegacyRecruitmentRecord` entries. Numeric evaluation columns are converted
using `pandas.to_numeric`, so invalid values become `NULL`, while textual
results such as "The assessment cannot be conducted" are stored unchanged.

## Cleaning Legacy Records

A maintenance command is available to tidy the legacy data:

```bash
python manage.py cleanup_legacy_records
```

This command removes entries that contain no real values.
