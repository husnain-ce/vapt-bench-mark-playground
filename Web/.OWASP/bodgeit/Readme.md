\# The BodgeIt Store



The BodgeIt Store is a deliberately insecure web application aimed at people who are new to penetration testing.







\---



\## Installation



\### Run with Docker (Recommended)

bash

docker run --rm -p 8080:8080 -it psiinon/bodgeit



Then open your browser and navigate to:



http://localhost:8080/bodgeit



The `--rm` flag automatically removes the container when you stop it.



\---



\## About



The BodgeIt Store is designed to be easy to set up and use. Key characteristics:



\- \*\*Easy to install\*\* — only requires Java and a servlet engine (e.g., Tomcat), or simply use the Docker image

\- \*\*Self-contained\*\* — no additional dependencies beyond Java and a servlet engine

\- \*\*Easy to modify\*\* — all functionality is implemented in JSPs, no IDE required

\- \*\*Cross platform\*\* — works on any OS that supports Java/Tomcat

\- \*\*No database to configure\*\* — uses an in-memory database that is automatically initialized on startup

\- \*\*Open source\*\*



\---



\## Vulnerabilities Covered



The BodgeIt Store includes the following significant vulnerabilities for hands-on practice:



| # | Vulnerability | Description |

|---|---|---|

| 1 | \*\*Cross-Site Scripting (XSS)\*\* | Inject malicious scripts into web pages viewed by other users |

| 2 | \*\*SQL Injection\*\* | Exploit unsanitized database queries to read or modify data |

| 3 | \*\*Hidden (Unprotected) Content\*\* | Access pages or resources that are not properly secured |

| 4 | \*\*Cross-Site Request Forgery (CSRF)\*\* | Trick users into performing unwanted actions on the application |

| 5 | \*\*Debug Code\*\* | Exploit debug endpoints and verbose error messages left in the application |

| 6 | \*\*Insecure Direct Object References (IDOR)\*\* | Access objects (files, records, etc.) by manipulating references |

| 7 | \*\*Application Logic Vulnerabilities\*\* | Exploit flaws in business logic and workflow design |



\---



\## Scoring System



The application includes a \*\*scoring page\*\* (linked from the "About Us" page) where you can:

\- Track hacking challenges

\- See whether you have completed each challenge

\- Monitor your progress and score



\---



\## Tools Recommended



\- \*\*\[OWASP ZAP](https://www.owasp.org/index.php/ZAP)\*\* — Recommended proxy tool for finding and testing vulnerabilities (the project lead also created the BodgeIt Store)

\- \*\*Burp Suite\*\* — Another popular alternative for intercepting and analyzing HTTP requests

\- \*\*Browser developer tools\*\* — Useful for inspecting forms, cookies, and requests



\---



\## Quick Reference



| Detail | Value |

|---|---|

| \*\*Docker Image\*\* | `psiinon/bodgeit` |

| \*\*Docker Size\*\* | \~214 MB |

| \*\*Port\*\* | `8080` |

| \*\*URL\*\* | `http://localhost:8080/bodgeit` |

| \*\*Language\*\* | Java / JSP |

| \*\*Build Tool\*\* | Apache Ant |

| \*\*Servlet Engine\*\* | Tomcat 9.0 |

| \*\*Repository\*\* | \[github.com/psiinon/bodgeit](https://github.com/psiinon/bodgeit) |

| \*\*Stars\*\* | 287 ⭐ |

| \*\*License\*\* | Open Source |



\---



\## Links



\- \*\*GitHub:\*\* \[github.com/psiinon/bodgeit](https://github.com/psiinon/bodgeit)

\- \*\*Docker Hub:\*\* \[hub.docker.com/r/psiinon/bodgeit](https://hub.docker.com/r/psiinon/bodgeit)

\- \*\*OWASP ZAP:\*\* \[owasp.org/www-project-zap](https://www.owasp.org/index.php/ZAP)

\- \*\*OWASP Juice Shop (Recommended Alternative):\*\* \[github.com/juice-shop/juice-shop](https://github.com/juice-shop/juice-shop)

