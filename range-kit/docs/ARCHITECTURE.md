# Architecture

How the range is wired, and why it is safe to run on an isolated VM.

## Network model

Everything hangs off one user-defined Docker bridge:

```
aqira-range   bridge   172.30.0.0/24   gateway 172.30.0.1
```

Created once by `bin/create-network.sh` as an **external** network; every compose
file joins it with `external: true`. Three reachability styles coexist:

```
                              ┌──────────────────────────── VM (host) ────────────────────────────┐
                              │                                                                    │
   browser / Aqira scanner ──►│  nginx :80  ──Host header──►  127.0.0.1:8101..8107  ──►  containers │
                              │     ▲                                                     on bridge  │
   /etc/hosts:               │     │  juice/dvwa/webgoat/vampi/log4shell/k8sgoat/localstack         │
     *.range.example.com ────┘     │                                                                 │
     → 127.0.0.1                    │                                                                 │
                                    │                                                                 │
   ms2.range → 172.30.0.11 ─────────┼──────────►  aqira-ms2   (no host ports, bridge-only)           │
   ms3.range → 172.30.0.12 ─────────┴──────────►  aqira-ms3   (no host ports, bridge-only)           │
                              └────────────────────────────────────────────────────────────────────┘
```

1. **Loopback web/API/cloud labs** publish to `127.0.0.1:<port>` only. nginx
   fronts them on `:80` by `Host` header, so `juice.range.example.com` resolves
   (via `/etc/hosts`) to `127.0.0.1` and nginx proxies to the right container port.
2. **Network labs** (Metasploitable 2/3) publish **no host ports**. They take
   static addresses on the bridge (`172.30.0.11`, `172.30.0.12`) and are reachable
   only from the host and other bridge members (e.g. the optional kali attacker).
3. **Static IaC labs** have no runtime at all — `cloud/iac-scan.sh` runs checkov
   over the TerraGoat/CFNGoat/Kubernetes-Goat manifests and writes reports.

Kubernetes Goat runs on a single-node **k3s** cluster (not the bridge); its landing
app is surfaced on `127.0.0.1:8106` by a keepalive `kubectl port-forward`
(`k8s/portforward.sh`), then fronted by nginx like the other web labs.

## Components and boundaries

| Unit | Purpose | Depends on |
|---|---|---|
| `bin/lib.sh` | shared paths, logging, RAM gate, probes | — |
| `bin/create-network.sh` | the one external bridge | docker |
| `bin/install-hosts.sh` | `/etc/hosts` block (idempotent) | root |
| `bin/install-nginx.sh` | reverse-proxy vhosts + reload | root, nginx |
| `bin/deploy-web/net/cloud.sh` | per-category compose bring-up | network |
| `k8s/*` | k3s install, image pre-pull, goat setup, port-forward | root, k3s |
| `cloud/*` | LocalStack seed, IaC scan, venv | python3 |
| `bin/deploy-all.sh` | phase orchestration + RAM gate | all of the above |
| `bin/verify.sh` | health table | curl |
| `bin/teardown.sh` | stop / purge / free RAM | docker, k3s |

Each script sources `lib.sh` for the canonical paths, so the kit is relocatable —
copy it anywhere and `BENCH_ROOT` resolves from the script's own location. No
absolute `/home/aqsec/...` paths are baked in (the original range scripts were
de-hardcoded when vendored).

## Safety model

- **No off-box exposure.** Web labs bind loopback; network labs bind no host port.
  Nothing listens on `0.0.0.0` by design. Keep the VM's firewall closed regardless.
- **Emulated cloud.** LocalStack is fully local (`localstack/localstack:3.8.1`
  Community). The seeded "leaked" AWS keys and public bucket are fake — no real
  account, no spend.
- **Deliberately vulnerable.** MS3-lite ships a source-built ProFTPd 1.3.5 with an
  un-authenticated `mod_copy` (CVE-2015-3306) and weak SSH creds. That is the
  point; never run it anywhere reachable from an untrusted network.

## RAM discipline

The full range (web + net + cloud + k3s) wants ~4 GB. `deploy-all.sh` gates the
k3s phase at 2500 MB free and self-skips below that (override `FORCE=1`). Use
`bin/teardown.sh` to drop the heavy labs and reclaim memory between runs.
