# Aqira Benchmark — Cyber-Range Deployment Kit

A **self-contained, portable kit** that rebuilds the Aqira cyber-range (11
intentionally-vulnerable labs) on a fresh Linux VM. Clone or `rsync` this folder
to the target machine and run one command.

The kit is ~2 MB: it vendors every configuration file and the Aqira-authored glue,
and **fetches the heavy bits** (Docker images, k3s, the Kubernetes-Goat repo, the
Python venv) at deploy time. Nothing multi-gigabyte travels with it.

> ⚠️ **Authorized use only.** Every lab is deliberately exploitable. Deploy only on
> an isolated VM you own. Web/API/cloud labs bind to **loopback (127.0.0.1)** only;
> the two network labs (Metasploitable 2/3) publish **no host ports** and are
> reachable only on the internal `aqira-range` bridge. Do not expose this host.

## Quickstart

```bash
# on the target VM, as root:
cd aqira-benchmark
sudo ./bin/bootstrap.sh            # preflight → network → hosts → nginx → all labs
./bin/verify.sh                    # health-probe every lab
```

Low on RAM or just want the web labs?

```bash
sudo ./bin/bootstrap.sh --web-only   # only the loopback web/API labs
```

Tear down to free memory (keeps images for a fast re-up):

```bash
./bin/teardown.sh                  # stop everything
./bin/teardown.sh --all            # + remove k3s, network, volumes, venv
```

## What gets deployed

| Lab | Category | Reach it at | Notes |
|---|---|---|---|
| OWASP Juice Shop | web | `juice.range.example.com` (→ :8101) | all challenges enabled |
| DVWA | web | `dvwa.range.example.com` (→ :8102) | |
| WebGoat + WebWolf | web | `webgoat.range.example.com/WebGoat` (→ :8103) | |
| VAmPI | api | `vampi.range.example.com` (→ :8104) | vulnerable REST API |
| Log4Shell (Solr 8.11) | web | `log4shell.range.example.com` (→ :8105) | CVE-2021-44228 |
| Kubernetes Goat | cloud-native | `k8sgoat.range.example.com` (→ :8106) | single-node k3s |
| LocalStack (+ seed) | cloud | `localstack.range.example.com` (→ :8107) | emulated AWS misconfigs |
| Metasploitable 2 | network | `172.30.0.11` (bridge only) | classic vuln host |
| Metasploitable 3 (MS3-lite) | network | `172.30.0.12` (bridge only) | ProFTPd 1.3.5 mod_copy + more |
| IaC goats (Terra/CFN/K8s) | iac-static | *checkov report* | no runtime service |
| kali-mcp (attacker) | — | `172.30.0.2` | optional, not provisioned here |

Full details in [`manifest.yaml`](manifest.yaml) and [`docs/LAB-CATALOG.md`](docs/LAB-CATALOG.md).

## Documentation

- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — prerequisites, phased bring-up, troubleshooting
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — network model, nginx/hosts wiring, safety model
- [`docs/LAB-CATALOG.md`](docs/LAB-CATALOG.md) — per-lab vuln surface and how to verify
- [`docs/KVM-MS3.md`](docs/KVM-MS3.md) — the KVM Metasploitable 3 path (best-effort) vs the working container
- [`docs/TEARDOWN.md`](docs/TEARDOWN.md) — stopping, purging, freeing RAM

## Layout

```
aqira-benchmark/
  manifest.yaml          # single source of truth: every lab
  bin/                   # orchestration: bootstrap, deploy-*, verify, teardown, installers
  compose/               # the 8 docker-compose files (vendored)
  vm/ms3-lite/           # MS3-lite build context (the working Metasploitable 3)
  vm/kvm/                # libvirt net + KVM MS3 scaffolding (best-effort)
  nginx/                 # reverse-proxy vhosts + proxy include
  hosts/                 # /etc/hosts block
  k8s/                   # k3s install, image pre-pull, goat setup, port-forward
  cloud/                 # LocalStack seed, IaC scan, TerraGoat + CFNGoat, venv setup
  docs/                  # the runbooks above
```
# vapt-bench-mark-playgroud
