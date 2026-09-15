## Business Expense App

A Flask-based business expense management web application with intentional vulnerabilities designed for security challenge purposes. The goal is simple on the surface — manage expenses — but getting the flag requires deep exploitation, including obtaining a reverse shell.

Author: Matthias Penner

---

## Installation

### Build the Docker Image

```bash
docker build -t business .
```

### Run the Container

```bash
docker run -p 5000:5000 business
```

### Access the Application

Open your browser and navigate to:

http://127.0.0.1:5000/

---

## Quick Start

| Step | Command |
|---|---|
| Build | `docker build -t business .` |
| Run | `docker run -p 5000:5000 business` |
| Access | `http://127.0.0.1:5000/` |
| Stop | `Ctrl+C` or `docker stop` |

---

## Challenge Overview

This application presents itself as a simple expense tracker, but hiding beneath the surface are multiple layers of vulnerabilities. The ultimate objective is to:

1. Identify and exploit vulnerabilities in the application
2. Escalate access to obtain a **reverse shell**
3. Grab the **flag** located somewhere on the system

> **Tip:** Use all features you have — or shouldn't have — at your disposal. The flag is far from simple to obtain.

