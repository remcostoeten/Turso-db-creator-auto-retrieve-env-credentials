## Turso DB Creator CLI

### Get a fresh Turso database up and running in your local develop enviorment in less than 15 seconds!
---
A simple yet powerful CLI tool that creates a fresh [https://turso.tech/](Turs) - Cloud SQLite database, generates an authentication key, and copies both—prefixed as `DATABASE_URL=` and `AUTH_TOKEN=`—to your clipboard or optionally via arguments automatically updates your existing `* .env*` file.

![Demo](demo.gif)

### Basic Usage
```bash
python3 generate-turso-db.py
```

### Command Line Arguments

#### Basic Options

| Option | Description |
|--------|-------------|
| `--name DB_NAME` | Custom name for the database. If not provided, Turso will generate a random name. |
| `--overwrite FILENAME` | Filename (e.g., `.env` or `.env.production`) to update/create in project root. |
| `--no-clipboard` | Skip copying credentials to the clipboard. |
| `--auto-reveal {on,off}` | Automatically reveal secrets without prompting. **Default:** `off` |

#### Environment Variable Options

| Option | Description |
|--------|-------------|
| `--env-url-name VAR_NAME` | Custom name for the database URL environment variable. **Default:** `DATABASE_URL` |
| `--env-token-name VAR_NAME` | Custom name for the auth token environment variable. **Default:** `TURSO_AUTH_TOKEN` |

#### Configuration

| Option | Description |
|--------|-------------|
| `--configure` | Open configuration menu to set preferences. |

#### 🗑️ Deletion Options

| Option | Description |
|--------|--------------|
| `--delete-generation` | Delete the last database created by THIS script (uses state file). |

#### Full Usage Syntax
```bash
python3 generate-turso-db.py [-h] [--name DB_NAME] [--overwrite FILENAME]
                              [--no-clipboard] [--auto-reveal {on,off}]
                              [--env-url-name VAR_NAME] [--env-token-name VAR_NAME]
                              [--configure] [--seed [MODE]] [--delete-generation]
```

### Examples

```shell
# Generate a new database, display credentials, and copy to clipboard
python3 generate-turso-db.py
```

```shell
# Generate a new database and update/create '.env.local' in the project root
python3 generate-turso-db.py --overwrite .env.local
```

```bash
# Generate a new database but do not copy credentials to clipboard
python3 generate-turso-db.py --no-clipboard
```

```shell
# Create a database with a custom name
python3 generate-turso-db.py --name my-awesome-db
```

```bash
# Auto-reveal secrets without prompting
python3 generate-turso-db.py --auto-reveal on
```

```shell
# Use custom environment variable names
python3 generate-turso-db.py --env-url-name CUSTOM_DB_URL --env-token-name CUSTOM_AUTH_TOKEN
```

### Database Seeding

| Option | Description |
|--------|-------------|
| `--seed [MODE]` | Run database seeding after creation. `MODE` can be: `drizzle` (run drizzle-kit push/migrate), `sql` (apply local SQL files), or `interactive` (choose method). If no mode is specified, it falls back to configuration or prompts the user. |

```bash
# Generate database and prompt for seeding method (interactive mode)
python3 generate-turso-db.py --seed

# Generate database and run Drizzle migrations
python3 generate-turso-db.py --seed drizzle

# Generate database and apply local SQL migration files
python3 generate-turso-db.py --seed sql
```

### Configuration

> [!TIP]
> For even easier access add this `alias create-turso="python3 ~/path/to/cloned/script/generate-turso-db.py` inside  your shell config."

```bash
# Open interactive configuration menu to set preferences, including seeding defaults and prompt behaviors
python3 generate-turso-db.py --configure
```

### Deletion Commands

```bash
# Delete the last database specifically created by this script (if tracked)
python3 generate-turso-db.py --delete-generation
```

#### Post-Creation Deletion

After creating a database, the script offers a post-completion prompt to delete the database if needed. This provides a safe way to clean up test databases immediately after creation.

## Requirements

- Python 3.6+
- Turso CLI
- pyperclip
- rich (optional)

But should be  smart enough to guide you through the install process  if something is missing

## Install Dependencies

```bash
pip install pyperclip rich
```

xxx,

Remco Stoeten
