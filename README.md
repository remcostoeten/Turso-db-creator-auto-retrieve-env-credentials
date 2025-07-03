# Turso Database & Token Generator

A Python script to automate the creation of Turso databases, generate authentication tokens, and manage these databases. It features automatic versioning and timestamp updates via Git pre-commit hooks.

## Features

- **Automated Database Creation**: Quickly creates a new Turso database.
- **Token Generation**: Automatically generates an authentication token for the new database.
- **Credential Display**: Shows the generated DB_URL and AUTH_TOKEN in a formatted box.
- **Clipboard Integration**: Copies the credentials to the clipboard (requires pyperclip and a clipboard tool like xclip or xsel on Linux).
- **.env File Update**: Optionally updates a specified .env file (e.g., .env, .env.local) with the new credentials.
- **Database Deletion**:
  - `--delete-generation`: Deletes the last database created by this script (tracks via a local state file).
  - `--delete-interactive`: Provides an interactive menu to list and delete any of your Turso databases.
- **Automatic Versioning**: Script version and "Last Updated" timestamp are automatically updated in the script's header on each Git commit using a pre-commit hook.
- **User-Friendly CLI**: Colored output, progress steps, and clear instructions.

## Prerequisites

- **Python 3**: Ensure Python 3 is installed on your system.
- **Turso CLI**: The Turso CLI must be installed and authenticated.
  - **Installation**: [Turso CLI Documentation](https://docs.turso.tech/cli)
  - **Login**: Run `turso auth login`
- **Pyperclip**: For clipboard functionality.
  - **Install via pip**: `pip install pyperclip`
- **Clipboard Tool (Linux)**: If you are on Linux and want clipboard functionality, you'll need xclip or xsel.
  - **Install xclip**: `sudo apt-get install xclip` (or your distribution's equivalent)
  - **Install xsel**: `sudo apt-get install xsel` (or your distribution's equivalent)

## Script Naming

For the Git pre-commit hook and examples below to work as intended, it's assumed your Python script is named `generate-turso-db.py`. If you've named it differently, please adjust the script name in the hook and commands accordingly.

## Usage

### 1. Generate Database & Credentials

To generate a new database, display credentials, and copy them to the clipboard:

```bash
python generate-turso-db.py
```

### 2. Update .env File

To generate a new database and update (or create) an .env file (e.g., .env.local) in your project root:

```bash
python generate-turso-db.py --overwrite .env.local
```

The script attempts to find your project root (e.g., by looking for a .git directory). The .env file will be placed there.

### 3. Skip Clipboard

To generate credentials without copying them to the clipboard:

```bash
python generate-turso-db.py --no-clipboard
```

### 4. Delete Last Generated Database

To delete the database that was last created by this script (this uses a state file `~/.turso_gen_state.json` to remember the last DB):

```bash
python generate-turso-db.py --delete-generation
```

### 5. Interactively Delete Databases

To see a list of all your Turso databases and choose one or more to delete interactively:

```bash
python generate-turso-db.py --delete-interactive
```

You will be prompted to select databases by number and confirm the deletion.

### 6. Help

To see all available options and examples:

```bash
python generate-turso-db.py --help
```

## Automatic Versioning & Timestamp (Git Pre-Commit Hook)

The script is designed to have its `SCRIPT_VERSION` and `LAST_UPDATED_TIMESTAMP` variables updated automatically with each Git commit.

### How it Works

The Python script (`generate-turso-db.py`) contains two global variables:

```python
SCRIPT_VERSION = "current_version_number"
LAST_UPDATED_TIMESTAMP = "timestamp_of_last_commit"
```

1. A Git pre-commit hook (a shell script) runs before each commit.
2. This hook reads the current `SCRIPT_VERSION`, increments it by 0.01.
3. It gets the current date and time for `LAST_UPDATED_TIMESTAMP`.
4. It then updates these values directly within the `generate-turso-db.py` file.
5. The modified `generate-turso-db.py` is then automatically added to the commit.

### Setting up the Pre-Commit Hook

1. **Navigate to your Git hooks directory:**
   In your repository, go to `.git/hooks/`.

2. **Create the pre-commit file:**
   If it doesn't exist, create a file named `pre-commit` (no extension).

   ```bash
   touch .git/hooks/pre-commit
   ```

3. **Make it executable:**

   ```bash
   chmod +x .git/hooks/pre-commit
   ```

4. **Add the hook script content:**
   Open `.git/hooks/pre-commit` in a text editor and paste the following shell script. Ensure `PYTHON_SCRIPT_NAME` matches your Python script's filename.

```bash
#!/bin/sh

# The name of your Python script
PYTHON_SCRIPT_NAME="generate-turso-db.py"
# Path to the Python script relative to the repository root
PYTHON_SCRIPT_PATH="./${PYTHON_SCRIPT_NAME}"

# --- Ensure script exists ---
if [ ! -f "$PYTHON_SCRIPT_PATH" ]; then
    echo "Error: Python script '$PYTHON_SCRIPT_PATH' not found. Pre-commit hook skipped."
    exit 0 # Exit 0 to allow commit if script is not relevant or temporarily removed
fi

# --- Ensure placeholder lines exist in the Python script ---
grep -q '^SCRIPT_VERSION = ' "$PYTHON_SCRIPT_PATH" || \
    sed -i.bak -e '1a\
SCRIPT_VERSION = "0.99" # Initial value, will become 1.00 on first commit
' "$PYTHON_SCRIPT_PATH" && rm "${PYTHON_SCRIPT_PATH}.bak"


grep -q '^LAST_UPDATED_TIMESTAMP = ' "$PYTHON_SCRIPT_PATH" || \
    sed -i.bak -e '1a\
LAST_UPDATED_TIMESTAMP = "Pending first commit" # Placeholder
' "$PYTHON_SCRIPT_PATH" && rm "${PYTHON_SCRIPT_PATH}.bak"


# --- Version Update ---
current_version_line=$(grep '^SCRIPT_VERSION = ' "$PYTHON_SCRIPT_PATH")
current_version_str=$(echo "$current_version_line" | sed -n 's/.*SCRIPT_VERSION = "\([^"]*\)".*/\1/p')

if ! echo "$current_version_str" | grep -qE '^[0-9]+\.[0-9]+$'; then
    current_version_str="0.99" # Default if extraction fails or format is wrong
fi
new_version=$(awk -v ver="$current_version_str" 'BEGIN { printf "%.2f", ver + 0.01 }')

# Update SCRIPT_VERSION line using awk for robustness with various sed versions
awk -v new_ver="\"$new_version\"" '/^SCRIPT_VERSION = / { $0 = "SCRIPT_VERSION = " new_ver } 1' "$PYTHON_SCRIPT_PATH" > "${PYTHON_SCRIPT_PATH}.tmp" && \
mv "${PYTHON_SCRIPT_PATH}.tmp" "$PYTHON_SCRIPT_PATH"


# --- Timestamp Update ---
current_timestamp=$(date +"%Y-%m-%d %H:%M:%S %Z")

# Update LAST_UPDATED_TIMESTAMP line using awk
awk -v new_ts="\"$current_timestamp\"" '/^LAST_UPDATED_TIMESTAMP = / { $0 = "LAST_UPDATED_TIMESTAMP = " new_ts } 1' "$PYTHON_SCRIPT_PATH" > "${PYTHON_SCRIPT_PATH}.tmp" && \
mv "${PYTHON_SCRIPT_PATH}.tmp" "$PYTHON_SCRIPT_PATH"

# Add the modified Python script to the staging area
git add "$PYTHON_SCRIPT_PATH"

exit 0
```

**Note on the hook script:**

- The sed commands for adding missing lines are basic; for more complex scripts, ensure they are inserted appropriately. The awk commands for updating are generally more robust across different sed versions for in-place replacement.
- The hook exits 0 even if the script isn't found to prevent blocking commits if the script is intentionally removed or renamed without updating the hook.

### Initial Script Variables

Ensure your Python script (`generate-turso-db.py`) initially contains these lines near the top (the hook will also try to add them if missing):

```python
# Script metadata (automatically updated by pre-commit hook)
SCRIPT_VERSION = "0.99" # Initial value, will become 1.00 on first commit
LAST_UPDATED_TIMESTAMP = "Pending first commit" # Placeholder
```

Now, each time you run `git commit`, the hook will update these values in your Python script, and the changes will be included in the commit. The ASCII header in the script's output will then reflect the latest version and update time.

## Script Output

The script uses colored output for better readability:

- **Steps**: Blue/Cyan
- **Success**: Green
- **Error**: Red
- **Warning**: Yellow
- **Info**: Cyan/Blue
- **Section Dividers**: Purple

The main generated credentials and the footer also use various colors to highlight important information.

## Troubleshooting

### Turso CLI Errors
Ensure Turso CLI is installed, in your PATH, and you are logged in (`turso auth login`).

### Clipboard Errors
- Make sure `pyperclip` is installed (`pip install pyperclip`).
- On Linux, ensure `xclip` or `xsel` is installed.
- If clipboard access is denied (e.g., in some remote environments), use the `--no-clipboard` flag.

### File Permissions
- Ensure the script has execute permissions if you run it directly (`chmod +x generate-turso-db.py`).
- Ensure you have write permissions for the .env file and the state file (`~/.turso_gen_state.json`).

### Pre-Commit Hook Not Running
- Verify the hook file is named `pre-commit` (no extension) in `.git/hooks/`.
- Ensure it has execute permissions (`chmod +x .git/hooks/pre-commit`).
- Check for any errors output by the hook during `git commit`.

### Version/Timestamp Not Updating
- Double-check the `PYTHON_SCRIPT_NAME` in the pre-commit hook script.
- Ensure the `SCRIPT_VERSION` and `LAST_UPDATED_TIMESTAMP` variable lines exist in your Python script exactly as the hook expects them (e.g., `SCRIPT_VERSION = "1.00"`).

---

This README should provide a comprehensive guide for users of your script.