# Setup

## Prerequisites

- Python 3.14+
- PostgreSQL
- Redis
- [uv](https://github.com/astral-sh/uv) (package manager)

## Quick start

```bash
# Clone the repository
git clone https://github.com/unicef/hope-ams.git
cd hope-ams

# Create virtual environment and install dependencies
uv sync --frozen

# Copy environment file
cp .envrc .envrc && direnv allow
# Or manually source it:
source .envrc

# Create the database
createdb ams

# Run migrations
uv run python manage.py migrate

# Start the development server
uv run python manage.py runserver
```

## Environment variables

See [Settings](../guide-adm/settings.md) for a full reference.
