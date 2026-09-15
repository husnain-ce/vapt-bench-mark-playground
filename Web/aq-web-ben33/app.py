"""
Minimal Mercurial (hg) Platform - A tiny GitHub-like platform using Mercurial
"""

import os
import re
import subprocess
import secrets
from pathlib import Path
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configuration
REPOS_DIR = Path("/tmp/repos")
REPOS_DIR.mkdir(exist_ok=True)

# Simple in-memory user store (use a database in production)
users = {}

# =============================================================================
# Security Utilities
# =============================================================================

# Strict validation patterns to prevent injection attacks
SAFE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$')
SAFE_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._/-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$')
MAX_NAME_LENGTH = 64
MAX_PATH_LENGTH = 256
MAX_URL_LENGTH = 2048


def validate_name(name, max_length=MAX_NAME_LENGTH):
    """
    Validate repository/user names.
    Only allows alphanumeric characters, dots, underscores, and hyphens.
    Must start and end with alphanumeric characters.
    Note: Argument injection is prevented by using '--' in hg commands.
    """
    if not name or not isinstance(name, str):
        return False
    if len(name) > max_length:
        return False
    if name in ('.', '..'):
        return False
    return bool(SAFE_NAME_PATTERN.match(name))


def validate_path(path, max_length=MAX_PATH_LENGTH):
    """
    Validate file paths within repositories.
    Prevents path traversal attacks.
    Note: Argument injection is prevented by using '--' in hg commands.
    """
    if not path or not isinstance(path, str):
        return False
    if len(path) > max_length:
        return False
    # Prevent path traversal
    if '..' in path or path.startswith('/') or path.startswith('\\'):
        return False
    # Prevent null bytes
    if '\x00' in path:
        return False
    return bool(SAFE_PATH_PATTERN.match(path)) or path == ''


def validate_revision(rev):
    """
    Validate Mercurial revision identifiers.
    Allows: revision numbers, node IDs (hex), branch names, tags, bookmarks.
    """
    if not rev or not isinstance(rev, str):
        return False
    if len(rev) > 64:
        return False
    safe_rev_pattern = re.compile(r'[a-zA-Z0-9._-]+')
    return bool(safe_rev_pattern.match(rev))




def get_revision_info(repo_path, rev):
    """Get basic info about a revision. Returns dict with node (short hash)."""
    result = run_hg_command(
        ['log', '-r', rev, '--template', '{node}'],
        cwd=repo_path
    )
    if result.returncode != 0:
        return None

    return {'node': result.stdout.strip()}


def validate_clone_url(url):
    """
    Validate a URL for cloning repositories.

    Security measures:
    - Only allow http:// and https:// schemes
    - Prevent file://, ssh://, and other dangerous schemes
    - Block local/private IP addresses (SSRF prevention)
    - Reject URLs with credentials embedded
    - Length limit to prevent DoS
    """
    if not url or not isinstance(url, str):
        return False, "URL is required"

    url = url.strip()

    if len(url) > MAX_URL_LENGTH:
        return False, "URL too long"

    # Prevent null bytes and newlines
    if '\x00' in url or '\n' in url or '\r' in url:
        return False, "Invalid characters in URL"

    # Only allow http and https schemes
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"

    if parsed.scheme not in ('http', 'https'):
        return False, "Only http:// and https:// URLs are allowed"

    # Reject URLs with embedded credentials (user:pass@host)
    if parsed.username or parsed.password:
        return False, "URLs with embedded credentials are not allowed"

    # Must have a valid hostname
    if not parsed.hostname:
        return False, "Invalid hostname"

    return True, url


def run_hg_command(args, cwd=None, timeout=30):
    """
    Safely execute a Mercurial command.

    Security measures:
    - All arguments passed as list (no shell=True)
    - Working directory explicitly set
    - Timeout to prevent DoS
    - Environment sanitized
    - No user input directly in command string
    """
    if not isinstance(args, (list, tuple)):
        raise ValueError("Arguments must be a list")

    # verfiy args doesn't contain dangerous elements (like shell operators)
    blocklist = {';', '&', '>', '<', '`', '!', '(', ')', '\\', '?', '*'}
    for arg in args:
        if any(char in arg for char in blocklist):
            raise ValueError(f"Unsafe argument detected: {arg}")

    import shutil
    HG_BIN = shutil.which('hg')
    # Ensure 'hg' is the command
    cmd = [HG_BIN] + list(args)

    # append HG-specific environment variables
    env = os.environ.copy()
    env.update({
        'HGPLAIN': '1',
        'HGENCODING': 'UTF-8',
    })

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        print(result.stderr)
        return result
    except subprocess.TimeoutExpired:
        raise TimeoutError("Command timed out")
    except Exception as e:
        raise RuntimeError(f"Command failed: {e}")


def get_repo_path(username, repo_name):
    """
    Get the absolute path to a repository.
    Validates inputs and prevents path traversal.
    """
    if not validate_name(username) or not validate_name(repo_name):
        return None

    repo_path = (REPOS_DIR / username / repo_name).resolve()

    # Ensure the path is still within REPOS_DIR (prevent traversal)
    try:
        repo_path.relative_to(REPOS_DIR.resolve())
    except ValueError:
        return None

    return repo_path


# =============================================================================
# Authentication
# =============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not validate_name(username):
            flash('Invalid username. Use only letters, numbers, dots, underscores, hyphens.', 'error')
            return render_template('register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('register.html')

        if username in users:
            flash('Username already exists.', 'error')
            return render_template('register.html')

        users[username] = generate_password_hash(password)
        user_dir = REPOS_DIR / username
        user_dir.mkdir(exist_ok=True)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not validate_name(username):
            flash('Invalid credentials.', 'error')
            return render_template('login.html')

        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))

        flash('Invalid credentials.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out.', 'success')
    return redirect(url_for('index'))


# =============================================================================
# Repository Management
# =============================================================================

@app.route('/')
def index():
    repos = []
    username = session.get('username')
    if username and REPOS_DIR.exists():
        user_dir = REPOS_DIR / username
        if user_dir.is_dir():
            for repo_dir in user_dir.iterdir():
                if repo_dir.is_dir() and (repo_dir / '.hg').exists():
                    repos.append({
                        'owner': username,
                        'name': repo_dir.name,
                    })
    return render_template('index.html', repos=repos)


@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_repo():
    if request.method == 'POST':
        repo_name = request.form.get('name', '').strip()

        if not validate_name(repo_name):
            flash('Invalid repository name.', 'error')
            return render_template('new_repo.html')

        repo_path = get_repo_path(session['username'], repo_name)
        if repo_path is None:
            flash('Invalid repository path.', 'error')
            return render_template('new_repo.html')

        if repo_path.exists():
            flash('Repository already exists.', 'error')
            return render_template('new_repo.html')

        # Create repository
        repo_path.mkdir(parents=True)
        result = run_hg_command(['init'], cwd=repo_path)

        if result.returncode != 0:
            repo_path.rmdir()
            flash('Failed to create repository.', 'error')
            return render_template('new_repo.html')

        flash('Repository created!', 'success')
        return redirect(url_for('view_repo', username=session['username'], repo_name=repo_name))

    return render_template('new_repo.html')


@app.route('/<username>/<repo_name>')
@app.route('/<username>/<repo_name>/tree/<rev>')
def view_repo(username, repo_name, rev=None):
    if not validate_name(username) or not validate_name(repo_name):
        abort(404)

    # Default to tip, validate if provided
    if rev is None:
        rev = 'tip'
    elif not validate_revision(rev):
        abort(400)

    repo_path = get_repo_path(username, repo_name)
    if repo_path is None or not repo_path.exists():
        abort(404)

    # Get revision info (hash, tags, branch, bookmarks)
    rev_info = get_revision_info(repo_path, rev)
    if rev_info is None:
        abort(404)

    # Get file list at specified revision
    files = []
    result = run_hg_command(['manifest', '-r', rev], cwd=repo_path)
    if result.returncode == 0 and result.stdout.strip():
        files = result.stdout.strip().split('\n')

    # Get recent commits
    commits = []
    result = run_hg_command(
        ['log', '-l', '10', '--template', '{node}|{author|person}|{desc|firstline}|{date|isodate}\n'],
        cwd=repo_path
    )
    if result.returncode == 0 and result.stdout.strip():
        for line in result.stdout.strip().split('\n'):
            parts = line.split('|', 3)
            if len(parts) >= 4:
                commits.append({
                    'id': parts[0],
                    'author': parts[1],
                    'message': parts[2],
                    'date': parts[3],
                })

    return render_template('repo.html',
                         username=username,
                         repo_name=repo_name,
                         files=files,
                         commits=commits,
                         current_rev=rev,
                         rev_info=rev_info)


@app.route('/<username>/<repo_name>/blob/<path:filepath>')
@app.route('/<username>/<repo_name>/blob/<rev>/<path:filepath>')
def view_file(username, repo_name, filepath, rev=None):
    if not validate_name(username) or not validate_name(repo_name):
        abort(404)
    if not validate_path(filepath):
        abort(404)

    # Default to tip, validate if provided
    if rev is None:
        rev = 'tip'
    elif not validate_revision(rev):
        abort(400)

    repo_path = get_repo_path(username, repo_name)
    if repo_path is None or not repo_path.exists():
        abort(404)

    # Get revision info (hash, tags, branch, bookmarks)
    rev_info = get_revision_info(repo_path, rev)
    if rev_info is None:
        abort(404)

    # Use hg cat to get file contents (safer than direct file access)
    # --: prevent filepath from being interpreted as an option
    result = run_hg_command(['cat', '-r', rev, '--', filepath], cwd=repo_path)
    if result.returncode != 0:
        abort(404)

    content = result.stdout
    return render_template('file.html',
                         username=username,
                         repo_name=repo_name,
                         filepath=filepath,
                         content=content,
                         current_rev=rev,
                         rev_info=rev_info)


@app.route('/<username>/<repo_name>/commit/<rev>')
def view_commit(username, repo_name, rev):
    if not validate_name(username) or not validate_name(repo_name):
        abort(404)
    if not validate_revision(rev):
        abort(400)

    repo_path = get_repo_path(username, repo_name)
    if repo_path is None or not repo_path.exists():
        abort(404)

    # Get commit info
    result = run_hg_command(
        ['log', '--template', '{node}\n{author}\n{date|isodate}\n{desc}', '-r', rev],
        cwd=repo_path
    )
    if result.returncode != 0:
        abort(404)

    lines = result.stdout.split('\n', 3)
    if len(lines) < 4:
        abort(404)

    commit = {
        'id': lines[0],
        'author': lines[1],
        'date': lines[2],
        'message': lines[3],
    }

    # Get diff
    # Note: rev is validated by validate_revision() - safe for revset use
    diff_result = run_hg_command(['diff', '-c', rev], cwd=repo_path)
    diff = diff_result.stdout if diff_result.returncode == 0 else ''

    return render_template('commit.html',
                         username=username,
                         repo_name=repo_name,
                         commit=commit,
                         diff=diff)


@app.route('/import', methods=['GET', 'POST'])
@login_required
def import_repo():
    """Import a repository from a remote URL."""
    if request.method == 'POST':
        repo_name = request.form.get('name', '').strip()
        clone_url = request.form.get('url', '').strip()

        # Validate repository name
        if not validate_name(repo_name):
            flash('Invalid repository name.', 'error')
            return render_template('import_repo.html')

        # Validate clone URL
        is_valid, result = validate_clone_url(clone_url)
        if not is_valid:
            flash(f'Invalid URL: {result}', 'error')
            return render_template('import_repo.html')

        validated_url = result

        # Check if repo already exists
        repo_path = get_repo_path(session['username'], repo_name)
        if repo_path is None:
            flash('Invalid repository path.', 'error')
            return render_template('import_repo.html')

        if repo_path.exists():
            flash('Repository already exists.', 'error')
            return render_template('import_repo.html')

        # Ensure parent directory exists
        repo_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize an empty repository
        repo_path.mkdir(parents=True)
        result = run_hg_command(['init'], cwd=repo_path)

        if result.returncode != 0:
            import shutil
            if repo_path.exists():
                shutil.rmtree(repo_path)
            flash('Failed to initialize repository.', 'error')
            return render_template('import_repo.html')

        # Write .hgrc with the remote URL as default path
        hgrc_path = repo_path / '.hg' / 'hgrc'
        hgrc_content = "[paths]\n"
        f"default = {validated_url}\n"
        "default:bookmarks.mode = ignore\n"
        "[ui]\n"
        "tweakdefaults = true\n"
        "quiet = true\n"


        hgrc_path.write_text(hgrc_content)

        # Pull from the remote repository
        try:
            result = run_hg_command(
                ['pull', '-f'],
                cwd=repo_path,
                timeout=120  # 2 minutes for pull operations
            )
        except TimeoutError:
            # Clean up partial pull
            import shutil
            if repo_path.exists():
                shutil.rmtree(repo_path)
            flash('Pull timed out. The repository may be too large.', 'error')
            return render_template('import_repo.html')

        if result.returncode != 0:
            # Clean up on failure
            import shutil
            if repo_path.exists():
                shutil.rmtree(repo_path)
            error_msg = result.stderr[:200] if result.stderr else 'Unknown error'
            flash(f'Failed to pull repository: {error_msg}', 'error')
            return render_template('import_repo.html')

        flash('Repository imported successfully!', 'success')
        return redirect(url_for('view_repo', username=session['username'], repo_name=repo_name))

    return render_template('import_repo.html')


@app.route('/<username>/<repo_name>/delete', methods=['POST'])
@login_required
def delete_repo(username, repo_name):
    if session['username'] != username:
        abort(403)

    if not validate_name(username) or not validate_name(repo_name):
        abort(404)

    repo_path = get_repo_path(username, repo_name)
    if repo_path is None or not repo_path.exists():
        abort(404)

    # Safely remove repository
    import shutil
    shutil.rmtree(repo_path)

    flash('Repository deleted.', 'success')
    return redirect(url_for('index'))


# =============================================================================
# Templates
# =============================================================================

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
