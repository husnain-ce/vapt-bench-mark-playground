# OWASP Juice Shop — Benchmark Target

Web application target for the OWASP Top 10 benchmarking task. Juice Shop is
an intentionally vulnerable, modern web app maintained as an official OWASP
project — it bundles well over 100 built-in challenges that span the entire
OWASP Top 10.

## Setup

1. Install [Docker](https://www.docker.com/)
2. Run `docker pull bkimminich/juice-shop`
3. Run `docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop`
4. Browse to http://localhost:3000 (on macOS and Windows browse to
   http://192.168.99.100:3000 if you are using docker-machine instead of the
   native docker installation)

> **Reproducibility tip:** `bkimminich/juice-shop` pulls `latest` by default,
> which changes over time. For a benchmark you re-run later, pin a specific
> version instead, e.g. `docker pull bkimminich/juice-shop:v18.0.0`, and note
> the exact tag you used below.

**Image version used for this benchmark:** _fill in after first pull_

## Access notes

- There's no default login — register your own account from the app.
- Progress is tracked on the **Score Board**, reachable from the app menu.
  It's hidden by default in some configs; it's the main place to track which
  challenges (vulnerabilities) you've confirmed.
- The Score Board has built-in **category** and **difficulty** filters — use
  these to scope your testing session to specific OWASP categories instead of
  testing everything at once.

## OWASP Top 10 (2021) coverage

Juice Shop's own challenge categories predate the current OWASP Top 10:2021
naming, so the mapping below is approximate in places — verify actual
category labels against the Score Board once it's running.

| OWASP Top 10 (2021) | Covered by Juice Shop? | Juice Shop category (Score Board) |
|---|---|---|
| A01: Broken Access Control | Yes | Broken Access Control |
| A02: Cryptographic Failures | Yes | Cryptographic Issues (+ some Sensitive Data Exposure) |
| A03: Injection | Yes | Injection |
| A04: Insecure Design | Partial | Scattered across multiple categories — no single dedicated bucket |
| A05: Security Misconfiguration | Yes | Security Misconfiguration |
| A06: Vulnerable and Outdated Components | Yes | Vulnerable Components |
| A07: Identification and Authentication Failures | Yes | Broken Authentication |
| A08: Software and Data Integrity Failures | Partial | Overlaps with Insecure Deserialization |
| A09: Security Logging and Monitoring Failures | Yes | Observability Failures |
| A10: Server-Side Request Forgery (SSRF) | Partial | Present, but not a standalone top-level category — confirm placement on the running Score Board |

**Legacy categories still present** (from earlier OWASP Top 10 editions, not
in the 2021 list but still useful for broader appsec testing): XML External
Entities (XXE), Improper Input Validation, Security through Obscurity,
Unvalidated Redirects, Broken Anti-Automation.

## How this fits the benchmark

- Test cases for this target go in `../../testcases/testcases.yaml`, tagged
  with `target: juice-shop`.
- Raw results (pass/fail, false positives, notes) go in
  `../../results/<tester-name>/juice-shop.csv` (or `.yaml`), one row per
  test case — see the repo root README for the schema.
- Don't hand-pick which challenges to test differently across targets — use
  the same OWASP category checklist for every target so results stay
  comparable.
