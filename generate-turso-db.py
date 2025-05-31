import subprocess
import re
import pyperclip
import argparse
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Script metadata (automatically updated by pre-commit hook)
SCRIPT_VERSION = "1.00"
LAST_UPDATED_TIMESTAMP = "2025-05-31 15:55:31 CEST"

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    PURPLE = '\033[35m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'

# Define a standard width for the content of all boxes
CONTENT_WIDTH = 60
STATE_FILE = Path.home() / ".turso_gen_state.json"

def print_ascii_header():
    """Print a beautiful ASCII header with version and update info."""
    # Prepare the version and timestamp line
    version_text = f"Version: {SCRIPT_VERSION}"
    last_updated_text = f"Last Updated: {LAST_UPDATED_TIMESTAMP}"
    
    # Combine with colors for display, but keep plain text for length calculation
    info_line_plain = f"{version_text}  {last_updated_text}"
    info_line_colored = f"{Colors.BOLD}{Colors.WHITE}{version_text}{Colors.ENDC}  {Colors.GRAY}{last_updated_text}{Colors.ENDC}"

    # Calculate visible length (without ANSI codes)
    visible_length = len(info_line_plain)
    
    # Calculate padding needed for centering
    if visible_length < CONTENT_WIDTH:
        total_padding = CONTENT_WIDTH - visible_length
        left_padding = total_padding // 2
        right_padding = total_padding - left_padding # Handles odd/even padding
    else:
        left_padding = 0
        right_padding = 0
        # If the text is too long, it won't be centered but will start from left.
        # Optionally, truncate info_line_colored if it's too long.
        # For now, we'll let it overflow if it's drastically longer than CONTENT_WIDTH.

    centered_info_line = f"{' ' * left_padding}{info_line_colored}{' ' * right_padding}"
    
    # If the centered_info_line (with padding but without outer box colors) is longer than CONTENT_WIDTH due to color codes,
    # we might need to adjust. However, the primary goal is to center the *visible* text.
    # The re.sub method is more robust for calculating visible length if colors were within version_text etc.
    # For this specific structure, direct length of plain parts is fine.

    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║{centered_info_line}{Colors.CYAN}║
║                                                              ║
║  {Colors.BOLD}{Colors.WHITE}        ████████╗██╗   ██╗██████╗ ███████╗ ██████╗{Colors.ENDC}{Colors.CYAN}          ║
║  {Colors.BOLD}{Colors.WHITE}        ╚══██╔══╝██║   ██║██╔══██╗██╔════╝██╔═══██╗{Colors.ENDC}{Colors.CYAN}         ║
║  {Colors.BOLD}{Colors.WHITE}           ██║   ██║   ██║██████╔╝███████╗██║   ██║{Colors.ENDC}{Colors.CYAN}         ║
║  {Colors.BOLD}{Colors.WHITE}           ██║   ██║   ██║██╔══██╗╚════██║██║   ██║{Colors.ENDC}{Colors.CYAN}         ║
║  {Colors.BOLD}{Colors.WHITE}           ██║   ╚██████╔╝██║  ██║███████║╚██████╔╝{Colors.ENDC}{Colors.CYAN}         ║
║  {Colors.BOLD}{Colors.WHITE}          ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝{Colors.ENDC}{Colors.CYAN}           ║
║                                                              ║
║           {Colors.BOLD}{Colors.YELLOW}🚀 Database Generator & Token Creator 🚀{Colors.ENDC}{Colors.CYAN}           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
""")

def print_step(step_num, total_steps, message):
    """Print a formatted step with progress indicator."""
    progress = "█" * step_num + "░" * (total_steps - step_num)
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}[{step_num}/{total_steps}]{Colors.ENDC} {Colors.CYAN}[{progress}]{Colors.ENDC} {Colors.BOLD}{message}{Colors.ENDC}")

def print_success(message):
    """Print a success message with checkmark."""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message with X mark."""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message with warning icon."""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    """Print an info message with info icon."""
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")

def print_section_divider(title):
    """Print a section divider with title, respecting CONTENT_WIDTH."""
    divider = "═" * CONTENT_WIDTH
    print(f"\n{Colors.PURPLE}╔{divider}╗")
    print(f"║{Colors.BOLD}{Colors.WHITE}{title.center(CONTENT_WIDTH)}{Colors.ENDC}{Colors.PURPLE}║")
    print(f"╚{divider}╝{Colors.ENDC}")

def print_env_vars_box(db_url, auth_token, db_name):
    """Print environment variables in a beautiful, perfectly aligned box."""
    print_section_divider("🔐 GENERATED CREDENTIALS")

    def create_padded_line(text_to_pad, total_width):
        # Calculate padding needed. Remove color codes for length calculation.
        plain_text = re.sub(r'\033\[[0-9;]*m', '', text_to_pad)
        padding = total_width - len(plain_text)
        return f"{text_to_pad}{' ' * max(0, padding)}" # Ensure padding is not negative

    line_title = create_padded_line(f"      {Colors.BOLD}{Colors.WHITE}DATABASE CREDENTIALS", CONTENT_WIDTH)
    line_db_name = create_padded_line(f" {Colors.BOLD}{Colors.WHITE}Database Name: {Colors.CYAN}{db_name}", CONTENT_WIDTH)
    line_created_at = create_padded_line(f" {Colors.BOLD}{Colors.WHITE}Created At:    {Colors.GRAY}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", CONTENT_WIDTH)
    
    # Ensure db_url and truncated_token are not longer than CONTENT_WIDTH - prefix_length
    db_url_display = db_url
    if len(db_url) > CONTENT_WIDTH - 1: # -1 for the leading space
        db_url_display = db_url[:CONTENT_WIDTH - 4] + "..."

    truncated_token = auth_token
    if len(auth_token) > 30: # Keep original truncation logic for token
        truncated_token = f"{auth_token[:30]}..."
    if len(truncated_token) > CONTENT_WIDTH -1:
        truncated_token = truncated_token[:CONTENT_WIDTH-4] + "..."


    line_db_url_val = create_padded_line(f" {Colors.YELLOW}{db_url_display}", CONTENT_WIDTH)
    line_auth_token_val = create_padded_line(f" {Colors.YELLOW}{truncated_token}", CONTENT_WIDTH)


    print(f"""
{Colors.BOLD}{Colors.OKGREEN}┌{'─' * CONTENT_WIDTH}┐
│{line_title}│
├{'─' * CONTENT_WIDTH}┤{Colors.ENDC}
{Colors.BOLD}{Colors.WHITE}│{line_db_name}│{Colors.ENDC}
{Colors.BOLD}{Colors.WHITE}│{line_created_at}│{Colors.ENDC}
{Colors.BOLD}{Colors.OKGREEN}├{'─' * CONTENT_WIDTH}┤{Colors.ENDC}
{Colors.BOLD}{Colors.WHITE}│ DB_URL: {' ' * (CONTENT_WIDTH - len("DB_URL: "))}│{Colors.ENDC}
{Colors.BOLD}{Colors.WHITE}│{line_db_url_val}│{Colors.ENDC}
{Colors.BOLD}{Colors.WHITE}│{' ' * CONTENT_WIDTH}│{Colors.ENDC}
{Colors.BOLD}{Colors.WHITE}│ AUTH_TOKEN: {' ' * (CONTENT_WIDTH - len("AUTH_TOKEN: "))}│{Colors.ENDC}
{Colors.BOLD}{Colors.WHITE}│{line_auth_token_val}│{Colors.ENDC}
{Colors.BOLD}{Colors.OKGREEN}└{'─' * CONTENT_WIDTH}┘{Colors.ENDC}
""")


def print_footer(db_name):
    """Print a beautiful, perfectly aligned footer."""
    line1_raw = "🎉 SUCCESS! Your Turso database is ready to use! 🎉"
    line2_raw = "📋 Credentials copied to clipboard"
    line3_raw = "🔧 Ready to paste into your .env file"
    line4_raw = "Much love xxx remcostoeten 💖" 

    line1 = f"{Colors.BOLD}{Colors.OKGREEN}{line1_raw}{Colors.ENDC}".center(CONTENT_WIDTH + len(f"{Colors.BOLD}{Colors.OKGREEN}{Colors.ENDC}") - len(line1_raw))
    line2 = f"{Colors.BOLD}{Colors.CYAN}{line2_raw}{Colors.ENDC}".center(CONTENT_WIDTH + len(f"{Colors.BOLD}{Colors.CYAN}{Colors.ENDC}") - len(line2_raw))
    line3 = f"{Colors.BOLD}{Colors.YELLOW}{line3_raw}{Colors.ENDC}".center(CONTENT_WIDTH + len(f"{Colors.BOLD}{Colors.YELLOW}{Colors.ENDC}") - len(line3_raw))
    line4 = f"{Colors.BOLD}{Colors.WHITE}{line4_raw}{Colors.ENDC}".center(CONTENT_WIDTH + len(f"{Colors.BOLD}{Colors.WHITE}{Colors.ENDC}") - len(line4_raw))

    # --- Logic for two-line delete command ---
    # Line 5a: Informational text
    text_5a_plain = "🗑️ To delete this DB, run:"
    text_5a_content_colored = f"{Colors.FAIL}{text_5a_plain}{Colors.ENDC}"
    padding_5a = CONTENT_WIDTH - len(text_5a_plain) # Use plain length for padding calculation
    # Construct the full content for line 5a to be placed between box borders
    # It starts with its own color, then padding, then PURPLE for the right border effect
    line5a_for_box = f"{text_5a_content_colored}{' ' * max(0, padding_5a)}{Colors.PURPLE}"

    # Line 5b: The command itself
    indent = "  " # Indentation for the command line
    script_name = os.path.basename(sys.argv[0])
    
    cmd_part1_plain = f"python {script_name}"
    cmd_part1_colored = f"{Colors.BOLD}{Colors.WHITE}{cmd_part1_plain}{Colors.ENDC}" # Command in bold white
    
    cmd_part2_plain = " --delete-generation"
    cmd_part2_colored = f"{Colors.FAIL}{cmd_part2_plain}{Colors.ENDC}" # Flag in fail color

    text_5b_plain_for_padding = f"{indent}{cmd_part1_plain}{cmd_part2_plain}" # Full plain text for padding
    text_5b_content_colored = f"{indent}{cmd_part1_colored}{cmd_part2_colored}" # Full colored command
    
    padding_5b = CONTENT_WIDTH - len(text_5b_plain_for_padding) # Use plain length for padding
    # Construct the full content for line 5b
    line5b_for_box = f"{text_5b_content_colored}{' ' * max(0, padding_5b)}{Colors.PURPLE}"
    # --- End of two-line delete command logic ---

    print(f"""
{Colors.PURPLE}╔{'═' * CONTENT_WIDTH}╗
║{line1}║
║{' ' * CONTENT_WIDTH}║
║{line2}║
║{line3}║
║{' ' * CONTENT_WIDTH}║
║{line5a_for_box}║ 
║{line5b_for_box}║ 
║{' ' * CONTENT_WIDTH}║
║{line4}║
╚{'═' * CONTENT_WIDTH}╝{Colors.ENDC}
""")

def run_command(command, timeout=30):
    """Run a shell command and return its output and error (if any)."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def save_last_generated_db(db_name):
    """Saves the last generated database name to a state file."""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({"last_generated_db": db_name}, f)
    except Exception as e:
        print_warning(f"Could not save state file: {e}")

def read_last_generated_db():
    """Reads the last generated database name from the state file."""
    if not STATE_FILE.exists():
        return None
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_generated_db")
    except (json.JSONDecodeError, IOError) as e:
        print_warning(f"Could not read state file: {e}")
        # Optionally, delete corrupted state file
        # STATE_FILE.unlink(missing_ok=True)
        return None

def delete_database(db_name):
    """Deletes a Turso database."""
    print_info(f"Attempting to delete database: {Colors.CYAN}{db_name}{Colors.ENDC}")
    command = f"turso db destroy {db_name} --yes" # --yes confirms deletion
    
    output, error, code = run_command(command, timeout=60)
    
    # Turso CLI might change its output format slightly.
    # Check for common success indicators.
    if code == 0 and (f"Destroyed database {db_name}" in output or "successfully deleted" in output.lower()):
        print_success(f"Successfully deleted database '{Colors.CYAN}{db_name}{Colors.ENDC}'")
        return True
    else:
        print_error(f"Failed to delete database '{Colors.CYAN}{db_name}{Colors.ENDC}'")
        # Provide more detailed error output from Turso CLI
        if error: print_error(f"Turso CLI Error: {error}")
        if output: print_info(f"Turso CLI Output: {output}")
        return False

def delete_last_generated_db():
    """Handler for the --delete-generation flag."""
    print_section_divider("🗑️ Delete Last Generated Database")
    db_name = read_last_generated_db()
    if not db_name:
        print_error("No previously generated database found to delete.")
        print_info(f"State file ({STATE_FILE}) not found, empty, or unreadable.")
        sys.exit(1)
    
    if delete_database(db_name):
        try:
            STATE_FILE.unlink() # Remove state file after successful deletion
            print_info("Cleared state file for the deleted database.")
        except OSError as e:
            print_warning(f"Could not remove state file {STATE_FILE}: {e}")
    else:
        sys.exit(1) # Exit if deletion failed

def interactive_delete():
    """Provides an interactive UI to delete databases."""
    print_section_divider("🗑️ Interactive Database Deletion")
    print_info("Fetching list of databases...")

    output, error, code = run_command("turso db list --json")
    if code != 0:
        print_error("Could not fetch database list.")
        if error: print_error(f"Turso CLI Error: {error}")
        sys.exit(1)

    try:
        data = json.loads(output)
        # The key might be 'databases' or 'dbs' depending on CLI version or if it's empty
        databases = data.get("databases", data.get("dbs", [])) 
    except (json.JSONDecodeError, KeyError) as e:
        print_error("Could not parse the list of databases.")
        print_info(f"Received output: {output}")
        print_error(f"Parsing error: {e}")
        sys.exit(1)

    if not databases:
        print_success("You have no databases to delete. All clear! ✨")
        sys.exit(0)

    print_info("Select databases to delete by typing their numbers, separated by spaces.")
    print_info(f"Example: '{Colors.YELLOW}1 3 4{Colors.ENDC}' to select databases 1, 3, and 4.")
    print("")

    for i, db_info in enumerate(databases):
        # Turso CLI output for db name can vary (e.g., 'Name' or 'name')
        db_name = db_info.get("Name", db_info.get("name", "N/A"))
        db_region = db_info.get("Region", db_info.get("region", "N/A"))
        print(f"  {Colors.BOLD}{Colors.WHITE}[{i+1}]{Colors.ENDC} {Colors.CYAN}{db_name}{Colors.ENDC} ({Colors.GRAY}Region: {db_region}{Colors.ENDC})")

    print("") 

    try:
        selection_str = input(f"{Colors.BOLD}{Colors.YELLOW}Enter numbers to delete (or press Enter to cancel): {Colors.ENDC}")
        if not selection_str.strip():
            print_info("Deletion cancelled by user.")
            sys.exit(0)

        selected_indices = []
        for item in selection_str.split():
            try:
                selected_indices.append(int(item) - 1)
            except ValueError:
                print_warning(f"Invalid input '{item}' skipped. Please enter numbers only.")
        
        dbs_to_delete_names = []
        valid_selections = False
        for i in selected_indices:
            if 0 <= i < len(databases):
                db_name_key = "Name" if "Name" in databases[i] else "name"
                dbs_to_delete_names.append(databases[i][db_name_key])
                valid_selections = True
            else:
                print_warning(f"Invalid selection number: {i+1}. Skipping.")
        
        if not valid_selections or not dbs_to_delete_names:
            print_error("No valid databases selected for deletion. Aborting.")
            sys.exit(1)

        print_section_divider("🚨 CONFIRM DELETION")
        print_warning("You are about to PERMANENTLY delete the following databases:")
        for db_name_to_delete in dbs_to_delete_names:
            print(f"  - {Colors.BOLD}{Colors.FAIL}{db_name_to_delete}{Colors.ENDC}")
        
        confirm = input(f"\n{Colors.BOLD}{Colors.YELLOW}Are you absolutely sure? This action cannot be undone. (yes/N): {Colors.ENDC}").strip().lower()

        if confirm == 'yes':
            print_info("Proceeding with deletion...")
            all_successful = True
            for db_name_to_delete in dbs_to_delete_names:
                if not delete_database(db_name_to_delete):
                    all_successful = False # Mark if any deletion fails
            if all_successful:
                print_success("Selected databases have been processed for deletion.")
            else:
                print_warning("Some databases could not be deleted. Check messages above.")
        else:
            print_info("Deletion aborted by user.")

    except ValueError: # Handles non-integer input if not caught by the loop
        print_error("Invalid input. Please enter numbers separated by spaces.")
        sys.exit(1)
    except KeyboardInterrupt:
        print_error("\nOperation cancelled by user.")
        sys.exit(1)


def check_dependencies():
    """Check if required dependencies are installed."""
    print_step(1, 6, "Checking system dependencies...")
    turso_output, turso_error, turso_code = run_command("turso --version")
    if turso_code != 0:
        print_error("Turso CLI is not installed or not in PATH!")
        print_info("Please install Turso CLI from: https://docs.turso.tech/reference/turso-cli")
        sys.exit(1)
    
    turso_version = turso_output.split('\n')[0] if turso_output else "Unknown version"
    print_success(f"Turso CLI found: {Colors.CYAN}{turso_version}{Colors.ENDC}")
    
    try:
        pyperclip.copy("test_clipboard_turso_gen") # Test with a unique string
        if pyperclip.paste() == "test_clipboard_turso_gen":
             print_success("Clipboard functionality available.")
        else:
            raise pyperclip.PyperclipException("Paste check failed")
    except Exception as e: # Catch broader exceptions for clipboard
        print_warning(f"Clipboard functionality might be limited or unavailable: {e}")
        print_info("For Linux, try: sudo apt-get install xclip or sudo apt-get install xsel")
        print_info("For macOS, clipboard access should be default.")
        print_info("For Windows, clipboard access should be default.")


def main():
    script_name = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
        description=f'{Colors.BOLD}{Colors.YELLOW}Turso Database & Token Generator{Colors.ENDC} - Automate Turso DB tasks.',
        formatter_class=argparse.RawTextHelpFormatter, # Allows for better formatting in help
        epilog=f"""
{Colors.BOLD}{Colors.WHITE}Examples:{Colors.ENDC}
  {Colors.CYAN}python {script_name}{Colors.ENDC}
    {Colors.GRAY}# Generate a new database, display credentials, and copy to clipboard.{Colors.ENDC}

  {Colors.CYAN}python {script_name} --overwrite .env.local{Colors.ENDC}
    {Colors.GRAY}# Generate a new database and update/create '.env.local' in the project root.{Colors.ENDC}

  {Colors.CYAN}python {script_name} --no-clipboard{Colors.ENDC}
    {Colors.GRAY}# Generate a new database but do not copy credentials to clipboard.{Colors.ENDC}

{Colors.BOLD}{Colors.FAIL}Deletion Commands:{Colors.ENDC}
  {Colors.CYAN}python {script_name} --delete-generation{Colors.ENDC}
    {Colors.GRAY}# Delete the last database specifically created by this script (if tracked).{Colors.ENDC}

  {Colors.CYAN}python {script_name} --delete-interactive{Colors.ENDC}
    {Colors.GRAY}# Show an interactive menu to select and delete any of your Turso databases.{Colors.ENDC}
        """
    )
    parser.add_argument('--overwrite', metavar='FILENAME', 
                       help='Filename (e.g., .env or .env.production) to update/create in project root.')
    parser.add_argument('--no-clipboard', action='store_true',
                       help='Skip copying credentials to the clipboard.')
    
    delete_group = parser.add_argument_group(f'{Colors.BOLD}{Colors.FAIL}Deletion Options{Colors.ENDC} (use one at a time)')
    delete_group.add_argument('--delete-generation', action='store_true',
                              help='Delete the last database created by THIS script (uses state file).')
    delete_group.add_argument('--delete-interactive', action='store_true',
                              help='Interactively select and delete any of your Turso databases.')

    args = parser.parse_args()

    if args.delete_generation:
        os.system('clear' if os.name == 'posix' else 'cls') # Clear screen for focused output
        delete_last_generated_db()
        sys.exit(0)

    if args.delete_interactive:
        os.system('clear' if os.name == 'posix' else 'cls')
        interactive_delete()
        sys.exit(0)

    os.system('clear' if os.name == 'posix' else 'cls')
    print_ascii_header()

    try:
        check_dependencies() # Checks Turso CLI and pyperclip

        # (Original script's find_project_root() and check_turso_auth() can be integrated here if needed)
        # For simplicity, assuming Turso auth is handled externally by user for now.
        # A basic auth check:
        print_step(2, 6, "Verifying Turso CLI authentication...")
        auth_output, auth_error, auth_code = run_command("turso auth status")
        if auth_code != 0 or "You are not logged in" in auth_output or "not authenticated" in auth_output.lower():
            print_error("Turso CLI authentication failed or you are not logged in.")
            print_info(f"Please run: {Colors.BOLD}turso auth login{Colors.ENDC}")
            sys.exit(1)
        whoami_output, _, _ = run_command("turso auth whoami")
        print_success(f"Turso CLI authentication verified (Logged in as: {Colors.CYAN}{whoami_output or 'user'}{Colors.ENDC}).")


        print_step(3, 6, "Creating new Turso database...")
        # Using retry_operation for robustness, assuming it's defined as in the original script
        # For now, direct call:
        create_output, create_error, create_code = run_command("turso db create", timeout=90) # Increased timeout
        if create_code != 0:
            print_error(f"Database creation failed: {create_error or 'Unknown error'}")
            sys.exit(1)
        
        db_name_match = re.search(r'(?:Created database|Database)\s+([\w-]+)', create_output) # More flexible regex
        if not db_name_match:
            print_error("Could not extract database name from Turso output.")
            print_info(f"Output: {create_output}")
            sys.exit(1)
        db_name = db_name_match.group(1)
        print_success(f"Database '{Colors.CYAN}{db_name}{Colors.ENDC}' created successfully!")
        save_last_generated_db(db_name)

        print_step(4, 6, "Retrieving database connection details...")
        show_output, show_error, show_code = run_command(f"turso db show {db_name}", timeout=60)
        if show_code != 0:
            print_error(f"Failed to get database details for {db_name}: {show_error}")
            sys.exit(1)

        url_match = re.search(r'URL:\s+(libsql://[\w.-]+)', show_output)
        if not url_match:
            print_error("Could not extract database URL from Turso output.")
            print_info(f"Output: {show_output}")
            sys.exit(1)
        db_url = url_match.group(1)
        print_success("Database URL retrieved.")

        print_step(5, 6, "Generating authentication token...")
        token_output, token_error, token_code = run_command(f"turso db tokens create {db_name}", timeout=60)
        if token_code != 0:
            print_error(f"Token creation failed for {db_name}: {token_error}")
            sys.exit(1)
        auth_token = token_output.strip() # Token is the direct output
        if not auth_token or len(auth_token) < 10: # Basic sanity check for token
            print_error("Generated token appears invalid or empty.")
            print_info(f"Output: {token_output}")
            sys.exit(1)
        print_success("Authentication token generated.")
        
        new_vars = {"DB_URL": db_url, "AUTH_TOKEN": auth_token}
        env_vars_string_for_clipboard = f"DB_URL={db_url}\nAUTH_TOKEN={auth_token}"

        print_env_vars_box(db_url, auth_token, db_name)

        print_step(6, 6, "Finalizing setup...")
        if args.overwrite:
            # Using a simplified version of original script's project root detection
            project_root = Path.cwd() # Default to current directory
            # Try to find a .git directory to define project root
            current_dir_check = Path.cwd()
            while current_dir_check != current_dir_check.parent: # Stop at system root
                if (current_dir_check / ".git").is_dir():
                    project_root = current_dir_check
                    print_info(f"Project root identified at: {Colors.CYAN}{project_root}{Colors.ENDC}")
                    break
                current_dir_check = current_dir_check.parent
            
            env_file_path = project_root / args.overwrite
            
            # Simplified update/append logic (original script's update_env_file is more robust)
            try:
                # Ensure directory exists
                env_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                mode = 'a' if env_file_path.exists() else 'w'
                with open(env_file_path, mode) as f:
                    if mode == 'a': f.write("\n\n# Turso Credentials (added by script)\n")
                    else: f.write("# Turso Credentials (generated by script)\n")
                    f.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"DB_URL={db_url}\n")
                    f.write(f"AUTH_TOKEN={auth_token}\n")
                print_success(f"Environment variables {'appended to' if mode == 'a' else 'written to'} {Colors.CYAN}{env_file_path}{Colors.ENDC}")
            except IOError as e:
                print_error(f"Could not write to {env_file_path}: {e}")
        else:
            print_info(f"To save credentials to a file, use: {Colors.BOLD}--overwrite FILENAME{Colors.ENDC}")

        if not args.no_clipboard:
            try:
                pyperclip.copy(env_vars_string_for_clipboard)
                print_success("Environment variables copied to clipboard!")
            except Exception as e: # Catch broader pyperclip errors
                print_warning(f"Could not copy to clipboard: {e}")
                print_info("You can manually copy the credentials from the box above.")
        
        print_footer(db_name)

    except KeyboardInterrupt:
        print_error("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        # For debugging, you might want to print the full traceback
        # import traceback
        # print_error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
