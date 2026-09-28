# Deployment Runbook

How to stand up the whole range on a fresh VM, phase by phase, and what to do
when a phase misbehaves.

## 1. Prerequisites

Target: a Linux VM **you own and control**, isolated from anything sensitive.

Required:
- Docker Engine + Compose (`docker compose` plugin or `docker-compose`)
- `curl`, `git`, `bash`
- root (for `/etc/hosts`, nginx, k3s)

For the full range (adds the k3s and cloud phases):
- **≥ 4 GB free RAM** (hard gate is 2500 MB before the k3s phase)
- ~15 GB free disk for images
- `python3` + `python3-venv` (for LocalStack seeding + checkov IaC scan)
- `nginx` (system package) to front the web labs by hostname

Optional (full-parity extras):
- `libvirt`/`virsh` + nested virtualization — only for the best-effort KVM
  Metasploitable 3 path (see `docs/KVM-MS3.md`). Not needed for the working
  MS3-lite container.

Install the baseline on Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin nginx git curl python3 python3-venv
sudo systemctl enable --now docker nginx
```

## 2. Copy the kit to the VM

```bash
rsync -a aqira-benchmark/ user@vm:/opt/aqira-benchmark/
# or: git clone <repo>; cd <repo>/aqira-benchmark   (if committed to a repo)
```

## 3. Preflight

```bash
./bin/preflight.sh
```

Checks Docker, Compose, RAM, disk, free ports, and reports which optional paths
(k3s, libvirt, python) are available. Hard failures stop you; warnings are advisory.

## 4. One-shot bring-up

```bash
sudo ./bin/bootstrap.sh
```

Runs, in order: preflight → create `aqira-range` network → install `/etc/hosts`
block → install + reload nginx → `deploy-all.sh`. Then it verifies.

Variants:

```bash
sudo ./bin/bootstrap.sh --web-only    # only loopback web/API labs
sudo ./bin/bootstrap.sh --no-k8s      # everything except the RAM-hungry k3s phase
sudo NO_NGINX=1 ./bin/bootstrap.sh    # skip nginx; reach labs by 127.0.0.1:<port>
```

## 5. Phased bring-up (manual control)

`deploy-all.sh` runs four independently re-runnable phases:

| Phase | Script | RAM gate | What |
|---|---|---|---|
| 1 | `bin/deploy-web.sh` | — | juice, dvwa, webgoat, vampi, log4shell (8101–8105) |
| 2 | `bin/deploy-cloud.sh` | — | LocalStack (8107) + seed; then `cloud/iac-scan.sh` |
| 3 | `bin/deploy-net.sh` | — | Metasploitable 2 (172.30.0.11) + MS3-lite build (172.30.0.12) |
| 4 | `k8s/deploy-k8s.sh` | **2500 MB** | k3s + Kubernetes Goat (8106) |

Run any phase on its own, e.g. just the web labs then the cluster later:

```bash
./bin/deploy-web.sh
# ...later, once RAM frees up...
FORCE=1 ./k8s/deploy-k8s.sh
```

The k3s phase self-skips if free RAM is under 2500 MB; re-run it with `FORCE=1`
to override the gate.

## 6. Verify

```bash
./bin/verify.sh
```

Probes web/API/cloud labs through nginx (by Host header) and network labs by TCP.
Heavy labs (WebGoat, k8s-goat, MS3-lite first build) can take a few minutes to
become healthy — re-run until green.

## Troubleshooting

**A web lab returns 000 / 502.** The container may still be starting. `docker ps`
to confirm it is up; `docker logs <container>` for detail. WebGoat and Juice Shop
have long start periods.

**`k8sgoat` fails but pods are Running.** The port-forward drops on pod restarts.
Restart it: `./k8s/portforward.sh start` (it runs a keepalive loop). If the
service name differs in your goat version, set `K8SGOAT_SVC=svc/<name>`.

**MS3-lite build fails.** The first build compiles ProFTPd 1.3.5 from source and
needs outbound access to `ftp.proftpd.org` + the Ubuntu 14.04 apt mirrors. Re-run
`./bin/deploy-net.sh`; the build is cached after it succeeds once.

**LocalStack seed errors.** Ensure the venv exists: `./cloud/venv-setup.sh`
(needs `python3-venv`). The seed is idempotent-ish; re-running is safe.

**k3s image pulls flap (ImagePullBackOff).** `./k8s/pull-images.sh` pre-imports
the scenario images into containerd with retries. Re-run it, then
`kubectl delete pod --all` to reschedule.

**Reaching labs without nginx.** Every web lab is also directly on
`127.0.0.1:<port>` (see the table in phase 5). nginx only adds the friendly
`*.range.example.com` hostnames.
