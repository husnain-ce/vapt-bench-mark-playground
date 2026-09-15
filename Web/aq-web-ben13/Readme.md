# Challenge 1

A Docker-based web challenge application.

---

## Build & Run

### Build the Docker Image
bash
sudo docker build -t challenge1 .

### Run the Container
bash
sudo docker run -p 5000:5000 challenge1

### Access the Application

Open your browser and navigate to:

http://127.0.0.1:5000/

---

## Quick Reference

| Step | Command |
|---|---|
| Build | `sudo docker build -t challenge1 .` |
| Run | `sudo docker run -p 5000:5000 challenge1` |
| Access | `http://127.0.0.1:5000/` |
| Stop | `Ctrl+C` or `sudo docker stop` |

---

## Technology Stack

| Component | Details |
|---|---|
| **Container** | Docker |
| **Port** | `5000` |
| **URL** | `http://127.0.0.1:5000/` |
| **Image** | `challenge1` |