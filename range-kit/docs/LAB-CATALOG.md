# Lab Catalog

Per-lab vulnerability surface and how to confirm it is live. Ground-truth for
what a scanner *should* find. See `manifest.yaml` for the machine-readable form.

> This kit deploys the targets; it does **not** score a scanner against them.
> The vuln notes below are the intended exploitation surface for reference.

## Web labs

### Juice Shop — `juice.range.example.com` → 127.0.0.1:8101
OWASP's modern vulnerable SPA. `NODE_ENV=unsafe` enables every challenge
(including ones disabled in ctf/prod). SQLi, XSS, broken auth, JWT issues, IDOR.
Verify: `curl -H 'Host: juice.range.example.com' http://127.0.0.1/` → 200.

### DVWA — `dvwa.range.example.com` → 127.0.0.1:8102
Classic Damn Vulnerable Web App. SQLi, command injection, file upload/inclusion,
CSRF, brute force, across low/medium/high security levels. Login: `admin/password`.
Verify: `.../login.php` → 200.

### WebGoat + WebWolf — `webgoat.range.example.com/WebGoat` → 127.0.0.1:8103
OWASP teaching app; lessons served under `/WebGoat`. WebWolf helper on loopback
`9103`. Verify: `.../WebGoat` → 200/302.

### VAmPI — `vampi.range.example.com` → 127.0.0.1:8104
Vulnerable REST API in `vulnerable=1` mode: BOLA, mass assignment, broken JWT auth.
Verify: `.../` → 200 (JSON banner).

### Log4Shell — `log4shell.range.example.com` → 127.0.0.1:8105
**CVE-2021-44228.** Apache Solr 8.11.0 (`vulhub/solr:8.11.0`). JNDI injection via a
logged parameter yields RCE (`uid=0`). The JVM debug port 5005 is intentionally
not published. Verify: `.../solr/` → 200/302.

## Cloud-native / cloud labs

### Kubernetes Goat — `k8sgoat.range.example.com` → 127.0.0.1:8106
Runs on single-node k3s. Scenarios: insecure RBAC / super-admin, sensitive keys in
container layers, hidden-in-layers, metadata-db, DIND escape, SSRF, etc. Exposed
via keepalive `kubectl port-forward` (`k8s/portforward.sh`).
Verify: `.../` → 200/302 once pods are Running.

### LocalStack — `localstack.range.example.com` → 127.0.0.1:8107
Emulated AWS (`s3,iam,sts,ec2,secretsmanager`). `cloud/localstack-seed.sh` plants
the intended misconfigs: a **public S3 bucket** (`aqira-public-loot`) holding fake
credentials + PII, an **over-permissive IAM policy** (`Action:* Resource:*`) on user
`range-dev`, and a **plaintext Secrets Manager** secret. All fake/emulated.
Verify: `.../_localstack/health` → 200.

## Network labs (bridge-only, no host ports)

### Metasploitable 2 — 172.30.0.11 (`ms2.range.example.com`)
The classic intentionally-vulnerable Linux host. The compose command explicitly
starts the full service set (Apache, Samba, Postfix, MySQL, PostgreSQL, Tomcat,
distcc, SNMP, ProFTPd, vsftpd/UnrealIRCd via rc.local, SSH). ~9 exploitable
services / multiple root paths. Verify: `tcp/22` open.

### Metasploitable 3 — MS3-lite — 172.30.0.12 (`ms3.range.example.com`)
Ubuntu 14.04 vulnerable surface reproduced in a container (the working MS3 — see
`docs/KVM-MS3.md` for why the KVM box path is best-effort):
- **ProFTPd 1.3.5 `mod_copy`** (CVE-2015-3306) — un-authenticated SITE CPFR/CPTO,
  the primitive `proftpd_modcopy_exec` abuses to plant a PHP webshell.
- **OpenSSH weak creds** — `vagrant/vagrant`, `root/vagrant`.
- **PHP command injection** — `ping.php`.
- **UNION-based SQLi** — `login.php` (sqlite-backed).
Verify: `tcp/21` open, then `tcp/22`, `tcp/80`.

## Static IaC lab

### IaC goats — checkov report (no runtime)
`cloud/iac-scan.sh` runs checkov over:
- **TerraGoat** — Terraform for AWS / Azure / GCP misconfigs.
- **CFNGoat** — CloudFormation misconfigs.
- **Kubernetes Goat manifests** — the goat scenarios (fetched by `k8s/deploy-k8s.sh`).
Output: `evidence/iac/proof/checkov_*.{txt,json}`. Hundreds of failed checks by
design. Verify: report files exist and list failures.

## Optional attacker

### kali-mcp — 172.30.0.2
A Kali workstation on the bridge for hands-on exploitation
(`docker exec kali-mcp msfconsole -q`). **Not provisioned by this kit** — bring
your own attacker container/VM and attach it to the `aqira-range` network.
