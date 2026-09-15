# Nightbyte — The Midnight Storefront

The midnight storefront for people who treat unreleased builds like a personality trait.

Find what the press account is hiding.

Author: ibk


## About

Nightbyte is a CTF-style web application centered around unreleased builds and hidden content. The application presents a storefront interface where certain accounts and content are restricted. The primary challenge is to uncover what the **press account** is hiding.


## Installation

### Build the Docker Image
bash
docker build -t nightbyte .

### Run the Container
bash
docker run -p 5000:5000 nightbyte

### Access the Application

Open your browser and navigate to:

http://127.0.0.1:5000/

---

## Quick Start

| Step | Command |
|---|---|
| Build | `docker build -t nightbyte .` |
| Run | `docker run -p 5000:5000 nightbyte` |
| Access | `http://127.0.0.1:5000/` |
| Stop | `Ctrl+C` or `docker stop` |

---



## Technology Stack

| Component | Details |
|---|---|
| **Framework** | Flask (Python) |
| **Port** | `5000` |
| **Container** | Docker |
| **Challenge Type** | CTF / Web Exploitation |

