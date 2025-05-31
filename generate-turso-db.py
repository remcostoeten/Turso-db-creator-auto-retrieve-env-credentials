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

def print_ascii_header():
    """Print a beautiful ASCII header."""
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
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

    # Helper to create a line with content padded to the correct width
    def create_padded_line(text, total_width):
        # Calculates visible length by removing color codes, then gets padding
        padding = total_width - len(re.sub(r'\033\[[0-9;]*m', '', text))
        return f"{text}{' ' * padding}"

    created_at_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Prepare each line's content
    line_title = create_padded_line(f"      {Colors.BOLD}{Colors.WHITE}DATABASE CREDENTIALS", CONTENT_WIDTH)
    line_db_name = create_padded_line(f" {Colors.BOLD}{Colors.WHITE}Database Name: {Colors.CYAN}{db_name}", CONTENT_WIDTH)
    line_created_at = create_padded_line(f" {Colors.BOLD}{Colors.WHITE}Created At:    {Colors.GRAY}{created_at_time}", CONTENT_WIDTH)
    line_db_url_val = create_padded_line(f" {Colors.YELLOW}{db_url}", CONTENT_WIDTH)
    line_auth_token_val = create_padded_line(f" {Colors.YELLOW}{auth_token[:30]}...", CONTENT_WIDTH)

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

def print_footer():
    """Print a beautiful, perfectly aligned footer."""
    line1 = f"{Colors.BOLD}{Colors.OKGREEN}🎉 SUCCESS! Your Turso database is ready to use! 🎉{Colors.ENDC}".center(CONTENT_WIDTH + len(f"{Colors.BOLD}{Colors.OKGREEN}{Colors.ENDC}"))
    line2 = f"{Colors.BOLD}{Colors.CYAN}📋 Credentials copied to clipboard{Colors.ENDC}".center(CONTENT_WIDTH + len(f"{Colors.BOLD}{Colors.CYAN}{Colors.ENDC}"))
    line3 = f"{Colors.BOLD}{Colors.YELLOW}🔧 Ready to paste into your .env file{Colors.ENDC}".center(CONTENT_WIDTH + len(f"{Colors.BOLD}{Colors.YELLOW}{Colors.ENDC}"))
    line4 = f"{Colors.BOLD}{Colors.WHITE}Much love xxx remcostoeten 💖{Colors.ENDC}".center(CONTENT_WIDTH + len(f"{Colors.BOLD}{Colors.WHITE}{Colors.ENDC}"))

    print(f"""
{Colors.PURPLE}╔{'═' * CONTENT_WIDTH}╗
║{line1}║
║{' ' * CONTENT_WIDTH}║
║{line2}║
║{line3}║
║{' ' * CONTENT_WIDTH}║
║{line4}║
║{' ' * CONTENT_WIDTH}║
╚{'═' * CONTENT_WIDTH}╝{Colors.ENDC}
""")

def run_command(command, timeout=30):
    """Run a shell command and return its output and error (if any)."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def check_dependencies():
    """Check if required dependencies are installed, with interactive install."""
    print_step(1, 6, "Checking system dependencies...")
    
    # Check if turso CLI is installed
    turso_output, turso_error, turso_code = run_command("turso --version")
    
    if turso_code != 0:
        print_error("Turso CLI is not installed!")
        try:
            choice = input(f"{Colors.WARNING}❓ Would you like this script to try and install it for you? (y/n): {Colors.ENDC}").lower()
        except KeyboardInterrupt:
            print_error("\nOperation cancelled.")
            sys.exit(1)
            
        if choice == 'y':
            print_info("Attempting installation...")
            install_command = ""
            platform = sys.platform

            if platform == "linux" or platform == "darwin": # Linux or macOS
                install_command = "curl -sSfL https://get.tur.so/install.sh | bash"
                print_info(f"Running command: {install_command}")
                try:
                    # Run the installer script
                    subprocess.run(install_command, shell=True, check=True)
                    print_success("Installation script finished!")
                    print_warning("Please re-run this script in a new terminal window to continue.")
                    sys.exit(0)
                except subprocess.CalledProcessError as e:
                    print_error(f"Installation failed: {e}")
                    print_info("Please install Turso CLI manually from: https://docs.turso.tech/reference/turso-cli")
                    sys.exit(1)

            elif platform == "win32": # Windows
                print_info("On Windows, please run one of the following commands in PowerShell:")
                print_info(f"  {Colors.CYAN}winget install turso.turso{Colors.ENDC}")
                print_info(f"  {Colors.CYAN}scoop install turso{Colors.ENDC}")
                print_warning("After installation, please re-run this script in a new terminal window.")
                sys.exit(1)
            else:
                print_error(f"Unsupported OS: {platform}")
                print_info("Please install Turso CLI manually from: https://docs.turso.tech/reference/turso-cli")
                sys.exit(1)
        else:
            print_error("Cannot continue without Turso CLI.")
            sys.exit(1)

    turso_version = turso_output.split('\n')[0] if turso_output else "Unknown version"
    print_success(f"Turso CLI found: {Colors.CYAN}{turso_version}{Colors.ENDC}")
    
    # Check if pyperclip works (clipboard functionality)
    try:
        pyperclip.copy("test")
        print_success("Clipboard functionality available")
    except Exception as e:
        print_warning(f"Clipboard may not work: {e}")
        print_info("Install xclip (Linux) or ensure clipboard access is available")


def validate_database_name(db_name):
    """Validate database name format."""
    if not db_name or len(db_name) < 3:
        return False
    # Turso database names should be alphanumeric with hyphens
    if not re.match(r'^[a-zA-Z0-9-]+$', db_name):
        return False
    return True

def update_env_file(file_path, new_vars):
    """Update .env file with new variables, backing up and validating."""
    backup_path = backup_env_file(file_path)
    try:
        if not os.path.exists(file_path):
            print_info(f"Creating new file: {file_path}")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write('# Turso Database Configuration\n')
                f.write(f'# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                f.write('\n'.join(f"{k}={v}" for k, v in new_vars.items()))
                f.write('\n')
            return
        with open(file_path, 'r') as f:
            lines = f.readlines()
        updated_lines = []
        updated = {key: False for key in new_vars.keys()}
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith('#') or not line_stripped:
                updated_lines.append(line.rstrip())
                continue
            if '=' in line_stripped:
                key = line_stripped.split('=')[0].strip()
                if key in new_vars and not updated[key]:
                    updated_lines.append(f'# OLD: {line.rstrip()}')
                    updated_lines.append(f'{key}={new_vars[key]}')
                    updated[key] = True
                else:
                    updated_lines.append(line.rstrip())
            else:
                updated_lines.append(line.rstrip())
        for key, value in new_vars.items():
            if not updated[key]:
                updated_lines.append('')
                updated_lines.append(f'# Added by Turso script on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                updated_lines.append(f'{key}={value}')
        with open(file_path, 'w') as f:
            f.write('\n'.join(updated_lines) + '\n')
        print_success(f"Successfully updated {file_path}")
    except Exception as e:
        print_error(f"Failed to update .env file: {e}")
        if backup_path and os.path.exists(backup_path):
            print_info(f"Backup available at: {backup_path}")
        raise

def find_project_root():
    """Find the project root by looking for common project files."""
    current_dir = Path.cwd()
    root_indicators = ['.git', 'pyproject.toml', 'package.json', 'Cargo.toml', 'go.mod', '.env', '.env.local', 'requirements.txt', 'composer.json']
    for parent in [current_dir] + list(current_dir.parents):
        for indicator in root_indicators:
            if (parent / indicator).exists():
                print_success(f"Project root detected: {Colors.CYAN}{parent}{Colors.ENDC} (found .git)")
                return str(parent)
    print_warning("No project root indicators found, using current directory")
    return str(current_dir)

def check_turso_auth():
    """Check if the user is authenticated with Turso CLI."""
    print_step(2, 6, "Verifying Turso CLI authentication...")
    def auth_check():
        output, error, code = run_command("turso auth status")
        if code != 0: raise Exception(f"Auth status check failed: {error}")
        if "You are not logged in" in output or "not authenticated" in output.lower(): raise Exception("Not authenticated with Turso CLI")
        return output
    try:
        retry_operation(auth_check, max_retries=2)
        print_success("Turso CLI authentication verified!")
        user_info, _, user_code = run_command("turso auth whoami")
        if user_code == 0 and user_info: print_info(f"Authenticated as: {Colors.CYAN}{user_info}{Colors.ENDC}")
    except Exception as e:
        print_error("Authentication failed!")
        print_info(f"Please run: {Colors.BOLD}turso auth login{Colors.ENDC}")
        sys.exit(1)

def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    print_ascii_header()
    parser = argparse.ArgumentParser(description='Generate Turso DB credentials and update .env file.', formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""
Examples:
  python turso_gen.py                           # Generate credentials only
  python turso_gen.py --overwrite .env         # Update .env file
  python turso_gen.py --overwrite .env.local   # Update .env.local file
        """)
    parser.add_argument('--overwrite', metavar='PATH', help='Path to .env or .env.local file to overwrite')
    parser.add_argument('--no-clipboard', action='store_true', help='Skip copying to clipboard')
    args = parser.parse_args()
    try:
        check_dependencies()
        project_root = find_project_root()
        check_turso_auth()
        print_step(3, 6, "Creating new Turso database...")
        def create_db():
            output, error, code = run_command("turso db create", timeout=60)
            if code != 0: raise Exception(f"Database creation failed: {error}")
            return output, error, code
        create_output, _, _ = retry_operation(create_db)
        db_name_match = re.search(r'Created database (\S+)', create_output)
        if not db_name_match:
            print_error(f"Could not extract database name from output: {create_output}")
            sys.exit(1)
        db_name = db_name_match.group(1).strip("'")
        if not validate_database_name(db_name):
            print_error(f"Invalid database name format: {db_name}")
            sys.exit(1)
        print_success(f"Database '{Colors.CYAN}{db_name}{Colors.ENDC}' created successfully!")
        print_step(4, 6, "Retrieving database connection details...")
        def get_db_details():
            output, error, code = run_command(f"turso db show {db_name}")
            if code != 0: raise Exception(f"Failed to get database details: {error}")
            return output, error, code
        show_output, _, _ = retry_operation(get_db_details)
        url_match = re.search(r'URL:\s+(libsql://[\w.-]+)', show_output)
        if not url_match:
            print_error(f"Could not extract database URL from output: {show_output}")
            sys.exit(1)
        db_url = url_match.group(1)
        if not validate_url(db_url):
            print_error(f"Invalid database URL format: {db_url}")
            sys.exit(1)
        print_success("Database URL retrieved and validated!")
        print_step(5, 6, "Generating authentication token...")
        def create_token():
            output, error, code = run_command(f"turso db tokens create {db_name}")
            if code != 0: raise Exception(f"Token creation failed: {error}")
            return output, error, code
        token_output, _, _ = retry_operation(create_token)
        auth_token = token_output.strip()
        if not validate_token(auth_token):
            print_error(f"Generated token appears to be invalid: {auth_token[:20]}...")
            sys.exit(1)
        print_success("Authentication token generated and validated!")
        new_vars = {"DB_URL": db_url, "AUTH_TOKEN": auth_token}
        env_vars = f"DB_URL={db_url}\nAUTH_TOKEN={auth_token}"
        print_env_vars_box(db_url, auth_token, db_name)
        print_step(6, 6, "Finalizing setup...")
        if args.overwrite:
            env_file_path = os.path.join(project_root, args.overwrite)
            check_existing_credentials(env_file_path)
            update_env_file(env_file_path, new_vars)
            print_success(f"Environment variables updated in {Colors.CYAN}{args.overwrite}{Colors.ENDC}")
        else:
            print_info("No overwrite path provided. Environment variables will not be saved to a file.")
            print_info(f"To save to file, use: {Colors.BOLD}--overwrite .env{Colors.ENDC}")
        if not args.no_clipboard:
            try:
                pyperclip.copy(env_vars)
                print_success("Environment variables copied to clipboard!")
            except Exception as e:
                print_warning(f"Could not copy to clipboard: {e}")
                print_info("You can manually copy the credentials from above")
        print_footer()
    except KeyboardInterrupt:
        print_error("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        sys.exit(1)

def validate_token(token):
    return token and len(token.split('.')) == 3

def validate_url(url):
    return url and url.startswith('libsql://') and 'turso.io' in url

def backup_env_file(file_path):
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup.{int(time.time())}"
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            print_success(f"Backup created: {Colors.CYAN}{backup_path}{Colors.ENDC}")
            return backup_path
        except Exception as e:
            print_warning(f"Could not create backup: {e}")
    return None

def check_existing_credentials(file_path):
    if not os.path.exists(file_path): return False
    try:
        with open(file_path, 'r') as f: content = f.read()
        if 'DB_URL=' in content or 'AUTH_TOKEN=' in content:
            print_warning("Existing credentials found in .env file! They will be commented out.")
            return True
    except Exception as e:
        print_warning(f"Could not read existing .env file: {e}")
    return False

def retry_operation(operation, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1: raise e
            print_warning(f"Attempt {attempt + 1} failed. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
    return None

if __name__ == "__main__":
    main()
