\# WebGoat — OWASP Top 10 Practice Lab



WebGoat is a deliberately insecure web application by OWASP. Use it to

practice exploiting and defending against common web vulnerabilities.



\---



\## Installation



```bash

docker run -it -p 127.0.0.1:8080:8080 -p 127.0.0.1:9090:9090 webgoat/webgoat

```



Open \*\*http://localhost:8080/WebGoat\*\* in your browser to start.



\---



\## OWASP Top 10 Coverage



| OWASP Category | Vulnerability | Covered by Repo? | Lessons Covered |

|---|---|---|---|

| \*\*A01 – Broken Access Control\*\* | Bypass access checks, privilege escalation | ✅ Yes | Bypass access checks, unauthorized data access, CSRF |

| \*\*A02 – Cryptographic Failures\*\* | Weak hashing, sensitive data exposure | ✅ Yes | Password cracking, session hijacking, crypto flaws |

| \*\*A03 – Injection\*\* | SQL, Command, LDAP, XPath, NoSQL Injection | ✅ Yes | SQL Injection, Command Injection, LDAP Injection, XPath Injection, NoSQL Injection |

| \*\*A04 – Insecure Design\*\* | Missing functional controls, business logic flaws | ⚠️ Partial | Limited business logic \& workflow flaw exercises |

| \*\*A05 – Security Misconfiguration\*\* | Default credentials, verbose errors | ✅ Yes | Default creds, debug modes, unnecessary features |

| \*\*A06 – Vulnerable Components\*\* | Outdated libraries, known CVEs | ❌ No | No dedicated lessons for component/library vulnerabilities |

| \*\*A07 – Authentication Failures\*\* | Brute-force, session fixation, weak passwords | ✅ Yes | Brute-force login, session fixation, credential attacks |

| \*\*A08 – Data Integrity Failures\*\* | Deserialization, data tampering | ✅ Yes | Deserialization attacks, form tampering |

| \*\*A09 – Logging \& Monitoring Failures\*\* | Bypass audit logs, hidden endpoints | ⚠️ Partial | Blind SQL injection, some audit bypass scenarios |

| \*\*A10 – SSRF\*\* | Server-side request forgery | ✅ Yes | SSRF exploitation, internal network probing |



\---



\## Quick Tips



\- The app runs on port \*\*8080\*\* and the companion \*\*WebWolf\*\* coach on \*\*9090\*\*.

\- Create an account inside the app to track your progress and lesson completion.

\- Use \*\*OWASP ZAP\*\* or \*\*Burp Suite\*\* as a proxy to intercept and analyze requests.

\- Disconnect from the Internet while using WebGoat — it is intentionally vulnerable.

