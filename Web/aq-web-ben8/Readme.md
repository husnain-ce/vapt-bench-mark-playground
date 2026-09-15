# Ghazy Corp —  Web Challenge

Welcome to Ghazy Corp — a corporate web application with hidden secrets. The `/mail` endpoint is just simulating mail service and shouldn't be vulnerable to something that will help you solving this challenge.

## Build & Run

### Build the Docker Image
bash
sudo docker build -t ghazy_crop .

### Run the Container
bash
sudo docker run -d --name ghazy-corp -p 8081:80 ghazy_crop

### Access the Application

Open your browser and navigate to:

http://127.0.0.1:8081/

The container runs in detached mode (`-d`) with the name `ghazy-corp`.

---

## Quick Reference

| Step | Command |
|---|---|
| Build | `sudo docker build -t ghazy_crop .` |
| Run | `sudo docker run -d --name ghazy-corp -p 8081:80 ghazy_crop` |
| Access | `http://127.0.0.1:8081/` |
| Stop | `sudo docker stop ghazy-corp` |
| Remove | `sudo docker rm ghazy-corp` |
| Logs | `sudo docker logs ghazy-corp` |

---

## About

Ghazy Corp is a web challenge representing a corporate web application. The application includes a mail simulation service at `/mail` (which is intentionally not the vulnerability) and hides a flag somewhere within the system.

- **Flag location:** `flag.txt` (on the server filesystem)
- **Database init:** `init.db`
- **Setup script:** `init.sh`
- **Source code:** `src/`

---

## Challenge Objective

Find what the press account is hiding. Retrieve the flag from `flag.txt` on the server.


## Key Files to Review

| File | Purpose | Security Notes |
|---|---|---|
| `src/` | Application source code | Check for injection, access control flaws |
| `Dockerfile` | Container configuration | Check base image and misconfigurations |
| `init.db` | Database initialization | Look for default credentials |
| `init.sh` | Setup script | Check for hardcoded secrets or weak permissions |
| `flag.txt` | Flag file | Target objective |

---

## Tips

- Use browser DevTools to inspect requests and responses
- Intercept traffic with **Burp Suite** or **OWASP ZAP**
- Try common paths like `/admin`, `/press`, `/hidden`, `/backup`
- Check HTTP headers for information leakage
- Review source code for commented-out debug routes


