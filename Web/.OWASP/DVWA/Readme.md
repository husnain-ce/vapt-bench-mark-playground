# Damn Vulnerable Web Application (DVWA)

DVWA is a PHP/MariaDB web application that is damn vulnerable. Its main goal is to be an aid for security professionals to test their skills and tools in a legal environment, help web developers better understand the processes of securing web applications and to aid both students and teachers to learn about web application security in a controlled classroom environment.

The aim of DVWA is to practice some of the most common web vulnerabilities, with various levels of difficulty, with a simple straightforward interface. There are both documented and undocumented vulnerabilities — this is intentional.

Author: Robin Wood (@digininja)
License: GPL-3.0

---

## Installation

### Using Docker Compose (Recommended)

Prerequisites: Docker and Docker Compose.
bash

docker compose up -d

DVWA is now available at:

http://localhost:4280

### Automated Installation (Debian-based)
bash
sudo bash -c "$(curl --fail --show-error --silent --location https://raw.githubusercontent.com/IamCarron/DVWA-Script/main/Install-DVWA.sh)"

### Manual Installation (Linux)
bash
apt update
apt install -y apache2 mariadb-server mariadb-client php php-mysqli php-gd libapache2-mod-php

git clone https://github.com/digininja/DVWA.git
cd DVWA
cp config/config.inc.php.dist config/config.inc.php

# Enable Apache module
a2enmod rewrite
apachectl restart

# Set up database (via browser)
# Visit http://localhost/DVWA/setup.php and click "Create / Reset Database"

---

## Quick Reference

| Detail | Value |
|---|---|
| **URL** | `http://localhost:4280` |
| **Login** | `http://127.0.0.1/login.php` |
| **Username** | `admin` |
| **Password** | `password` |
| **DB Server** | `127.0.0.1` |
| **DB Port** | `3306` |
| **DB User** | `dvwa` |
| **DB Password** | `p@ssw0rd` |
| **DB Name** | `dvwa` |
| **Framework** | PHP / MariaDB |
| **Container** | Docker Compose |
| **License** | GPL-3.0 |
| **Stars** | 13.6k ⭐ |
| **Repository** | [github.com/digininja/DVWA](https://github.com/digininja/DVWA) |

---

## About

DVWA is a deliberately vulnerable web application designed for security practice. It includes:

- **Multiple difficulty levels** — Low, Medium, High, and Impossible
- **Documented and undocumented vulnerabilities** — Find them all
- **Straightforward interface** — Simple to navigate, easy to test
- **Both documented and hidden vulnerabilities** — Encourages independent discovery

> **WARNING:** DVWA is damn vulnerable! Do not deploy to any public-facing server. Use a virtual machine with NAT networking mode.

---

## OWASP Top 10 Coverage

| OWASP Category | Vulnerability | Covered? | Details |
|---|---|---|---|
| **A01 – Broken Access Control** | IDOR, privilege escalation, CSRF | ✅ Yes | Multiple labs covering access control flaws |
| **A02 – Cryptographic Failures** | Weak hashing, sensitive data | ✅ Yes | Password handling vulnerabilities |
| **A03 – Injection** | SQLi, XSS, Command Injection, LDAP | ✅ Yes | SQL Injection, XSS (Reflected/Stored/DOM), Command Injection |
| **A04 – Insecure Design** | Business logic flaws | ✅ Yes | Logic flaws in various modules |
| **A05 – Security Misconfiguration** | Default creds, debug mode | ✅ Yes | Default credentials, configurable security levels |
| **A06 – Vulnerable Components** | Outdated libraries | ⚠️ Partial | Uses older PHP libraries intentionally |
| **A07 – Authentication Failures** | Weak passwords, session flaws | ✅ Yes | Brute-forceable passwords, session issues |
| **A08 – Data Integrity Failures** | CSRF, data tampering | ✅ Yes | CSRF module included |
| **A09 – Logging & Monitoring** | Missing logs | ❌ No | Not a focus area |
| **A10 – SSRF** | Server-side request forgery | ⚠️ Partial | Possible in certain modules |

---

## Vulnerability Categories

| Category | Description |
|---|---|
| **SQL Injection** | Classic SQLi across multiple difficulty levels |
| **Cross-Site Scripting (XSS)** | Reflected, Stored, and DOM-based XSS |
| **Command Injection** | OS command execution via vulnerable inputs |
| **File Inclusion** | Local File Inclusion (LFI) and Remote File Inclusion (RFI) |
| **File Upload** | Unrestricted file upload vulnerabilities |
| **CSRF** | Cross-Site Request Forgery |
| **Broken Authentication** | Session hijacking, credential brute-forcing |
| **Insecure CAPTCHA** | Bypassing CAPTCHA mechanisms |
| **SQL Injection (Blind)** | Blind SQLi requiring boolean/time-based extraction |
| **Authorization Bypass** | Bypassing access controls |

---

## Project Structure

DVWA/
├── Dockerfile                  # Container build configuration
├── compose.yml                 # Docker Compose orchestration
├── index.php                   # Main entry point
├── login.php                   # Login page
├── logout.php                  # Logout handler
├── setup.php                   # Database setup wizard
├── security.php                # Security configuration page
├── instructions.php            # Instructions for each vulnerability
├── about.php                   # About page
├── phpinfo.php                 # PHP info page
├── robots.txt                  # Robots exclusion
├── security.txt                # Security policy
├── favicon.ico                 # Favicon
├── COPYING.txt                 # GPL-3.0 license
├── config/
│   └── config.inc.php.dist     # Default config file template
├── database/
│   └── ...                     # Database schemas and SQL files
├── docs/                       # Documentation
├── dvwa/                       # Core DVWA framework files
├── hackable/
│   └── uploads/                # Writeable upload directory
├── external/
│   └── recaptcha/              # reCAPTCHA integration
├── vulnerabilities/
│   └── api/                    # Vulnerable API module (Composer)
├── tests/                      # Security regression tests
└── .github/                    # CI/CD configuration

---

## Configuration

### Config File
bash
cp config/config.inc.php.dist config/config.inc.php

### Default Database Credentials
php
$_DVWA['db_server']    = '127.0.0.1';
$_DVWA['db_port']      = '3306';
$_DVWA['db_user']      = 'dvwa';
$_DVWA['db_password']  = 'p@ssw0rd';
$_DVWA['db_database']  = 'dvwa';

### Environment Variables (Docker)
yaml
environment:
  - DB_SERVER=db
  - DEFAULT_SECURITY_LEVEL=low

### Disable Authentication (For Testing)
php
$_DVWA['disable_authentication'] = true;
$_DVWA['default_security_level'] = 'low';

---

## PHP Configuration

### Enable Remote File Inclusion
ini
allow_url_include = on
allow_url_fopen = on

### Enable Error Display
ini
display_errors = On
display_startup_errors = On

### Apache Module
bash
a2enmod rewrite
apachectl restart

---

## Docker Port Configuration

DVWA uses port 4280 by default instead of port 80. To change:
yaml
ports:
  - 127.0.0.1:8806:80

Access at `http://localhost:8806`.

---

## SQLite Support (Alternative to MySQL)

Switch SQLi testing to SQLite3:
php
$_DVWA["SQLI_DB"]     = "sqlite";
$_DVWA["SQLITE_DB"]   = "sqli.db";

Copy `database/sqli.db.dist` over `database/sqli.db` if needed.

---

## reCAPTCHA Setup

1. Generate API keys at https://www.google.com/recaptcha/admin/create
2. Add to `config/config.inc.php`:
php
$_DVWA['recaptcha_public_key']  = 'your-public-key';
$_DVWA['recaptcha_private_key'] = 'your-private-key';

---

## Troubleshooting

| Issue | Solution |
|---|---|
| 404 or Apache default page | Browse to `/DVWA` (case-sensitive) |
| Blank screen | Enable `display_errors` in PHP |
| Database access denied | Verify config credentials match DB |
| Connection refused | Start MariaDB: `sudo service mysql start` |
| Unknown authentication | Switch to MariaDB or configure `mysql_native_password` |
| MariaDB Docker fails | Add memory cgroup volume mount |
| SELinux issue (CentOS) | `setsebool -P httpd_can_network_connect_db 1` |

---

## Default Credentials

| Field | Value |
|---|---|
| **Username** | `admin` |
| **Password** | `password` |
| **Login URL** | `http://127.0.0.1/login.php` |

---

## Technology Stack

| Component | Details |
|---|---|
| **Language** | PHP |
| **Database** | MariaDB / MySQL / SQLite |
| **Web Server** | Apache with mod_rewrite |
| **Templates** | PHP (embedded) |
| **Container** | Docker Compose |
| **JavaScript** | Client-side validation |

---

## Links

- **Project Home:** [github.com/digininja/DVWA](https://github.com/digininja/DVWA)
- **Automated Install Script:** [github.com/IamCarron/DVWA-Script](https://github.com/IamCarron/DVWA-Script)
- **Docker Build:** `docker compose up -d`
- **License:** [GNU GPL-3.0](https://www.gnu.org/licenses/)
- **CTF Archive:** [sajjadium/ctf-archives](https://github.com/sajjadium/ctf-archives)

---

## License

This file is part of Damn Vulnerable Web Application (DVWA).

DVWA is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

DVWA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with DVWA. If not, see https://www.gnu.org/licenses/.