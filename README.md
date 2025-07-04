# Turso DB Creator CLI

![Demo](demo.gif)

A simple but genius  CLI tool to create Turso databases and generate authentication tokens, copy to clipboard prefixed with enviorment variable,  or ov  erwrite existing `.env`.

## Usage

### Basic Usage
```bash
python3 generate-turso-db.py
```

### Command Line Arguments

```
usage: generate-turso-db.py [-h] [--name DB_NAME] [--overwrite FILENAME] 
                            [--no-clipboard] [--auto-reveal {on,off}] 
                            [--env-url-name VAR_NAME] [--env-token-name VAR_NAME] 
                            [--configure] [--delete-generation] [--delete-interactive]

Turso Database & Token Generator - Automate Turso DB tasks.

options:
  -h, --help            show this help message and exit
  --name DB_NAME        Custom name for the database. If not provided, Turso will generate a random name.
  --overwrite FILENAME  Filename (e.g., .env or .env.production) to update/create in project root.
  --no-clipboard        Skip copying credentials to the clipboard.
  --auto-reveal {on,off}
                        Automatically reveal secrets without prompting. Default: off
  --env-url-name VAR_NAME
                        Custom name for the database URL environment variable. Default: DATABASE_URL
  --env-token-name VAR_NAME
                        Custom name for the auth token environment variable. Default: TURSO_AUTH_TOKEN
  --configure           Open configuration menu to set preferences.

Deletion Options (use one at a time):
  --delete-generation   Delete the last database created by THIS script (uses state file).
  --delete-interactive  Interactively select and delete any of your Turso databases.
```

### Examples

```bash
# Generate a new database, display credentials, and copy to clipboard
python3 generate-turso-db.py

# Generate a new database and update/create '.env.local' in the project root
python3 generate-turso-db.py --overwrite .env.local

# Generate a new database but do not copy credentials to clipboard
python3 generate-turso-db.py --no-clipboard

# Create a database with a custom name
python3 generate-turso-db.py --name my-awesome-db

# Auto-reveal secrets without prompting
python3 generate-turso-db.py --auto-reveal on

# Use custom environment variable names
python3 generate-turso-db.py --env-url-name CUSTOM_DB_URL --env-token-name CUSTOM_AUTH_TOKEN
```

### Configuration

```bash
# Open interactive configuration menu to set preferences and disable prompts
python3 generate-turso-db.py --configure
```

### Deletion Commands

```bash
# Delete the last database specifically created by this script (if tracked)
python3 generate-turso-db.py --delete-generation

# Show an interactive menu to select and delete any of your Turso databases
python3 generate-turso-db.py --delete-interactive
```

## Features

- Creates Turso databases
- Generates auth tokens
- Masks credentials for security
- Copies to clipboard
- Beautiful terminal UI

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
